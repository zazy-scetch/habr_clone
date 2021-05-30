from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from apps.account.forms import ChangePasswordForm, ArticleEditForm, ArticleCreate
from apps.account.forms import HabrUserProfileEditForm
from apps.articles.models import Article, Hub, LikesViewed
from apps.articles.views import notification, all_notification
from apps.authorization.models import HabrUser
from apps.moderator.models import VerifyArticle


@login_required
def read_profile(request):
    title = "Профиль пользователя"
    current_user = request.user
    # TODO импорт вьюшки во вьюшку - результат несоблюдения "толстые модели,
    #  тонкие контроллеры"
    if request.user.is_authenticated:
        notifications = notification(request)
    else:
        notifications = None

    page_data = {
        "title": title,
        "current_user": current_user,
        "notifications": notifications,
    }
    return render(request, "account/read_profile.html", page_data)


@login_required
@transaction.atomic()
def add_article(request):
    article_add = ArticleCreate(request.POST, request.FILES)
    is_success = False
    is_fail = False
    error_messages = []
    if request.method == "POST":
        if article_add.is_valid():
            article_add.save(commit=False)
            article_add.instance.author = request.user
            article_add.save()
            is_success = True
            return HttpResponseRedirect(reverse("account:user_articles"))
        else:
            is_fail = True
            for error in article_add.errors:
                error_messages.append(
                    f'Поле {article_add[error].label}: '
                    f'{article_add.errors[error].as_text()}')

    if request.user.is_authenticated:
        notifications = notification(request)
    else:
        notifications = None

    title = "Создание статьи"
    page_data = {
        "title": title,
        "article_add": article_add,
        "notifications": notifications,
        "is_success": is_success,
        "is_fail": is_fail,
        'error_messages': error_messages,

    }
    return render(request, "account/form_add_article.html", page_data)


@login_required
@transaction.atomic()
def del_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    article.del_article(pk)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required
@transaction.atomic()
def draft_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    article.draft_article(pk)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required
@transaction.atomic()
def edit_profile(request):
    title = "Редактирование профиля"
    is_success = False
    is_fail = False
    error_messages = []
    if request.method == "POST":
        profile_edit_form = HabrUserProfileEditForm(
            request.POST, request.FILES, instance=request.user.habruserprofile
        )
        if profile_edit_form.is_valid():
            profile_edit_form.save()
            is_success = True
        else:
            is_fail = True
            for error in profile_edit_form.errors:
                error_messages.append(
                    f'Поле {profile_edit_form[error].label}:'
                    f' {profile_edit_form.errors[error].as_text()}'
                )
    profile_edit_form = HabrUserProfileEditForm(
        instance=request.user.habruserprofile)

    if request.user.is_authenticated:
        notifications = notification(request)
    else:
        notifications = None

    page_data = {
        "title": title,
        "edit_form": profile_edit_form,
        "notifications": notifications,
        "is_success": is_success,
        "is_fail": is_fail,
        "error_messages": error_messages,

    }
    return render(request, "account/edit_profile.html", page_data)


@login_required
def user_articles(request, page=1):
    """
    функция отвечает за Мои статьи
    """
    title = "Мои статьи"

    if request.user.is_authenticated:
        notifications = notification(request)
        articles_with_statuses = \
            VerifyArticle.get_articles_with_statuses(request.user.id)
    else:
        notifications = None
        articles_with_statuses = None
    # articles = Article.get_by_author(request.user.id)

    paginator = Paginator(articles_with_statuses, 12)
    try:
        articles_paginator = paginator.page(page)
    except PageNotAnInteger:
        articles_paginator = paginator.page(1)
    except EmptyPage:
        articles_paginator = paginator.page(paginator.num_pages)

    page_data = {
        "title": title,
        "articles": articles_paginator,
        "notifications": notifications,
        # "articles_with_statuses": articles_with_statuses,
    }
    return render(request, "account/user_articles.html", page_data)


@login_required
def publications(request, page=1):
    """
    функция отвечает за мои публикации
    """
    title = "Мои публикации"
    # articles = Article.get_by_author(author_pk=request.user.id, draft=0)

    if request.user.is_authenticated:
        notifications = notification(request)
        articles_with_statuses = \
            VerifyArticle.get_articles_with_statuses(request.user.id, draft=0)
    else:
        notifications = None
        articles_with_statuses = None

    paginator = Paginator(articles_with_statuses, 5)
    try:
        articles_paginator = paginator.page(page)
    except PageNotAnInteger:
        articles_paginator = paginator.page(1)
    except EmptyPage:
        articles_paginator = paginator.page(paginator.num_pages)

    page_data = {
        "title": title,
        "articles": articles_paginator,
        "notifications": notifications,
        # "articles_with_statuses": articles_with_statuses,

    }
    return render(request, "account/user_articles_publications.html",
                  page_data)


