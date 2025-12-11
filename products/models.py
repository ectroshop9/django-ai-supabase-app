
from django.db import models
from accounts.models import Customer # استيراد نموذج العميل

# 1. نموذج Category (التصنيف)
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Categories" # عرض الاسم بصيغة الجمع في لوحة الإدارة
        
    def __str__(self):
        return self.name

# 2. نموذج TechnicalFile (الملف التقني الذي يتم بيعه)
class TechnicalFile(models.Model):
    # ربط الملف بالتصنيف
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='files')
    
    # صورة الملف (للعرض في البوت)
    file_image = models.ImageField(upload_to='file_images/', blank=True, null=True) 
    
    title = models.CharField(max_length=200) 
    description = models.TextField() 
    
    # سعر الملف بالكوينات 
    price_coins = models.IntegerField() 
    
    # مسار الملف الفعلي (خارجي أو داخلي) 
    file_url = models.URLField(max_length=500, help_text="رابط الملف الخارجي أو الداخلي") 
    
    is_available = models.BooleanField(default=True) # حالة التوفر

    def __str__(self):
        return f"{self.title} - {self.price_coins} Coins"

# 3. نموذج Purchase (سجل عملية الشراء)
class Purchase(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    file = models.ForeignKey(TechnicalFile, on_delete=models.CASCADE)
    # السعر الذي تم دفعه (للتاريخ)
    paid_price = models.IntegerField() 
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Purchase by {self.customer.serial} of {self.file.title}"

    # [تعديل] الربط بمصدر التخزين
    
    
    # [تعديل] مسار/رابط الملف الفعلي داخل هذا المصدر
    file_path = models.URLField(
        max_length=500, 
        help_text="الرابط المباشر للملف (Direct Share Link) داخل المصدر المحدد."
    )
    
   