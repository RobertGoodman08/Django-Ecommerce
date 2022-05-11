from django.urls import path
from users.views import login_form, register_form, logout_func,\
    favourite_list, favourite_add, token_send, success, verify, \
    error_page, user_update, user_password, user_orders, user_orderdetail,\
    user_order_product, user_order_product_detail, \
    index, my_payment_methods, my_refunds_and_cancellations
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', index, name='user_profile'),

    path('login/', login_form, name='login'),
    path('logout/', logout_func, name='logout'),
    path('register/', register_form, name='register'),
    path('favourite_list/', favourite_list, name='favourite_list'),
    path('fav/<int:id>/', favourite_add, name='favourite_add'),



    # ---------------------------------------------------------------------


    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'), # сброс пароля || Восстановление пароля
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),



    # ---------------------------------------------------------------------

    path('token', token_send, name="token_send"),
    path('success', success, name='success'),
    path('verify/<auth_token>', verify, name="verify"),
    path('error', error_page, name="error"),


    # ---------------------------------------------------------------------

    path('update/', user_update, name='user_update'),
    path('password/', user_password, name='user_password'),
    path('orders/', user_orders, name='user_orders'),
    path('orders_product/', user_order_product, name='user_order_product'),
    path('orderdetail/<int:id>', user_orderdetail, name='user_orderdetail'),
    path('order_product_detail/<int:id>/<int:oid>', user_order_product_detail, name='user_order_product_detail'),

    path('my_payment_methods/', my_payment_methods, name='my_payment_methods'),
    path('my_refunds_and_cancellations/', my_refunds_and_cancellations, name='my_refunds_and_cancellations'),


]