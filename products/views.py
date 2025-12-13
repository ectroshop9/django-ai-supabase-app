from rest_framework import generics
from .models import Category, TechnicalFile
from .serializers import CategorySerializer, FileDetailSerializer

class CategoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class FileList(generics.ListAPIView):
    queryset = TechnicalFile.objects.filter(is_available=True)
    serializer_class = FileDetailSerializer

class FileDetail(generics.RetrieveAPIView):
    queryset = TechnicalFile.objects.filter(is_available=True)
    serializer_class = FileDetailSerializer
    lookup_field = 'id'
