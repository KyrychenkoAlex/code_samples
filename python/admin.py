import datetime
import json
import urllib.parse

from django.conf.urls import url
from django.contrib import admin
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.db.models import Count, Sum, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.cache import never_cache

from admin_forms import DocumentAdminForm, ReviewFilterForm
from models import Statistic, Document

from core import settings


class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'course', 'notetaker', 'publish_date', 'status')
    list_filter = (
        'd_type', 'course__course_structure__school', 'publisher',
        'course__cancelled', 'course__status', 'status'
    )
    ordering = ('-publish_date',)
    fieldsets = (('Note', {
        'fields': (
            ('notetaker', 'content_editor'),
            ('editing_status', 'admin_notes'),
            'document',
            'course',
            'title',
            ('d_type', 'publisher', 'status', 'credits'),
            'description',
            'lecture_outline',
            'key_terms',
            'lecture_num',
            'lecture_date',
            'pages',
            'error_msg',
            'full_id',
            'preview_id',
        )
    }),)
    raw_id_fields = ('course', 'notetaker', 'content_editor')
    readonly_fields = ('full_id', 'preview_id', 'pages', 'error_msg')
    search_fields = ('title', 'course__course_structure__short_name',
                     'notetaker__email', 'notetaker__username')

    form = DocumentAdminForm

    def get_form(self, request, obj=None, **kwargs):
        form = super(DocumentAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def get_queryset(
            self,
            request,
            d_type=None,
            status=None,
            school=None,
            exclude_status=None,
            publisher=Document.test,
            editing_status=None):
        q = Q()

        if d_type:
            try:
                d_type = int(d_type)
            except:
                d_type = None
            if d_type and d_type != 0:
                q.add(Q(d_type=d_type), Q.AND)

        if status:
            try:
                status = int(status)
            except:
                status = None
            if status and status != 0:
                q.add(Q(status=status), Q.AND)

        if editing_status:
            try:
                editing_status = int(editing_status)
            except:
                editing_status = None
            if editing_status and editing_status > 0:
                q.add(Q(editing_status=editing_status), Q.AND)

        if school:
            q.add(Q(notetaker__profile__school=school), Q.AND)
            q.add(Q(scraping_status=Document.NOT_SCRAPED), Q.AND)

        if publisher:
            q.add(Q(publisher=publisher), Q.AND)

        qs = Document.objects.filter(q)
        if exclude_status:
            qs = qs.exclude(status=exclude_status)

        if request.user.profile.is_content_editor:
            qs = qs.filter(content_editor=request.user)

        if request.user.profile.is_school_administrator:
            qs = qs.filter(
                course__course_structure__school=request.user.profile.school)

        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def notetaker_name(self, document):
        notetaker = document.notetaker
        if notetaker.first_name and notetaker.last_name:
            return "%s %s" % (notetaker.first_name, notetaker.last_name)
        return notetaker

    def has_add_permission(self, request, obj=None):
        return request.user.has_perm('document.add_document')

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('document.change_document')

    def get_urls(self):
        urls = [
            url(r'^review/$', self.review),
            url(r'^doc_details/$', self.doc_details),
            url(r'^rank_up_document_conversion/$',
                self.rank_up_document_conversion),
            url(r'^update_status/$', self.update_status),
            url(r'^update_type/$', self.update_type),
            url(r'^update_credits/$', self.update_credits),
            url(r'^marketing/$', self.marketing),
            url(r'^try_scrap_again/$', self.try_scrap_again),
            url(r'^duplicated/$', self.duplicated),
        ]
        return urls + super(DocumentAdmin, self).get_urls()

    @method_decorator(staff_member_required)
    @never_cache
    def review(self, request):
        review_filter_form = ReviewFilterForm(request.GET or None)
        if review_filter_form.is_valid():
            status = review_filter_form.cleaned_data['statefilter']
            school = review_filter_form.cleaned_data['school']
            d_type = review_filter_form.cleaned_data['d_type']
            needsedit = review_filter_form.cleaned_data['needsedit']
            documents = self.get_queryset(
                request,
                status=status,
                school=school,
                d_type=d_type,
                editing_status=needsedit).order_by('-id')

            course = review_filter_form.cleaned_data['course']
            if course:
                if int(course) == 1:
                    isnull = False
                elif int(course) == 2:
                    isnull = True
                documents = documents.filter(course__isnull=isnull)

        else:
            documents = self.get_queryset(request).order_by('id')

        paginator = Paginator(documents, 30)
        page = request.GET.get('page')
        try:
            documents = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            documents = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of
            # results.
            documents = paginator.page(paginator.num_pages)

        query = request.GET.copy()
        if 'page' in query:
            del query['page']

        template = 'admin/document/fancy_list.html'
        context = {
            'documents': documents,
            'form': review_filter_form,
            'DRAFT': Document.DRAFT,
            'PUBLISHED': Document.PUBLISHED,
            'CROWD': Document.CROWD,
            'TYPE_VALUES': Document.TYPE_VALUES,
            'app_label': self.model._meta.app_label,
            'verbose_name': self.model._meta.verbose_name.title(),
            'obj_name': self.model._meta.object_name.lower(),
            'media': self.media,
            'query': query,
        }
        return render(request, template, context)

    @method_decorator(staff_member_required)
    @never_cache
    def rank_up_document_conversion(self, request):
        from universal.models import DelayedTask
        data = {"ranked_up": False}
        if request.is_ajax() and request.method == "POST":
            document_id = request.POST.get('document_id')
            if document_id:
                DelayedTask.objects.document_conversion_rank_up(
                    document_id=document_id,
                    rank=1)
            data['ranked_up'] = True
        return HttpResponse(json.dumps(data), content_type="application/json")

    @method_decorator(staff_member_required)
    def doc_details(self, request):
        found = False
        content = None

        if request.is_ajax():
            if request.method == "POST":
                document_id = request.POST.get('document_id')
                try:
                    document_id = int(document_id)
                except:
                    document_id = None

                if document_id:
                    found = True
                    error_message = ''
                    document = Document.objects.get(id=document_id)
                    data = {
                        'type': 'view',
                        'document': document,
                        'place': 'admin',
                    }
                    user = request.user
                    user_data = {
                        'user': user,
                        'is_authorized': True,
                        'is_staff': user.is_staff,
                        'is_superuser': user.is_superuser,
                        'is_premium': user.profile.has_premium,
                    }
                    data.update(user_data)

                    course = document.course
                    all_dates = []
                    c_dates = []
                    course_name = 'None'
                    school = None
                    if course:
                        current_term = (
                            course.course_structure.school.current_term)
                        if (course.term == current_term and course.notetaker
                                and not course.cancelled):
                            for n in range((current_term.end -
                                            current_term.start).days + 1):
                                date = current_term.start + \
                                       datetime.timedelta(n)
                                all_dates.append(date)
                            c_dates = course.course_dates(all_dates)
                            course_name = course.short_name()

                        school = course.course_structure.school

                    conversion_info = None
                    # if not document has been converted, try to convert it
                    document_url = ''
                    if document.dc_success:
                        document_url = urllib.parse.urljoin(
                            settings.MEDIA_URL, str(document.dc_pdf_full)
                        )
                    else:
                        conversion_info = document.get_info_about_conversion()

                    content = loader.render_to_string(
                        'admin/document/detail_div.html', {
                            'document_url': document_url,
                            'conversion_info': conversion_info,
                            'document': document,
                            'course_dates': c_dates,
                            'dates': all_dates,
                            'course_name': course_name,
                            'error_message': error_message
                        })

        response_dict = {'found': found, 'content': content}
        data = json.dumps(response_dict)

        return HttpResponse(data, content_type="application/json")

    @method_decorator(staff_member_required)
    def update_type(self, request):
        updated = False
        type = None

        if request.is_ajax():
            if request.method == "POST":
                document_id = request.POST.get('document_id')
                d_type = request.POST.get('type')
                try:
                    document_id = int(document_id)
                except:
                    document_id = None

                if document_id and d_type:
                    document = Document.objects.get(id=document_id)
                    document.d_type = d_type
                    document.save()
                    updated = True

        response_dict = {'updated': updated}
        data = json.dumps(response_dict)

        return HttpResponse(data, content_type="application/json")


# REGISTER ADMINS
admin.site.register(Document, DocumentAdmin)
