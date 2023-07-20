from django import forms
from orders.models import Addaddress
class AddressForm(forms.ModelForm):
    class Meta:
     model = Addaddress
     fields = ['user','first_name', 'last_name', 'phone', 'email', 'address_line1', 'address_line2', 'country', 'state', 'city']