from .pricing import *
from .utils import calculate_storage_days


def calculate_deposit_amount(pallets):
    return HANDLING_IN_FEE * pallets


def calculate_withdraw_amount(pallets_to_withdraw, storage_records, trans_date):
    remaining = pallets_to_withdraw
    storage_cost = 0
    breakdown_rows = []

    for record in storage_records:
        if remaining <= 0:
            break

        pallets_taken = min(record.pallet_count, remaining)
        days = calculate_storage_days(record.date_stored, trans_date)

        cost = pallets_taken * days * STORAGE_FEE_PER_DAY
        storage_cost += cost

        breakdown_rows.append({
            "pallets": pallets_taken,
            "days": days,
            "cost": cost,
        })

        remaining -= pallets_taken

    handling_cost = pallets_to_withdraw * HANDLING_OUT_FEE
    total = storage_cost + handling_cost
    return total, breakdown_rows