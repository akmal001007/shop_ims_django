from django.contrib import admin
from django.db.models import F, Sum, ExpressionWrapper, DecimalField
from .models import Supplier, Product, Purchase, Customer, Sale, SaleItem, StockAdjustment, Share
from django.utils.translation import gettext_lazy as _

class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'product_name', 'description', 'barcode', 'category',
        'purchase_price', 'selling_price', 'quantity_in_stock',
        'min_stock_level', 'supplier', 'created_at'
    )
    list_filter = ('category', 'supplier', 'created_at')
    search_fields = ('product_name', 'barcode')
    list_per_page = 10
    ordering = ('created_at',)
    verbose_name = _("Product")
    verbose_name_plural = _("Products")

class SupplierAdmin(admin.ModelAdmin):
    list_display = ('supplier_name', 'contact_person', 'phone', 'email', 'address')
    search_fields = ('supplier_name', 'contact_person')
    list_per_page = 10
    verbose_name = _("Supplier")
    verbose_name_plural = _("Suppliers")

class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'product', 'quantity', 'unit_price', 'total_cost', 'purchase_date', 'received_by')
    list_filter = ('purchase_date', 'supplier')
    search_fields = ('product__product_name',)
    list_per_page = 10
    verbose_name = _("Purchase")
    verbose_name_plural = _("Purchases")

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'phone')
    search_fields = ('customer_name', 'phone')
    list_per_page = 10
    verbose_name = _("Customer")
    verbose_name_plural = _("Customers")

class SaleAdmin(admin.ModelAdmin):
    list_display = ('customer', 'sale_date', 'total_amount', 'payment_method')
    list_filter = ('sale_date', 'payment_method')
    search_fields = ('customer__customer_name',)
    list_per_page = 10
    verbose_name = _("Sale")
    verbose_name_plural = _("Sales")

class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('sale', 'product', 'quantity', 'unit_price')
    list_filter = ('sale',)
    search_fields = ('product__product_name',)
    list_per_page = 10
    verbose_name = _("Sale Item")
    verbose_name_plural = _("Sale Item")

class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'reason', 'adjusted_by')
    list_filter = ('product',)
    search_fields = ('product__product_name', 'reason')
    list_per_page = 10
    verbose_name = _("Stock Adjustment")
    verbose_name_plural = _("Stock Adjustment")

class ShareAdmin(admin.ModelAdmin):
    list_display = ('partner_name', 'percentage', 'provision', 'created_at')
    search_fields = ('partner_name',)
    list_per_page = 10
    verbose_name = _("Share")
    verbose_name_plural = _("Shares")

    def provision(self, obj):
        profit_qs = SaleItem.objects.annotate(
            profit_per_item=ExpressionWrapper(
                (F('unit_price') - F('product__purchase_price')) * F('quantity'),
                output_field=DecimalField()
            )
        ).aggregate(total_profit=Sum('profit_per_item'))

        total_profit = profit_qs['total_profit'] or 0
        return round((obj.percentage / 100) * total_profit, 2)

    provision.short_description = _('Provision (Estimate)')

# Register models
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Sale, SaleAdmin)
admin.site.register(SaleItem, SaleItemAdmin)
admin.site.register(StockAdjustment, StockAdjustmentAdmin)
admin.site.register(Share, ShareAdmin)

# Admin site translation
admin.site.site_title = _("Inventory")
admin.site.site_header = _("Inventory")
admin.site.index_title = _("Inventory Dashboard")
