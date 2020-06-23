import os

from django.conf import settings
from django.core.files.storage import default_storage
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, DeleteView
from django.views.generic.list import ListView

from . import get_importlog_model
from .forms import CsvImportForm
from .tasks import run_importer

ImportLog = get_importlog_model()


class ListImportsView(ListView):
    model = ImportLog


class ImportDetailView(DetailView):
    model = ImportLog


class ImportDeleteView(DeleteView):
    model = ImportLog

    def get_success_url(self, *args, **kwargs):
        return reverse('djimporter:importlog-list')


class ImportFormView(FormView):
    form_class = CsvImportForm
    importer_class = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        importer_class = self.get_importer_class()
        importer = importer_class('')
        context['importer'] = importer
        return context

    def form_valid(self, form):
        """
        After calling this method, valid form will be available on `self.form`
        """
        # store valid form to allow other methods access it
        # e.g. get_importer_context
        self.form = form
        self.task_log = self.create_import_task(form.files['upfile'])

        return HttpResponseRedirect(self.get_success_url())

    def create_import_task(self, csv_file):
        importer_class = self.get_importer_class()

        task_log = ImportLog.objects.create(
            status=ImportLog.CREATED,
            user=str(self.request.user),
            input_file=csv_file.name,
        )

        # save file to persistent storage
        name = os.path.join(settings.MEDIA_ROOT, csv_file.name)
        csv_path = default_storage.save(name, csv_file)

        dotted_path = "{module}.{name}".format(
            module=importer_class.__module__,
            name=importer_class.__name__,
        )

        context = self.get_importer_context()
        run_importer(dotted_path, csv_path, task_log.id, context=context)

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

    def get_importer_context(self):
        return {}

    def get_success_url(self):
        return reverse('djimporter:importlog-detail', kwargs={'pk': self.task_log.id})
