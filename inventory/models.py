from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta

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
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE, verbose_name=_("Supplier"))
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name=_("Product"))

    box_quantity = models.IntegerField(_("Number of Boxes"), null=True, blank=True)
    packages_per_box = models.IntegerField(_("Packages per Box"), null=True, blank=True)
    items_per_package = models.IntegerField(_("Items per Package"), null=True, blank=True)

    cost_per_box = models.DecimalField(_("Cost per Box"), max_digits=10, decimal_places=2, null=True, blank=True)
    cost_per_package = models.DecimalField(_("Cost per Package"), max_digits=10, decimal_places=2, null=True, blank=True)
    cost_per_item = models.DecimalField(_("Cost per Item"), max_digits=10, decimal_places=2, null=True, blank=True)

    total_cost_value = models.DecimalField(_("Total Cost"), max_digits=15, decimal_places=2, blank=True, null=True)

    purchase_date = models.DateField(_("Purchase Date"))
    expire_date = models.DateField(_("Expire Date"), null=True, blank=True)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_("Received By"))

    class Meta:
        verbose_name = _("Purchase")
        verbose_name_plural = _("Purchases")

    def save(self, *args, **kwargs):
        # Auto-calculate missing cost fields
        if self.box_quantity and self.packages_per_box:
            if self.cost_per_box and not self.cost_per_package:
                self.cost_per_package = self.cost_per_box / self.packages_per_box
            if self.cost_per_package and self.items_per_package and not self.cost_per_item:
                self.cost_per_item = self.cost_per_package / self.items_per_package

        if self.packages_per_box and self.items_per_package and self.cost_per_package and not self.cost_per_item:
            self.cost_per_item = self.cost_per_package / self.items_per_package

        if self.cost_per_item and self.items_per_package and self.packages_per_box and not self.cost_per_box and self.box_quantity:
            self.cost_per_package = self.cost_per_item * self.items_per_package
            self.cost_per_box = self.cost_per_package * self.packages_per_box

        # Total cost calculation
        self.total_cost_value = self.calculated_total_cost

        # Update product stock
        if self.product:
            self.product.quantity_in_stock += self.total_items
            self.product.save()

        super().save(*args, **kwargs)

    @property
    def total_items(self):
        box = self.box_quantity or 1
        pack = self.packages_per_box or 1
        item = self.items_per_package or 1
        return box * pack * item

    @property
    def total_packages(self):
        box = self.box_quantity or 1
        pack = self.packages_per_box or 1
        return box * pack

    @property
    def calculated_total_cost(self):
        if self.box_quantity and self.cost_per_box:
            return self.box_quantity * self.cost_per_box
        elif self.packages_per_box and self.cost_per_package:
            return self.packages_per_box * self.cost_per_package
        elif self.items_per_package and self.cost_per_item:
            return self.items_per_package * self.cost_per_item
        return Decimal('0.00')

    def __str__(self):
        return f"{self.product.product_name} Purchase on {self.purchase_date}"

        
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
    sale = models.ForeignKey("Sale", verbose_name=_("Sale"), on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey("Product", verbose_name=_("Product"), on_delete=models.CASCADE)

    box_quantity = models.IntegerField(_("Number of Boxes"), null=True, blank=True)
    packages_per_box = models.IntegerField(_("Packages per Box"), null=True, blank=True)
    items_per_package = models.IntegerField(_("Items per Package"), null=True, blank=True)

    cost_per_box = models.DecimalField(_("Cost per Box"), max_digits=10, decimal_places=2, null=True, blank=True)
    cost_per_package = models.DecimalField(_("Cost per Package"), max_digits=10, decimal_places=2, null=True, blank=True)
    cost_per_item = models.DecimalField(_("Cost per Item"), max_digits=10, decimal_places=2, null=True, blank=True)

    total_cost_value = models.DecimalField(_("Total Cost"), max_digits=15, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Step-by-step cost derivation
        if self.box_quantity and self.cost_per_box:
            if self.packages_per_box:
                self.cost_per_package = self.cost_per_box / self.packages_per_box
            if self.packages_per_box and self.items_per_package:
                self.cost_per_item = self.cost_per_box / (self.packages_per_box * self.items_per_package)

        self.total_cost_value = self.calculated_total_cost
        super().save(*args, **kwargs)

    @property
    def quantity(self):
        """Total items = boxes × packages × items."""
        return (self.box_quantity or 0) * (self.packages_per_box or 0) * (self.items_per_package or 0)

    @property
    def unit_price(self):
        """Price per single item."""
        return self.cost_per_item or 0

    @property
    def calculated_total_cost(self):
        """Smart total cost calculator based on available info."""
        if self.cost_per_item:
            return self.quantity * self.cost_per_item
        elif self.cost_per_package and self.packages_per_box:
            return (self.box_quantity or 0) * self.packages_per_box * self.cost_per_package
        elif self.cost_per_box:
            return (self.box_quantity or 0) * self.cost_per_box
        return 0

    def __str__(self):
        return f"{self.product} in Sale #{self.sale.id}"

        
class StockAdjustment(models.Model):
    product = models.ForeignKey(Product, verbose_name=_("Product"), on_delete=models.CASCADE)
    quantity = models.IntegerField(_("Quantity"))
    reason = models.TextField(_("Reason"))
    adjusted_by = models.ForeignKey(User, verbose_name=_("Adjusted By"), on_delete=models.SET_NULL, null=True)

class Meta:
        verbose_name = _("Stock Adjustment")
        verbose_name_plural = _("Stock Adjustment")
        
class Share(models.Model):
    partner_name = models.CharField(_("Partner Name"), max_length=100)
    capital = models.DecimalField(_("Capital"), max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Share")
        verbose_name_plural = _("Shares")

    def __str__(self):
        return f"{self.partner_name} - {self.capital}"

    def calculate_percentage(self):
        total_capital = Share.objects.aggregate(total=models.Sum('capital'))['total'] or 1
        return round((self.capital / total_capital) * 100, 2)

    def calculate_provision(self):
        # Here we fetch total profit from the TotalProfit model
        from .models import TotalProfit
        total_profit = TotalProfit.objects.first()
        if total_profit:
            return round((self.calculate_percentage() / 100) * total_profit.amount, 2)
        return 0
    @property
    def percentage(self):
        total_capital = Share.objects.aggregate(total=models.Sum('capital'))['total'] or 1
        return (self.capital / total_capital) * 100



class TotalProfit(models.Model):
    amount = models.DecimalField(_("Total Profit"), max_digits=12, decimal_places=2)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Total Profit")
        verbose_name_plural = _("Total Profits")

    def __str__(self):
        return str(self.amount)
    

class MonthlyReport(models.Model):
    month = models.CharField(max_length=20)  # e.g., "April 2025"
    total_purchase_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total_sales_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total_profit = models.DecimalField(max_digits=12, decimal_places=2)
    report_data = models.JSONField()  # If using Django 3.1+. Else use jsonfield.JSONField()

    def __str__(self):
        return self.month