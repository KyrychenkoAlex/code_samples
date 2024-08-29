from django import forms
from django.forms import ValidationError

from models import Statistic, Tag, Document
from school.models import School, CourseStructure


class TagAdminForm(forms.ModelForm):
    tags = forms.CharField(
        max_length=2200,
        widget=forms.Textarea(attrs={'cols': 60, 'rows': 6})
    )

    class Meta:
        model = Tag
        exclude = ('name',)


class DocumentAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DocumentAdminForm, self).__init__(*args, **kwargs)
        self.fields['document'].max_length = 85

    def clean(self):  # remove spaces in file name
        if self.cleaned_data.get('document'):
            spaceless_name = self.cleaned_data['document'].name
            spaceless_name = spaceless_name.replace(' ', '_')
            self.cleaned_data['document'].name = spaceless_name

        return self.cleaned_data

    def save(self, commit=True):
        document = super(DocumentAdminForm, self).save(commit)

        if (document.status == Document.PUBLISHED and
                document.scraping_status == Document.SKIPPED):
            document.scraping_status = Document.TAGGED

        if commit:
            document.save()
        document.save_admin_stats(
            user=self.current_user,
            msg='Changed status of study resource',
            admin_section=Statistic.STUDY_RESOURCES)

        return document

    class Meta:
        model = Document
        exclude = ()
        widgets = {
            'description': forms.Textarea(
                attrs={'cols': 60, 'rows': 2}
            )
        }


class ReviewFilterForm(forms.Form):
    school = forms.ChoiceField(choices=[('', 'School')], required=False)
    statefilter = forms.ChoiceField(
        choices=(
            (0, 'All docs'),
            (Document.DRAFT, 'Unapproved'),
            (Document.PUBLISHED, 'Approved'),
            (Document.TRASH, 'Trash'),
            (Document.ARCHIVED, 'Archived'),
        ),
        required=False
    )
    d_type = forms.ChoiceField(
        choices=(
            (0, 'All docs'),
            (Document.NOTE, 'Lecture Notes'),
            (Document.STUDY_GUIDE, 'Study Guides'),
        ),
        required=False
    )

    needsedit = forms.ChoiceField(
        choices=(
            (0, 'All docs'),
            (Document.NO_EDITING, 'No Editing Needed'),
            (Document.NEEDS_EDITING, 'Needs Editing'),
            (Document.EDITS_SUBMITTED, 'Edits Submitted'),
        ),
        required=False
    )

    course = forms.ChoiceField(
        choices=(
            (0, 'All docs'),
            (1, 'Course entered'),
            (2, 'No course'),
        ),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(ReviewFilterForm, self).__init__(*args, **kwargs)
        statuses = (Document.DRAFT, Document.PUBLISHED)

        statefilter = self.data.get('statefilter', None)
        if statefilter in statuses:
            self.fields['school'].choices += School.objects.filter(
                enable_subscriptions=True).values_list('id', 'short_name')
        else:
            self.fields['school'].choices += School.objects.all().values_list(
                'id', 'short_name')


class ScrapedFilterForm(forms.Form):
    status_choices = (
        (Document.UNCATEGORIZED, 'Uncategorized'),
        (Document.TAGGED, 'Tagged'),
        (Document.REJECTED, 'Rejected'),
        (Document.SKIPPED, 'Skipped'),
        (Document.UNSURE, 'Unsure'),
        (Document.SCRAPING_DELETED, 'Deleted'),
        (Document.SCRAPED_WITH_ERRORS, 'With errors')
    )
    scraping_status = forms.ChoiceField(choices=status_choices)
    school = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'filter-select'
            })
    )
    d_type = forms.ChoiceField(
        choices=(
            ('0', 'All doc types'),
            (Document.NOTE, 'Lecture Note'),
            (Document.STUDY_GUIDE, 'Study Guide'),
            (Document.CHAPTER_SUMMARY, 'Chapter Summary'),
            (Document.DEFINITION_SHEET, 'Definition Sheet'),
            (Document.LECTURE_SLIDES, 'Lecture Slides'),
            (Document.LAB, 'Lab'),
            (Document.PRACTICE_PROBLEMS, 'Practice Problems'),
            (Document.PRACTICE_EXAM, 'Practice Exam'),
            (Document.FORMULA_SHEET, 'Formula Sheet'),
            (Document.SYLLABUS, 'Syllabus'),
            (Document.ESSAY, 'Essay'),
            (Document.ASSIGNMENT, 'Assignment'),
            (Document.MISCELLANEOUS, 'Miscellaneous'),
            (Document.PRESENTATION, 'Presentation'),
        ),
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'filter-select'
            }
        )
    )
    q = forms.CharField(required=False)

    def __init__(self, scraping_status, *args, **kwargs):
        super(ScrapedFilterForm, self).__init__(*args, **kwargs)

        self.fields['school'].choices = [('', 'All schools'),
                                         ('0', 'Without school')] + \
                                        list(School.objects.values_list('id',
                                                                        'short_name'))

        if scraping_status != Document.UNCATEGORIZED:
            queryset = Document.objects.filter(scraping_status=scraping_status)
            valid_choices = list(
                queryset.values_list('d_type', flat=True).distinct())
            valid_choices.append('0')
            type_choices = [
                i for i in self.fields['d_type'].choices
                if i[0] in valid_choices
            ]
            self.fields['d_type'].choices = type_choices


