from django.contrib import admin
from .models import Supplier, Product, Purchase, Customer, Sale, SaleItem, StockAdjustment

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'description', 'barcode', 'category', 'purchase_price', 'selling_price', 'quantity_in_stock', 'min_stock_level', 'supplier', 'created_at')
    list_filter = ('category', 'supplier', 'created_at')
    search_fields = ('product_name', 'barcode')
    list_per_page = 20
    ordering = ('created_at',)

class SupplierAdmin(admin.ModelAdmin):
    list_display = ('supplier_name', 'contact_person', 'phone', 'email', 'address')
    search_fields = ('supplier_name', 'contact_person')
    list_per_page = 20

class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'product', 'quantity', 'unit_price', 'total_cost', 'purchase_date', 'received_by')
    list_filter = ('purchase_date', 'supplier')
    search_fields = ('product__product_name',)
    list_per_page = 20

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'phone')
    search_fields = ('customer_name', 'phone')
    list_per_page = 20

class SaleAdmin(admin.ModelAdmin):
    list_display = ('customer', 'sale_date', 'total_amount', 'payment_method')
    list_filter = ('sale_date', 'payment_method')
    search_fields = ('customer__customer_name',)
    list_per_page = 20

class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('sale', 'product', 'quantity', 'unit_price')
    list_filter = ('sale',)
    search_fields = ('product__product_name',)
    list_per_page = 20

class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'reason', 'adjusted_by')
    list_filter = ('product',)
    search_fields = ('product__product_name', 'reason')
    list_per_page = 20
    


admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Sale, SaleAdmin)
admin.site.register(SaleItem, SaleItemAdmin)
admin.site.register(StockAdjustment, StockAdjustmentAdmin)

admin.site.site_title = "Inventory"
admin.site.site_header = "Inventory"
admin.site.index_title = "Inventory Dashboard"
