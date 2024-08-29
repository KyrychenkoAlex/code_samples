import logging
import time

from abc import ABC, abstractmethod
from typing import Union, List

from django.db.models import Avg, Min, Max
from django.utils import timezone

from models import Document, DocumentWeight, DocumentPaywallSetting

logger = logging.getLogger('import')


class BaseRule(ABC):
    """
    Abstract class for weight rules
    """

    def __init__(self, document: Document, weight: float, values: dict):
        self.document = document
        self.weight = weight
        self.values = values

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Rule name
        """
        pass

    @abstractmethod
    def run(self) -> Union[float, int]:
        """
        Main function to run the rule
        """
        pass


class DocumentViewsRatioRule(BaseRule):
    """
    View ratio rule that calculates ratio between published date and views
    by formula: document views / (now - publish date)
    """
    name = "views_ratio"

    def run(self):
        time_diff = (timezone.now() - self.document.publish_date).days

        if time_diff == 0:
            ratio = 0
        else:
            ratio = self.document.views / time_diff

        return ratio


class IsAcademicDocumentRule(BaseRule):
    """
    The rule that checks if a document is "academic document"
    if yes then multiply current weight on "__multiplier_percentage"
    if no then return 0
    """
    name = "academic_document"
    __multiplier_percentage = 10

    def run(self):
        if not self.document.is_academic_document:
            views_ratio_value = self.values.get(DocumentViewsRatioRule.name, 0)
            return views_ratio_value * (self.__multiplier_percentage / 100)
        else:
            return 0


class LikesRatioRule(BaseRule):
    """
    Likes/Dislikes ratio rule
    Formula: Likes / Dislikes
    """
    name = "likes_ratio"
    __multiplier_percentage = 10
    __domination_percentage = 20

    def run(self):
        likes = self.document.likesbookmarks_set.filter(like=True).count()
        dislikes = self.document.likesbookmarks_set.filter(
            dislike=True).count()

        views_ratio_value = self.values.get(DocumentViewsRatioRule.name, 0)
        domination_percentage = self.__domination_percentage / 100

        likes_domination_percentage = likes * domination_percentage
        dislikes_domination_percentage = dislikes * domination_percentage

        if likes >= dislikes + likes_domination_percentage:
            value = views_ratio_value * (self.__multiplier_percentage / 100)
        elif dislikes >= likes + dislikes_domination_percentage:
            value = views_ratio_value * (-self.__multiplier_percentage / 100)
        else:
            value = 0

        return value


class DocumentWeightCalculator:
    """
    Class represent calculation of all rules
    :return document weight
    """

    def __init__(self, document: Document):
        self.weight = 0
        self.values = dict()
        self.rules = [
            DocumentViewsRatioRule,
            IsAcademicDocumentRule,
            LikesRatioRule
        ]

        self.document = document

    def run(self) -> float:
        for rule in self.rules:
            rule_instance = rule(self.document, self.weight, self.values)
            rule_value = rule_instance.run()

            self.values[rule_instance.name] = rule_value

            self.weight += rule_value

        return float(self.weight)


class DocumentWeightService:
    __chunk_size = 1000

    @classmethod
    def make_and_save_aggregation(cls, setting):
        """
        Calculate min, avg, max weight values and save it to new setting
        """
        weight_agg = DocumentWeight.objects.aggregate(
            Min('weight'), Avg('weight'), Max('weight')
        )

        setting.weight_min = round(weight_agg['weight__min'], 5)
        setting.weight_avg = round(weight_agg['weight__avg'], 5)
        setting.weight_max = round(weight_agg['weight__max'], 5)

        setting.save()

    @classmethod
    def get_paywall_setting(cls, force_create=False):
        """
        Get paywall setting
        If setting doesn't exist or force_create=True
        then new setting will be created
        """
        is_not_created = False

        try:
            paywall_setting = DocumentPaywallSetting.objects.latest(
                'created_at')
        except DocumentPaywallSetting.DoesNotExist:
            is_not_created = True

        if force_create or is_not_created:
            paywall_setting = DocumentPaywallSetting.objects.create(
                weight_min=0,
                weight_avg=0,
                weight_max=0,
                documents_count=0
            )

        return paywall_setting

    def calculate_documents(self, documents: List[Document]):
        """
        Function that calculates list of documents and update current setting
        """
        if len(documents) == 0:
            return

        paywall_setting = self.get_paywall_setting()

        # Calculate new weight for documents
        documents_count = 0
        logger.info("Started scoring documents")
        start_time = time.time()
        for document in documents:
            weight = DocumentWeightCalculator(document).run()

            obj, created = DocumentWeight.objects.update_or_create(
                document=document,
                defaults={
                    'document_paywall_setting': paywall_setting,
                    'weight': round(weight, 5)
                }
            )

            if created:
                documents_count += 1
        end_time = time.time()
        logger.info(f"Finished scoring documents. "
                    f"Execution time - {end_time - start_time}")

        paywall_setting.documents_count += documents_count
        self.make_and_save_aggregation(paywall_setting)

    def run(self):
        """
        Function that re-calculates weight for documents
        """
        # Clear previous weight for documents before applying new ones
        logger.info("Started removing all previous documents weights")
        DocumentWeight.objects.all().delete()
        logger.info("Completed removing all previous documents weights")

        documents = Document.objects.filter(
            dc_success=True,
            status=Document.PUBLISHED
        )
        documents_count = documents.count()

        logger.info(f"Found {documents_count} documents")

        # Create a new setting for paywall protection
        paywall_setting = self.get_paywall_setting(force_create=True)
        paywall_setting.documents_count = documents_count

        # Calculate new weight for documents
        logger.info("Started scoring documents")
        start_time = time.time()
        for document in documents.iterator(chunk_size=self.__chunk_size):
            weight = DocumentWeightCalculator(document).run()

            DocumentWeight.objects.create(
                document=document,
                document_paywall_setting=paywall_setting,
                weight=round(weight, 5)
            )
        end_time = time.time()
        logger.info(f"Finished scoring documents. "
                    f"Execution time - {end_time - start_time}")

        self.make_and_save_aggregation(paywall_setting)
