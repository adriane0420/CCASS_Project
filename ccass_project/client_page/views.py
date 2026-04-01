from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.db import transaction as db_transaction
import json

from .models import ClientStorage, Transaction
from .forms import PalletTransactionForm
from .calculations import calculate_deposit_amount, calculate_withdraw_amount
from .paymongo import create_payment_intent, attach_payment_method
from datetime import date
from .pricing import *


@login_required
def client_dashboard(request):
    storages = ClientStorage.objects.filter(
        client=request.user
    ).order_by('-date_stored')

    total_pallets = storages.aggregate(
        total=Sum('pallet_count')
    )['total'] or 0

    transactions = Transaction.objects.filter(
        client=request.user
    ).order_by('-transaction_date')

    return render(request, 'clients_page/client_dashboard.html', {
        'storages': storages,
        'transactions': transactions,
        'total_pallets': total_pallets,
    })


@login_required
def pallet_transaction(request):
    form = PalletTransactionForm()
    total_pallets = ClientStorage.objects.filter(
        client=request.user
    ).aggregate(total=Sum('pallet_count'))['total'] or 0

    if request.method == 'POST':
        form = PalletTransactionForm(request.POST)

        if form.is_valid():
            transaction_type = form.cleaned_data['transaction_type']
            pallet_count = form.cleaned_data['pallet_count']
            date_stored = form.cleaned_data['date_stored']

            if pallet_count <= 0:
                messages.error(request, "Pallet count must be greater than zero.")
                return redirect('pallet_transaction')

            # Calculate amount
            breakdown = {}
            if transaction_type == 'deposit':
                amount = pallet_count * HANDLING_IN_FEE

                breakdown = {
                    "transaction_type": "Deposit Pallets",
                    "pallet_count": pallet_count,
                    "rate": HANDLING_IN_FEE,
                    "days": 1,
                    "formula": f"{pallet_count} × ₱{HANDLING_IN_FEE}",
                    "total": amount,
                }

            elif transaction_type == 'withdraw':
                if pallet_count > total_pallets:
                    messages.error(
                        request,
                        "You cannot withdraw more pallets than you currently have."
                    )
                    return redirect('client_dashboard')

                storage_records = ClientStorage.objects.filter(
                    client=request.user
                ).order_by('date_stored')

                total_amount, rows = calculate_withdraw_amount(
                    pallet_count,
                    storage_records,
                    date_stored
                )

                amount = total_amount

                formula_lines = []

                for r in rows:
                    formula_lines.append(
                        f"{r['pallets']} × ₱{STORAGE_FEE_PER_DAY} × {r['days']} days"
                    )

                formula_lines.append(
                    f"{pallet_count} × ₱{HANDLING_OUT_FEE} (handling out)"
                )

                breakdown = {
                    "transaction_type": "Withdraw Pallets",
                    "pallet_count": pallet_count,
                    "formula_lines": formula_lines,
                    "total": amount,
                }


            else:
                messages.error(request, "Invalid transaction type.")
                return redirect('pallet_transaction')


            # Create PayMongo PaymentIntent (centavos)
            payment_intent = create_payment_intent(amount * 100)

            # Build breakdown
            # if transaction_type == "deposit":
            #     rate = 75  # Handling in fee per pallet
            #     formula = f"{pallet_count} * {rate}"
            #     total = amount
            # elif transaction_type == "withdraw":
            #     # Calculate days rendered (difference between today and date_stored)
            #     days_rendered = (date.today() - date_stored).days
            #     if days_rendered < 1:
            #         days_rendered = 1
            #     rate = 75  # Handling out fee
            #     formula = f"{pallet_count} * {rate} * {days_rendered}"
            #     total = amount

            # breakdown = {
            #     "transaction_type": transaction_type.title(),
            #     "pallet_count": pallet_count,
            #     "rate": rate,
            #     "days": days_rendered if transaction_type == "withdraw" else 0,
            #     "formula": formula,
            #     "total": total
            # }

            request.session['pending_transaction'] = {
                'transaction_type': transaction_type,
                'pallet_count': pallet_count,
                'payment_intent_id': payment_intent['data']['id'],
                'amount': amount,
                'date_stored': str(date_stored),
                'breakdown': breakdown,
            }

            return render(request, "clients_page/paymongo_checkout.html", {
                "client_key": payment_intent["data"]["attributes"]["client_key"],
                "public_key": settings.PAYMONGO_PUBLIC_KEY,
                "amount": amount,
                'breakdown': breakdown,
            })

    return render(request, 'clients_page/pallet_transaction.html', {
        'form': form,
        'total_pallets': total_pallets
    })


@login_required
def confirm_payment(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    pending = request.session.get("pending_transaction")
    breakdown = pending.get("breakdown")
    if not pending:
        return JsonResponse({"error": "No pending transaction found"}, status=400)

    try:
        data = json.loads(request.body)
        payment_method_id = data.get("payment_method_id")
        if not payment_method_id:
            return JsonResponse({"error": "Missing payment_method_id"}, status=400)

        response = attach_payment_method(
            pending["payment_intent_id"],
            payment_method_id
        )

        attributes = response["data"]["attributes"]
        status = attributes.get("status")
        last_error = attributes.get("last_payment_error")

        if status != "succeeded":
            return JsonResponse({
                "status": "failed",
                "error": last_error or f"Payment status: {status}"
            }, status=400)

        # ================= PAYMENT SUCCEEDED =================
        transaction_type = pending["transaction_type"]
        pallet_count = pending["pallet_count"]
        amount = pending["amount"]

        price_per_pallet = amount / pallet_count
        total_price = amount

        # Safely restore date_stored from session (deposit only)
        date_stored = None
        if transaction_type == "deposit":
            date_stored_str = pending.get("date_stored")
            if not date_stored_str:
                raise ValueError("Missing date_stored for deposit")
            date_stored = date.fromisoformat(date_stored_str)

        with db_transaction.atomic():

            if transaction_type == "deposit":
                ClientStorage.objects.create(
                    client=request.user,
                    pallet_count=pallet_count,
                    date_stored=date_stored
                )

            elif transaction_type == "withdraw":
                remaining = pallet_count
                storages = ClientStorage.objects.filter(
                    client=request.user
                ).order_by("date_stored")

                for storage in storages:
                    if remaining <= 0:
                        break

                    if storage.pallet_count <= remaining:
                        remaining -= storage.pallet_count
                        storage.delete()
                    else:
                        storage.pallet_count -= remaining
                        storage.save()
                        remaining = 0

            Transaction.objects.create(
                client=request.user,
                transaction_type=transaction_type,
                pallets_purchased=pallet_count,
                price_per_pallet=price_per_pallet,
                total_price=total_price
            )

        # Clear session after success
        del request.session["pending_transaction"]

        return JsonResponse({"status": "success"})

    except Exception as e:
        print("CONFIRM PAYMENT ERROR:", str(e))
        return JsonResponse(
            {"status": "error", "error": str(e)},
            status=500
        )