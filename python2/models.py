from decimal import Decimal

from django.db import models
from django.core.exceptions import ValidationError

from models import TimestampedAbstractModel
from plan.choices import (
    RuleChoices,
    RuleValueTypeChoices,
    ParametersChoices,
    ObjectiveChoices,
    ProgramChoices,
    PlanChoices,
    PhaseChoices,
    PlatformChoice
)
from utils.validate import validate_rule_input_value_type, \
    validate_datestr_format


class Program(TimestampedAbstractModel):
    """
    Model for saving the program details

    Title is required. Other fields are optional.
    """
    title = models.PositiveSmallIntegerField(
        choices=ProgramChoices.choices,
        default=ProgramChoices.EVOLUTION
    )
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created_at', ]
        indexes = [
            models.Index(fields=['title'])
        ]

    def __str__(self):
        return self.get_title_display()

    def get_active_plan(self):
        return self.get_plan.filter(active=True)


class Plan(TimestampedAbstractModel):
    """
    Model for saving the plan details
    """
    title = models.PositiveSmallIntegerField(
        choices=PlanChoices.choices,
        default=PlanChoices.EVOLUTION_STANDARD_PLAN
    )
    program = models.ForeignKey(
        Program,
        related_name='get_plan',
        on_delete=models.CASCADE
    )
    description = models.TextField(null=True, blank=True)
    limited_to = models.IntegerField(
        "Plan purchase limit",
        default=1,
        help_text="Applicable for Evaluation, Endurance & Journey Plans"
    )
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created_at', ]
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['program']),
        ]

    def __str__(self):
        return f"{self.get_title_display()}"


class Phase(TimestampedAbstractModel):
    """
    Model for saving Phase details
    """
    title = models.PositiveSmallIntegerField(
        choices=PhaseChoices.choices,
        default=PhaseChoices.EVOLUTION_STANDARD_PHASE
    )
    description = models.TextField(null=True, blank=True)
    plan = models.ForeignKey(
        Plan,
        related_name='get_phase',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.get_title_display()}"

    class Meta:
        ordering = ['created_at', ]
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['plan']),
        ]


class AccountSizeAndPrice(TimestampedAbstractModel):
    account_size = models.PositiveIntegerField(default=0)
    price = models.DecimalField(
        "Price in SI Coin",
        help_text="Plan price in SI coin",
        decimal_places=2,
        max_digits=20,
        default=Decimal(0)
    )
    account_reset_price = models.DecimalField(
        "Account Reset Price in SI Coin",
        help_text="Account Reset price in SI coin",
        decimal_places=2,
        max_digits=20,
        default=Decimal(0)
    )
    additional_profit_target = models.DecimalField(
        default=Decimal(0),
        decimal_places=2,
        max_digits=20,
        help_text="This will be added to the plan's default profit target."
    )
    additional_max_lots_per_day = models.DecimalField(
        default=Decimal(0),
        decimal_places=2,
        max_digits=20,
        help_text="This will be added to the plan's default max lots per day."
    )
    purchasable = models.BooleanField(default=True)
    profit_split = models.PositiveIntegerField("Reward Percentage", default=0)
    platform = models.PositiveSmallIntegerField(choices=PlatformChoice.choices,
                                                blank=True, null=True)
    phase = models.ForeignKey(
        Phase,
        related_name='get_account_size',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['account_size', ]
        verbose_name = 'Account Size and Price'
        verbose_name_plural = 'Account Size and Price'
        indexes = [
            models.Index(fields=['purchasable']),
            models.Index(fields=['phase']),
        ]

    def __str__(self):
        return f"{self.id}"


class PhaseRule(TimestampedAbstractModel):
    rule = models.PositiveSmallIntegerField(choices=RuleChoices.choices)
    active = models.BooleanField(default=True)
    value_type = models.PositiveSmallIntegerField(
        choices=RuleValueTypeChoices.choices,
        null=True,
        blank=True
    )
    value = models.CharField(max_length=127, null=True, blank=True)
    phase = models.ForeignKey(
        Phase,
        related_name='get_phase_rule',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.get_rule_display()}"

    class Meta:
        unique_together = ('rule', 'phase',)
        ordering = ['created_at', ]
        indexes = [
            models.Index(fields=['rule']),
            models.Index(fields=['phase']),
            models.Index(fields=['active']),
        ]

    def clean(self):
        if self.active and not self.value:
            raise ValidationError(
                f"Please enter a valid {self.get_rule_display()} "
                "value or mark it as inactive"
            )
        elif self.value and not self.value_type:
            raise ValidationError("Please enter a valid Rule Value Type")
        elif self.value and self.value_type:
            return validate_rule_input_value_type(self.value_type, self.value)
