from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    business_name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    phone_number = models.IntegerField(unique=True, null=True)

    def __str__(self):
        return self.email


class QRCodeForBuyGoods(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    till_number = models.CharField(max_length=200, null=True, unique=True)
    photo = models.ImageField(upload_to='qr_codes/', null=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.user.username


class QRCodeForPayBill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    business_number = models.CharField(max_length=200, null=True, unique=True)
    account_number_or_name = models.CharField(max_length=200, null=True, unique=True)
    photo = models.ImageField(upload_to='qr_codes/', null=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.user.username
