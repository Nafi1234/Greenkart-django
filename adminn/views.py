from django.shortcuts import render,redirect,get_object_or_404
from  django.contrib import messages,auth
from django.http import HttpResponse # Create your views here.
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from accounts.models import Category
from storeapp.models import Product,ProductGallery,Variation
from django.urls import reverse
from .forms import CategoryForm
from orders.models import OrderProduct,Order,Wallet
from accounts.models import Account
from django.db.models import Sum, F
from django.db import models
from django.db.models import FloatField
from .models import Coupon
from .forms import CouponForm
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.utils import timezone
import pdfkit
from django.db.models import F, ExpressionWrapper, FloatField
from decimal import Decimal
from django.contrib.auth import logout

from django.db.models import Count






def adminlogin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(request, email=email, password=password)
        if user is not None and user.is_active and user.is_superadmin:
            auth.login(request, user)
            messages.success(request, 'You are now logged in as a super admin.')
            return redirect('adminchart')  # Replace 'dashboard' with the URL of your admin dashboard view
        else:
            messages.error(request, 'Invalid login credentials or you are not a super admin.')
            return redirect('adminlogin')  # Redirect back to the admin login page

    if request.user.is_authenticated and request.user.is_superadmin:
        return redirect('adminchart')  # Redirect to the admin dashboard view if the user is already logged in and is a super admin

    return render(request, 'adminlogin.html')
def adminlogout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('adminlogin')

@login_required(login_url='adminlogin') 
def category(request):
    print('haiiiiiiiiiiiiiii')
    categories= Category.objects.all()
    print('here printing categories',categories)
    context={'categories':categories}
    return render(request,'category.html',context)
@login_required(login_url='adminlogin') 
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    return redirect(reverse('category'))
@login_required(login_url='adminlogin') 
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save(commit=False)
            offer_percentage = request.POST.get('offer')
            if offer_percentage and offer_percentage.strip():  # Check if offer_percentage is not empty or whitespace
                category.offer_percentage = float(offer_percentage)
            else:
                category.offer_percentage = 0  # Set default value if offer field is not provided or is empty
            category.save()
            return redirect('category')
        else:
            print(form.errors)
    else:
        form = CategoryForm()
    return render(request, 'category.html', {'form': form})
@login_required(login_url='adminlogin') 
def adminproduct(request):
    products=Product.objects.all()

    context={'products':products}
    return render(request,'adminproduct.html',context)
