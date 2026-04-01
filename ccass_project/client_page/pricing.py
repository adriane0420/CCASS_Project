from emp_page.models import Product

def get_price(service_name):
    try:
        return Product.objects.get(name=service_name).price
    except Product.DoesNotExist:
        return 0  # fallback safety

HANDLING_IN_FEE = float(get_price("Handling In"))     # PHP per pallet
HANDLING_OUT_FEE = float(get_price("Handling Out"))    # PHP per pallet
STORAGE_FEE_PER_DAY = float(get_price("Storage Fee"))  # PHP per pallet per day