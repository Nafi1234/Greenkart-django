from django.shortcuts import render,redirect,get_object_or_404
from storeapp.models import Product,Variation
from .models import Cart,CartItem
from storeapp.models import Variation
from django .core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from accounts.models  import UserProfile
from orders.models import Addaddress
from .forms import AddressForm
from django.utils import timezone
from adminn.models import Coupon
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.urls import reverse

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
        print("///////////////////////////////////////****",cart)
    return cart
def add_cart(request, product_id):
    current_user = request.user
    print('nasfiiiiiiiiiiiiiii',current_user)
    product = Product.objects.get(id=product_id) #get the product
    # If the user is authenticated
    print('here printing cart_id@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',request.session.get('cart')  ,request.session)
    if current_user.is_authenticated:
        print('naafffffffffffi',current_user)
        product_variation = []
        if request.method == 'POST':
            print(request.POST)
            for item in request.POST:
                key = item
                value = request.POST[key]
                print('key',key)
                print('value',value)

                try:
                    print("entered the try")
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    print(variation)
                    product_variation.append(variation)
                    print('//////////////////',product_variation)
                except:
                    print('except')
                    pass

 
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        print(is_cart_item_exists)
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            print('carrtitem_________________________________________',cart_item)
            cart_item_sum = cart_item.aggregate(total_quantity=Sum('quantity'))['total_quantity']
            if cart_item_sum is None or cart_item_sum < product.stock:
                ex_var_list = []
                id = []
                print('before',ex_var_list)
                print('afterrrrrrrrrrrrrrrrrrrrrrr')

                for item in cart_item:
                    existing_variation = item.variations.all()
                    print('existing_variation',existing_variation)
                    ex_var_list.append(set(existing_variation))
                    print('ex_var_list',ex_var_list)
                    id.append(item.id)
            #print([product_variation[1],product_variation[0]],'---------------------------------------',ex_var_list)
                    product_variation_set = set(product_variation)

                if   product_variation_set in ex_var_list:
                # increase the cart item quantity
                    print('new ex_varlist-----------------------------------',ex_var_list)
                    index = ex_var_list.index(product_variation_set)
                    item_id = id[index]
                    item = CartItem.objects.get(product=product, id=item_id)
                    item.quantity += 1
                    item.save()

                else:
                    item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                    if len(product_variation) > 0:
                        item.variations.clear()
                        item.variations.add(*product_variation)
                    item.save()
            else:
                return HttpResponseRedirect(reverse('cart') + '?message=out_of_stock')
            

                redirect('cart')
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation) 
            cart_item.save()
        return redirect('cart')
    # If the user is not authenticated
    else:
        print('gooooooooooooooooooooooooooooooooooody')
        
        product_variation = []

        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except Variation.DoesNotExist:
                    pass

        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))

            cart.save()

        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()

        if is_cart_item_exists:
            
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            print(product.stock)
            print('haiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
            cart_item_sum = cart_item.aggregate(total_quantity=Sum('quantity'))['total_quantity']

            print('here printing cart_item_sum', cart_item_sum)
            
            if cart_item_sum is None or cart_item_sum < product.stock:
                ex_var_list = []
                id = []

                for item in cart_item:
                    existing_variation = item.variations.all()
                    ex_var_list.append(set(existing_variation))
                    id.append(item.id)

                    print("printing the existing value", ex_var_list)

                product_variation_set = set(product_variation)

                if product_variation_set in ex_var_list:
        # Increase the cart item quantity
                    index = ex_var_list.index(product_variation_set)
                    item_id = id[index]
                    item = CartItem.objects.get(product=product, id=item_id)
                    item.quantity += 1
                    item.save()
                else:
                    item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                    if len(product_variation) > 0:
                        item.variations.clear()
                        item.variations.add(*product_variation)
                    item.save()
            else:
                #messages.error(request, 'Out of stock.')
                return HttpResponseRedirect(reverse('cart') + '?message=out_of_stock')
                return redirect('cart')        
        else:
            print("cart", cart, "product", product)

            cart_item = CartItem.objects.create(
        product=product,
        quantity=1,
        cart=cart,
    )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()

    return redirect('cart')


def remove_cart(request,product_id,cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')
def remove_cart_items(request,product_id,cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')
    
        
def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.selling_price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass 

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax'       : tax,
        'grand_total': grand_total,
    }
    return render(request, 'cart.html', context)
@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.selling_price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass #just ignore
    userprofile=None
    try:
        
        userprofile = UserProfile.objects.get(user=request.user)
    except ObjectDoesNotExist:
        pass
    try:
        latest_addresses = Addaddress.objects.filter(user=request.user).order_by('-id')[:2]
    except Addaddress.DoesNotExist:
        latest_addresses = []

    addresses_with_fields = [
        {
            'address': address,
            'fields': address.get_all_fields()
        }
        for address in latest_addresses
    ]
    print(userprofile)
    context = {
        'total': total,
        'userprofile':userprofile,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax'       : tax,
        'grand_total': grand_total,
         'addresses_with_fields':addresses_with_fields
    }
    return render(request, 'checkout.html', context)
@login_required(login_url='login')
def add_address(request):
    
    if request.method == 'POST':
        print('asrewwwwwwwwwwwww')
        form = AddressForm(request.POST)
        print(form)
        if form.is_valid():
            ("haiiiiiiiiiiiiiiiiiiiiiiiiii")
            print('haisdsdsdd')
            form.save()
            # Optionally, you can associate the address with the current user
            # For example, if you have a ForeignKey field 'user' in the Address model
           #address = form.save(commit=False)
            #address.user = request.user.id
            #address.save()
            return redirect('checkout')  # Redirect to the checkout page or any other desired page
        else:
            ("form is nullasddddddddddddddddddddddddddddddd ")
        
    else:
        form = AddressForm()
    return render(request, 'checkout.html', {'form': form})

def get_valid_coupons(request):
    print('get_valid_coupons view is called')  # Debugging statement
    try:
        # Get the list of valid coupons from the database
        valid_coupons = Coupon.objects.filter(valid_from__lte=timezone.now(), valid_to__gte=timezone.now())

        # Create a list of dictionaries containing coupon code and discount amount
        coupons_list = [{"code": coupon.coupon_code, "discount": coupon.discount_amount} for coupon in valid_coupons]

        # Return the list of valid coupons as a JSON response
        return JsonResponse(coupons_list, safe=False)
    except Exception as e:
        print(f'Error: {e}')  # Print the specific exception message for debugging purposes
        return JsonResponse({'error': 'Internal Server Error'}, status=500)
