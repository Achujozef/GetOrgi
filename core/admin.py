from django.contrib import admin
from .models import Category, Product,Review,OrgiUser,Delivery,CartItem,Address,OrderItem,Order
# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(CartItem)
admin.site.register(Delivery)
admin.site.register(OrgiUser)
admin.site.register(Review)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(OrderItem)