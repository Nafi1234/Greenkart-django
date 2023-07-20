from django.db import models
from django.utils import timezone

# Create your models here.
class Coupon(models.Model):
    coupon_code = models.CharField(max_length=50, unique=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    min_spend = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateField(default=timezone.now)
    valid_to = models.DateField()

    def is_valid(self):
        today = timezone.now().date()
        return self.valid_from <= today <= self.valid_to