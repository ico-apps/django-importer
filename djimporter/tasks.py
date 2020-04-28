import json
import os

from django.db import transaction

from .models import ImportLog


class TaskGenericImporter(object):
    def __init__(self, path_file, context={}, log_id=None):
        self.context = context
        self.path_file = path_file['path']
        self.log_id = log_id
        self.errors = []
        self.save()

    def save_generic(self):
        csv = self.csv_model(self.path_file, context=self.context)
        csv.is_valid()
        csv.save()
        self.errors = csv.errors
        self.num_rows = len(csv.list_objs)

    def save(self):
        with transaction.atomic():
            self.save_generic()

        os.remove(self.path_file)
        log = ImportLog.objects.get(id=self.log_id)
        log.errors = json.dumps(self.errors)
        log.num_rows = self.num_rows
        if self.errors:
            log.status = "Errors"
        else:
            log.status = "Finished"
        log.save()
