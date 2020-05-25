import json

from django.db import models


class AbstractBaseLog(models.Model):
    CREATED = 'created'
    RUNNING = 'running'
    FAILED = 'failed'
    COMPLETED = 'completed'
    STATUS_CHOICES = (
        (CREATED, 'CREATED'),
        (RUNNING, 'RUNNING'),
        (FAILED, 'FAILED'),
        (COMPLETED, 'COMPLETED'),
    )

    status = models.CharField(max_length=25, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.CharField(max_length=50)

    errors = models.TextField(blank=True)
    num_rows = models.IntegerField(null=True)
    input_file = models.CharField(max_length=100)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def list_errors(self):
        return json.loads(self.errors or "[]")


class ImportLog(AbstractBaseLog):
    pass
