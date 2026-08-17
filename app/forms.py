from django import forms


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
