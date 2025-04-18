import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Store, Product
from django.core.exceptions import PermissionDenied
from django.contrib import messages
import json
from twilio.rest import Client  # Import Twilio client
from datetime import datetime, timedelta
from collections import defaultdict
import random

# Twilio configuration (replace with your credentials)
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = 'your_twilio_phone_number'

logger = logging.getLogger(__name__)

def home(request):
    stores = Store.objects.all()
    selected_store_id = request.GET.get('store_id')
    selected_store = Store.objects.filter(id=selected_store_id).first()
    products = Product.objects.filter(store=selected_store) if selected_store else []

    logger.info(f"Home page accessed. Selected store ID: {selected_store_id}. Selected store: {selected_store}. Products: {products}")

    return render(request, 'home.html', {
        'stores': stores,
        'selected_store': selected_store,
        'products': products,
    })

@login_required
def product_view(request: HttpRequest) -> HttpResponse:
    stores = Store.objects.filter(owner=request.user)
    selected_store_id = request.GET.get('store_id')
    selected_store = stores.filter(id=selected_store_id).first()

    if not selected_store:
        logger.warning(f"Unauthorized access attempt by user {request.user} to store ID: {selected_store_id}")
        raise PermissionDenied("You do not have permission to view this store.")

    products = Product.objects.filter(store=selected_store)

    logger.info(f"Product view accessed by user {request.user}. Selected store ID: {selected_store_id}. Selected store: {selected_store}. Products: {products}")

    return render(request, 'product.html', {
        'selected_store': selected_store,
        'products': products,
    })

@login_required
def save_product_changes(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product_name = request.POST.get('name')
        product_price = request.POST.get('price')
        product_quantity = request.POST.get('quantity')

        product = get_object_or_404(Product, id=product_id)

        if product.store.owner != request.user:
            logger.warning(f"Unauthorized edit attempt by user {request.user} on product {product.id}")
            raise PermissionDenied("You do not have permission to edit this product.")

        try:
            product.name = product_name
            product.price = float(product_price)
            product.quantity = int(product_quantity)
            product.save()

            logger.info(f"Product updated successfully by user {request.user}: {product}")
        except (ValueError, TypeError) as e:
            logger.error(f"Error updating product: {e}")
            return HttpResponse("Invalid data provided", status=400)

        return redirect(f"/products/?store_id={product.store.id}")
    else:
        return HttpResponse("Invalid request method", status=405)

@login_required
def add_product(request):
    if request.method == 'POST':
        store_id = request.POST.get('store_id')
        if not store_id:
            return JsonResponse({'error': 'Store ID is required'}, status=400)

        try:
            store = get_object_or_404(Store, id=store_id, owner=request.user)
        except ValueError:
            return JsonResponse({'error': 'Invalid Store ID'}, status=400)

        name = request.POST.get('name')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        image = request.POST.get('image')

        try:
            product = Product.objects.create(
                store=store,
                name=name,
                price=price,
                quantity=quantity,
                image=image
            )
            return JsonResponse({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'quantity': product.quantity,
                'image': product.image,
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def owner_view(request):
    owner = request.user
    stores = Store.objects.filter(owner=owner)
    products = Product.objects.filter(store__in=stores).order_by('-id')  # Order by latest (descending)

     # Generate present day sales data based on sold_quantity
    present_day_sales = {}
    today = datetime.today().strftime('%Y-%m-%d')
    for product in products:
        present_day_sales[product.name] = product.sold_quantity  # Use sold_quantity for today's sales

    # Generate past month sales data based on sold_quantity
    past_month_sales = {}
    for product in products:
        past_month_sales[product.name] = {}
        for i in range(30):  # Simulate sales for the last 30 days
            date = datetime.today() - timedelta(days=i)
            past_month_sales[product.name][date.strftime('%Y-%m-%d')] = random.randint(0, product.sold_quantity)

    logger.info(f"Owner view accessed by user {owner}. Stores: {stores}")

    return render(request, 'owner.html', {
        'owner': owner,
        'stores': stores,
        'products': products,
        'present_day_sales': present_day_sales,  # Pass present day sales data
        'past_month_sales': past_month_sales,  # Pass past month sales data
    })

@login_required
def adjust_quantity(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity_change = data.get('quantity_change')

            if not product_id or quantity_change is None:
                return JsonResponse({'error': 'Product ID and quantity change are required.'}, status=400)

            product = get_object_or_404(Product, id=product_id, store__owner=request.user)
            product.quantity += quantity_change

            if quantity_change < 0:  # Selling products
                if product.quantity < 0:
                    return JsonResponse({'error': 'Not enough stock to sell.'}, status=400)
                product.sold_quantity += abs(quantity_change)

            product.save()

            # Send SMS if quantity is less than 10
            if product.quantity < 10:
                send_low_stock_sms(product)

            return JsonResponse({
                'id': product.id,
                'quantity': product.quantity,
                'sold_quantity': product.sold_quantity,
            })
        except ValueError:
            return JsonResponse({'error': 'Invalid quantity change.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def send_low_stock_sms(product):
    """Send an SMS alert for low stock."""
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = f"Alert: The stock for {product.name} is low ({product.quantity} remaining). Please restock soon."
    recipient_number = product.store.owner.profile.phone_number  # Fetch dynamically if available
    try:
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=recipient_number
        )
        logger.info(f"Low stock SMS sent for product {product.name} to {recipient_number}")
    except Exception as e:
        logger.error(f"Failed to send SMS for product {product.name}: {e}")

@login_required
def sell_product(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity_sold = data.get('quantity_sold')

            if not product_id or quantity_sold is None:
                return JsonResponse({'error': 'Product ID and quantity sold are required.'}, status=400)

            product = get_object_or_404(Product, id=product_id, store__owner=request.user)
            product.sell(quantity_sold)

            return JsonResponse({'id': product.id, 'quantity': product.quantity, 'sold_quantity': product.sold_quantity})
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def custom_404_view(request: HttpRequest, exception) -> HttpResponse:
    logger.error(f"404 error at path: {request.path}")
    return render(request, '404.html', status=404)

def custom_500_view(request: HttpRequest) -> HttpResponse:
    logger.error("500 error occurred", exc_info=True)
    return render(request, '500.html', status=500)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirect authenticated users to the home page
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Redirect to home after successful login
        else:
            return render(request, 'login.html', {'form': form, 'error': 'Invalid username or password.'})
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirect authenticated users to the home page
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            return render(request, 'registration.html', {'form': form, 'error': 'Registration failed. Please correct the errors below.'})
    else:
        form = UserCreationForm()
    return render(request, 'registration.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')  # Redirect to home page after logout
