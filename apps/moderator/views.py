from datetime import datetime

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from apps.authorization.models import HabrUser
from apps.moderator.forms import BannedUserForm, RemarkCreateForm, \
    ComplainCreateForm, ReasonCreateForm
from apps.moderator.models import BannedUser, VerifyArticle, \
    ComplainToArticle, ComplainToComment


def complaints(request):
    title = "Жалобы"
    complaints_to_article = ComplainToArticle.get_all_complaints()
    complaints_to_comments = ComplainToComment.get_all_complaints()
    page_data = {
        "title": title,
        "articles": complaints_to_article,
        "comments": complaints_to_comments,
    }
    return render(request, "moderator/complaints.html", page_data)


def review_articles(request):
    """получение всех статей на проверку"""
    articles = VerifyArticle.get_all_articles_for_verifications()
    title = "Статьи на проверку"
    page_data = {
        "title": title,
        "articles": articles,
    }
    return render(request, "moderator/review_articles.html", page_data)


def add_user_ban(request, pk):
    title = "Блокирование пользователя"
    current_user = HabrUser.objects.get(pk=pk)

    if request.method == 'POST':
        ban_form = BannedUserForm(request.POST)
        if ban_form.is_valid():
            banned_user_query = BannedUser.objects.filter(offender=pk)
            if banned_user_query:
                banned_user = banned_user_query[0]
                banned_user.is_active = True
                banned_user.reason = request.POST["reason"]
                if request.POST.get("is_forever"):
                    banned_user.is_forever = True
                else:
                    banned_user.is_forever = False
                banned_user.num_days = request.POST["num_days"]
                banned_user.date_ban = datetime.today()
                banned_user.save()
            else:
                banned_user = BannedUser.objects.create(
                    offender=current_user,
                    reason=request.POST["reason"],
                    num_days=request.POST["num_days"],
                    is_active=True,
                    is_forever=True if request.POST.get("is_forever")
                    else False
                )
            banned_user.set_ban_email()
            return HttpResponseRedirect(reverse("articles:author_profile",
                                                args=[pk]))
        else:
            messages.error(request, 'ошибка')
    else:
        ban_form = BannedUserForm()
    page_data = {
        "title": title,
        "ban_form": ban_form,
        "current_user_pk": pk,
    }
    return render(request, 'moderator/add_ban.html', page_data)


def remove_user_ban(request, pk):
    current_user = BannedUser.objects.get(offender=pk)
    current_user.delete()
    current_user.unset_ban_email()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# def remove_user_ban(request, pk):
#     if request.is_ajax():
#         current_user = BannedUser.objects.get(offender=pk)
#         current_user.delete()
#         content = {
#             'current_user': current_user,
#             'user': request.user,
#         }
#         # result = render_to_string('moderator/includes/ban_buttons.html', content)
#         result = render_to_string('articles/author_profile.html', content)
#         return JsonResponse({'result': result})


def banned_users(request):
    title = "Заблокированные пользователи"
    banned_users_query = BannedUser.objects.filter(is_active=True)
    page_data = {
        "title": title,
        "banned_users": banned_users_query
    }
    return render(request, "moderator/banned_users.html", page_data)


def allow_publishing(request, pk):
    """Разрешение модератором публикации статьи"""
    VerifyArticle.allow_publishing(pk)
    return HttpResponseRedirect(reverse('moderator:review_articles'))


def reject_publishing(request, pk):
    """Отказ модератором на публикацию статьи"""
    form_remark = RemarkCreateForm(request.POST or None)
    page_data = {
        "pk": pk,
        "form_remark": form_remark,
    }
    return render(request, 'moderator/form_return_article.html', page_data)


def return_article(request, pk):
    """отправка на доработку и с обязательной причиной отказа"""
    if request.method == 'POST':
        form_remark = RemarkCreateForm(request.POST or None)
        if form_remark.is_valid():
            VerifyArticle.return_article(request.POST["remark"], pk)
    else:
        form_remark = RemarkCreateForm()
    return HttpResponseRedirect(reverse("moderator:review_articles"))


def complain_to_article(request, pk):
    """Жалоба на статью"""
    form_complain = ComplainCreateForm(request.POST or None)
    page_data = {
        "pk": pk,
        "form_complain": form_complain,
    }
    return render(request, 'moderator/form_complain_article.html',
                  page_data)


def complain_to_comment(request, pk, pk_article=None):
    """Жалоба на комментарий"""
    form_complain = ComplainCreateForm(request.POST or None)
    page_data = {
        "pk": pk,
        "form_complain": form_complain,
        "pk_article": pk_article,
    }
    return render(request, 'moderator/form_complain_comment.html',
                  page_data)


def send_complain_to_article(request, pk):
    """отправка жалобы на статью на модерацию"""
    if request.method == 'POST':
        form_complain = ComplainCreateForm(request.POST or None)
        if form_complain.is_valid():
            ComplainToArticle.send_complain_to_article(
                pk,
                request.POST["text_complain"],
                request.user.pk
            )
    else:
        form_complain = ComplainCreateForm()
    return HttpResponseRedirect(reverse("articles:main_page"))


def send_complain_to_comment(request, pk, pk_article=None):
    """отправка жалобы на комментарий на модерацию"""
    if request.method == 'POST':
        form_complain = ComplainCreateForm(request.POST or None)
        if form_complain.is_valid():
            ComplainToComment.send_complain_to_comment(
                pk,
                request.POST["text_complain"],
                request.user.pk
            )
    else:
        form_complain = ComplainCreateForm()
    if pk_article is None:
        return HttpResponseRedirect(reverse("articles:main_page"))
    return HttpResponseRedirect(reverse("articles:article",
                                        args=(pk_article,)))


def ban_article(request, pk):
    ComplainToArticle.reject_article(pk)
    return HttpResponseRedirect(reverse("moderator:complaints"))


def no_ban_article(request, pk):
    ComplainToArticle.allow_article(pk)
    return HttpResponseRedirect(reverse("moderator:complaints"))


def ban_comment(request, pk):
    form_reason = ReasonCreateForm(request.POST or None)
    page_data = {
        "pk": pk,
        "form_reason": form_reason,
    }
    return render(request, 'moderator/form_reason_ban_comment.html',
                  page_data)


def send_ban_comment(request, pk):
    ComplainToComment.reject_comment(pk)
    if request.method == 'POST':
        form_reason = ReasonCreateForm(request.POST or None)
        if form_reason.is_valid():
            ComplainToComment.objects.filter(pk=pk).update(
                text_reason=request.POST["text_reason"]
            )
    else:
        form_reason = ReasonCreateForm()
    return HttpResponseRedirect(reverse("moderator:complaints"))


def no_ban_comment(request, pk):
    ComplainToComment.allow_comment(pk)
    return HttpResponseRedirect(reverse("moderator:complaints"))
