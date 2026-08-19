import logging
from dataclasses import dataclass, field

from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, UpdateView

from .forms import WareExcelUploadForm, WareForm
from .models import Ware, Room, Location
from .parser.parse_inventory import parse_inventory_file
from app.parser import fields_names as fnames

#from .parser.excel_in import parse_inventory_xlsx #задатки под будущий парсер


logger = logging.getLogger(__name__)


@dataclass
class ParseResult:
    rows: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class WareListView(ListView):
    model = Ware
    template_name = 'app/ware_list.html'
    context_object_name = 'wares'
    paginate_by = 50

    def get_queryset(self):
        return (
            Ware.objects.visible()
            .select_related('category', 'project', 'location', 'location__room', 'location__room__housing', 'supplier')
        )


class WareUpdateView(UpdateView):
    model = Ware
    form_class = WareForm
    success_url = reverse_lazy('app:list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Изделие "{self.object.name}" обновлено.')
        return response


class WareExcelUploadView(View):
    template_name = 'app/ware_upload.html'

    def get(self, request):
        return render(request, self.template_name, {'form': WareExcelUploadForm()})

    def post(self, request):
        form = WareExcelUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form}, status=400)

        try:
            # Парсим файл
            rows = list(parse_inventory_file(form.cleaned_data['file']))

            if not rows:
                messages.warning(request, 'Файл успешно прочитан, но данные не найдены.')
                return render(request, self.template_name, {'form': form})

        except Exception as exc:
            logger.exception('Ware Excel import failed')
            messages.error(request, f'Ошибка при чтении файла: {exc}')
            return render(request, self.template_name, {'form': form}, status=400)

        created, updated = 0, 0
        errors = []

        try:
            with transaction.atomic():
                for row in rows:
                    try:
                        # Ищем по инвентарному номеру
                        inventory = row.get(fnames.INVENTORY)
                        if not inventory:
                            errors.append(f'Пропущена строка {row.get("row_num")}: нет инвентарного номера')
                            continue

                        # Получаем или создаём запись
                        obj, was_created = Ware.objects.update_or_create(
                            inventory=inventory,
                            defaults={
                                'name': row.get(fnames.NAME, '')[:255],
                                'quantity': row.get(fnames.QUANTITY, 0),
                                'price': row.get(fnames.PRICE, 0.0),
                                'location': None
                            }
                        )

                        if was_created:
                            created += 1
                        else:
                            updated += 1

                    except Exception as e:
                        errors.append(f'Ошибка в строке {row.get("row_num")}: {str(e)}')
                        logger.exception(f'Ошибка при импорте строки {row.get("row_num")}')

        except Exception as exc:
            logger.exception('Ware Excel import failed')
            messages.error(request, f'Импорт прерван из-за ошибки: {exc}')
            return render(request, self.template_name, {'form': form}, status=500)

        messages.success(request, f'Импорт завершён: добавлено {created}, обновлено {updated}.')

        if errors:
            messages.warning(request, f'Пропущено строк с ошибками: {len(errors)}.')
            for err in errors[:10]:
                messages.warning(request, err)

        return redirect('app:list')


def get_rooms_by_housing(request, housing_id):
    """Возвращает комнаты для выбранного корпуса"""
    rooms = Room.objects.filter(housing_id=housing_id).values('id', 'name')
    return JsonResponse(list(rooms), safe=False)


def get_locations_by_room(request, room_id):
    """Возвращает локации для выбранной комнаты"""
    locations = Location.objects.filter(room_id=room_id).values('id', 'name')
    return JsonResponse(list(locations), safe=False)