@login_required
def draft(request, page=1):
    """
    функция отвечает за Черновик
    """
    title = "Черновик"
    # articles = Article.get_by_author(author_pk=request.user.id, draft=1)
    if request.user.is_authenticated:
        notifications = notification(request)
        articles_with_statuses = \
            VerifyArticle.get_articles_with_statuses(request.user.id, draft=1)

    else:
        notifications = None
        articles_with_statuses = None

    paginator = Paginator(articles_with_statuses, 5)
    try:
        articles_paginator = paginator.page(page)
    except PageNotAnInteger:
        articles_paginator = paginator.page(1)
    except EmptyPage:
        articles_paginator = paginator.page(paginator.num_pages)

    page_data = {
        "title": title,
        "articles": articles_paginator,
        "notifications": notifications,
        # "articles_with_statuses": articles_with_statuses,

    }
    return render(request, "account/user_articles_draft.html", page_data)


@login_required
@transaction.atomic()
def edit_password(request):
    title = "Изменить пароль"
    is_success = False
    is_fail = False
    error_messages = []
    user = HabrUser.objects.get(username=request.user)
    if request.method == "POST":
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_password = request.POST.get("old_password")
            new_password = request.POST.get("new_password")
            repeat_new_passw = request.POST.get("repeat_password")
            if check_password(old_password, user.password) and new_password == repeat_new_passw:
                user.password = make_password(new_password)
                user.save()
                is_success = True
                update_session_auth_hash(request, user)
            else:
                if not check_password(old_password, user.password):
                    is_fail = True
                    error_messages.append('Введенный старый пароль неверный')
                if new_password != repeat_new_passw:
                    is_fail = True
                    error_messages.append('Введенные пароли не совпадают')
        else:
            is_fail = True
            for error in form.errors:
                error_messages.append(f'Поле {form[error].label}: {form.errors[error].as_text()}')
    else:
        form = ChangePasswordForm()

    if request.user.is_authenticated:
        notifications = notification(request)
    else:
        notifications = None
    page_data = {
        "title": title,
        "edit_form": form,
        "notifications": notifications,
        "is_success": is_success,
        "is_fail": is_fail,
        "error_messages": error_messages,

    }
    return render(request, "account/edit_password.html", page_data)


@login_required
@transaction.atomic()
def edit_article(request, pk):
    """
    функция отвечает за редактирование статьи
    """
    title = "Создание статьи"
    edit_article = get_object_or_404(Article, pk=pk)
    is_success = False
    is_fail = False
    error_messages = []
    if request.method == "POST":
        edit_form = ArticleEditForm(request.POST, request.FILES,
                                    instance=edit_article)
        if edit_form.is_valid():
            edit_article.updated = timezone.now()
            edit_article.save()
            edit_form.save()
            # снимаем с публикации и удаляем из табл. модерации
            edit_article.draft = True
            if VerifyArticle.objects.filter(
                    verification=edit_article.pk).exists():
                VerifyArticle.objects.get(
                    verification=edit_article.pk).delete()
            edit_article.save()
            is_success = True
            return HttpResponseRedirect(reverse("account:user_articles"))
        else:
            is_fail = True
            for error in edit_form.errors:
                error_messages.append(f'Поле {edit_form[error].label}: {edit_form.errors[error].as_text()}')
    else:
        edit_form = ArticleEditForm(instance=edit_article)

    if request.user.is_authenticated:
        notifications = notification(request)
    else:
        notifications = None

    page_data = {
        "title": title,
        "update_form": edit_form,
        "media_url": settings.MEDIA_URL,
        "notifications": notifications,
        "is_success": is_success,
        "is_fail": is_fail,
        "error_messages": error_messages,
    }

    return render(request, "account/edit_article.html", page_data)


@login_required
@transaction.atomic()
def bookmarks_page(request, page=1):
    bookmarks = Article.get_bookmarks(request.user.id)
    title = "Закладки"

    if request.user.is_authenticated:
        notifications = notification(request)
    else:
        notifications = None

    paginator = Paginator(bookmarks, 20)
    try:
        bookmarks_paginator = paginator.page(page)
    except PageNotAnInteger:
        bookmarks_paginator = paginator.page(1)
    except EmptyPage:
        bookmarks_paginator = paginator.page(paginator.num_pages)

    page_data = {
        "title": title,
        "articles": bookmarks_paginator,
        "notifications": notifications,
    }
    return render(request, "account/bookmarks.html", page_data)

@login_required
@transaction.atomic()
def notifications_page(request):
    notification_all= all_notification(request)
    title = f"Все ведомления {request.user}"
    if request.user.is_authenticated:
        notifications = notification(request)
    else:
        notifications = None

    page_data = {
        "title": title,
        "notification_all": notification_all,
        "notifications": notifications,
    }
    return render(request, "account/notifications.html", page_data)


def my_likes(request):
    title = f"Понравившиеся статьи"
    if request.user.is_authenticated:
        notifications = notification(request)
    else:
        notifications = None
    page_data = {
        "title": title,
        "all_my_likes": LikesViewed.get_likes(request),
        "notifications": notifications,
    }
    return render (request, "account/my_likes.html", page_data)


@login_required
@transaction.atomic()
def verify_article(request, pk):
    """отправка статьи на модерацию"""
    # если удалось отправить, то перезагрузить страницу
    if VerifyArticle.send_article_to_verify(pk, request.user.pk):
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    else:
        return HttpResponseRedirect(reverse_lazy("account:user_articles"))
        pass
