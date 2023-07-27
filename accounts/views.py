from django.shortcuts import render,redirect,get_object_or_404
from .forms import Registration,UserForm,UserProfileForm
from .models import Account,UserProfile,ReferralCoupon
from  django.contrib import messages,auth
from django.contrib.auth.hashers import check_password
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from greenkart.views import home
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from cart.views import _cart_id
from cart.models import Cart, CartItem
from orders.models import Order,OrderProduct,Wallet
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import decimal
import random
import string
import json
import uuid


# Create your views here.
def register(request): 
    if request.method == 'POST':
        form = Registration(request.POST, request=request)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            referral_code = form.cleaned_data['referral_code']
            print(referral_code)
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password,referral_code=referral_code)
            user.phone_number = phone_number
            user.save()
            profile = UserProfile(user=user)
    
            profile.save()
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('account/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            return redirect('/accounts/login/?command=verification&email=' + email)

    else:
        form = Registration()

    context = {
        'form': form,
    }
    
    return render(request, 'account/register.html', context)

    
def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    # Getting the product variations by cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    # Get the cart items from the user to access his product variations
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    # product_variation = [1, 2, 3, 4, 6]
                    # ex_var_list = [4, 6, 3, 5]

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                # next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('home')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'account/login.html')

def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        referral_code = request.session.get('referral_code')
        wallet= Wallet.objects.create(user=user,balance=0)
        
        print('referral',referral_code)
        print('before')
        
        if referral_code:
            try:
                print('try')
                 
                # Get user who generated the referral code
                json_object = json.loads(referral_code)

                code = json_object['fields']['code']
                print(code)
                generated_by = ReferralCoupon.objects.get(code=code ).generated_by_account
                print('generated_by',generated_by)
                wallet = get_object_or_404(Wallet, user=generated_by)
                print('wallet',wallet)
                # Add 50 to the user's wallet
                wallet.balance+=50
                wallet.save()

                # Delete the referral code from the session
                del request.session['referral_code']
            except ReferralCoupon.DoesNotExist:
                pass

        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')
def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('account/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            }) 
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')
    return render(request, 'account/forgotPassword.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'account/resetPassword.html')
@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')
@login_required(login_url = 'login')
def dashboard(request):
    return render(request,'account/userdashboard.html')
@login_required(login_url = 'login')
def editprofile(request):
    print('hello')
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('editprofile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'account/editprofile.html', context)

@login_required(login_url = 'login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    print(request.path)
    context = {
        'orders': orders,
    }
    return render(request, 'account/my_orders.html', context)
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save() 
                # auth.logout(request)
                messages.success(request, 'Password updated successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('change_password')
    return render(request, 'account/change_password.html')

def cancel_order(request, order_id):
    # Get the order
    order = get_object_or_404(Order, id=order_id)
    print(order)
    # Check if the order is already canceled
    if order.status == 'Cancelled':
        is_canceled = False
    else:
        # Update the order status to 'Cancelled'
        order.status = 'Cancelled'
        order.save()

        # Update the payment status to 'refunded'
        payment = order.payment
        if payment:
            payment.status = 'refunded'
            payment.save()

        
            user = payment.user
            wallet, created = Wallet.objects.get_or_create(user=user)
            wallet.balance +=  decimal.Decimal(str(order.order_total))
            wallet.save()

       
        order_products = OrderProduct.objects.filter(order=order)
        order_products.delete()

 
        for order_product in order_products:
            product = order_product.product
            product.stock += order_product.quantity
            product.save()

        is_canceled = True

    return redirect("my_orders")
def generate_referral_code(length=8):
    characters = string.ascii_letters + string.digits
    referral_code = ''.join(random.choice(characters) for _ in range(length))
    return referral_code
@login_required(login_url = 'login')
def refferal(request):
    user = request.user
    
    # Check if the user already has a referral code
    referral_coupon = ReferralCoupon.objects.filter(generated_by_account =user).first()
    
    if referral_coupon:
        referral_code = referral_coupon.code  # Retrieve the existing referral code
    else:
        referral_code = str(uuid.uuid4().hex[:10])   # Generate a new referral code
        ReferralCoupon.objects.create(generated_by_account=user, code=referral_code, is_valid=True)
    
    context = {
        'referral_code': referral_code
    }
    return render(request, 'account/refferel.html', context)
@login_required(login_url = 'login')
def wallet(request):
    user=request.user
    wallet, created = Wallet.objects.get_or_create(user=user, defaults={'balance': 0})

    print(wallet)
    balance=wallet.balance
    context={
        'balance':balance
    }
    return render(request,'account/wallet.html',context)
@login_required(login_url = 'login')
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_products = order.orderproduct_set.all() 
    
    for order_product in order_products:
        print(order_product.refund_status )
        # Check if the order status is 'Delivered'
        if order_product.order.status.strip() == 'Delivered':
            # Calculate the date 30 days ago from now
            thirty_days_ago = timezone.now() - timedelta(days=30)
            print("asdsdsadasdadadasd")
            
            # Check if the order was created within the last 30 days
            if order_product.order.created_at > thirty_days_ago:
                order_product.show_return_button = True
            else:
                order_product.show_return_button = False
        else:
            order_product.show_return_button = False
        print(order_product.show_return_button )
    print(order.status)
    print(order.created_at)
    context={
        'order':order,
        'order_products':order_products,
    }
    return render(request, 'account/view detail.html', context)
@login_required(login_url = 'login')
def inovicesucessfull(request,order_number):
    order = Order.objects.get(order_number=order_number, is_ordered=True)
    ordered_products = OrderProduct.objects.filter(order_id=order.id)
    context={
     'ordered_products':ordered_products,
     'order':order}
         
    return render(request,'orders/successful.html',context)
@login_required(login_url = 'login')
def initiate_refund(request, order_id):
    print(order_id)
    print('haiiiiiiiiiiiiiiiiiiiiiiiiiiii')
    if request.method == 'POST':
        order_product = get_object_or_404(OrderProduct, id=order_id)
        print(order_product)

        # Check if the order product is eligible for refund
        if order_product.refund_status == 'Requested':
            # Mark the order product as refund initiated
            order_product.refund_status = 'Initiated'
            order_product.save()

            # Perform any additional refund initiation logic here
            
            return redirect('my_orders')  # Redirect to a success page after refund initiation

    return redirect('my_orders')
