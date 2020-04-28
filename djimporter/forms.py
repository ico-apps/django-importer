import os
import string
import random

from django import forms
from django.core.validators import FileExtensionValidator
from django.core.files.storage import default_storage
from django.contrib.auth import get_user_model
from django.conf import settings

from .models import ImportLog
from . import tasks


User = get_user_model()


class CSVFileField(forms.FileField):
    validators = [FileExtensionValidator(allowed_extensions=['csv'])]
    widget = forms.FileInput(attrs={'accept': ".csv"})


class UploadForm(forms.Form):
    mpfile = CSVFileField(label='CSV file')


class TempFile(dict):
    def __init__(self, file, **kwargs):
        self.original_name = file.name
        self.name = default_storage.get_available_name(self.original_name)
        self.path = os.path.join(settings.MEDIA_ROOT, self.name)

        items = {
            'path': self.path,
            'original_name': self.original_name,
            'name': self.name
        }
        super().__init__(items, **kwargs)

        self.save(file)

    def save(self, file):
        with default_storage.open(self.path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

    def delete(self):
        os.remove(self.path)



class BaseImportMix(forms.Form):
    mscheme = None

    def create_log(self):
        concept = "Import %s" % self.input_file
        log = ImportLog.objects.create(
            concept=concept,
            status="In progress",
            input_file=self.input_file,
            monitoringscheme=self.mscheme,
            user=self.user
        )
        return log.id


class UploadGenericForm(BaseImportMix):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    mpfile = CSVFileField(label='CSV file')
    model_csv = None
    name_file = "mpfile"

    def clean_mpfile(self):
        file_csv = self.files[self.name_file]
        file_path = TempFile(file_csv)
        self.input_file = self.files[self.name_file].name
        self.log_id = self.create_log()
        self.task(file_path, log_id=self.log_id)

