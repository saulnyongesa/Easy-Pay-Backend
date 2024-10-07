from django.contrib import admin

from base.models import *

# Register your models here.
admin.site.register(User)
admin.site.register(QRCodeForBuyGoods)
admin.site.register(QRCodeForPayBill)
