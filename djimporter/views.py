from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from ico_monitoring.mixins import CustomContextMixin
from ico_monitoring.models import Membership, MonitoringScheme

from .models import ImportLog


# TODO(@slamora) decouple of CustomContextMixin
class ImportBase(CustomContextMixin, FormView):
    """
    view for import a file with Monitoring Sites

    """
    template_name = "ico_monitoring/importer/import_base.html"
    form_class = None   # should be overrided on child classes

    def form_valid(self, form):
        path = reverse_lazy('djimporter:importlog-detail', args=[form.log_id])
        return HttpResponseRedirect(path)


# TODO(@slamora) decouple of (MonitoringScheme, Membership, CustomContextMixin)
class BaseLogsImportMix(CustomContextMixin):
    """
    Is used for control the permitions and show the
    correct query
    """
    def get_queryset(self):
        if self.request.user.is_superuser:
            return ImportLog.objects.all().order_by('-created_at')
        else:
            mschemes = MonitoringScheme.objects.filter(
                memberships__user=self.request.user,
                memberships__role=Membership.PROJECT_COORDINATOR,
            )
            return ImportLog.objects.filter(
                monitoringscheme__in=mschemes
                ).order_by("-created_at")


class ListImportsView(BaseLogsImportMix, ListView):
    paginate_by = 20
    title = _("Import logs")


class ImportDetailView(BaseLogsImportMix, DetailView):
    subtitle = _("Import log detail")
