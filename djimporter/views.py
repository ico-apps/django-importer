import os

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from .forms import CsvImportForm
from .models import ImportLog
from .tasks import run_importer


class ListImportsView(ListView):
    model = ImportLog


class ImportDetailView(DetailView):
    model = ImportLog


class ImportFormView(FormView):
    form_class = CsvImportForm
    importer_class = None

    def form_valid(self, form):
        task_log = self.create_import_task(form.files['upfile'])
        return redirect('djimporter:importlog-detail', pk=task_log.id)

    def create_import_task(self, csv_file):
        importer_class = self.get_importer_class()

        task_log = ImportLog.objects.create(
            status=ImportLog.CREATED,
            user=self.request.user,
            input_file=csv_file.name,
        )

        # save file to persistent storage
        name = os.path.join(settings.MEDIA_ROOT, csv_file.name)
        csv_path = default_storage.save(name, csv_file)

        dotted_path = "{module}.{name}".format(
            module=importer_class.__module__,
            name=importer_class.__name__,
        )

        run_importer(dotted_path, csv_path, task_log.id)

        return task_log

    def get_importer_class(self):
        """
        Return the class to use for the importer.
        Defaults to using `self.importer_class`.

        """
        assert self.importer_class is not None, (
            "'%s' should either include a `importer_class` attribute, "
            "or override the `get_serializer_class()` method."
            % self.__class__.__name__
        )

        return self.importer_class
