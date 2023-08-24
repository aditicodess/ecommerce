from django.urls import path
from products.views import create_product, delete_product, upload_product_image
from django.urls import re_path

urlpatterns = [
    path("create/", create_product, name="create_product"),
    path("upload/image/", upload_product_image, name="upload_product_image"),
    re_path("(?P<slug>[\w\-]+)/$", delete_product, name="delete_product"),
]
