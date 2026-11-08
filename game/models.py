from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db import models
from .fields import MoneyField


class PlayerProgress(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress')
    money = MoneyField(max_digits=24, decimal_places=2, default=0)
    lifetime_earnings = MoneyField(max_digits=24, decimal_places=2, default=0)
    last_income_at = models.DateTimeField(auto_now_add=True)
    last_work_at = models.DateTimeField(null=True, blank=True)
    last_daily_claim_at = models.DateTimeField(null=True, blank=True)
    discovered_businesses = models.ManyToManyField('Business', blank=True, related_name='discoverers')
    achievement_points = models.PositiveIntegerField(default=0)
    total_points_earned = models.PositiveIntegerField(default=0)
    total_businesses_purchased = models.PositiveIntegerField(default=0)
    total_upgrades_purchased = models.PositiveIntegerField(default=0)
    total_work_actions = models.PositiveIntegerField(default=0)
    total_daily_claims = models.PositiveIntegerField(default=0)
    most_business_types = models.PositiveIntegerField(default=0)
    run_earnings = MoneyField(max_digits=24, decimal_places=2, default=0)
    prestige_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.user.username} progress'

class Business(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    base_price = MoneyField(
        max_digits=24,
        decimal_places=2,
        default=10,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    income_per_second = MoneyField(
        max_digits=24,
        decimal_places=2,
        default=1,
        validators=[MinValueValidator(Decimal('0.00'))],
    )

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(base_price__gte=Decimal('0.01')), name='positive_business_price'),
            models.CheckConstraint(condition=models.Q(income_per_second__gte=Decimal('0.00')), name='nonnegative_business_income'),
        ]

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class OwnedBusiness(models.Model):
    player = models.ForeignKey(
        PlayerProgress,
        on_delete=models.CASCADE,
        related_name="owned_businesses",
    )
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="owners",
    )
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    upgrade_level = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(10)])

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(quantity__gte=1), name='positive_owned_quantity'),
            models.CheckConstraint(condition=models.Q(upgrade_level__lte=10), name='business_upgrade_limit'),
            models.UniqueConstraint(
                fields=["player", "business"],
                name="unique_player_business",
            )
        ]

    def __str__(self):
        return (
            f"{self.player.user.username}: "
            f"{self.quantity} × {self.business.name}"
        )

class AchievementClaim(models.Model):
    player = models.ForeignKey(PlayerProgress, on_delete=models.CASCADE, related_name='achievement_claims')
    code = models.CharField(max_length=60)
    claimed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['player', 'code'], name='unique_player_achievement')]


class GlobalUpgrade(models.Model):
    player = models.ForeignKey(PlayerProgress, on_delete=models.CASCADE, related_name='global_upgrades')
    code = models.CharField(max_length=60)
    level = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(3)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['player', 'code'], name='unique_player_global_upgrade'),
            models.CheckConstraint(condition=models.Q(level__gte=1, level__lte=3), name='global_upgrade_limit'),
        ]
