from .models import MonthlyReport, Sale, Purchase, Share, SaleItem, Product
from django.db.models import Sum
from django.utils.timezone import now
from datetime import date
import calendar

def generate_monthly_report():
    today = now().date()
    first_day = today.replace(day=1)
    last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])

    # Aggregates
    total_sales = Sale.objects.filter(sale_date__range=(first_day, last_day)).aggregate(total=Sum('total_amount'))['total'] or 0
    total_purchases = Purchase.objects.filter(purchase_date__range=(first_day, last_day)).aggregate(total=Sum('total_cost_value'))['total'] or 0

    sale_items = SaleItem.objects.filter(sale__sale_date__range=(first_day, last_day))
    profit = sum((item.unit_price - item.product.purchase_price) * item.quantity for item in sale_items)

    partner_profits = []
    for share in Share.objects.all():
        share_profit = (share.percentage / 100) * profit
        partner_profits.append({
            "partner": share.partner_name,
            "percentage": share.percentage,
            "profit": share_profit
        })

    stock_summary = []
    for product in Product.objects.all():
        purchased = Purchase.objects.filter(product=product).aggregate(total=Sum('box_quantity'))['total'] or 0
        sold = SaleItem.objects.filter(product=product).aggregate(total=Sum('quantity'))['total'] or 0
        stock_summary.append({
            "product_name": product.product_name,
            "purchased": purchased,
            "sold": sold,
            "remaining": product.quantity_in_stock or 0
        })

    # Save the report
    MonthlyReport.objects.update_or_create(
        month=first_day,
        defaults={
            "total_purchase_amount": total_purchases,
            "total_sales_amount": total_sales,
            "total_profit": profit,
            "report_data": {
                "stock": stock_summary,
                "partner_profits": partner_profits,
            }
        }
    )
