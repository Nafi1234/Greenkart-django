from django import forms
from  .models import Account,UserProfile,ReferralCoupon
from django.core.serializers import serialize
class Registration(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password',
        'class': 'form-control',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password'
    }))
    referral_code = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Enter Referral Code'
    }))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password', 'referral_code']
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # Store the request object
        super(Registration, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    def clean_referral_code(self):
        referral_code = self.cleaned_data.get('referral_code','')

        if referral_code:
            try:
                referral_coupon = ReferralCoupon.objects.get(code=referral_code, is_valid=True)
                referral_coupon_data = serialize('json', [referral_coupon])
                referral_coupon_json = referral_coupon_data[1:-1]  # Remove brackets from serialized data
                self.request.session['referral_code'] = referral_coupon_json
            except ReferralCoupon.DoesNotExist:
                raise forms.ValidationError('Invalid referral code.')

        return referral_code
    def clean_phone_number(self):
        phonenumber=self.cleaned_data['phone_number']
        if len(phonenumber) !=10:
            raise forms.ValidationError("enter phone number which is 10 digit")
        return phonenumber
    def clean(self):
        cleaned_data=super(Registration,self).clean()
        password=cleaned_data.get('password')
        confirm_password=cleaned_data.get('confirm_password')

        
        if password != confirm_password:
            raise forms.ValidationError (
                {'confirm_password': ["Passwords do not match."]}
                
            )
        return cleaned_data

    
class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    def clean_phone_number(self):
        phonenumber=self.cleaned_data['phone_number']
        if len(phonenumber) !=10:
            raise forms.ValidationError("enter phone number which is 10 digit")
        return phonenumber

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['address_line1', 'address_line2', 'city', 'state', 'country']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['address_line1'].widget.attrs['placeholder'] = 'Enter Address Line 1'
        self.fields['address_line2'].widget.attrs['placeholder'] = 'Enter Address Line 2'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
