from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.urls import reverse


class MyAccountManger(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None,referral_code=None):
        if not email:
            raise ValueError('User must have an email address')

        if not username:
            raise ValueError('User must have an username')

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
            referral_code=referral_code,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, username, password):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            password = password,
            first_name = first_name,
            last_name = last_name,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user
    
class Account(AbstractBaseUser):
    first_name =models.CharField(max_length=50)
    last_name =models.CharField(max_length=50)
    username =models.CharField(max_length=50, unique=True)
    email =models.EmailField(max_length=100,unique=True)
    phone_number =models.CharField(max_length=50)
    referral_code = models.CharField(max_length=10, blank=True, null=True)
    
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login      = models.DateTimeField(auto_now_add=True)
    is_admin        = models.BooleanField(default=False)
    is_staff        = models.BooleanField(default=False)
    is_active        = models.BooleanField(default=False)
    is_superadmin        = models.BooleanField(default=False)
    
    USERNAME_FIELD ='email'
    REQUIRED_FIELDS =['username','first_name','last_name']
    objects =MyAccountManger()
    def __str__(self):
        return self.email
    def has_perm(self, perm, obj=None):
        return self.is_admin
    def has_module_perms(self, add_label):
        return True
class Category(models.Model):
    category_name=models.CharField(max_length=50, unique=True)
    slug=models.CharField(max_length=100,unique=True)
    description = models.CharField(max_length=255,blank=True)
    cat_image= models.ImageField(upload_to='photos/categories',blank=True)
    offer_percentage = models.FloatField(null=True, blank=True, validators=[MinValueValidator(1)])
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Update the selling prices of the products associated with this category
        products = self.product_set.all()
        for product in products:
            product.save()


    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.category_name
    
    def get_url(self):
            return reverse('products_by_category', args=[self.slug])
class UserProfile(models.Model):
    user=models.OneToOneField(Account,on_delete=models.CASCADE)
    address_line1=models.CharField(blank=True,max_length=200)
    address_line2=models.CharField(blank=True,max_length=200)
    city=models.CharField(blank=True,max_length=20)
    state= models.CharField(blank=True ,max_length=20)
    country=models.CharField(blank=True,max_length=20)
    
    def __str__(self):
        return str(self.user)
    def fulladdress(self):
        return f'{self.address_line1} {self.address_line2}'
class ReferralCoupon(models.Model):
    code = models.CharField(max_length=10, unique=True)
    generated_by_account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name='generated_coupons'
    )
    is_valid = models.BooleanField(default=False)
    # ... other fields and properties

    def __str__(self):
        return self.code