class StudyDocumentForm(forms.Form):
    title = forms.CharField()
    type = forms.CharField()
    school = forms.ModelChoiceField(queryset=School.objects.all(),
                                    required=False)
    course = forms.CharField(required=False)
    document = forms.ModelChoiceField(queryset=Document.objects.all())

    def clean_course(self):
        error_msg = ('Either select course or create one using correct '
                     'format: department short name;course number;course '
                     'title')
        course = self.cleaned_data['course']
        if course:
            try:
                cs = CourseStructure.objects.get(id=course)
                return cs
            except CourseStructure.DoesNotExist:
                raise ValidationError(error_msg)
            except CourseStructure.MultipleObjectsReturned:
                raise ValidationError('Error with selected coursestructure')
            except ValueError:
                # create course structure here
                course_array = course.split(';')
                if (2 <= len(course_array) < 4) and course_array[0] and \
                        course_array[1]:
                    return course_array
                else:
                    raise ValidationError(error_msg)
        else:
            return None


class ScrapedDocumentForm(forms.Form):
    document = forms.ModelChoiceField(queryset=Document.objects.exclude(
        scraping_status=Document.NOT_SCRAPED))


class UpdateStatusScrapedForm(ScrapedDocumentForm):
    status_choices = ((Document.TAGGED, 'Tagged'), (Document.SCRAPING_DELETED,
                                                    'Deleted'),
                      (Document.SKIPPED, 'Skipped'), (Document.UNSURE,
                                                      'Unsure'))
    status = forms.ChoiceField(choices=status_choices)


class ScrapedEditForm(forms.Form):
    title = forms.CharField()
    type = forms.ChoiceField(choices=Document.TYPE_VALUES)
    school = forms.ModelChoiceField(
        queryset=School.objects.all(), required=False)
    course = forms.CharField(required=False)


class ScrapedEditTaggedForm(ScrapedEditForm):
    school = forms.ModelChoiceField(queryset=School.objects.all())

    def clean_course(self):
        error_msg = ('Either select course or create one using correct '
                     'format: department short name;course number;course '
                     'title')
        course = self.cleaned_data['course']
        try:
            cs = CourseStructure.objects.get(id=course)
            return cs
        except CourseStructure.DoesNotExist:
            raise ValidationError(error_msg)
        except CourseStructure.MultipleObjectsReturned:
            raise ValidationError('Error with selected coursestructure')
        except ValueError:
            # create course structure here
            course_array = course.split(';')
            if (2 <= len(course_array) < 4) and course_array[0] and \
                    course_array[1]:
                return course_array
            else:
                raise ValidationError(error_msg)
