from django.shortcuts import render,redirect
from cart.models import CartItem,Cart
from .models import Order,Payment,OrderProduct,Addaddress
from storeapp.models import Product
from django.contrib import messages
import datetime
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect,HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.core.exceptions import ObjectDoesNotExist
import uuid
from django.http import HttpResponseBadRequest
from adminn.models import Coupon
import datetime
from decimal import Decimal
from django.shortcuts import get_object_or_404
from .models import Wallet
from django.db.models import F
from accounts.models import UserProfile
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from xhtml2pdf import pisa





def place_order(request, total=0, quantity=0):
    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.selling_price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax

    print("herererequest.method",request.method)
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code', '')
        selected_address_id = request.POST.get('address')
        print('selected_address', selected_address_id)
        print(coupon_code)
    
        if selected_address_id == 'user-profile':
        # Get address details from user profile
            selected_address = UserProfile.objects.get(user=current_user)
            user_data = selected_address.user
            first_name = user_data.first_name
            last_name = user_data.last_name
            phone = ''
            email = ''
        else:
        # Get address details from selected address ID
            selected_address = Addaddress.objects.get(id=selected_address_id)
            user_data = selected_address.user
            first_name = selected_address.first_name
            last_name = selected_address.last_name
            phone = selected_address.phone
            email = selected_address.email
    
        data = Order()
        data.user = user_data
        data.first_name = first_name
        data.last_name = last_name
        data.phone = phone
        data.email = email
        data.address_line_1 = selected_address.address_line1
        data.address_line_2 = selected_address.address_line2
        data.country = selected_address.country
        data.state = selected_address.state
        data.city = selected_address.city
        data.order_note = ''
        data.order_total = grand_total
        data.tax = tax
        data.ip = request.META.get('REMOTE_ADDR')
        print(data)
        data.save()
    
        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr, mt, dt)
        current_date = d.strftime("%Y%m%d")  # 20210305
        order_number = current_date + str(data.id)
        data.order_number = order_number
        data.save()
    
        order = Order.objects.get(user=user_data, is_ordered=False, order_number=order_number)
        grand_total_session = request.session.get('grand_total')
        wallet = Wallet.objects.get(user=request.user)
        wallet_balance = wallet.balance
        print(grand_total)
        print(grand_total_session)
        grand_total_session = Decimal(grand_total_session) if grand_total_session else None
    
        grand_total = Decimal(grand_total) if grand_total else 0
    
        if grand_total_session is not None:
            context_grand_total = grand_total_session
        else:
            context_grand_total = grand_total
        
        if wallet_balance and (
            (wallet_balance > (grand_total_session or Decimal('0'))) or
            (Decimal('1') <= wallet_balance <= (grand_total_session or Decimal('0')))
        ):
            print(wallet_balance)
            if grand_total_session is None:
                deducted_amount = wallet_balance
            else:
                deducted_amount = min(wallet_balance, grand_total_session)
            if grand_total_session is not None:
                grand_total = grand_total_session
            print('deducted_amount', deducted_amount)
            print('session', grand_total_session)
            deducted_amount_decimal = Decimal(str(deducted_amount))
            deducted_amount_float = float(deducted_amount_decimal)
            request.session['deducted_amount'] = deducted_amount_float

            grand_total -= deducted_amount_decimal
            print(deducted_amount_decimal)
            print(grand_total)
            
        else:
            wallet_balance = Decimal('0')
    
        context = {
        'order': order,
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': (Decimal('0.00') if grand_total < 0 or grand_total_session < 0 else grand_total_session)
            if grand_total_session and not wallet_balance else grand_total.quantize(Decimal('0.00')),
        'order_number': order_number,
        'deducted_amount': deducted_amount_decimal if 'deducted_amount' in locals() else None,
    }
    
        return render(request, 'orders/payments.html', context)
    else:
        print('form is invalid')
        return redirect('checkout')


