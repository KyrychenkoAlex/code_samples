from django import forms

from models import Document, EssayCategory
from school.models import Course, CourseStructure, Professor, Term


class CommentForm(forms.Form):
    content = forms.CharField(widget=forms.TextInput())
    anonymous = forms.BooleanField(required=False)
    original = forms.IntegerField(required=False)


class TagForm(forms.Form):
    tags = forms.CharField()


class TextareaQuestion(forms.Textarea):
    template_name = 'widgets/textarea_question.html'

    def __init__(self, *args, **kwargs):
        self.message = kwargs.pop('message')
        super(TextareaQuestion, self).__init__(*args, **kwargs)

    def get_context_data(self):
        return {'message': self.message}


class DocumentTagForm(forms.ModelForm):
    description = forms.CharField(required=False, widget=forms.Textarea)
    d_type = forms.ChoiceField(
        required=False,
        choices=(('', 'Category'),) + Document.TYPE_VALUES[:-1]
    )
    essay_cat = forms.ModelChoiceField(
        required=False, queryset=EssayCategory.objects.order_by('name'))
    term = forms.ModelChoiceField(
        required=False,
        queryset=Term.objects.filter(year__gt=1).order_by(
            '-year', '-semester')
    )
    user_course = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your course'})
    )

    def clean_user_course(self):
        data = self.cleaned_data['user_course']
        if not data and not self.instance.user_essay:
            raise forms.ValidationError("Course is required")

        return data

    def save(self, commit=True):
        document = super(DocumentTagForm, self).save(commit=False)

        school = self.school

        user_course = document.user_course
        user_professor = document.user_professor
        term = self.cleaned_data['term']
        d_type = 12 if document.user_essay else self.cleaned_data['d_type']

        course_structures = CourseStructure.objects.filter(
            lookup=user_course,
            school=school
        )
        if course_structures.exists():
            course_structure = course_structures[0]
            document.user_course = ''

            professor = None
            if user_professor:
                if ',' in user_professor:
                    last, first = (user_professor.split(',')[0],
                                   ' '.join(user_professor.split(',')[1:]))
                    first = first.strip()
                    last = last.strip()
                else:
                    first = None
                    last = user_professor
                professors = Professor.objects.filter(
                    first_name=first,
                    last_name=last,
                    school=school
                )
                if professors.exists():
                    professor = professors[0]
                    document.user_professor = ''

            if not professor:
                try:
                    # could be only one professor because of unique together
                    # in model
                    professor = Professor.objects.get(
                        school=school,
                        first_name='A',
                        last_name='Staff'
                    )
                except Professor.DoesNotExist:
                    professor = Professor.objects.create(
                        first_name='A',
                        last_name='Staff',
                        full_name='Staff, A',
                        school=school
                    )

            if not term:
                term, created = Term.objects.get_or_create(
                    school=school,
                    year=1
                )

            course, created = Course.objects.get_or_create(
                term=term,
                course_structure=course_structure,
                professor=professor,
                status=Course.CROWD
            )
            document.course = course

        document.status = Document.DRAFT
        document.d_type = d_type
        if document.user_essay:
            document.essay_cat = self.cleaned_data['essay_cat']

        if commit:
            document.save(force=True)

        return document

    class Meta:
        model = Document
        fields = ('title', 'description', 'user_course', 'user_professor')


class DocumentEditForm(forms.ModelForm):
    new_file = forms.FileField(required=False)

    class Meta:
        model = Document
        fields = ()


class DocumentUploadForm(forms.Form):
    file = forms.FileField(max_length=85)
