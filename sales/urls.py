from django.urls import path
from . import views

urlpatterns = [
    path('purchases/', views.purchase_file, name='purchase-file'),
    path('purchases/<int:purchase_id>/download/', views.create_download, name='create-download'),
    path('my-purchases/', views.my_purchases, name='my-purchases'),
]
