from django.urls import reverse

from plan import factories
from plan.models import PhaseParameter
from user_plan.models import UserPlan
from plan.choices import (
    ParametersChoices, ProgramChoices, PhaseChoices, PlanChoices)
from tests import BaseAPITestCase


class PlanPurchaseTestUtils(object):
    @staticmethod
    def get_plan_purchase_url():
        return reverse('plan:plan-purchase')


class TestEndurancePlanPurchase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.user.wallet.credit(100, "PURCHASED_SI_TEST_COIN")

        self.program1 = factories.ProgramFactory.create(
            title=ProgramChoices.ENDURANCE)

        self.plan1 = factories.PlanFactory.create(
            program=self.program1, title=PlanChoices.ENDURANCE_PLAN,
            limited_to=1)
        self.phase1 = factories.PhaseFactory.create(
            plan=self.plan1,
            title=PhaseChoices.ENDURANCE_PHASE1)
        PhaseParameter.objects.create(
            parameter=ParametersChoices.PLATFORMS,
            value="MT4 or MT5", phase=self.phase1)
        PhaseParameter.objects.create(
            parameter=ParametersChoices.LEVERAGE,
            value=100, phase=self.phase1)
        account_size = factories.AccountSizeFactory.create(
            phase=self.phase1, price=5)
        self.account_size_value = account_size.account_size

    def _create_a_plan_purchase_payload(
            self, plan=None, platform="MT4", account_size=None):
        return {
            "plan_id": plan,
            "platform": platform,
            "quantity": 1,
            "account_size": account_size,
            "account_label": "Evolution Trading Account",
            "payment_method": "si_coin",
            "fe_redirect_url": "/app/home"
        }

    def test_plan_purchase_with_valid_parameters(self):
        data = self._create_a_plan_purchase_payload(
            plan=self.plan1.id, account_size=self.account_size_value)

        response = self.user_client.post(
            PlanPurchaseTestUtils.get_plan_purchase_url(),
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, 201)

    def test_plan_purchase_with_an_invalid_platform(self):
        data = self._create_a_plan_purchase_payload(
            plan=self.plan1.id, account_size=self.account_size_value,
            platform="MT10")
        response = self.user_client.post(
            PlanPurchaseTestUtils.get_plan_purchase_url(),
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(response.json()['platform'][0], "Invalid platform")

    def test_plan_purchase_without_choosing_a_platform(self):
        data = self._create_a_plan_purchase_payload(
            plan=self.plan1.id, account_size=self.account_size_value,
            platform="")
        response = self.user_client.post(
            PlanPurchaseTestUtils.get_plan_purchase_url(),
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            response.json()['platform'][0], "This field may not be blank.")

    def test_plan_purchase_with_an_invalid_account_size(self):
        invalid_account_size = 10000000000
        data = self._create_a_plan_purchase_payload(
            plan=self.plan1.id, account_size=invalid_account_size)
        response = self.user_client.post(
            PlanPurchaseTestUtils.get_plan_purchase_url(),
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            response.json()['non_field_errors'][0], "Invalid account_size")

    def test_plan_purchase_plan_without_choosing_an_account_size(self):
        data = self._create_a_plan_purchase_payload(plan=self.plan1.id)
        response = self.user_client.post(
            PlanPurchaseTestUtils.get_plan_purchase_url(),
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            response.json()['account_size'][0], "'This field may not be null.")

    def test_plan_purchase_more_than_limited_size(self):
        UserPlan.objects.all().delete()
        data = self._create_a_plan_purchase_payload(
            plan=self.plan1.id, account_size=self.account_size_value)

        response = self.user_client.post(
            PlanPurchaseTestUtils.get_plan_purchase_url(),
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, 201)

        response = self.user_client.post(
            PlanPurchaseTestUtils.get_plan_purchase_url(),
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            response.json()['plan_id'][0],
            "You have purchased the maximum limit of this plan")

    def test_plan_purchase_with_insufficient_wallet_balance(self):
        UserPlan.objects.all().delete()

        current_balance = self.user.wallet.current_balance
        self.user.wallet.debit(
            current_balance, "DEBITED_FULL_SI_COIN_FOR_TEST")
        data = self._create_a_plan_purchase_payload(
            plan=self.plan1.id, account_size=self.account_size_value)
        response = self.user_client.post(
            PlanPurchaseTestUtils.get_plan_purchase_url(),
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            response.json()['non_field_errors'][0],
            "Insufficient SI coin balance")

        # restore wallet
        self.user.wallet.credit(100, "PURCHASED_SI_TEST_COIN")
