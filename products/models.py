from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        
    def __str__(self):
        return self.name

class TechnicalFile(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='files')
    file_image = models.ImageField(upload_to='file_images/', blank=True, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price_coins = models.IntegerField()
    file_url = models.URLField(max_length=500)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} - {self.price_coins} Coins"
