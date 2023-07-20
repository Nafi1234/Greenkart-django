from django import forms
from accounts.models import Category
from .models import Coupon
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name','slug','description','cat_image','offer_percentage']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['offer_percentage'].required = False
class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['coupon_code', 'discount_amount', 'min_spend', 'valid_from', 'valid_to']
        widgets = {
            'valid_from': forms.DateInput(attrs={'type': 'date'}),
            'valid_to': forms.DateInput(attrs={'type': 'date'}),
        }