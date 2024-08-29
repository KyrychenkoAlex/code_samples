from decimal import Decimal

from django.utils import timezone
from django.conf import settings

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView, ListAPIView

from payment.choices import OrderStatus, PaymentOperation, \
    PaymentMethod
from payment.models import PlanPurchaseOrder, DiscountCode, Payment
from plan import models
from plan import serializers
from platform.facade import PlatformFacade
from user_affiliate.models import UserAffiliate
from user_plan.models import UserPlan, UnlockedPlan
from utils import plan as plan_utils
from utils.user_affiliate import charge_affiliate_commission
from utils.user_plan import (
    create_user_plan_label, award_plan_prize, active_new_plan
)
from notification.models import Notification, NotificationData
from utils.payment import get_payment_method, apply_discount_code, \
    get_ip
from payment import constants as payment_cst
from payment.api import PlanPurchasePaymentAPIView
from wallet.choices import Currency


class ProgramAPIView(ListAPIView):
    """
        - List all SI Program plans
    """
    queryset = models.Program.objects.prefetch_related(
        'get_plan__get_phase').filter(active=True)
    serializer_class = serializers.ProgramSerializer


class PlanPurchaseAPIView(APIView):
    """
        - View for purchasing a program plan
    """
    serializer_class = serializers.PlanPurchaseSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        account_size = request.data['account_size']
        quantity = int(request.data['quantity'])

        plan = models.Plan.objects.get(id=request.data['plan_id'])
        phase = plan_utils.get_phase(plan)
        platform = plan_utils.get_platform(request.data.get('platform'), phase)
        plan_price = plan_utils.get_plan_price_by_account_size_and_phase(
            account_size, phase, platform)

        payment_method = get_payment_method(
            request.data.get('payment_method'), value_type="string")

        user_plans = []
        unlocked_user_plans = []
        replicated_user_plans = []

        if plan_price == 0:
            [
                PlatformFacade(platform).accounts.create(user_plan)
                for user_plan in user_plans
            ]
        elif payment_method == payment_cst.SI_COIN_PAYMENT:
            user_plans_price, user_plans = apply_discount_code(
                request.user, plan_price, serializer.data.get('discount_code'),
                user_plans=user_plans, save_usage=True
            )

            for user_plan in user_plans:
                PlatformFacade(platform).accounts.create(user_plan)

            request.user.wallet.debit(
                user_plans_price,
                "PURCHASED-A-PLAN",
                f'Purchased {plan.title}, Quantity: {quantity}'
            )

            currency = Currency.USD.value
            country_code = request.user.country.code if request.user.country \
                else "GB"
            plans_price_in_usd = user_plans_price * Decimal(
                settings.SI_COIN_DOLLAR_BASE_VALUE)

            if serializer.data.get('discount_code'):
                discount_code = DiscountCode.objects.get(
                    code=serializer.data.get('discount_code')
                )
                discount_percentage = discount_code.discount_percentage
            else:
                discount_code = None
                discount_percentage = 0

            if request.user.affiliate_code:
                try:
                    user_affiliate_instance = UserAffiliate.objects.get(
                        code=request.user.affiliate_code, active=True)
                    affiliate_discount_percentage = (
                        user_affiliate_instance.rank.discount_percentage)
                except UserAffiliate.DoesNotExist:
                    user_affiliate_instance = None
                    affiliate_discount_percentage = 0
            else:
                user_affiliate_instance = None
                affiliate_discount_percentage = 0

            order = PlanPurchaseOrder.objects.create(
                user=request.user,
                user_plan=user_plans[0],
                cost=plans_price_in_usd,
                currency=currency,
                order_status=OrderStatus.COMPLETED.value,
                discount_code_applied=discount_code,
                discount_percentage=discount_percentage,
                affiliate_applied=user_affiliate_instance,
                affiliate_discount_percentage=affiliate_discount_percentage,
                plan_creation_completed=True
            )
            order.user_plans.add(*user_plans)

            Payment.objects.create(
                plan_purchase_order=order,
                payment_method=PaymentMethod.SI_COIN_PAYMENT,
                payment_type=PaymentOperation.CREDIT.value,
                amount=plans_price_in_usd,
                currency=currency,
                payment_status=OrderStatus.COMPLETED.value,
                payment_date=timezone.now(),
                merchant_order_id=f"SI-PLAN-PURCHASE-{order.id}",
                fe_redirect_url=request.data.get('fe_redirect_url'),
                first_name=request.user.first_name,
                last_name=request.user.last_name,
                email=request.user.email,
                address_country=country_code,
                ipaddress=get_ip(request),
            )

            if not discount_code:
                charge_affiliate_commission(
                    self.request.user, plans_price_in_usd, order)
        else:
            request.data['user_plans_ids'] = [
                user_plan.id for user_plan in user_plans]
            return PlanPurchasePaymentAPIView().post(request)

        plans = user_plans + unlocked_user_plans + replicated_user_plans
        for plan in plans:
            active_new_plan(plan)

        serializer = serializers.UserPlanSerializer(user_plans, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WithdrawProfitAPIView(APIView):
    """
    View for withdrawing profit from the MetaTrader account
    """
    serializer_class = serializers.WithdrawProfitInputSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        user_plan = UserPlan.objects.get(
            id=serializer.data.get("user_plan_id"),
            user=request.user
        )

        PlatformFacade(user_plan.platform).withdrawal.withdraw_profit(
            user_plan, Decimal(serializer.data.get("amount"))
        )

        return Response({"status": "success"}, status=status.HTTP_200_OK)


class PhaseUpgradeAPIView(APIView):
    """
    View for upgrading the SI phase
    """
    serializer_class = serializers.PhaseUpgradeInputSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        user_plan = UserPlan.objects.get(
            id=serializer.data.get("user_plan_id"),
            user=request.user
        )

        PlatformFacade(user_plan.platform).plans.upgrade_user_plan(user_plan)

        Notification.create_notification(
            NotificationData.PHASE_UPGRADED,
            user=user_plan.user,
            obj=user_plan
        )

        if user_plan.phase.title == models.PhaseChoices.ENDURANCE_PHASE3:
            Notification.create_notification(
                NotificationData.EVALUATION_PASSED,
                user=user_plan.user,
                obj=user_plan
            )

        return Response({"status": "success"}, status=status.HTTP_200_OK)
