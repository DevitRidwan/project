from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'invoices/(?P<id>[\w-]+)$', views.view_invoice, name="invoice"),
]
