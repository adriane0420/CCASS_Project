from django.utils.timezone import now

def calculate_storage_days(storage_date, trans_date):
    return (trans_date - storage_date).days