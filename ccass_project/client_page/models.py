from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ClientStorage(models.Model):
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='storages'
    )
    pallet_count = models.PositiveIntegerField()
    date_stored = models.DateField()

    def __str__(self):
        return f"{self.client.username} - {self.pallet_count} pallets"


class Transaction(models.Model):
    TRANSACTION_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
    ]

    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transactions'
    )

    employee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_transactions'
    )

    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_CHOICES,
        null=True,
        blank=True,
    )

    pallets_purchased = models.PositiveIntegerField()
    price_per_pallet = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transaction_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.id} - {self.client} - {self.transaction_type} - {self.pallets_purchased}"
