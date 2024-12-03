from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="accounts_user_set",
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="accounts_user_permissions",
        blank=True,
    )


class UserDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"Details for {self.user.username}"
