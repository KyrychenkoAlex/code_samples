import tempfile
from datetime import datetime

from django.contrib.auth.models import User
from django.db.models import F, Value
from django.db.models.functions import Concat

from accounts.models import UserProfile
from forms import DocumentUploadForm
from models import Document
from school.models import (
    School,
    CourseStructure,
    Course,
    Professor,
    Term,
)
from utils import plupload


class SeedUploadDoc:
    _is_last_chunk: bool

    def __init__(self, request):
        self.request = request
        self.tmp_file_destination = 'media/tmp/'
        self.convert_document = request.POST.get("convert_document",
                                                 True) is True
        self.wait_for_convert = request.POST.get("wait_for_convert",
                                                 True) is True

    @property
    def file_form(self):
        if hasattr(self, "_file_form"):
            return self._file_form

        form = DocumentUploadForm(self.request.POST, self.request.FILES)
        if not form.is_valid():
            raise ValueError("Form is invalid")

        self._file_form = form
        return self._file_form

    @property
    def file_name(self):
        file_name = self.request.POST.get("file_name") or ""
        name, extension = file_name.rsplit(".", 1)
        if not (name or extension):
            raise ValueError('"file_name" has no name or extension')
        return file_name

    @property
    def is_last_chunk(self):
        return getattr(self, '_is_last_chunk', False)

    @property
    def file_object(self):
        if hasattr(self, "_file_object"):
            return self._file_object

        tmp_file = tempfile.NamedTemporaryFile()
        try:
            self._is_last_chunk = plupload.save_tmp_file_obj(
                request=self.request,
                forms=self.request.POST,
                files=self.request.FILES,
                dest=self.tmp_file_destination,
                file_obj=tmp_file)

            self._file_object = tmp_file
        except Exception as ex:
            tmp_file.close()
            raise ValueError(str(ex))

        return self._file_object

    @property
    def user(self):
        if hasattr(self, "_user"):
            return self._user

        user = User.objects.filter(username='admin@test.com').first()
        profile = getattr(user, "profile", None)
        if profile is None:
            UserProfile.objects.create(user=user, alias="admin1",
                                       school=self.default_school)

        self._user = user
        return self._user

    @property
    def gb_school(self):
        if hasattr(self, "_gb_school"):
            return self._gb_school

        school_name, school_lookup = (
            self.request.POST.get("gb_school"),
            self.request.POST.get("gb_school_lookup") or "lookup"
        )

        lookup_concat = Concat(F("short_name"), Value(": "), F("name"))
        school = School.objects \
            .annotate(lookup=lookup_concat) \
            .filter(**{school_lookup: school_name}) \
            .first()

        if not school:
            school = self.default_school

        self._gb_school = school
        return self._gb_school

    @property
    def default_school(self):
        if hasattr(self, "_default_school"):
            return self._default_school

        self._default_school = School.objects.filter(short_name='UCLA').first()
        return self._default_school

    @property
    def gb_course(self):
        if hasattr(self, "_gb_course"):
            return self._gb_course

        school = self.gb_school
        if not school:
            self._gb_course = None
            return self._gb_course

        course_name, course_lookup = (
            self.request.POST.get("gb_course"),
            self.request.POST.get("gb_course_lookup") or "short_name"
        )
        course_structure = CourseStructure.objects.filter(
            **{course_lookup: course_name},
            school_id=school.id
        ).first()
        if not course_structure:
            self._course = None
            return self._course

        professor = Professor.objects \
            .filter(first_name__iexact="A",
                    last_name__iexact="Staff",
                    school_id=school.id) \
            .first()

        if not professor:
            professor = Professor(
                first_name='A',
                last_name='Staff',
                full_name='Staff, A',
                school_id=school.id)
            professor.save()

        term, _ = Term.objects.get_or_create(school_id=school.id, year=1)
        course, _ = Course.objects.get_or_create(
            term=term,
            course_structure=course_structure,
            professor=professor,
            status=Course.CROWD)
        self._course = course
        return self._course

    @property
    def document_title(self):
        if hasattr(self, "_document_title"):
            return self._document_title

        doc_name, school_name, course_name, professor_name = (
            self.request.POST.get("name") or "UndefinedDocName",
            self.request.POST.get("school") or "UndefinedSchool",
            self.request.POST.get("course") or "UndefinedCourse",
            self.request.POST.get("professor") or "UndefinedProfessor"
        )

        gb_school, gb_course = self.gb_school, self.gb_course
        if gb_school and gb_course:
            title = doc_name

        elif gb_school and not gb_course:
            title = f"{gb_school.name}__{course_name}__{professor_name}"

        else:
            title = f"{school_name}__{course_name}__{professor_name}"
        return title

    def generate_document(self):
        _document = Document(
            notetaker=self.user,
            title=self.document_title,
            publisher=Document.test,
            status=Document.DRAFT,
            school=self.gb_school,
            course=self.gb_course,
            dc_success=None)
        return _document

    def create_document(self):
        _document = self.generate_document()
        # todo add unique value to doc name
        _document.document.save(
            self.file_name,
            self.file_object.file,
            save=False)

        _document.updated_at = datetime.utcnow()
        _document.save(ignore_convert=True)
        _document.convert_document()
        return _document

    def run(self):
        document, is_processed, error = None, False, ""
        try:
            # init file object
            _ = self.file_object

            if self.is_last_chunk:
                document = self.create_document()
                is_processed = True
        except Exception as ex:
            error = str(ex)

        file_object = getattr(self, "_file_object", None)
        if file_object is not None:
            file_object.close()  # remove file from tmp dir

        return document, is_processed, error
