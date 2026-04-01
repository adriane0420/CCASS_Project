# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from client_page.models import Transaction
from .models import Product
from django.shortcuts import get_object_or_404
from django.contrib import messages

User = get_user_model()

def is_employee(user):
    return user.is_authenticated and user.role == 'employee'


@login_required
@user_passes_test(is_employee)
def employee_dashboard(request):
    total_transactions = Transaction.objects.count()
    recent_transactions = Transaction.objects.order_by('-transaction_date')[:5]

    return render(request, 'employees/dashboard.html', {
        'total_transactions': total_transactions,
        'recent_transactions': recent_transactions,
    })


@login_required
@user_passes_test(is_employee)
def transaction_list(request):
    transactions = Transaction.objects.select_related('client', 'employee').order_by('-transaction_date')

    # Filters
    client_query = request.GET.get('client')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    site_filter = request.GET.get('site')

    if client_query:
        transactions = transactions.filter(client__username__icontains=client_query)

    if start_date:
        transactions = transactions.filter(transaction_date__date__gte=start_date)

    if end_date:
        transactions = transactions.filter(transaction_date__date__lte=end_date)

    # Filter by client site (caloocan or taguig)
    if site_filter in ['caloocan', 'taguig']:
        transactions = transactions.filter(client__site=site_filter)

    return render(request, 'employees/transactions.html', {
        'transactions': transactions,
        'selected_site': site_filter,
    })


@login_required
@user_passes_test(is_employee)
def add_employee(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        phone_number = request.POST['phone_number']

        User.objects.create_user(
            username=username,
            password=password,
            email=email,
            phone_number=phone_number,
            role='employee'
        )

        return redirect('employee_dashboard')

    return render(request, 'employees/add_employee.html')


####### PRODUCTS CRUD ######
@login_required
@user_passes_test(is_employee)
def manage_products(request):

    if request.method == "POST":
        product_id = request.POST.get("product_id")
        price = request.POST.get("price")
        updated_at = request.POST.get("updated_at")

        # DELETE
        if "delete" in request.POST:
            Product.objects.filter(id=product_id).delete()
            messages.success(request, "Service deleted.")
            return redirect("manage_products")

        # UPDATE
        if product_id:
            product = Product.objects.get(id=product_id)
            product.price = price
            product.save()
            messages.success(request, "Price updated.")
            return redirect("manage_products")

        # CREATE / RESTORE
        service_name = request.POST.get("service_name")

        Product.objects.update_or_create(
            name=service_name,
            defaults={"price": price}
        )

        messages.success(request, "Service saved.")
        return redirect("manage_products")

    products = Product.objects.all()
    return render(request, "employees/manage_products.html", {
        "products": products
    })
