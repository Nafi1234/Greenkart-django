from django.shortcuts import render
from storeapp.models import Product
def home(request):
    products = Product.objects.filter(is_available=True).order_by('-created_date')[:6]
    context={
        'products':products
    }
    return render(request,'index.html',context)