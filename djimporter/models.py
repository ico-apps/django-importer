import json

from django.db import models

# TODO(@slamora) remove dependency with ico_monitoring
from ico_monitoring.models import MonitoringScheme


class Log(models.Model):
    concept = models.CharField(max_length=50)
    status = models.CharField(max_length=25)
    created_at = models.DateTimeField(auto_now=True)
    user = models.CharField(max_length=50)

    class Meta:
        abstract = True


class ImportLog(Log):
    errors = models.TextField(null=True)
    num_rows = models.IntegerField(null=True)
    input_file = models.CharField(max_length=100)
    monitoringscheme = models.ForeignKey(
        MonitoringScheme,
        on_delete=models.SET_NULL,
        null=True
    )

    def list_errors(self):
        return json.loads(self.errors or "[]")
