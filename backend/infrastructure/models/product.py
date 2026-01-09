from django.db import models


class Product(models.Model):
    """Product model for infrastructure layer."""
    
    code = models.CharField(max_length=100, primary_key=True, verbose_name='Product Code')
    name = models.CharField(max_length=255, verbose_name='Product Name')
    # Django handles mutable defaults (list, dict) correctly in JSONField
    features = models.JSONField(default=list, verbose_name='Features')
    prices = models.JSONField(default=dict, verbose_name='Prices by Currency')
    company = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE,
        related_name='products',
        db_column='company_nit',
        verbose_name='Company'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
