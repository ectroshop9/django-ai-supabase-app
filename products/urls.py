from django.urls import path
from .views import CategoryList, FileList, FileDetail

urlpatterns = [
    path('categories/', CategoryList.as_view(), name='category-list'),
    path('files/', FileList.as_view(), name='file-list'),
    path('files/<int:id>/', FileDetail.as_view(), name='file-detail'),
]
