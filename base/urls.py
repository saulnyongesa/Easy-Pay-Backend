from django.urls import path

from base import views
urlpatterns = [
    path('', views.dashboard, name='dashboard-url'),

    path('qr-code/bg/', views.show_buy_goods_qr, name='show-qr-buygoods-url'),
    path('qr-gnerate/bg/', views.generate_qr_buygoods, name='generate-qr-buygoods-url'),

    path('qr-code/pb/', views.show_pay_bill_qr, name='show-qr-paybill-url'),
    path('qr-gnerate/pb/', views.generate_qr_paybill, name='generate-qr-paybill-url'),

    path('scan-pay/<phone>/<amount>/<till_number>/', views.buy_goods_payment, name="buy-goods-pay"),
    path('scan-pay/<phone>/<amount>/<business_number>/<account_number>/', views.pay_bill_payment, name="pay-bill-pay"),




    path("usr/signup/", views.sign_up, name="sign-up-url"),
    path("usr/sign_in/", views.sign_in, name="sign-in-url"),
    path("usr/sign-out/", views.sign_out, name="sign-out-url"),
    path("usr/edit/", views.user_edit, name="user-edit-url"),
    path("usr/profile/", views.my_profile, name="profile-url"),
]
