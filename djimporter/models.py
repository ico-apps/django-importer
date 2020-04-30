from django.db import models


class AbstractBaseLog(models.Model):
    concept = models.CharField(max_length=50)
    status = models.CharField(max_length=25)
    created_at = models.DateTimeField(auto_now=True)
    user = models.CharField(max_length=50)

    class Meta:
        abstract = True
