from django.urls import path
from home.views import index, get_product
from django.urls import re_path

urlpatterns = [
    re_path("(?P<slug>[\w\-]+)/$", get_product, name="get_product"),
    path("", index, name="index"),
]
