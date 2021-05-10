import json
import os

from django.utils.module_loading import import_string
from django.db.transaction import TransactionManagementError
from django.db import transaction
from background_task import background

from . import get_importlog_model

ImportLog = get_importlog_model()


@background(schedule=0)
def run_importer(csv_model, csv_filepath, log_id, context={}, delimiter=None, headers_mapping=None):
    """
    csv_model: should be string dotted_path e.g. 'djimporter.FooCsv'
    context: should be serializable
    """
    importer_class = import_string(csv_model)
    # mark task as running
    log = ImportLog.objects.get(id=log_id)
    log.status = ImportLog.RUNNING
    log.save()

    # run importer
    importer = importer_class(csv_filepath, context=context, delimiter=delimiter, headers_mapping=headers_mapping)
    importer.is_valid()
    importer.save()

    # update log with import result
    if importer.errors:
        log.status = ImportLog.FAILED
        log.errors = json.dumps(importer.errors)
    else:
        log.status = ImportLog.COMPLETED
        log.num_rows = len(importer.list_objs)
    log.save()

    # clean up
    os.remove(csv_filepath)
