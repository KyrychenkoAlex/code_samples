import datetime
import os
import random
import string
import traceback
import slugify

from django.utils import timezone
from django.db import models
from django.db.models import F
from django.urls import reverse
from sorl.thumbnail import ImageField
from tinymce.models import HTMLField

from models import DocumentPaywallSetting, DocumentWeight


class Document(models.Model):
    NOTE = '1'
    STUDY_GUIDE = '2'
    CHAPTER_SUMMARY = '3'
    DEFINITION_SHEET = '4'
    LECTURE_SLIDES = '5'
    LAB = '6'
    PRACTICE_PROBLEMS = '7'
    PRACTICE_EXAM = '8'
    FORMULA_SHEET = '9'
    SYLLABUS = '10'
    MISCELLANEOUS = '11'
    ESSAY = '12'
    ASSIGNMENT = '13'
    PRESENTATION = '14'

    PLATFORM = '1'
    CROWD = '2'
    PUBLISHER_VALUES = (
        (PLATFORM, 'Platform'),
        (CROWD, 'Crowd'),
    )
    PUBLISHER_KEYS = [el[0] for el in PUBLISHER_VALUES]

    DRAFT = '1'
    PUBLISHED = '2'
    TRASH = '3'
    ARCHIVED = '5'
    UNTAGGED = '6'
    SCRAPED = '7'
    UNAPPROVED = '8'
    STATUS_VALUES = (
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published'),
        (TRASH, 'Trash'),
        (ARCHIVED, 'Archived'),
        (UNTAGGED, 'Untagged'),
        (SCRAPED, 'Scraped'),
    )
    STATUS_KEYS = [el[0] for el in STATUS_VALUES]

    NOT_SCRAPED = '1'
    PENDING_DOWNLOAD = '2'
    DOWNLOAD_FAILED = '3'
    DOWNLOADED = '4'
    TAGGED = '5'
    UNCATEGORIZED = '6'
    REJECTED = '7'
    SKIPPED = '8'
    UNSURE = '9'
    SCRAPING_DELETED = '10'
    SCRAPED_WITH_ERRORS = '11'

    ESSAY_UNAPPROVED = '0'
    ESSAY_APPROVED = '1'
    ESSAY_UNSURE = '2'
    ESSAY_ARCHIVED = '3'
    ESSAY_FOREIGN = '4'
    ESSAY_SKIPPED = '5'
    ESSAY_DECLINED = '6'

    document = models.FileField(
        upload_to='raw', verbose_name="Choose File", max_length=700)
    document_preview = models.FileField(
        upload_to='preview', verbose_name="Choose File", max_length=700)

    dc_pdf_full = models.FileField(blank=True, null=True)
    dc_pdf_preview = models.FileField(blank=True, null=True)
    dc_thumbnail = models.FileField(blank=True, null=True)
    dc_text = models.FileField(blank=True, null=True)
    dc_success = models.NullBooleanField(default=None)

    title = models.CharField(max_length=700)
    d_type_raw = models.CharField(
        max_length=100, blank=True, verbose_name="Raw document type")
    publisher = models.CharField(
        max_length=1, choices=PUBLISHER_VALUES, default=CROWD,
        verbose_name="Publisher", db_index=True)
    description = models.CharField(
        max_length=700, verbose_name="Description (not required)",
        null=True, blank=True)
    thumb = ImageField(
        upload_to='thumbs', blank=True, null=True, max_length=700)

    # Course
    course = models.ForeignKey('school.Course', on_delete=models.CASCADE,
                               null=True, blank=True)

    # Additional Information
    tags = models.ManyToManyField("document.Tag", blank=True)
    publish_date = models.DateTimeField(default=datetime.datetime.now)
    lecture_num = models.PositiveIntegerField(
        verbose_name="Lecture #", null=True, blank=True)
    lecture_date = models.DateField(
        verbose_name="Lecture Date", null=True, blank=True)

    source = models.CharField(max_length=1000, blank=True)
    domain = models.CharField(max_length=30, blank=True)

    key_terms = HTMLField(blank=True)
    lecture_outline = HTMLField(blank=True)

    # Behind the scenes data
    pages = models.PositiveIntegerField(default=0)
    preview_pages = models.CharField(max_length=200, null=True, blank=True)
    views = models.PositiveIntegerField(default=0)
    notetaker = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE,
        related_name="uploaded_documents", null=True)
    content_editor = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, related_name="editor_documents",
        null=True, blank=True)
    status = models.CharField(
        max_length=1, choices=STATUS_VALUES, default=UNTAGGED, db_index=True)
    admin_notes = models.TextField(blank=True, verbose_name="Editing Notes")

    full_id = models.CharField(max_length=700, null=True, blank=True)
    preview_id = models.CharField(max_length=700, null=True, blank=True)
    error_msg = models.CharField(max_length=300, null=True, blank=True)

    credits = models.IntegerField(default=0)

    user_course = models.CharField(
        max_length=300, verbose_name='User Course Name', blank=True)
    user_professor = models.CharField(
        max_length=200, verbose_name='User Professor Name', blank=True)

    md5 = models.CharField(max_length=32, default='')

    slug = models.SlugField(
        verbose_name='slug', max_length=255, default='', editable=False)

    user_essay = models.BooleanField(
        default=False, verbose_name='Essay uploads')
    essay_categories = models.ManyToManyField(
        "document.EssayCategory", blank=True, verbose_name='Essay category')

    scrap_task = models.ForeignKey(
        'scraper.DocumentTask', on_delete=models.CASCADE, null=True)
    school = models.ForeignKey(
        'school.School', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return u'%s' % self.title

    @property
    def published(self):
        return self.status == self.PUBLISHED

    @property
    def is_academic_document(self):
        """
        Check if current document is academic and is fully accessed for
        everyone
        """
        result = False
        if self.scraping_status == self.SKIPPED or not self.course_id:
            result = True
        return result

    @property
    def filename(self):
        return os.path.basename(self.document.name)

    @staticmethod
    def get_absolute_url_static(id_, slug):
        return reverse('course_document_slug', args=[id_, slug])

    def get_slug_value(self):
        slug = self.title
        return slugify.slugify(slug).lower()

    def access_allowed(self, user):
        try:
            now = timezone.now()
            profile = user.profile if user and user.is_authenticated else None
            is_essays_access_enable = profile and profile.has_essays_access

            # Allow access if user uploaded this document
            if profile and profile.documents.filter(id=self.id).exists():
                return True

            # Allow access if user uploaded this course
            if (self.course and profile
                    and profile.courses.filter(id=self.course_id).exists()):
                return True

            # Allow access if the user has membership
            if user.membership_set.filter(end_date__gte=now).exists():
                return True

            # Allow access if
            # the document is an essay
            # and the user has essay access
            if self.d_type == self.ESSAY and is_essays_access_enable:
                return True

            setting = DocumentPaywallSetting.objects.latest('created_at')
            max_weight_for_free_access = (setting.weight_avg * (
                    setting.weight_avg_percentage / 100))

            document_weight = DocumentWeight.objects.get(document_id=self.id)

            # Allow access if the document has free access
            if document_weight.weight <= max_weight_for_free_access:
                return True

            return False
        except DocumentPaywallSetting.DoesNotExist:
            # Documents were not scored
            return False
        except DocumentWeight.DoesNotExist:
            # The document was not scored
            return False
        except Exception as ex:
            print(traceback.format_exc())
            return False

    class Meta:
        permissions = (
            ('download', 'Can download document'),
        )
