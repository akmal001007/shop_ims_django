from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render
from django.db.models import Sum
from datetime import date, datetime
from django.utils.timezone import now
from .models import Purchase, Sale, SaleItem, Product, Share, MonthlyReport
from inventory.utils import generate_monthly_report
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.utils.translation import gettext as _


def my_view(request):
    messages.success(request, _("Product added successfully"))

def product_list(request):
    if request.method == 'GET':
        products = Product.objects.all().values(
            'id', 'product_name', 'category', 'quantity_in_stock', 'selling_price', 'barcode'
        )
        return JsonResponse(list(products), safe=False)

@csrf_exempt
def product_create(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product = Product.objects.create(
            product_name=data['product_name'],
            description=data.get('description'),
            barcode=data['barcode'],
            category=data['category'],
            purchase_price=data['purchase_price'],
            selling_price=data['selling_price'],
            quantity_in_stock=data['quantity_in_stock'],
            min_stock_level=data['min_stock_level'],
            supplier_id=data['supplier_id']
        )
        return JsonResponse({'id': product.id, 'message': 'Product created successfully'})

def daily_report(request):
    today = now().date()

    # Total purchase amount for today
    total_purchase_amount = Purchase.objects.filter(purchase_date=today).aggregate(
        total=Sum('total_cost_value')
    )['total'] or 0

    # Total sales amount for today
    total_sales_amount = Sale.objects.filter(sale_date__date=today).aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    # Calculate total real profit (sales - cost)
    sale_items = SaleItem.objects.filter(sale__sale_date__date=today)
    total_profit = 0
    for item in sale_items:
        purchase_price = item.product.purchase_price or 0
        sell_price = item.unit_price or 0
        quantity = item.quantity or 0
        total_profit += (sell_price - purchase_price) * quantity

    # Remaining stock calculation
    remaining_stock = []
    products = Product.objects.all()
    for product in products:
        purchased_items = Purchase.objects.filter(product=product)
        sold_items = SaleItem.objects.filter(product=product)

        total_purchased = sum(
            (p.box_quantity or 0) * (p.packages_per_box or 0) * (p.items_per_package or 0)
            for p in purchased_items
        )
        total_sold = sum(
            (s.box_quantity or 0) * (s.packages_per_box or 0) * (s.items_per_package or 0)
            for s in sold_items
        )
        remaining = total_purchased - total_sold

        remaining_stock.append({
            'product_name': product.product_name,
            'purchased': total_purchased,
            'sold': total_sold,
            'remaining': remaining,
        })

    # Partner profit calculation
    shares = Share.objects.all()
    partner_profits = []
    for share in shares:
        share_profit = (share.percentage / 100) * total_profit
        partner_profits.append({
            'partner': share.partner_name,
            'percentage': share.percentage,
            'profit': share_profit,
        })

    return render(request, 'inventory/report.html', {
        'total_purchase_amount': total_purchase_amount,
        'total_sales_amount': total_sales_amount,
        'profit': total_profit,
        'remaining_stock': remaining_stock,
        'partner_profits': partner_profits,
    })
    
    
def monthly_report(request):
    month = int(request.GET.get('month', datetime.now().month))
    year = int(request.GET.get('year', datetime.now().year))

    # Filter data by selected month and year
    purchases = Purchase.objects.filter(purchase_date__month=month, purchase_date__year=year)
    sales = Sale.objects.filter(sale_date__month=month, sale_date__year=year)
    sale_items = SaleItem.objects.filter(sale__sale_date__month=month, sale__sale_date__year=year)

    total_purchases = purchases.aggregate(total=Sum('total_cost_value'))['total'] or 0
    total_sales_price = sales.aggregate(total=Sum('total_amount'))['total'] or 0

    # Calculate total quantity sold manually
    total_sales_count = sum(
        (item.box_quantity or 0) * (item.packages_per_box or 0) * (item.items_per_package or 0)
        for item in sale_items
    )

    # Calculate profit
    profit = 0
    for item in sale_items:
        quantity = (item.box_quantity or 0) * (item.packages_per_box or 0) * (item.items_per_package or 0)
        unit_price = item.cost_per_item or 0
        purchase_price = item.product.purchase_price or 0
        profit += (unit_price - purchase_price) * quantity

    remaining_stock = Product.objects.aggregate(stock=Sum('quantity_in_stock'))['stock'] or 0

    shares = Share.objects.all()
    share_profits = []
    for share in shares:
        share_profits.append({
            'partner_name': share.partner_name,
            'percentage': share.percentage,
            'profit': round((share.percentage / 100) * profit, 2),
        })

    context = {
        'month': month,
        'year': year,
        'total_purchases': total_purchases,
        'total_sales_price': total_sales_price,
        'total_sales_count': total_sales_count,
        'remaining_stock': remaining_stock,
        'profit': profit,
        'share_profits': share_profits,
    }

    return render(request, 'inventory/monthly_report.html', context)

def monthly_report_list(request):
    # Query all reports (or filter as needed)
    reports = MonthlyReport.objects.all()  

    # Calculate Total Sales dynamically
    total_sales = Sale.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    # Calculate Total Purchases dynamically
    total_purchases = Purchase.objects.aggregate(Sum('total_cost_value'))['total_cost_value__sum'] or 0

    # Fetch additional purchase details
    purchase_details = Purchase.objects.all()

    context = {
        'reports': reports,
        'total_sales': total_sales,
        'total_purchases': total_purchases,
        'purchase_details': purchase_details,
        'products': [] 
    }

    return render(request, 'inventory/permanent_report_list.html', context)

def download_report_pdf(request):
    # Create a response object with PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="permanent_report.pdf"'

    # Create a PDF object
    p = canvas.Canvas(response, pagesize=letter)
    
    # Example: Add content to the PDF (you can format it however you'd like)
    p.drawString(100, 750, "Permanent Report")
    reports = MonthlyReport.objects.all()  # Fetch your data (adjust the query as needed)
    
    y_position = 730
    for report in reports:
        p.drawString(100, y_position, f"Report: {report.title}")  # Adjust based on your model fields
        y_position -= 20

    # Finish the PDF
    p.showPage()
    p.save()

    return response