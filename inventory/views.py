from django.http import JsonResponse
from .models import Product
from django.views.decorators.csrf import csrf_exempt
import json

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

