from django import forms
from django.core.validators import FileExtensionValidator


class CSVFileField(forms.FileField):
    validators = [FileExtensionValidator(allowed_extensions=['csv'])]
    widget = forms.FileInput(attrs={'accept': ".csv"})


class CsvImportForm(forms.Form):
    upfile = CSVFileField(label='CSV file')
