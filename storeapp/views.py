from django.shortcuts import render,redirect,get_object_or_404
from storeapp.models import Product,ProductGallery
from accounts.models import Category
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .models import Product
from django.db.models import Q
from cart.models import CartItem,Cart
from django.db.models import Sum



def storepage(request, category_slug=None):
    categories=None
    products= None
    print(category_slug)
    if category_slug!=None:
        print(category_slug)
        categories = get_object_or_404(Category,slug=category_slug)
        products =Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 1)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count=products.count
    else:
        products=Product.objects.all().filter(is_available=True)
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count=products.count
    context={
        'products':paged_products,
        'product_count':product_count
    }
    return render(request,'store.html',context)
def productdetails(request,category_slug,product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)
    
    print(request.session)
    total_quantity = 0
    #try:
      #  cart = Cart.objects.get(cart_id=_cart_id(request))
    #except Cart.DoesNotExist:
     #   pass
    #if cart:
     #  total_quantity = CartItem.objects.filter(
      # product=single_product,
      #      cart_id=cart,
       #     is_active=True
      # ).aggregate(total_quantity=Sum('quantity'))['total_quantity']
   # print('here printint total_quantity',total_quantity) 

        
    context={'single_product':single_product,
             'product_gallery':product_gallery,
             }
    return render(request,'store/productdetail.html',context)
def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword),is_available=True)
            print(products)
            product_count = products.count()
    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request, 'store.html', context)
