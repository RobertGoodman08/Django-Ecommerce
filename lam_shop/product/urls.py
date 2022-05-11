from django.urls import path
from product.views import index, get_detail, get_category, compare_list, compare_add, AddLike,\
    AddDislike, get_brand, get_search, get_stock, brand_list, support_chat, contacts

urlpatterns = [
    path('', index, name='index'),
    path('product/<slug:slug>/', get_detail, name='detail'),
    path('category/<int:category_id>/', get_category, name='category'),
    path('brand/<int:brand_id>/', get_brand, name='brand'),
    path('compare_list/', compare_list, name='compare_list'),
    path('compare_add/<int:id>/', compare_add, name='compare_add'),
    path('<int:pk>/like/', AddLike.as_view(), name='like'),
    path('<int:pk>/dislike/', AddDislike.as_view(), name='dislike'),
    path('search/', get_search, name='search'),
    path('stock/', get_stock, name='stock'),
    path('brand_list/', brand_list, name='brand_list'),
    path('support_chat/', support_chat, name='support_chat'),
    path('contacts/', contacts, name='contacts'),
]