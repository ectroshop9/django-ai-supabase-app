from django.contrib import admin
from .models import Category, TechnicalFile

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']

@admin.register(TechnicalFile)
class TechnicalFileAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'price_coins', 'is_available']
    search_fields = ['title', 'description']
