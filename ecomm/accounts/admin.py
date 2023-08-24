from django.contrib import admin

# Register your models here.
from .models import Profile, Cart, CartItems, Vendor, User

admin.site.register(Vendor)
admin.site.register(Profile)
admin.site.register(Cart)
admin.site.register(CartItems)
admin.site.register(User)
