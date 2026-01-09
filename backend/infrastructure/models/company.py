from django.db import models


class Company(models.Model):
    """Company model for infrastructure layer."""
    
    nit = models.CharField(max_length=50, primary_key=True, verbose_name='NIT')
    name = models.CharField(max_length=255, verbose_name='Company Name')
    address = models.TextField(verbose_name='Address')
    phone = models.CharField(max_length=50, verbose_name='Phone Number')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'companies'
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.nit})"
