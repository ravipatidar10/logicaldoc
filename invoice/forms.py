from django.forms import ModelForm

from .models import Invoice


class InvoiceForm(ModelForm):

    class Meta:
        model = Invoice

        fields = [
            'invoice_description',
        ]
        labels = {
            'invoice_description': 'Invoice Description'
        }
