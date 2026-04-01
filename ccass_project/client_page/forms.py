from django import forms
from django.utils.timezone import now

class PalletTransactionForm(forms.Form):
    TRANSACTION_CHOICES = [
        ('deposit', 'Deposit Pallets'),
        ('withdraw', 'Withdraw Pallets'),
    ]

    transaction_type = forms.ChoiceField(
        choices=TRANSACTION_CHOICES
    )
    pallet_count = forms.IntegerField(
        min_value=1,
        label="Number of Pallets"
    )

    date_stored = forms.DateField(
        label="Transaction Date",
        widget=forms.DateInput(attrs={
            "type": "date",
            "min": now().date()
        }),
        initial=now().date()
    )

    def clean_date_stored(self):
        date_stored = self.cleaned_data["date_stored"]
        today = now().date()

        if date_stored < today:
            raise forms.ValidationError(
                "Date stored cannot be earlier than today."
            )

        return date_stored