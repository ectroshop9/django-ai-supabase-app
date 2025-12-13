from rest_framework import serializers
from .models import Category, TechnicalFile

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description')

class FileDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = TechnicalFile
        fields = (
            'id', 'title', 'description', 
            'file_image', 'price_coins', 
            'category_name'
        )
