from django.contrib import admin
from django.db.models import F, Sum, ExpressionWrapper, DecimalField
from .models import Supplier, Product, Purchase, Customer, Sale, SaleItem, StockAdjustment, Share, TotalProfit
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta
from django.utils.html import format_html


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
    list_display = (
        'supplier', 
        'product', 
        'box_quantity', 
        'total_packages_display',
        'total_items_display',
        'cost_per_item',
        'display_total_cost', 
        'purchase_date', 
        'expire_date', 
        'highlight_expire_date',
        'received_by'
    )
    list_filter = ('purchase_date', 'supplier', 'expire_date')
    search_fields = ('product__product_name',)
    list_per_page = 10

    def highlight_expire_date(self, obj):
        if obj.expire_date and obj.expire_date <= date.today() + timedelta(days=30):
            return format_html('<span style="color: red; font-weight: bold;">{}</span>', obj.expire_date)
        return obj.expire_date
    highlight_expire_date.short_description = _("Expire Date")

    def display_total_cost(self, obj):
        return "{:.2f}".format(obj.total_cost_value or 0)
    display_total_cost.short_description = _("Total Cost")

    def total_packages_display(self, obj):
        return obj.total_packages
    total_packages_display.short_description = _("Total Packages")

    def total_items_display(self, obj):
        return obj.total_items
    total_items_display.short_description = _("Total Items")

    class Media:
        js = ('admin/js/purchase_auto_calculate.js',)  # Ensure the JS file is loaded

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:  # if editing existing purchase (obj is not None)
            self.Media.js = ()  # Disable JS for editing (no auto-calculation needed)
        else:
            self.Media.js = ('admin/js/purchase_auto_calculate.js',)  # Enable JS for adding new purchase
        return form


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
    list_display = (
        'sale', 
        'product', 
        'box_quantity', 
        'packages_per_box', 
        'items_per_package', 
        'total_cost_value'  # Use total_cost instead of total_cost_value
    )
    list_filter = ('sale',)
    search_fields = ('product__product_name',)
    list_per_page = 10

    # Optionally, display total cost value
    def total_cost(self, obj):
        # Assuming `obj.total_cost` calculates the cost for the sale item.
        return "{:.2f}".format(obj.total_cost or 0)
    total_cost.short_description = _("Total Cost")

    class Media:
        js = ('admin/js/saleitem_auto_calculate.js',)

class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'reason', 'adjusted_by')
    list_filter = ('product',)
    search_fields = ('product__product_name', 'reason')
    list_per_page = 10
    verbose_name = _("Stock adjustment")
    verbose_name_plural = _("Stock adjustments")

class ShareAdmin(admin.ModelAdmin):
    list_display = ('partner_name', 'capital', 'show_percentage', 'show_provision', 'created_at')
    fields = ('partner_name', 'capital')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['capital'].required = True
        return form

    def show_percentage(self, obj):
        return f"{obj.calculate_percentage()}%"

    show_percentage.short_description = _("Percentage")

    def show_provision(self, obj):
        return f"{obj.calculate_provision()}"

    show_provision.short_description = _("Provision (Estimated)")
    

class TotalProfitAdmin(admin.ModelAdmin):
    list_display = ('amount', 'updated_at')

# Register models
admin.site.register(TotalProfit, TotalProfitAdmin)
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
