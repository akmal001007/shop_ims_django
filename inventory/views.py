from django.http import JsonResponse
from .models import Product
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render
from django.db.models import Sum
from datetime import date
from datetime import datetime
from django.utils.timezone import now
from .models import Purchase, Sale, SaleItem, Product, Share

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

    # Total purchase amount
    total_purchase_amount = Purchase.objects.filter(purchase_date=today).aggregate(total=Sum('total_cost'))['total'] or 0

    # Total sales amount
    total_sales_amount = Sale.objects.filter(sale_date__date=today).aggregate(total=Sum('total_amount'))['total'] or 0

    # Calculate actual profit per item sold
    sale_items = SaleItem.objects.filter(sale__sale_date__date=today)
    total_profit = 0

    for item in sale_items:
        product = item.product
        purchase_price = product.purchase_price  # Assuming this is the average or last purchase price
        sell_price = item.unit_price
        quantity = item.quantity

        item_profit = (sell_price - purchase_price) * quantity
        total_profit += item_profit

    # Remaining stock logic
    remaining_stock = []
    products = Product.objects.all()
    for product in products:
        purchased = Purchase.objects.filter(product=product).aggregate(total=Sum('quantity'))['total'] or 0
        sold = SaleItem.objects.filter(product=product).aggregate(total=Sum('quantity'))['total'] or 0
        remaining = purchased - sold
        remaining_stock.append({
            'product_name': product.product_name,
            'purchased': purchased,
            'sold': sold,
            'remaining': remaining
        })

    # Partner profits based on real profit
    shares = Share.objects.all()
    partner_profits = []
    for share in shares:
        share_profit = (share.percentage / 100) * total_profit
        partner_profits.append({
            'partner': share.partner_name,
            'percentage': share.percentage,
            'profit': share_profit
        })

    return render(request, 'inventory/report.html', {
        'total_purchase_amount': total_purchase_amount,
        'total_sales_amount': total_sales_amount,
        'profit': total_profit,
        'remaining_stock': remaining_stock,
        'partner_profits': partner_profits,
    })
    today = now().date()

    total_purchase = Purchase.objects.filter(purchase_date=today).aggregate(total=Sum('total_cost'))['total'] or 0
    total_sales = Sale.objects.filter(sale_date__date=today).aggregate(total=Sum('total_amount'))['total'] or 0

    # Actual profit calculation (sales - purchases)
    profit = total_sales - total_purchase

    # Remaining stock per product
    remaining_stock = []
    products = Product.objects.all()
    for product in products:
        purchased = Purchase.objects.filter(product=product).aggregate(total=Sum('quantity'))['total'] or 0
        sold = SaleItem.objects.filter(product=product).aggregate(total=Sum('quantity'))['total'] or 0
        remaining = purchased - sold
        remaining_stock.append({
            'product_name': product.product_name,
            'purchased': purchased,
            'sold': sold,
            'remaining': remaining
        })

    # Calculate partner profits based on actual profit
    shares = Share.objects.all()
    partner_profits = []
    for share in shares:
        share_profit = (share.percentage / 100) * profit
        partner_profits.append({
            'partner': share.partner_name,
            'percentage': share.percentage,
            'profit': share_profit
        })

    return render(request, 'inventory/report.html', {
        'total_purchase_amount': total_purchase,
        'total_sales_amount': total_sales,
        'remaining_stock': remaining_stock,
        'partner_profits': partner_profits,
        'profit': profit,
    })
    today = now().date()

    # Total purchases today
    purchases = Purchase.objects.filter(purchase_date=today)
    total_purchase_amount = purchases.aggregate(total=Sum('total_cost'))['total'] or 0

    # Total sales today
    sale_items = SaleItem.objects.filter(sale__sale_date__date=today)
    total_sales_amount = sale_items.aggregate(total=Sum('unit_price'))['total'] or 0

    # Calculate total quantity sold today per product
    sold_quantities = (
        SaleItem.objects
        .filter(sale__sale_date__date=today)
        .values('product__product_name')
        .annotate(total_sold=Sum('quantity'))
    )

    # Remaining stock per product
    products = Product.objects.all()
    remaining_stock = [
        {
            'product_name': product.product_name,
            'purchased': product.quantity_in_stock + sum(
                item['total_sold'] for item in sold_quantities if item['product__product_name'] == product.product_name
            ),
            'sold': sum(item['total_sold'] for item in sold_quantities if item['product__product_name'] == product.product_name),
            'remaining': product.quantity_in_stock
        }
        for product in products
    ]

    # Partner profits (based on total sales only)
    shares = Share.objects.all()
    partner_profits = []

    for share in shares:
        partner_profits.append({
            'partner': share.partner_name,
            'percentage': share.percentage,
            'profit': (share.percentage / 100) * total_sales_amount
        })

    return render(request, 'inventory/report.html', {
        'total_purchase_amount': total_purchase_amount,
        'total_sales_amount': total_sales_amount,
        'total_sales_price': total_sales_price,
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

    total_purchases = purchases.aggregate(total=Sum('total_cost'))['total'] or 0
    total_sales_price = sales.aggregate(total=Sum('total_amount'))['total'] or 0
    total_sales_count = sale_items.aggregate(total=Sum('quantity'))['total'] or 0

    # Calculate profit
    profit = 0
    for item in sale_items:
        purchase_price = item.product.purchase_price
        profit += (item.unit_price - purchase_price) * item.quantity

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