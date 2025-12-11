# في products/admin.py
from django.contrib import admin
from .models import Category, TechnicalFile, Purchase

# تسجيل نموذج التصنيفات
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# تسجيل نموذج الملفات التقنية
@admin.register(TechnicalFile)
class TechnicalFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price_coins', 'is_available')
    list_filter = ('category', 'is_available')
    search_fields = ('title', 'description')
    
# تسجيل نموذج المشتريات
@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('customer', 'file', 'paid_price', 'timestamp')
    list_filter = ('file__category',)
    search_fields = ('customer__serial', 'file__title')
    # منع التعديل اليدوي على السجل
    readonly_fields = ('customer', 'file', 'paid_price', 'timestamp')