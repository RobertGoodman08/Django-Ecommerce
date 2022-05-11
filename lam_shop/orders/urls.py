from django.urls import path
from orders.views import shopcart
from . import views

urlpatterns = [
    path('cart/', shopcart, name='shopcart'),
    path('addtoshopcart/<int:id>', views.addtoshopcart, name='addtoshopcart'),
    path('deletefromcart/<int:id>', views.deletefromcart, name='deletefromcart'),
]