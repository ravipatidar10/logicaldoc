from django.db import models


class Invoice(models.Model):
    invoice_description = models.CharField(max_length=500)
    logical_doc_id = models.IntegerField(default=None, null=True, blank=True)
