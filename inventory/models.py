from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Supplier(models.Model):
    supplier_name = models.CharField(_("Supplier Name"), max_length=100)
    contact_person = models.CharField(_("Contact Person"), max_length=100)
    phone = models.CharField(_("Phone"), max_length=20, blank=True)
    email = models.EmailField(_("Email"), blank=True)
    address = models.TextField(_("Address"), blank=True)

    class Meta:
        verbose_name = _("Supplier")
        verbose_name_plural = _("Suppliers")
        
    def __str__(self):
        return self.supplier_name

class Product(models.Model):
    product_name = models.CharField(_("Product Name"), max_length=100)
    description = models.TextField(_("Description"), blank=True, null=True)
    barcode = models.CharField(_("Barcode"), max_length=50, blank=True)
    category = models.CharField(_("Category"), max_length=50, blank=True)
    purchase_price = models.DecimalField(_("Purchase Price"), max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(_("Selling Price"), max_digits=10, decimal_places=2)
    quantity_in_stock = models.IntegerField(_("Quantity in Stock"))
    min_stock_level = models.IntegerField(_("Minimum Stock Level"))
    supplier = models.ForeignKey(Supplier, verbose_name=_("Supplier"), on_delete=models.CASCADE)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        
    def __str__(self):
        return self.product_name

class Purchase(models.Model):
    supplier = models.ForeignKey(Supplier, verbose_name=_("Supplier"), on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name=_("Product"), on_delete=models.CASCADE)
    quantity = models.IntegerField(_("Quantity"))
    unit_price = models.DecimalField(_("Unit Price"), max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(_("Total Cost"), max_digits=10, decimal_places=2)
    purchase_date = models.DateField(_("Purchase Date"))
    received_by = models.ForeignKey(User, verbose_name=_("Received By"), on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = _("Purchase")
        verbose_name_plural = _("Purchases")
        
class Customer(models.Model):
    customer_name = models.CharField(_("Customer Name"), max_length=100)
    phone = models.CharField(_("Phone"), max_length=20, blank=True)

    class Meta:
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")
        
    def __str__(self):
        return self.customer_name

class Sale(models.Model):
    customer = models.ForeignKey(Customer, verbose_name=_("Customer"), on_delete=models.SET_NULL, null=True, blank=True)
    sale_date = models.DateTimeField(_("Sale Date"), auto_now_add=True)
    total_amount = models.DecimalField(_("Total Amount"), max_digits=10, decimal_places=2)
    
    PAYMENT_CHOICES = (
        ('cash', _("Cash")),
        ('card', _("Card")),
        ('mobile', _("Mobile Money")),
    )
    payment_method = models.CharField(_("Payment Method"), max_length=10, choices=PAYMENT_CHOICES)

    class Meta:
        verbose_name = _("Sale")
        verbose_name_plural = _("Sales")
        
    def __str__(self):
        return f"Sale #{self.id} - {self.customer.customer_name if self.customer else _('No Customer')} on {self.sale_date.strftime('%Y-%m-%d')}"

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, verbose_name=_("Sale"), on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name=_("Product"), on_delete=models.CASCADE)
    quantity = models.IntegerField(_("Quantity"))
    unit_price = models.DecimalField(_("Unit Price"), max_digits=10, decimal_places=2)
class Meta:
        verbose_name = _("Sale item")
        verbose_name_plural = _("Sale items")
        
class StockAdjustment(models.Model):
    product = models.ForeignKey(Product, verbose_name=_("Product"), on_delete=models.CASCADE)
    quantity = models.IntegerField(_("Quantity"))
    reason = models.TextField(_("Reason"))
    adjusted_by = models.ForeignKey(User, verbose_name=_("Adjusted By"), on_delete=models.SET_NULL, null=True)

class Meta:
        verbose_name = _("Stock adjustment")
        verbose_name_plural = _("Stock adjustment")
        
class Share(models.Model):
    partner_name = models.CharField(_("Partner Name"), max_length=100)
    percentage = models.DecimalField(_("Percentage"), max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Share")
        verbose_name_plural = _("Shares")
        
    def __str__(self):
        return f"{self.partner_name} - {self.percentage}%"
