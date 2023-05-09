from django.core.files.storage import default_storage
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, DeleteView
from django.views.generic.list import ListView

from . import get_importlog_model
from .forms import CsvImportForm, UploadDataCsvGuessForm
from .tasks import run_importer

ImportLog = get_importlog_model()


class ListImportsView(ListView):
    model = ImportLog
    template_name = "djimporter/importlog_list.html"
    url_detail = 'djimporter:importlog-detail'
    url_delete = 'djimporter:importlog-delete'

    def get_context_data(self):
        context = super().get_context_data()
        context.update({
            'url_detail': self.url_detail,
            'url_delete': self.url_delete,
        })
        return context

class ImportDetailView(DetailView):
    model = ImportLog
    template_name = "djimporter/importlog_detail.html"

class ImportLogGetView(View):
    
    def get(self, request, *args, **kwargs):
        import_log = ImportLog.objects.get(pk=self.kwargs['pk'])
        return JsonResponse({'status':import_log.status, 'id':self.kwargs['pk']}, safe=False)

class ImportDeleteView(DeleteView):
    model = ImportLog
    template_name = "djimporter/importlog_confirm_delete.html"

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

        # Create a dict that maps current file headers with expected headers names (fields and extra_fiels in Meta).
        # The dict has the following format:
        # {
        #   file_header_value1: importer_header_value1,
        #   file_header_value2: importer_header_value2,
        #   ...
        # }
        header_mapping = {}
        for field_name in form.cleaned_data:
            if field_name.startswith('header_'):
                header_mapping[form.cleaned_data[field_name]] = field_name.replace('header_', '', 1)

        kwargs = {}
        if 'delimiter' in form.cleaned_data:
            kwargs['delimiter'] = form.cleaned_data['delimiter']
            print('Hi ha delimiter')

        if len(header_mapping) > 0:
            kwargs['headers_mapping'] = header_mapping
            print('Hi ha header mapping')

        print(form.files['upfile'])
        self.task_log = self.create_import_task(form.files['upfile'], **kwargs)

        return HttpResponseRedirect(self.get_success_url())

    def create_import_task(self, csv_file, delimiter=None, headers_mapping=None):
        importer_class = self.get_importer_class()
        task_log = self.create_import_log(csv_file)

        # save file to persistent storage
        name = default_storage.save(csv_file.name, csv_file)
        csv_path = default_storage.path(name)

        dotted_path = "{module}.{name}".format(
            module=importer_class.__module__,
            name=importer_class.__name__,
        )

        context = self.get_importer_context()
        run_importer(dotted_path, csv_path, task_log.id, context=context,
                     delimiter=delimiter, headers_mapping=headers_mapping)

        return task_log

    def create_import_log(self, csv_file):
        task_log = ImportLog.objects.create(
            status=ImportLog.CREATED,
            user=str(self.request.user),
            input_file=csv_file.name,
        )
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


class ImportFormGuessCsvView(ImportFormView):
    form_class = UploadDataCsvGuessForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        headers = self.importer_class.Meta.fields.copy()
        if hasattr(self.importer_class.Meta, 'extra_fields'):
            headers.extend(self.importer_class.Meta.extra_fields)
        kwargs.update({
            'headers': headers
        })
        return kwargs