from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^invoices/(?P<id>[\w-]+)/edit$', views.edit_invoice, name="edit_invoice"),
    url(r'^invoices/(?P<id>[\w-]+)/add_line$', views.add_line, name="add_line"),
    url(r'^invoices/(?P<id>[0-9]+)$', views.view_invoice, name="invoice"),
    url(r'^company/(?P<id>[\d]+)/$', views.company_overview, name="company"),
    url(r'^client/(?P<id>[\d]+)/$', views.client_overview, name="client"),
    url(r'^company/(?P<id>[\d]+)/invoices/(?P<page>[\d]*)$', views.company_invoices, name="company_invoices"),
    url(r'^client/(?P<id>[\d]+)/invoices/(?P<page>[\d]*)$', views.client_invoices, name="client_invoices"),
    url(r'^invoices/(?P<id>[\w-]+)$', views.view_invoice, name="invoice"),
    url(r'^$', views.index, name="invoice"),
]
