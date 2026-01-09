from django.db import models


class InventoryItem(models.Model):
    """Inventory item model for infrastructure layer."""
    
    company = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE,
        related_name='inventory_items',
        db_column='company_nit',
        verbose_name='Company'
    )
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='inventory_items',
        db_column='product_code',
        verbose_name='Product'
    )
    quantity = models.IntegerField(default=0, verbose_name='Quantity')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'inventory'
        verbose_name = 'Inventory Item'
        verbose_name_plural = 'Inventory Items'
        unique_together = [['company', 'product']]
        ordering = ['company', 'product']
    
    def __str__(self):
        return f"{self.company.name} - {self.product.name}: {self.quantity}"
