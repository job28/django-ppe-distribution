from django.contrib import admin
from .models import Item, Order, PickupHub

class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'image_url')

admin.site.register(Item)
admin.site.register(Order)
admin.site.register(PickupHub)