@login_required(login_url='adminlogin') 
def toggle_availability(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.is_available = not product.is_available  # Toggle the availability
    product.save()
    return redirect('adminproduct')


@login_required(login_url='adminlogin')
def add_product(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        slug =request.POST.get('slug')

        description = request.POST.get('description')
        price = int(request.POST.get('price'))
        image = request.FILES.get('image')
        stock = request.POST.get('stock')
        is_available = request.POST.get('is_available')== 'on'
        category_id = request.POST.get('category')
        offer = float(request.POST.get('offer', 0)) 

    # Convert the offer value to a float
    


        # Create a new Product object and save it
        product = Product(
            product_name=product_name,
            slug=slug,
            description=description,
            price=price,
            images=image,
            stock=stock,
            is_available=is_available,
            category_id=category_id,
            offer=offer
        )
        product.save()
        product_gallery_images = request.FILES.getlist('product_gallery')
        for gallery_image in product_gallery_images:
            product_gallery = ProductGallery(product=product, image=gallery_image)
            product_gallery.save()

        return redirect('adminproduct')  # Redirect to the appropriate page

    # Retrieve the available categories
    categories = Category.objects.all()

    return render(request, 'addproduct.html', {'categories': categories})
@login_required(login_url='adminlogin')
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_gallery = ProductGallery.objects.filter(product=product)

    categories = Category.objects.all()  # Assuming you have the Category model defined

    context = {
        'product': product,
        'product_gallery': product_gallery,
        'categories': categories
    }

    return render(request, 'admineditproduct.html', context)
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product_name = request.POST['product_name']
        slug = request.POST['slug']
        description = request.POST['description']
        price = int(request.POST.get('price'))
        image = request.FILES.get('image')
        stock = request.POST['stock']
        is_available = 'is_available' in request.POST
        offer = float(request.POST.get('offer', 0)) 
        category_id = request.POST['category']

        # Update the product fields
        product.product_name = product_name
        product.slug = slug
        product.description = description
        product.price = price
        if image:
            product.images = image
        product.stock = stock
        product.is_available = is_available
        product.offer=offer
        product.category_id = category_id
        product.save()

    return redirect('adminproduct') 
@login_required(login_url='adminlogin')
def user_management(request):
    accounts = Account.objects.all()
    context = {
        'accounts': accounts
    }
    return render(request, 'adminuser.html', context)
def adminorder(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        order_number = request.POST.get('order_number')
        new_status = request.POST.get('new_status')

        try:
            order = Order.objects.get(order_number=order_number)
            order.status = new_status
            order.save()
            print('newwww',order.status)
            return JsonResponse({'success': True})
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Order not found'})
    else:
        order_products = Order.objects.filter(is_ordered=True).order_by('-created_at')
        order = OrderProduct.objects.all()
        context = {'order_products': order_products, 'order': order}
        return render(request, 'adminorders.html', context)
@login_required(login_url='adminlogin') 
def delete_order(request, order_number):
    if request.method == 'POST':
        order = Order.objects.get(order_number=order_number)
        order_products = order.orderproduct_set.all()
        
        for order_product in order_products:
            product = order_product.product
            product.stock += order_product.quantity
            product.save()
        

        order.delete()
        return redirect('adminorder')
@login_required(login_url='adminlogin') 

def dashboard(request):
    # Retrieve the order products data
    order_products = OrderProduct.objects.all()

    # Get the selected date range from the request
    date_range = request.GET.get('date_range')
    # Set the default start and end dates
    end_date = timezone.now()  # Use the current datetime in the timezone of the database
    start_date = end_date - timedelta(days=7)  # Default to the past 7 days

    # Adjust the start and end dates based on the selected date range
    if date_range == 'daily':
        start_date = end_date - timedelta(days=1)
    elif date_range == 'weekly':
        start_date = end_date - timedelta(weeks=1)
    elif date_range == 'monthly':
        start_date = end_date - timedelta(days=30)  # Assuming 30 days in a month
    elif date_range == 'custom':
        print('haiiiiiiiiiiii')
        # Retrieve the custom start and end dates from the request parameters
        start_date_param = request.GET.get('start_date')
        end_date_param = request.GET.get('end_date')
        print('printing start_date_param',start_date_param)
        print('printing',end_date_param)
        # Parse the custom start and end dates if they are provided
        if start_date_param and end_date_param:

            try:
                print('start_date_param:', start_date_param)
                print('end_date_param:', end_date_param)
                start_date = datetime.strptime(start_date_param, '%m/%d/%Y').date()
                end_date = datetime.strptime(end_date_param, '%m/%d/%Y').date()
                print('start_date:', start_date)
                print('end_date:', end_date)
            except ValueError as e:
                print('ValueError:', str(e))
        # Handle invalid date formats here if needed
                pass
    print('here i am printing',end_date)
    # Filter the order products based on the selected date range
    filtered_order_products = order_products.filter(created_at__range=(start_date, end_date))
    top_selling_products = []
    print(filtered_order_products)
    grouped_order_products = OrderProduct.objects.filter(created_at__range=(start_date, end_date)).values('product').annotate(
    total_quantity_sold=Sum('quantity'),
    revenue=ExpressionWrapper(Sum(F('quantity') * F('product_price')), output_field=FloatField())
)
    top_products = grouped_order_products.order_by('-total_quantity_sold')[:5]
    for item in top_products:
        product_id = item['product']
        total_quantity_sold = item['total_quantity_sold']
        revenue = item['revenue']
        

    # Retrieve the corresponding product details based on the product_id
        product = Product.objects.get(id=product_id)
        product_details = { 
        'product_name': product.product_name,
        'total_quantity_sold': total_quantity_sold,
        'revenue': revenue
    }

    # Add the product details to the top_selling_products list
    top_selling_products.append(product_details)
    print(top_selling_products)

    # Calculate the total sales and total orders
    total_sales = sum(op.quantity * op.product_price for op in filtered_order_products)
    total_orders = len(filtered_order_products)

    # Calculate the average order value
    average_order_value = total_sales / total_orders if total_orders > 0 else 0

    # Pass the data to the template
    context = {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'average_order_value': average_order_value,
        'top_selling_products':top_selling_products
    }
    download = request.GET.get('download')
    if download:
        # Generate the PDF using the sales_report_partial.html template
        sales_report_html = render(request, 'salesreportpartial.html', context).content.decode('utf-8')
        pdf = pdfkit.from_string(sales_report_html, False, configuration=pdfkit.configuration(wkhtmltopdf='C:/Users/HP/Downloads/wkhtmltoxs/wkhtmltox/bin/wkhtmltopdf.exe'))

        # Set the response headers for file download
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

        # Write the PDF content to the response
        response.write(pdf)
        return response

    return render(request, 'admindashboard.html', context)

    
def coupon_list(request):
    coupons = Coupon.objects.all()
    form = CouponForm()
    return render(request, 'admincoupon.html', {'coupons': coupons,'form': form})

def add_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('coupon_list')
        else:
            print(form.errors)
            print(request.POST)
    else:
        form = CouponForm()
    coupons = Coupon.objects.all()  # Add this line to retrieve the updated list of coupons
    return render(request, 'admincoupon.html', {'coupons': coupons, 'form': form})

def edit_coupon(request):
    coupon = get_object_or_404(Coupon)
    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            return redirect('coupon_list')
    else:
        form = CouponForm(instance=coupon)
    return render(request, 'admincoupon.html', {'form': form, 'coupon': coupon})

def delete_coupon(request, coupon_id):
    print("Coupon ID:", coupon_id) 
    coupon = get_object_or_404(Coupon, id=coupon_id)
    print("Coupon Object:", coupon) 
    print(coupon_id)
    if request.method == 'POST':
        coupon.delete()
        print("Coupon deleted!") 
        return redirect('coupon_list')
    return render(request, 'admincoupon.html', {'coupon': coupon})
def list_variations(request):
    variations = Variation.objects.select_related('product')

    context = {
        'variations': variations
    }
    return render(request, 'adminvariation.html', context)
def add_variation(request):
    if request.method == 'POST':
        product_id = request.POST.get('product')
        variation_category = request.POST.get('variationCategory')
        variation_value = request.POST.get('variationValue')

        product = get_object_or_404(Product, id=product_id)

        variation = Variation.objects.create(
            product=product,
            variation_category=variation_category,
            variation_value=variation_value
        )

        return redirect('list_variations')

    products = Product.objects.filter(is_available=True)
    variation_categories = Variation._meta.get_field('variation_category').choices

    context = {
        'products': products,
        'variation_categories': variation_categories,
    }
    return render(request, 'addvariation.html', context)
def adminwallet(request):
    wallet = Wallet.objects.filter(is_available=True)
    context = {
        'wallet':wallet,
    }
    return render (request,'includes/adminwallet.html',context)
@login_required(login_url='adminlogin') 
def order_detail(request, order_number):
    print(order_number)
    order = Order.objects.get(order_number=order_number)
    print(order)
    order_products = order.orderproduct_set.all() 
    print('here printing order_prodcuts',order_products)
      
    context={
        'order':order,
        'order_products':order_products,
    }
    return render(request, 'adminorderproduct.html', context)
def update_refund_status(request, order_id):
    if request.method == 'POST':
        print('update_refund_status')
        order_product = get_object_or_404(OrderProduct, id=order_id)
        order_product.refund_status = 'Refunded'
        order_product.save()


            # Add the refunded amount to the user's wallet
        user_wallet, _ = Wallet.objects.get_or_create(user=order_product.user)
        user_wallet.balance +=  Decimal(str(order_product.product_price * order_product.quantity))
        user_wallet.save()

        return redirect('adminorder')  # Redirect to a success page or appropriate URL

    return redirect('my_orders')
@login_required(login_url='adminlogin') 
def adminchart(request):
    current_date = datetime.now().date()
    five_days_ago = current_date - timedelta(days=5)

# Step 2: Query the Order model to retrieve orders placed within the last 5 days
    last_five_days_orders = Order.objects.filter(created_at__gte=five_days_ago)

# Step 3: Group the orders by day and calculate the total sum of order_total per day
    orders_by_day = last_five_days_orders.values('created_at__date').annotate(total_sum=Sum('order_total'))

# Step 4: Create an array to store the total sums for each day
    total_sums_array = [0] * 5  # Initialize the array with zeros for all 5 days

# Step 5: Fill the array with the total sums for each day
    for data in orders_by_day:
        date = data['created_at__date']
        total_sum = data['total_sum']
        days_ago = (current_date - date).days
        total_sums_array[5 - days_ago - 1] = total_sum
    print(total_sums_array)
    
    total_users_count = Account.objects.count()
    print(total_users_count)
    totalproducts=Product.objects.count()
    totalorders=Product.objects.count()
# Step 6: Print or use the total_sums_array as needed
    context = {
        'total_sums_array': total_sums_array,
        'total_users_count':total_users_count,
        'totalproducts':totalproducts,
        'totalorders':totalorders
    }
    
    
    return render(request,'adminchart.html',context)