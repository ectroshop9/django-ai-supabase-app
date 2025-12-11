# في products/urls.py
from django.urls import path
from .views import (
    PurchaseView, PurchaseListView,
    CategoryListView, FilesByCategoryView
)

urlpatterns = [
    # المتجر
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/<int:category_id>/files/', FilesByCategoryView.as_view(), name='files_by_category'),
    
    # الشراء والمشتريات
    path('purchase/', PurchaseView.as_view(), name='file_purchase'),
    path('my-purchases/', PurchaseListView.as_view(), name='purchase_list'),
]