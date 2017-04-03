from django.forms import ModelForm
from django.forms.models import inlineformset_factory

from .models import Invoice, LineItem

class InvoiceForm(ModelForm):
	class Meta:
		model = Invoice
		fields = "__all__"

class LineItemForm(ModelForm):
	class Meta:
		model = LineItem
		fields = "__all__"

LineItemFormset = inlineformset_factory(
	Invoice, LineItem,
	fields = ('name', 'description', 'price', 'quantity', 'taxable'),
	extra = 0
	)