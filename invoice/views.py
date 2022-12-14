from datetime import datetime
import json
import os

from django.db import transaction
from django.shortcuts import render, redirect, HttpResponse
from django.template.loader import render_to_string
from django.conf import settings

from weasyprint import HTML
import requests
from requests.auth import HTTPBasicAuth

from .forms import InvoiceForm
from .models import Invoice

def create_invoice(request):
    if request.method == 'POST':
        error_msg = ''
        request_data = request.POST
        with transaction.atomic():
            form = InvoiceForm(request_data)
            if form.is_valid():

                invoice_obj = form.save()

                template = render_to_string(
                    'invoice.html', {'invoice_description': request_data.get('invoice_description')})
                HTML(string=template).write_pdf(target=f"{request_data.get('invoice_description')}.pdf")
                f = open(f"{request_data.get('invoice_description')}.pdf", 'rb')

                auth = HTTPBasicAuth(username='admin', password='admin')
                payload = {"language":"en","fileName":f"{request_data.get('invoice_description')}.pdf","folderId":4 }

                files = { 
                    'document': (None, json.dumps(payload), 'application/json'),
                    'content': (os.path.basename(settings.BASE_DIR), f, 'application/octet-stream')
                    }
                
                headers = {'Content-Type': 'multipart/form-data'}
                res = requests.post(
                    'http://localhost:8080/services/rest/document/create', 
                    headers=headers, 
                    files=files, 
                    auth=auth
                )
                os.remove(f"{request_data.get('invoice_description')}.pdf")
                if res.status_code == 200:
                    logical_doc_id = res.json().get('id')
                    invoice_obj.logical_doc_id = logical_doc_id
                    invoice_obj.save()
                    return redirect('list_invoices')
                else:
                    invoice_obj.delete()
                    error_msg = res.text
                    if not error_msg:
                        error_msg = 'something went wrong'
                    return render(request, 'create_invoice.html', {'form': form, 'error_msg': error_msg}) 
            else:
                error_msg = 'Invalid entries'
                return render(request, 'create_invoice.html', {'form': form, 'error_msg': error_msg})
    form = InvoiceForm()
    return render(request, 'create_invoice.html', {'form': form})

def list_invoices(request):
    invoices = Invoice.objects.all()
    return render(request, 'list_invoices.html', {'invoices': invoices})

def get_invoice_doc(request):
    logical_doc_id = request.GET.get('logical_doc_id')
    auth = HTTPBasicAuth(username='admin', password='admin')
    res = requests.get(
        f"http://localhost:8080/services/rest/document/getContent?docId={logical_doc_id}",
        auth=auth
    )
    invoice = Invoice.objects.get(logical_doc_id=logical_doc_id)
    response = HttpResponse(res.content, content_type='application/pdf')
    response['Content-Disposition'] = f'inline;filename={invoice.invoice_description}_{logical_doc_id}.pdf'
    return response
