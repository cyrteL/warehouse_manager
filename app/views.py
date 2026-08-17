import logging
from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, UpdateView

from .forms import WareExcelUploadForm
from .models import Ware
#from .parser.excel_in import parse_inventory_xlsx #задатки под будущий парсер

logger = logging.getLogger(__name__)


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
    fields = ['status', 'category', 'project', 'location']
    success_url = reverse_lazy('app:list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Изделие "{self.object.name}" обновлено.')
        return response


#Это будет выгрузка с экселя, но парсера пока нет
'''
class WareExcelUploadView(View):
    template_name = 'app/ware_upload.html'

    def get(self, request):
        return render(request, self.template_name, {'form': WareExcelUploadForm()})

    def post(self, request):
        form = WareExcelUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form}, status=400)

        result = parse_inventory_xlsx(form.cleaned_data['file'])

        if not result.rows and result.errors:
            for err in result.errors[:20]:
                messages.error(request, err)
            return render(request, self.template_name, {'form': form}, status=400)

        created, updated = 0, 0
        try:
            with transaction.atomic():
                for row in result.rows:
                    obj, was_created = Ware.objects.update_or_create(
                        inventory=row.inventory,
                        defaults={
                            'name': row.name,
                            'quantity': row.quantity,
                            'price': row.price,
                            'accounting_code': row.accounting_code,
                            'source_department': row.source_department,
                        },
                    )
                    created += was_created
                    updated += not was_created
        except Exception as exc:
            logger.exception('Ware Excel import failed')
            messages.error(request, f'Импорт прерван из-за ошибки: {exc}')
            return render(request, self.template_name, {'form': form}, status=500)

        messages.success(request, f'Импорт завершён: добавлено {created}, обновлено {updated}.')
        if result.errors:
            messages.warning(request, f'Пропущено строк с ошибками: {len(result.errors)}.')
            for err in result.errors[:20]:
                messages.warning(request, err)

        return redirect('app:list')
'''
