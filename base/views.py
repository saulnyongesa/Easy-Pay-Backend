from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
import qrcode
from io import BytesIO
from .serializer import *

from rest_framework.response import Response
from rest_framework.decorators import api_view
from .mpesa import *

from .forms import *
from .models import *


@login_required(login_url='sign-in-url')
def dashboard(request):
    return render(request, 'index.html')


def show_buy_goods_qr(request):
    qr = QRCodeForBuyGoods.objects.filter(user_id=request.user.id)
    context = {
        "photos": qr
    }
    return render(request, 'buy-goods.html', context)


@login_required(login_url='sign-in-url')
def generate_qr_buygoods(request):
    if request.method == "POST":
        till_number = request.POST.get("till_number")
        try:
            data = QRCodeForBuyGoods.objects.get(till_number=till_number)
            if data:
                messages.error(request, 'Till Already Registered')
                return redirect('show-qr-buygoods-url')
        except QRCodeForBuyGoods.DoesNotExist:
            data_str = f"{till_number}"
            # Generate QR code image
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data_str)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            # Save the QR code image as a photo
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            photo_file = BytesIO(buffer.getvalue())
            qr_code_photo = QRCodeForBuyGoods.objects.create(
                user=request.user,
                till_number=till_number,
            )
            qr_code_photo.photo.save('qr_code.png', photo_file)
            messages.success(request, 'QR Code for Till Number: ' + till_number + " has been generated successfully")
            return redirect('show-qr-buygoods-url')

    return render(request, 'generate-qr-buy-goods.html')


def show_pay_bill_qr(request):
    qr = QRCodeForPayBill.objects.filter(user_id=request.user.id)
    context = {
        "photos": qr
    }
    return render(request, 'pay-bill.html', context)


@login_required(login_url='sign-in-url')
def generate_qr_paybill(request):
    if request.method == "POST":
        business_number = request.POST.get("business_number")
        account_number = request.POST.get("account_number")

        try:
            data = QRCodeForPayBill.objects.get(business_number=business_number)
            if data:
                messages.error(request, 'Business Number Already Registered')
                return redirect('show-qr-buygoods-url')
        except QRCodeForPayBill.DoesNotExist:
            data_str = f"{business_number},{account_number}"
            # Generate QR code image
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data_str)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            # Save the QR code image as a photo
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            photo_file = BytesIO(buffer.getvalue())
            qr_code_photo = QRCodeForPayBill.objects.create(
                user=request.user,
                business_number=business_number,
                account_number_or_name=account_number
            )
            qr_code_photo.photo.save('qr_code.png', photo_file)
            messages.success(request,
                             'QR Code for Business Number: ' + business_number + " and Account No.: " + account_number + " has been generated successfully")
            return redirect('show-qr-paybill-url')

    return render(request, 'generate-qr-pay-bill.html')


# USER CREATION AND AUTH FUN
def sign_up(request):
    if request.method == "POST":
        business_name = request.POST.get('business_name').upper()
        email = request.POST.get('email').lower()
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        try:             
            try:
                User.objects.get(phone_number=phone)
                messages.error(request, "Phone already used")
                return redirect('sign-up-url')
            except User.DoesNotExist:
                User.objects.get(email=email)
                messages.error(request, "Email already used")
        except User.DoesNotExist:
                user = User.objects.create(
                    business_name=business_name,
                    username=email,
                    email=email,
                    phone_number=phone,
                    password=make_password(password),
                )
                user.save()
                messages.success(request, 'Account created successfully')
                return redirect('sign-in-url') 
    return render(request, 'sign-up.html')


def sign_in(request):
    if request.user.is_authenticated:
        messages.success(request, "You're Logged us " + request.user.username)
        return redirect('dashboard-url')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in, Welcome!")
            return redirect('dashboard-url')
        elif User.DoesNotExist:
            messages.error(request, 'Invalid username or password')
            return redirect('sign-in-url')

    return render(request, 'sign-in.html')


@login_required(login_url='sign-in-url')
def sign_out(request):
    logout(request)
    return redirect('sign-in-url')


@login_required(login_url='sign-in-url')
def my_profile(request):
    user = User.objects.get(id=request.user.id)
    context = {
        "user": user,
    }
    return render(request, 'profile.html', context)


@login_required(login_url='sign-in-url')
def user_edit(request):
    form = UserForm(instance=request.user)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "You updated your profile")
            return redirect('profile-url')
    context = {
        "form": form,
    }
    return render(request, 'user-edit.html', context)


# APIS FUNCTIONS
@api_view(['GET', 'POST'])
def buy_goods_payment(request, phone, amount, till_number):
    user = QRCodeForBuyGoods.objects.get(till_number=till_number)
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    call_back_url = 'https://upward-husky-marginally.ngrok-free.app/scan-pay/'
    headers = {"Authorization": "Bearer %s" % access_token}
    if access_token and api_url and headers:
        request_payload = {
            "BusinessShortCode": LipanaMpesaPassword.Business_short_code,
            "Password": LipanaMpesaPassword.decode_password,
            "Timestamp": LipanaMpesaPassword.lipa_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": user.till_number,
            "PhoneNumber": phone,
            "CallBackURL": call_back_url,
            "AccountReference": user.user.business_name,
            "TransactionDesc": "Fare Payment",
        }
        response = requests.post(api_url, json=request_payload, headers=headers)
        if response.status_code == 200:
            serializer = BuyGoodsSerializer(user, many=False)
            return JsonResponse(serializer.data)
        else:
            return HttpResponse("Failed to initiate payment", status=response.status_code)
    else:
        return HttpResponse("Invalid access token, API URL, or headers", status=500)


@api_view(['GET', 'POST'])
def pay_bill_payment(request, phone, amount, business_number, account_number):
    user = QRCodeForPayBill.objects.get(business_number=business_number, account_number_or_name=account_number)
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    call_back_url = 'https://upward-husky-marginally.ngrok-free.app/scan-pay/'
    headers = {"Authorization": "Bearer %s" % access_token}
    if access_token and api_url and headers:
        request_payload = {
            "BusinessShortCode": LipanaMpesaPassword.Business_short_code,
            "Password": LipanaMpesaPassword.decode_password,
            "Timestamp": LipanaMpesaPassword.lipa_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": user.business_number,
            "PhoneNumber": phone,
            "CallBackURL": call_back_url,
            "AccountReference": user.account_number_or_name,
            "TransactionDesc": "Fare Payment",
        }
        response = requests.post(api_url, json=request_payload, headers=headers)
        if response.status_code == 200:
            serializer = BuyGoodsSerializer(user, many=False)
            return JsonResponse(serializer.data)
        else:
            return HttpResponse("Failed to initiate payment", status=response.status_code)
    else:
        return HttpResponse("Invalid access token, API URL, or headers", status=500)