def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code', '')
        grand_total = Decimal(request.POST.get('grand_total', '0'))

        current_date = datetime.date.today()
        try:
            coupon = Coupon.objects.get(coupon_code=coupon_code, valid_from__lte=current_date, valid_to__gte=current_date)
            if coupon.min_spend <= grand_total:
                discount_amount = coupon.discount_amount
                grand_total -= discount_amount
                print(grand_total)
                request.session['coupon'] = {
                    'code': coupon.coupon_code,
                    'discount': float(discount_amount),
                }


        
                request.session['grand_total'] = str(grand_total)

                
                return JsonResponse({
                    'success': True,
                    'coupon': {
                        'code': coupon.coupon_code,
                        'discount':  float(discount_amount),
                    },'grand_total': str(grand_total),
                })
            else:
            
                return JsonResponse({'success': False, 'invalid_coupon': 'Coupon code is not valid for the current order total.'})
        except Coupon.DoesNotExist:
    
            return JsonResponse({'success': False, 'invalid_coupon': 'Invalid coupon code.'})

    return JsonResponse({'success': False, 'error': 'Invalid request.'})

def remove_coupon(request):
    if request.method == 'POST':
        coupon = request.session.get('coupon')
        print(coupon)

        if coupon:
            discount_amount = Decimal(coupon.get('discount', 0))
            grand_total = Decimal(request.session.get('grand_total', '0'))



            grand_total += discount_amount
            print(grand_total)

            del request.session['coupon']

            request.session['grand_total'] = str(grand_total)

            return JsonResponse({'success': True, 'grand_total': str(grand_total)})

        else:
            return JsonResponse({'success': False, 'error': 'No coupon found.'})

    return JsonResponse({'success': False, 'error': 'Invalid request.'})

def payments(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        payment_method = body['payment_method']

        if payment_method == 'PayPal':
            order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['order_number'])

            # Store transaction details inside Payment model
            payment = Payment(
                user=request.user,
                payment_id=body['order_number'],
                payment_method=body['payment_method'],
                amount_paid=order.order_total,
                status=body['status'],
            )
            payment.save()

        elif payment_method == 'COD':
            order_number = body['order_number']
            
            try:
                order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_number)

                payment = Payment(
                    user=request.user,
                    payment_method='Cash On Delivery',
                    amount_paid=order.order_total,
                    status='Paid',
                )
                payment.payment_id = str(uuid.uuid4())  # Generate a unique payment_id using UUID
                payment.save()

            except ObjectDoesNotExist as e:
                print(e)
                return JsonResponse({'error': 'Order does not exist.'})
        else:
            return JsonResponse({'error': 'Invalid payment method.'})

        order.payment = payment
        order.is_ordered = True
        order.save()

        cart_items = CartItem.objects.filter(user=request.user)

        for item in cart_items:
            order_product = OrderProduct(
                order=order,
                payment=payment,
                user=request.user,
                product=item.product,
                quantity=item.quantity,
                product_price=item.product.price,
                ordered=True,
            )
            order_product.save()
            order_product.variations.set(item.variations.all())

            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            product.save()

        
        CartItem.objects.filter(user=request.user).delete()

        data = {
            'order_number': order.order_number,
            'transID': payment.payment_id,
        }
        return JsonResponse(data)

    return JsonResponse({'error': 'Invalid request method.'})
def successful(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    deducted_amount = request.session.get('deducted_amount')
    user = request.user  # Assuming you have user authentication
    wallet = Wallet.objects.get(user=user)
    wallet_balance = wallet.balance
    if deducted_amount is not None:
        if wallet_balance is not None:
            wallet_balance -= Decimal(deducted_amount)
            wallet.balance = wallet_balance
            wallet.save()
    if 'deducted_amount' in request.session:
        del request.session['deducted_amount']   
    if 'grand_total' in request.session:
        del request.session['grand_total']

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/successful.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')

def download_invoice(request):
    # Generate or fetch the necessary invoice data
    # ...

    # Render the invoice template using the fetched data
    template = get_template('orders/invoice.html')
    context = {}  # Add the necessary context data for the invoice
    rendered_template = template.render(context)

    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()
    page_size = (800, 1200)  # Custom page size in pixels (adjust as needed)

    # Convert the HTML template to PDF and write it to the buffer
    pisa_status = pisa.CreatePDF(rendered_template, dest=buffer, pagesize=page_size)

    if pisa_status.err:
        return HttpResponse('PDF conversion error', status=500)

    # File buffer is now ready to be used to create the HttpResponse
    buffer.seek(0)

    # Create the HttpResponse object with the appropriate PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

    # Write the PDF buffer to the response
    response.write(buffer.getvalue())

    return response
