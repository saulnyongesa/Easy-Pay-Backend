from rest_framework import serializers
from base.models import *


# Create a model serializer
class BuyGoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCodeForBuyGoods
        fields = ('till_number', "user")


class PayBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCodeForPayBill
        fields = ('business_number', 'account_number_or_name')
