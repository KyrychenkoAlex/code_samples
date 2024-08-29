import datetime
import json
import os
import tempfile

from django.contrib.auth.decorators import login_required
from django.http import (
    HttpResponse, HttpResponseRedirect, Http404, JsonResponse
)
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from utils import plupload
from utils.auth import basicauth

from accounts.forms import SchoolForm
from forms import (
    CommentForm, TagForm, NotetakerUploadForm, DocumentUploadForm
)
from models import (
    Comment, Document, DocumentRevision, EssayCategory, LikesBookmarks,
    EssayDocument, Tag, DocumentsDownloadRequests, DocumentVisit
)
from services import SeedUploadDoc


@login_required
def flag_comment(request):
    flagged = False

    if request.is_ajax():
        if request.method == "POST":
            comment_id = request.POST.get('comment_id')
            try:
                comment_id = int(comment_id)
            except:
                comment_id = None
            if comment_id:
                comment = Comment.objects.get(id=comment_id)
                comment.flag(request.user)
                flagged = True

    msg = "Comment successfully flagged" if flagged else (
        "Problem flagging message")
    response_dict = {'msg': msg, 'success': flagged}
    data = json.dumps(response_dict)

    return HttpResponse(data, content_type="application/json")


@login_required
def add_comment(request, document_id):
    try:
        document_id = int(document_id)
    except:
        raise Http404('No %s matches the given query.' % Document)
    document = get_object_or_404(Document, id=document_id)

    if not document.access_allowed(request.user):
        link = reverse(
            'course_document_slug', args=[document.id, document.slug])
        return HttpResponseRedirect(
            link + "?msg=Comments disabled for preview")

    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            content = comment_form.cleaned_data['content']
            anonymous = comment_form.cleaned_data['anonymous']
            comment = Comment(
                content=content,
                user=request.user,
                document=document,
                anonymous=anonymous)

            original = comment_form.cleaned_data['original']
            if original:
                try:
                    original_comment = Comment.objects.get(id=original)
                except:
                    # this should actually result in an error
                    pass
                if original_comment:
                    comment.original = original_comment

            comment.save()

    link = reverse('course_document_slug', args=[document.id, document.slug])
    return HttpResponseRedirect(link + "?msg=Comment successfully added")


@login_required
def add_tags(request, document_id):
    document = get_object_or_404(Document, id=document_id)

    if not document.access_allowed(request.user):
        link = reverse(
            'course_document_slug', args=[document.id, document.slug])
        return HttpResponseRedirect(link + "?msg=Tags disabled for preview")

    if request.method == "POST":
        tag_form = TagForm(request.POST)
        if tag_form.is_valid():
            tags_string = tag_form.cleaned_data['tags']
            for tag_string in tags_string.split(','):
                tag, created = Tag.objects.get_or_create(name=tag_string)
                tag.document_set.add(document)

    link = reverse('course_document_slug', args=[document.id, document.slug])
    return HttpResponseRedirect(link + "?msg=Tags successfully added")


@login_required
def remove_tag(request, document_id, tag_id):
    try:
        document_id = int(document_id)
    except:
        raise Http404('No %s matches the given query.' % Document)
    document = get_object_or_404(Document, id=document_id)

    tag = get_object_or_404(Tag, id=tag_id)

    if not document.access_allowed(request.user):
        link = reverse(
            'course_document_slug', args=[document.id, document.slug])
        return HttpResponseRedirect(link + "?msg=Tags disabled for preview")

    tag.document_set.remove(document)

    link = reverse('course_document_slug', args=[document.id, document.slug])
    return HttpResponseRedirect(link + "?msg=Tags removed from document")


def _save_uploaded_document(temp_file, user, name, user_essay):
    # TODO: move to model
    title, extension = os.path.splitext(name)

    # max 80 characters for filename
    length = 80 - len(extension)
    name = title[:length] + extension

    document = Document(notetaker=user, title=title[:100])
    document.document.save(name, temp_file, save=False)
    document.user_essay = user_essay
    document.updated_at = datetime.datetime.now()
    document.save()


def _handle_uploaded_file(f, chunk, filepath):
    """
    Writes chunks to filepath provided
    """
    mode = 'ab' if int(chunk) > 0 else 'wb'
    _file = open(filepath, mode)
    if f.multiple_chunks:
        for chunk in f.chunks():
            _file.write(chunk)
    else:
        _file.write(f.read())

    _file.close()


def _handle_valid_upload(request):
    # Step 1: temp file
    # this code handles uploading one file, that may be broken
    # up into pieces

    file_obj = tempfile.NamedTemporaryFile()
    forms = request.POST
    files = request.FILES
    dest = 'media/tmp/'

    text_respons = 'This file seems to have been already uploaded: '

    save_file = True

    res = plupload.save_tmp_file_obj(request, forms, files, dest, file_obj)

    if res:
        # Step 2: save file in GCS and add entry to postgres

        file_title = files['file'].name
        untagged_documents = Document.objects \
            .filter(notetaker=request.user, status=Document.UNTAGGED) \
            .order_by('-publish_date')

        try:
            if file_title.split(".")[0] in untagged_documents.values_list(
                    'title', flat=True):
                save_file = False
                request.session[
                    'duplicate_text'] = f'{text_respons} <b>{file_title}</b>'
            elif file_title == 'blob':
                file_title = forms['name']
                if file_title.split(".")[0] in untagged_documents.values_list(
                        'title', flat=True):
                    save_file = False
                    request.session[
                        'duplicate_text'] = (f'{text_respons} <b>'
                                             f'{file_title}</b>')
        except:
            pass

        if save_file:
            user_essay = request.POST.get('user_essay', False) is not False
            _save_uploaded_document(
                temp_file=file_obj.file,
                user=request.user,
                name=request.POST.get('name'),
                user_essay=user_essay)
            # Step 3: cleanup
            file_obj.close()  # automatically deleted when closed


@login_required
@never_cache
def document_upload_redesign(request):
    school = None
    school_form = None

    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        name = request.POST.get('name')
        unique = request.POST.get('unique')

        if form.is_valid() and name and unique:
            _handle_valid_upload(request)

            if request.is_ajax():
                response = HttpResponse(
                    content='{"jsonrpc" : "2.0", "result" : null, "id" : '
                            '"id"}',
                    content_type='text/plain; charset=UTF-8')
                response['Expires'] = 'Mon, 1 Jan 2000 01:00:00 GMT'
                response[
                    'Cache-Control'] = ('no-store, no-cache, must-revalidate, '
                                        'post-check=0, pre-check=0')
                response['Pragma'] = 'no-cache'
                return response

            return redirect('document_untagged')
    else:
        form = DocumentUploadForm()
        school_form = SchoolForm()
        school = request.user.profile.school

    template = 'document/upload_redesign.html'
    context = {
        'form': form,
        'school': school,
        'school_form': school_form,
        'is_notetaker': request.user.profile.is_notetaker,
        'hide_menu': True,
    }
    return render(request, template, context)


@csrf_exempt
@basicauth
def seed_upload_document(request):
    document, is_processed, error = SeedUploadDoc(request=request).run()
    doc_id = document.id if document else None
    dc_success = document.dc_success if document else False
    resp_data = {
        "id": doc_id,
        "processed": is_processed,
        "dc_success": dc_success,
        "error": error
    }
    return HttpResponse(
        json.dumps(resp_data),
        content_type='application/json')
