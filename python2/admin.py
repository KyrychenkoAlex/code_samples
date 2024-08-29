from django.contrib import admin

from solo.admin import SingletonModelAdmin

from plan import models


class PhaseRuleInlineAdmin(admin.TabularInline):
    model = models.PhaseRule
    extra = 0


class PhaseParameterInlineAdmin(admin.TabularInline):
    model = models.PhaseParameter
    extra = 0


class PhaseObjectiveInlineAdmin(admin.TabularInline):
    model = models.PhaseObjective
    extra = 0


class PhaseInlineAdmin(admin.TabularInline):
    model = models.Phase
    extra = 0


class PlanInlineAdmin(admin.TabularInline):
    model = models.Plan
    extra = 0


class AccountSizeInlineAdmin(admin.TabularInline):
    model = models.AccountSizeAndPrice
    extra = 0


@admin.register(models.Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('id', 'title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = (PlanInlineAdmin,)


@admin.register(models.Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'program',)
    list_filter = ('program',)
    search_fields = ('id', 'title', 'program__title', 'description',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = (PhaseInlineAdmin,)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('program')


@admin.register(models.Phase)
class PhaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'plan', 'created_at')
    list_filter = ('plan__program',)
    search_fields = ('id', 'title', 'plan__title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = (
        AccountSizeInlineAdmin, PhaseRuleInlineAdmin,
        PhaseParameterInlineAdmin, PhaseObjectiveInlineAdmin
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('plan')


@admin.register(models.UserAgreement)
class UserAgreementAdmin(SingletonModelAdmin):
    pass
