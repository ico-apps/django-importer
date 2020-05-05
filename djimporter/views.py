from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import ImportLog


class ListImportsView(ListView):
    model = ImportLog


class ImportDetailView(DetailView):
    model = ImportLog
