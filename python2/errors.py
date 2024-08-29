from rest_framework.exceptions import APIException, ValidationError


class BadRequestException(APIException):
    status_code = 400
    default_detail = "Invalid request"
    default_code = "bad_request"


class InsufficientProfit(BadRequestException):
    """Raised when a trade account has insufficient profit to
    run an operation.
    We're subclassing from :mod:`django.db.IntegrityError`
    so that it is automatically rolled-back during django's
    transaction lifecycle.
    """
    default_detail = "You don't have any profit to withdraw"


class AmountExceedsProfitError(BadRequestException):
    default_detail = "Amount should be less than profit"


class OpenTradeExist(BadRequestException):
    default_detail = "Open trade exist"


class PlanIsNotAvailable(BadRequestException):
    default_detail = "This plan is not available"


class InvalidUserPlan(BadRequestException):
    default_detail = "Invalid user_plan_id"


class WithdrawalNotAllowed(BadRequestException):
    default_detail = "Withdrawal is not allowed on this plan"


class WithdrawalNotAllowedToday(BadRequestException):
    default_detail = "Withdrawal is not allowed today"


class MultipleWithdrawalNotAllowed(BadRequestException):
    default_detail = "You can withdraw once in a withdrawal window"


class ScaleUpNotAllowed(BadRequestException):
    default_detail = "This plan is not available for scale up"