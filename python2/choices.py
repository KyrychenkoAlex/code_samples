from django.db import models

from plan import constants


class PlatformChoice(models.IntegerChoices):
    """
    Class representing available Trading platform choices
    """

    MT4 = 0, constants.MT4
    MT5 = 1, constants.MT5
    MT4_OR_MT5 = 2, constants.MT4_OR_MT5
    SIRIX = 3, constants.SIRIX


class ProgramChoices(models.IntegerChoices):
    """
    Class representing SI Program choices
    """

    EVOLUTION = 0, constants.EVOLUTION
    ENDURANCE = 1, constants.ENDURANCE
    SPRINT = 2, constants.SPRINT
    JOURNEY = 3, constants.JOURNEY
    TOURNAMENT = 4, constants.TOURNAMENT
    INCEPTION = 5, constants.INCEPTION
    EXPERT = 6, constants.EXPERT


class PlanChoices(models.IntegerChoices):
    """
    Class representing Plan choices
    """

    EVOLUTION_STANDARD_PLAN = 0, constants.EVOLUTION_STANDARD_PLAN
    EVOLUTION_DYNAMIC_PLAN = 1, constants.EVOLUTION_DYNAMIC_PLAN
    ENDURANCE_PLAN = 2, constants.ENDURANCE_PLAN
    SPRINT_SERIOUS_SCALPER_PLAN = 3, constants.SPRINT_SERIOUS_SCALPER_PLAN
    SPRINT_FOREX_FRENZY_PLAN = 4, constants.SPRINT_FOREX_FRENZY_PLAN
    SPRINT_GOLD_DIGGER_PLAN = 5, constants.SPRINT_GOLD_DIGGER_PLAN
    SPRINT_CRYPTO_CRAZY_PLAN = 6, constants.SPRINT_CRYPTO_CRAZY_PLAN
    SPRINT_SWING_CITY_PLAN = 7, constants.SPRINT_SWING_CITY_PLAN
    SPRINT_RISK_RUN_PLAN = 8, constants.SPRINT_RISK_RUN_PLAN
    JOURNEY_PLAN = 9, constants.JOURNEY_PLAN

    EVOLUTION_STANDARD_FREE_TRAIL_PLAN = (10,
                                          constants.EVOLUTION_STANDARD_FREE_TRAIL_PLAN)
    ENDURANCE_FREE_TRAIL_PLAN = 11, constants.ENDURANCE_FREE_TRAIL_PLAN

    EVOLUTION_LITE_PLAN = 12, constants.EVOLUTION_LITE_PLAN
    INCEPTION_PLAN = 13, constants.INCEPTION_PLAN

    EXPERT_PLAN = 14, constants.EXPERT_PLAN
