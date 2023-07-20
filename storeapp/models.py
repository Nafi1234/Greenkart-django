from django.db import models
from accounts.models import Category
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    offer = models.FloatField(null=True, blank=True, validators=[MinValueValidator(1)])
    selling_price = models.IntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.category.offer_percentage is not None and not self.offer:
            discount = self.price * (float(self.category.offer_percentage) / 100)
            self.selling_price = round(self.price - discount)
        elif self.category.offer_percentage is not None and self.offer:
            category_discount = self.price * (float(self.category.offer_percentage) / 100)
            product_discount = self.price * (float(self.offer) / 100)
            self.selling_price = round(self.price - category_discount - product_discount)
        elif self.category.offer_percentage is None and self.offer:
            discount = self.price * (float(self.offer) / 100)
            self.selling_price = round(self.price - discount)
        else:
            self.selling_price = self.price
        print(f"Selling Price: {self.selling_price}")


        super().save(*args, **kwargs)


    def get_url(self):
        return reverse('productdetail',args=[self.category.slug,self.slug])
    def __str__(self):
        return self.product_name
class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)

    def sizes(self): 
        return super(VariationManager, self).filter(variation_category='size', is_active=True)

variation_category_choice = (
    ('color', 'color'),
    ('size', 'size'),
)

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    variation_value     = models.CharField(max_length=100)
    is_active           = models.BooleanField(default=True)
    created_date        = models.DateTimeField(auto_now=True)

    objects = VariationManager()
    def get_variation_display(self):
        return self.variation_value

    def __str__(self):
        return self.variation_value
class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='store/products', max_length=255)

    def __str__(self):
        return self.product.product_name

    class Meta:
        verbose_name = 'productgallery'
        verbose_name_plural = 'product gallery'