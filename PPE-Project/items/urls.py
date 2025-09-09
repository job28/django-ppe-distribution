# items/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='items_index'),            # item list page
    path('buy/<int:item_id>/', views.buy_item, name='buy_item'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('accounts/logout/', views.custom_logout, name='logout'),


]
