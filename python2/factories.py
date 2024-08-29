import factory.fuzzy

from plan import choices
from plan.models import (
    Plan, Phase, Program, PhaseRule, PhaseParameter, AccountSizeAndPrice
)


class ProgramFactory(factory.django.DjangoModelFactory):
    title = factory.fuzzy.FuzzyChoice(
        choices.ProgramChoices.choices, getter=lambda c: c[0]
    )
    description = factory.Faker('sentence', nb_words=200)

    class Meta:
        model = Program


class PlanFactory(factory.django.DjangoModelFactory):
    title = factory.fuzzy.FuzzyChoice(
        choices.PlanChoices.choices, getter=lambda c: c[0]
    )
    description = factory.Faker('sentence', nb_words=10)
    program = factory.SubFactory(ProgramFactory)

    class Meta:
        model = Plan


class PhaseFactory(factory.django.DjangoModelFactory):
    title = factory.fuzzy.FuzzyChoice(
        choices.PhaseChoices.choices, getter=lambda c: c[0]
    )
    description = factory.Faker('sentence', nb_words=10)
    plan = factory.SubFactory(PlanFactory)

    class Meta:
        model = Phase
