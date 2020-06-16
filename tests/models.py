from django.db import models


class DJImporterModel(models.Model):
    """
    Base for test models that sets app_label, so they play nicely.
    """

    class Meta:
        app_label = 'tests'
        abstract = True

# ForeignKey
class ForeignKeyTarget(DJImporterModel):
    name = models.CharField(max_length=100)


class ForeignKeySource(DJImporterModel):
    name = models.CharField(max_length=100)
    target = models.ForeignKey(ForeignKeyTarget, related_name='sources',
                               help_text='Target', verbose_name='Target',
                               on_delete=models.CASCADE)
