from __future__ import unicode_literals
import os
from datetime import date
from decimal import Decimal

from django.conf import settings
#from localflavor.id_.forms import IDPhoneNumberField
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models
from django.template.defaultfilters import slugify

__all__ = ['Client', 'Company', 'Terms', 'LineItem', 'InvoiceManager', 'Invoice', 'Stylesheet', 'Item']

class Entity(models.Model):
	name = models.CharField(max_length=128)
	contact_person = models.CharField(max_length=128, blank=True)
	address = models.CharField(max_length=100)
	city = models.CharField(max_length=50)
	state = models.CharField(max_length=25)
	zip_code = models.CharField(max_length=10, blank=True)
	phone_number = PhoneNumberField()
	email = models.EmailField()

	class Meta:
		abstract = True

	def __unicode__(self):
		return self.name

	def full_address(self):
		return "%s %s %s %s" %(self.address, self.city, self.state, self.zip_code)

class Client(Entity):
	project = models.CharField(max_length=128, blank=True)

	@models.permalink
	def get_absolute_url(self):
		return ('client', (), {'id':self.id})

	def receipts_to_date(self):
		items = LineItem.objects.filter(invoice__client=self).only("price", "quantity", "taxable", "invoice", "invoice__company__tax__rate").select_related("invoice__company")
		total = 0
		for item in items:
			total += item.total()
		return total

class Company(Entity):
	website = models.URLField(blank=True)
	numbering_prefix = models.CharField(max_length=10, unique=True)
	billing_email = models.EmailField(blank=True)
	tax_rate = models.DecimalField(max_digits=4, decimal_places=2)

	class Meta:
		verbose_name_plural = "Companies"

	@models.permalink
	def get_absolute_url(self):
		return ('company', (), {'id':self.id})

	def tax_multiplayer(self):
		return self.tax_rate/100 + 1

class Terms(models.Model):
	name = models.CharField(max_length=128)
	description = models.TextField(max_length=256)

	class Meta:
		verbose_name_plural = "Terms"

	def __unicode__(self):
		return self.name

class AbstractItem(models.Model):
	name = models.CharField(max_length=128, blank=True)
	description = models.CharField(max_length=256, blank=True)
	cost = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
	price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
	taxable = models.BooleanField()

	class Meta:
		abstract = True

	def __unicode__(self):
		return unicode(self.name)

class LineItem(AbstractItem):
	item = models.ForeignKey("Item", blank=True, null=True)
	quantity = models.DecimalField(max_digits=7, decimal_places=2)
	invoice = models.ForeignKey("Invoice", related_name="line_item", editable=False)

	class Meta:
		verbose_name = "Line Item"
		verbose_name_plural = "Line Items"

	def ext_prices(self):
		ext_price = self.price * self.quantity
		return ext_price.quantize(Decimal('.01'))

	def save(self, *args, **kwargs):
		if self.item_id is not None:
			self.name = self.item.name
			self.description = self.item.description
			self.cost = self.item.cost
			self.price = self.item.price
			self.taxable = self.item.taxable
		super(LineItem, self).save(*args, **kwargs)

class InvoiceManager(models.Manager):
	def get_query_set(self):
		return super(InvoiceManager, self).get_query_set().none()

class Invoice(models.Model):
	objects = models.Manager()
	manager = InvoiceManager()
	STATUS_CHOICES = (
		("unsent", "Unsent"),
		("sent", "Sent"),
		("partial", "Partial"),
		("paid", "Paid"),
		("other", "Other"),
		)
	company = models.ForeignKey(Company, related_name='invoices')
	client = models.ForeignKey(Client, related_name='invoices')
	invoice_date = models.DateField(default=date.today)
	invoice_number = models.CharField(max_length=20, blank=True)
	due_date = models.DateField(default=date.today)
	status = models.CharField(max_length=10, choices = STATUS_CHOICES)
	status_notes = models.CharField(max_length=128, blank=True)
	terms = models.ForeignKey(Terms)

	@models.permalink
	def get_absolute_url(self):
		return ('invoice', (), {'id':self.invoice_number})

	def __unicode__(self):
		return self.invoice_number

	def get_invoice_number(self):
		return "%s%05d" % (self.company.numbering_prefix, self.id)

	def taxable_amount(self):
		taxable = 0
		for line in self.line_items.all():
			if line.taxable:
				taxable += line.ext_price()
		return taxable

	def tax(self):
		tax = self.taxable_amount() * self.company.tax_rate/100
		return tax.quantize(Decimal('.01'))

	def subtotal(self):
		subtotal = 0
		for line in self.line_items.all():
			subtotal += line.ext_price()
		return subtotal

	def total(self):
		total = 0
		for line in self.line_items.all():
			total += line.total()
		return total

	def save(self, force_insert=False, force_update=False):
		super(Invoice, self).save(force_insert, force_update)
		if not self.invoice_number:
			self.invoice_number = self.get_invoice_number()
			self.save()

def stylesheet_upload(instance, filename):
	file, ext = os.path.splitext(filename)
	file_slug = '%s%s' %(slugify(file), ext)
	company_id = unicode(instance.company.id)
	upload_dir = settings.get("INVENTORY_UPLOAD_DIR", "inventory").strip("/")
	return os.path.join(upload_dir, "stylesheets", company_id, file_slug)

class Stylesheet(models.Model):
	company = models.ForeignKey("Company", related_name="stylesheet")
	name = models.CharField(max_length=128)
	description = models.CharField(max_length=256)
	stylesheet = models.FileField(upload_to=stylesheet_upload)
	introduction_text = models.TextField(max_length=256, blank=True)
	feedback_text = models.TextField(max_length=256, blank=True)
	misc_text = models.TextField(max_length=256, blank=True)
	thank_you_text = models.TextField(max_length=256, blank=True)

class Item(AbstractItem):
	pass