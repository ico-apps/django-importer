from django import forms
from django.core.validators import FileExtensionValidator


class CSVFileField(forms.FileField):
    validators = [FileExtensionValidator(allowed_extensions=['csv'])]
    widget = forms.FileInput(attrs={'accept': ".csv"})


class CsvImportForm(forms.Form):
    upfile = CSVFileField(label='CSV file')
    warning_mode = forms.BooleanField(
        label='Allow partial imports (warn user instead of fail)',
        required=False,
    )


class UploadDataCsvGuessForm(CsvImportForm):
    delimiter = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.headers = kwargs.pop("headers")
        self.json_fields = kwargs.pop("json_fields")
        super().__init__(*args, **kwargs)

        # Add a field for each expected header
        for header in self.headers:
            self.fields['header_' + header] = forms.CharField(label=header, widget=forms.Select())

        for field in self.json_fields:
            self.fields['json_' + field] = forms.CharField(label=field, widget=forms.SelectMultiple())

    def clean_delimiter(self):
        delimiter = self.cleaned_data["delimiter"]
        if delimiter == '<Tab>':
            return '\t'
        elif delimiter == '<Space>':
            return ' '
        return delimiter
