from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from infrastructure.models import User, Company, Product, InventoryItem


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model."""
    
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_active', 'is_staff'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Admin interface for Company model."""
    
    list_display = ['nit', 'name', 'phone', 'created_at']
    search_fields = ['nit', 'name', 'phone']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for Product model."""
    
    list_display = ['code', 'name', 'company', 'created_at']
    search_fields = ['code', 'name', 'company__name']
    list_filter = ['company', 'created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    """Admin interface for InventoryItem model."""
    
    list_display = ['company', 'product', 'quantity', 'updated_at']
    search_fields = ['company__name', 'product__name']
    list_filter = ['company', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
