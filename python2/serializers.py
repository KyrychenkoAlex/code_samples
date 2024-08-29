from rest_framework import serializers

from django.conf import settings

from plan import models
from plan import constants
from plan import errors
from utils import plan as plan_utils
from user_plan.models import UserPlan, UnlockedPlan
from platform import constants as brokeree_cst
from payment.serializers import PaymentBaseInputSerializer
from payment import errors as payment_errors
from payment import constants as payment_cst
from utils.payment import apply_discount_code, validate_discount_code


class ObjectiveSerializer(serializers.ModelSerializer):
    objective = serializers.SerializerMethodField()
    value_type = serializers.SerializerMethodField()

    class Meta:
        model = models.PhaseObjective
        fields = ['objective', 'value', 'value_type', 'active']

    @staticmethod
    def get_objective(obj):
        return obj.get_objective_display()

    @staticmethod
    def get_value_type(obj):
        return obj.get_value_type_display()


class ParameterSerializer(serializers.ModelSerializer):
    parameter = serializers.SerializerMethodField()
    value_type = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()

    class Meta:
        model = models.PhaseParameter
        fields = ['parameter', 'value', 'value_type', 'active']

    @staticmethod
    def get_value(obj):
        if obj.value_type == models.RuleValueTypeChoices.YES_OR_NO:
            return True if obj.value in constants.BOOLEAN_TRUE_OPTIONS else \
                False
        if (obj.active and obj.parameter ==
                models.ParametersChoices.INSTRUMENTS_ALLOWED):
            if obj.value == "FOREX":
                return brokeree_cst.SPRINT_FOREX_FRENZY_INSTRUMENTS
            elif obj.value == "GOLD":
                return brokeree_cst.SPRINT_GOLD_DIGGER_INSTRUMENTS
            elif obj.value == "CRYPTO":
                return brokeree_cst.SPRINT_CRYPTO_CRAZY_INSTRUMENTS
            else:
                return ["all"]
        return obj.value

    @staticmethod
    def get_parameter(obj):
        return obj.get_parameter_display()

    @staticmethod
    def get_value_type(obj):
        if obj.value_type == models.RuleValueTypeChoices.YES_OR_NO:
            return "Boolean"
        return obj.get_value_type_display()


class PlanPurchaseSerializer(PaymentBaseInputSerializer):
    """
    Serializer for validating purchase a plan POST request
    """
    plan_id = serializers.CharField(required=True)
    platform = serializers.CharField(required=False)
    account_size = serializers.IntegerField(required=False)
    account_label = serializers.CharField(required=False)
    discount_code = serializers.CharField(required=False, allow_blank=True)
    quantity = serializers.IntegerField(required=True)

    def validate_plan_id(self, value):
        try:
            plan = models.Plan.objects.get(id=value)
        except:
            raise serializers.ValidationError("Invalid plan id")
        if not models.Phase.objects.filter(plan=plan):
            raise errors.PlanIsNotAvailable()
        if (plan.title == models.PlanChoices.ENDURANCE_PLAN and not
        models.Phase.objects.filter(
                title=models.PhaseChoices.ENDURANCE_PHASE1)):
            raise errors.PlanIsNotAvailable()
        if (plan.title == models.PlanChoices.ENDURANCE_FREE_TRAIL_PLAN and
                not models.Phase.objects.filter(
                title=models.PhaseChoices.ENDURANCE_FREE_TRAIL_PHASE1)):
            raise errors.PlanIsNotAvailable()
        return super(PlanPurchaseSerializer, self).validate(value)

    def validate_platform(self, value):
        if value and value not in constants.TRADING_PLATFORMS:
            raise serializers.ValidationError("Invalid platform")
        return super(PlanPurchaseSerializer, self).validate(value)

    def validate(self, data):
        if data.get("payment_method") == "bank" and not data.get("currency"):
            raise payment_errors.CurrencyRequired()
        elif data.get("payment_method") == "bank" and data.get("currency") \
                not in payment_cst.TRUELAYER_ACCEPTED_CURRENCIES:
            raise payment_errors.InvalidTruelayerCurrency()

        user = self.context.get('request').user

        if user.country in settings.COUNTRY_PLAN_PURCHASE_RESTRICTION:
            raise payment_errors.LocationNotAllowedForPlanPurchase()

        platform = plan_utils.get_platform(data.get('platform'))

        plan = models.Plan.objects.get(id=data.get("plan_id"))
        account_size = data.get("account_size")

        phase = plan_utils.get_phase(plan)

        # Validate the account size
        valid_account_sizes = models.AccountSizeAndPrice.objects.filter(
            phase=phase).values_list('account_size', flat=True).distinct()

        if not account_size:
            raise serializers.ValidationError("Account size value is required")
        elif account_size and account_size not in valid_account_sizes:
            raise serializers.ValidationError("Invalid account_size")

        # Validate the platform selection
        if not data.get("platform"):
            raise serializers.ValidationError("platform value is required")

        # Validate the plan purchase limit
        user_plan_count = UserPlan.objects.filter(
            user=user, phase=phase, active=True
        ).count()
        if plan.title == models.PlanChoices.JOURNEY_PLAN:
            if not user_plan_count < plan.limited_to:
                raise serializers.ValidationError(
                    {"plan_id": "You have purchased "
                                "the maximum limit of this plan"}
                )
        elif plan.program.title == models.ProgramChoices.JOURNEY:
            raise serializers.ValidationError(
                {"plan_id": "This plan is not purchasable"}
            )
        elif plan.program.title in [
            models.ProgramChoices.EVOLUTION,
            models.ProgramChoices.ENDURANCE,
            models.ProgramChoices.SPRINT,
            models.ProgramChoices.INCEPTION,
            models.ProgramChoices.EXPERT
        ] and not plan.limited_to > user_plan_count:
            raise serializers.ValidationError(
                {"plan_id": "You have purchased "
                            "the maximum limit of this plan"}
            )

        # Validate the plan purchase quantity
        possible_to_purchase = plan.limited_to - user_plan_count
        if possible_to_purchase == 0 or possible_to_purchase < 0:
            raise serializers.ValidationError(
                {
                    "plan_id": "You have purchased the maximum limit of this"
                               " plan"}
            )

        # Validate discount code
        if data.get("discount_code"):
            discount_code = validate_discount_code(
                user, plan, data.get("discount_code"), data.get("quantity")
            )
        else:
            discount_code = None

        # Validate the coin balance before purchasing a plan
        price = plan_utils.get_plan_price_by_account_size_and_phase(
            account_size, phase, platform
        )

        if discount_code:
            plan_price, _ = apply_discount_code(user, price, discount_code)
            price = plan_price * int(data.get("quantity", 1))

        # Verify whether the user possesses the unlocked plan
        if UnlockedPlan.objects.filter(
                user=self.context.get('request').user, phase=phase,
                account_size=account_size, redeemed=False).exists():
            price = 0

        if (data.get(
                "payment_method") == "si_coin" and price >
                user.wallet.current_balance):
            raise serializers.ValidationError("Insufficient SI coin balance")

        return super(PlanPurchaseSerializer, self).validate(data)
