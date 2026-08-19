from django import forms

from app import models


class WareExcelUploadForm(forms.Form):
    file = forms.FileField(
        label='Файл',
        help_text='Только формат .xlsx и не более 10 МБ',
    )

    def clean_file(self):
        f = self.cleaned_data['file']
        if not f.name.lower().endswith('.xlsx'):
            raise forms.ValidationError('Поддерживаются только файлы .xlsx')

        if f.size > 10 * 1024 * 1024:
            raise forms.ValidationError('Файл слишком большой(максимум 10 МБ)')
        return f


class WareForm(forms.ModelForm):
    housing = forms.ModelChoiceField(
        queryset=models.Housing.objects.all(),
        required=False,
        label='Корпус'
    )
    room = forms.ModelChoiceField(
        queryset=models.Room.objects.none(),
        required=False,
        label='Кабинет'
    )
    location = forms.ModelChoiceField(
        queryset=models.Location.objects.none(),
        required=False,
        label='Локация'
    )

    class Meta:
        model = models.Ware
        fields = ['status', 'category', 'project']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and self.instance.location:
            # Устанавливаем начальные значения
            location = self.instance.location
            room = location.room
            housing = room.housing

            self.fields['housing'].initial = housing.id
            self.fields['room'].queryset = models.Room.objects.filter(housing=housing.id)
            self.fields['room'].initial = room.id
            self.fields['location'].queryset = models.Location.objects.filter(room=room.id)
            self.fields['location'].initial = location.id
        else:
            self.fields['room'].queryset = models.Room.objects.none()
            self.fields['location'].queryset = models.Location.objects.none()

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.cleaned_data.get('location'):
            instance.location = self.cleaned_data['location']
        elif self.cleaned_data.get('room'):
            # Создаём локацию если её нет
            location, _ = models.Location.objects.get_or_create(
                room=self.cleaned_data['room'],
                defaults={'name': f'Локация {self.cleaned_data["room"].name}'}
            )
            instance.location = location

        if commit:
            instance.save()
        return instance

