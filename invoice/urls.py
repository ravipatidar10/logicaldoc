from django.urls import path

from .views import *

urlpatterns = [
    path('create_invoice/', create_invoice, name='create_invoice'),
    path('', list_invoices, name='list_invoices'),
    path('get_invoice_doc', get_invoice_doc, name='get_invoice_doc'),
]
