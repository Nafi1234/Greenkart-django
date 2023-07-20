from django.db import models
from accounts.models import Account
from storeapp.models import Variation,Product

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('COD', 'Cash on Delivery'),
        ('PayPal', 'PayPal'),
    )

    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD_CHOICES, default='COD')
    amount_paid = models.CharField(max_length=100) # this is the total amount paid
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id
 

class Order(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('shipped','shipped'),
        (' Delivered', ' Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    order_note = models.CharField(max_length=100, blank=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS, default='New')
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def __str__(self):
        return self.first_name


class OrderProduct(models.Model):
    REFUND_STATUS = (
        ('Requested', 'Return Requested'),
        ('Initiated', 'Refund Initiated'),
        ('Refunded', 'Refunded'),
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True) 
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    refund_status = models.CharField(max_length=20, choices=REFUND_STATUS, default='Requested')
    def mark_as_refunded(self):
        # Update the refund status to "Refunded"
       

        # Add the refunded amount to the user's wallet
       
        user_wallet, _ = Wallet.objects.get_or_create(user=self.user)
        user_wallet.balance += self.product_price * self.quantity
        user_wallet.save()

       

        # Update the order status to "Refunded" if all products in the order are refunded
        order = self.order
        if order.orderproduct_set.filter(refund_status='Requested').count() == 0:
            order.status = 'Refunded'
            order.save()

    def __str__(self):
        return self.product.product_name
class Wallet(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_available = models.BooleanField(default=False)

    def __str__(self):
        return f"Wallet of {self.user.username}"

    def save(self, *args, **kwargs):
        if self.balance  >1:
            self.is_available = True
        else:
            self.is_available = False
        super().save(*args, **kwargs)
class Addaddress(models.Model):
    user=models.ForeignKey(Account,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    address_line1 = models.CharField(max_length=50)
    address_line2 = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    def get_all_fields(self):
        fields = [
            ('First Name', self.first_name),
            ('Address Line 1', self.address_line1),
            ('Address Line 2', self.address_line2),
            ('Country', self.country),
            ('State', self.state),
            ('City', self.city),
        ]
        return fields
    