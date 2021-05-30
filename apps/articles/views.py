import datetime

from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse

from apps.articles.models import Article, LikesViewed, DislikesViewed
from apps.authorization.models import HabrUser, KarmaPositiveViewed,\
    KarmaNegativeViewed
from apps.authorization.models import HabrUserProfile
from apps.comments.forms import CommentCreateForm
from apps.comments.models import Comment, Sorted, CommentLikesViewed, \
    CommentDislikesViewed
from apps.moderator.models import BannedUser, Moderator, VerifyArticle, \
    ComplainToArticle, ComplainToComment


def main_page(request, pk=None, page=1):
    """рендер главной страницы"""
    title = "главная страница"

    if pk is None:
        hub_articles = Article.get_articles()
    else:
        hub_articles = Article.get_by_hub(pk)

    last_articles = Article.get_last_articles(hub_articles)
    if request.user.is_authenticated:
        notifications = notification(request)
    else:
        notifications = None
    paginator = Paginator(hub_articles, 5)
    try:
        articles_paginator = paginator.page(page)
    except PageNotAnInteger:
        articles_paginator = paginator.page(1)
    except EmptyPage:
        articles_paginator = paginator.page(paginator.num_pages)

    page_data = {
        "title": title,
        "articles": articles_paginator,
        "last_articles": last_articles,
        "current_user": request.user,
        "notifications": notifications,
    }
    return render(request, "articles/articles.html", page_data)


def hub(request, pk=None, page=1):
    if pk is None:
        hub_articles = Article.get_articles()
    else:
        hub_articles = Article.get_by_hub(pk)

    last_articles = Article.get_last_articles(hub_articles)

    paginator = Paginator(hub_articles, 5)
    try:
        articles_paginator = paginator.page(page)
    except PageNotAnInteger:
        articles_paginator = paginator.page(1)
    except EmptyPage:
        articles_paginator = paginator.page(paginator.num_pages)

    if request.user.is_authenticated:
        notifications = notification(request)
    else:
        notifications = None

    page_data = {
        "pk": pk,
        "articles": articles_paginator,
        "last_articles": last_articles,
        "notifications": notifications,

    }
    return render(request, "articles/articles_hub.html", page_data)


def article(request, pk=None):
    hub_articles = Article.get_articles()
    last_articles = Article.get_last_articles(hub_articles)
    current_article = Article.get_article(pk)
    comments = Comment.get_comments(pk)
    form_comment = CommentCreateForm(request.POST or None)
    comments_is_liked = None
    comments_is_disliked = None
    notifications = None
    is_moderator = False
    status = False
    is_complained = None
    is_complained_comments = None
    if current_article is None:
        return HttpResponseRedirect(reverse("articles:main_page"))
    if request.user.is_authenticated:
        notifications = notification(request)

        comments_is_liked = Comment.get_liked_comments_by_user(pk,
                                                               request.user.id)
        comments_is_disliked = Comment.get_disliked_comments_by_user(
            pk,
            request.user.id
        )
        current_article.views.add(request.user)
        current_article.liked = current_article.likes.filter(
            pk=request.user.pk
        ).exists()
        current_article.disliked = current_article.dislikes.filter(
            pk=request.user.pk
        ).exists()
        current_article.bookmarked = current_article.bookmarks.filter(
            pk=request.user.pk
        ).exists()
        current_article.author_liked = (
            current_article.author.habruserprofile.karma_positive.filter(
                pk=request.user.pk
            ).exists()
        )
        current_article.author_disliked = (
            current_article.author.habruserprofile.karma_negative.filter(
                pk=request.user.pk
            ).exists()
        )
        is_moderator = Moderator.is_moderator(request.user.id)
        if is_moderator:
            status = VerifyArticle.get_status_verification_article(pk)
        is_complained = ComplainToArticle.article_is_complained(pk)
        # is_complained_comments = ComplainToComment\
        #     .get_complaints_of_article(pk)

    page_data = {
        "article": current_article,
        "last_articles": last_articles,
        "comments": comments,
        "form_comment": form_comment,
        "media_url": settings.MEDIA_URL,
        "notifications": notifications,
        "comments_is_liked": comments_is_liked,
        "comments_is_disliked": comments_is_disliked,
        "is_moderator": is_moderator,
        "status": status,
        "is_complained": is_complained,
        # "is_complained_comments": is_complained_comments,
    }
    return render(request, "articles/article.html", page_data)


def change_article_rate(request):
    if request.is_ajax() and request.user.is_authenticated:
        rated_article = request.GET.get("article")
        field = request.GET.get("field")
        rated_article = Article.objects.get(pk=rated_article)
        if request.user != rated_article.author:
            if field == "like":
                if rated_article.likes.filter(pk=request.user.pk).exists():
                    rated_article.likes.remove(request.user)
                    rated_article.author.habruserprofile.rating -= 1
                elif rated_article.dislikes.filter(pk=request.user.pk).exists():
                    rated_article.likes.add(request.user)
                    rated_article.dislikes.remove(request.user)
                    rated_article.author.habruserprofile.rating += 2
                else:
                    rated_article.likes.add(request.user)
                    rated_article.author.habruserprofile.rating += 1
            elif field == "dislike":
                if rated_article.dislikes.filter(pk=request.user.pk).exists():
                    rated_article.dislikes.remove(request.user)
                    rated_article.author.habruserprofile.rating += 1
                elif rated_article.likes.filter(pk=request.user.pk).exists():
                    rated_article.dislikes.add(request.user)
                    rated_article.likes.remove(request.user)
                    rated_article.author.habruserprofile.rating -= 2
                else:
                    rated_article.dislikes.add(request.user)
                    rated_article.author.habruserprofile.rating -= 1
            else:
                if rated_article.bookmarks.filter(pk=request.user.pk).exists():
                    rated_article.bookmarks.remove(request.user)
                else:
                    rated_article.bookmarks.add(request.user)
            rated_article.rating = rated_article.likes.count() - \
                                   rated_article.dislikes.count()
            rated_article.author.habruserprofile.save()
            rated_article.save()
        return JsonResponse(
            {
                "likes": rated_article.likes.count(),
                "dislikes": rated_article.dislikes.count(),
                "author_rating": rated_article.author.habruserprofile.rating,
                "like": rated_article.likes.filter(pk=request.user.pk
                                                   ).exists(),
                "dislike": rated_article.dislikes.filter(
                    pk=request.user.pk
                ).exists(),
            }
        )


def like_dislike_author_ajax(request):
    if request.is_ajax() and request.user.is_authenticated:
        user = request.GET.get("user")
        field = request.GET.get("field")
        if request.user.pk != int(user):
            user = HabrUserProfile.objects.get(pk=user)
            if field == "like":
                if user.karma_positive.filter(pk=request.user.pk).exists():
                    user.karma_positive.remove(request.user)
                elif user.karma_negative.filter(pk=request.user.pk).exists():
                    user.karma_positive.add(request.user)
                    user.karma_negative.remove(request.user)
                else:
                    user.karma_positive.add(request.user)
            elif field == "dislike":
                if user.karma_negative.filter(pk=request.user.pk).exists():
                    user.karma_negative.remove(request.user)
                elif user.karma_positive.filter(pk=request.user.pk).exists():
                    user.karma_negative.add(request.user)
                    user.karma_positive.remove(request.user)
                else:
                    user.karma_negative.add(request.user)
        user.save()
        return JsonResponse(
            {
                "karma": user.karma,
                "liked": user.karma_positive.filter(
                    pk=request.user.pk
                ).exists(),
                "disliked": user.karma_negative.filter(
                    pk=request.user.pk
                ).exists(),
            }
        )


def show_author_profile(request, pk=None):
    title = "Информация об авторе"
    author = get_object_or_404(HabrUser, pk=pk)
    author_banned_query = BannedUser.objects.filter(offender=author, is_active=True)
    if author_banned_query:
        author_banned = author_banned_query[0]
    else:
        author_banned = None
    page_data = {
        "title": title,
        "current_user": author,
        "author_banned": author_banned,
    }
    return render(request, "articles/author_profile.html", page_data)


def search_articles(request, page=1):
    """рендер главной страницы после поиска"""
    title = "главная страница"

    found_articles = Article.get_search_articles(request.GET)

    last_articles = Article.get_last_articles(found_articles)
    paginator = Paginator(found_articles, 20)
    try:
        articles_paginator = paginator.page(page)
    except PageNotAnInteger:
        articles_paginator = paginator.page(1)
    except EmptyPage:
        articles_paginator = paginator.page(paginator.num_pages)
    if request.user.is_authenticated:
        notifications = notification(request)
    else:
        notifications = None
    page_data = {
        "title": title,
        "last_articles": last_articles,
        "current_user": request.user,
        "articles": articles_paginator,
        "value_search": request.GET.get('search', ''),
        "notifications": notifications,
    }
    return render(request, "articles/includes/search_articles.html", page_data)


def post_list(request, pk=None, page=1):
    '''функция используется для сортировке всех статей или сортировки статей по хабу'''
    if request.is_ajax():
        sorted_query = request.GET['content']
        if pk is None:
            hub_articles = Sorted.sort(sorted_query).get_data()
        else:
            hub_articles = Sorted.sort(sorted_query, pk).get_data()

        paginator = Paginator(hub_articles, 5)
        try:
            articles_paginator = paginator.page(page)
        except PageNotAnInteger:
            articles_paginator = paginator.page(1)
        except EmptyPage:
            articles_paginator = paginator.page(paginator.num_pages)

        page_data = {
            "articles": articles_paginator,
            "current_user": request.user,
        }
        result = render_to_string('articles/includes/post_list.html', page_data)
        return JsonResponse({'result': result})


def post_list_search(request, page=1):
    """ функция используется для сортировке статей поиска"""
    if request.is_ajax():
        search_query = request.GET['search_value']
        sorted_query = request.GET['content']
        hub_articles = Article.get_search_articles(request.GET)
        hub_articles = Sorted.sort(sorted_query, search_query=hub_articles).get_data()

        paginator = Paginator(hub_articles, 5)
        try:
            articles_paginator = paginator.page(page)
        except PageNotAnInteger:
            articles_paginator = paginator.page(1)
        except EmptyPage:
            articles_paginator = paginator.page(paginator.num_pages)

        page_data = {
            "articles": articles_paginator,
            "current_user": request.user,
            "value_search": search_query,
        }
        result = render_to_string('articles/includes/post_list.html', page_data)
        return JsonResponse({'result': result})


def post_list_user(request, user_pk, page=1):
    """ функция используется для сортировке статей пользователя"""
    if request.is_ajax():
        sorted_query = request.GET['sorted']
        if user_pk is None:
            hub_articles = Sorted.sort(sorted_query).get_data()
        else:
            hub_articles = Sorted.sort(sorted_query, user_pk).get_data()

        paginator = Paginator(hub_articles, 5)
        try:
            articles_paginator = paginator.page(page)
        except PageNotAnInteger:
            articles_paginator = paginator.page(1)
        except EmptyPage:
            articles_paginator = paginator.page(paginator.num_pages)

        page_data = {
            "articles": articles_paginator,
            "current_user": request.user,
        }
        result = render_to_string('articles/includes/post_list.html',
                                  page_data)
        return JsonResponse({'result': result})


def notification(request):
    result_notification, current_notifications = [], []
    current_articles = Article.get_by_author(author_pk=request.user.pk)
    for itm_article in current_articles:
        likes = LikesViewed.objects.filter(article_id=itm_article.id,
                                           viewed=False)
        dislikes = DislikesViewed.objects.filter(article_id=itm_article.id,
                                                 viewed=False)
        comments = Comment.get_comments(itm_article.id) \
            .filter(viewed=False).exclude(author_id=request.user.pk)
        answered_you = Comment.get_comments(itm_article.id) \
            .filter(viewed=False,
                    parent__author_id=request.user.pk,
                    )

        likes_karma = KarmaPositiveViewed.objects.filter(
            viewed=False,
            profile_author=request.user.pk
        )
        dislikes_karma = KarmaNegativeViewed.objects.filter(
            viewed=False,
            profile_author=request.user.pk
        )
        comment_likes = CommentLikesViewed.objects.filter(
            viewed=False,
            comment__author_id = request.user.pk

        )
        comment_dislikes = CommentDislikesViewed.objects.filter(
            viewed=False,
            comment__author_id = request.user.pk
        )

        for answer in answered_you:
            current_notifications.append(("answered_you", answer))
        for comment in comments:
            current_notifications.append(("comment", comment))
        for like in likes:
            current_notifications.append(("like", like))
        for dislike in dislikes:
            current_notifications.append(("dislike", dislike))
        for like_karma in likes_karma:
            current_notifications.append(("like_karma", like_karma))
        for dislike_karma in dislikes_karma:
            current_notifications.append(("dislike_karma", dislike_karma))
        for comment_like in comment_likes:
            current_notifications.append (("comment_like", comment_like))
        for comment_dislike in comment_dislikes:
            current_notifications.append (("comment_dislike", comment_dislike))
        result_notification = list(set(current_notifications))
    return result_notification


def mark_all_as_viewed(request):
    """отмечаем все уведомления как просмотренные"""
    current_articles = Article.get_by_author(author_pk=request.user.pk)
    for i in current_articles:
        LikesViewed.objects.filter(article_id=i.id).update(viewed=True)
        DislikesViewed.objects.filter(article_id=i.id).update(viewed=True)
        Comment.get_comments(i.id).update(viewed=True)
        Comment.get_comments (i.id).filter (parent__author_id=request.user.pk
                     ).update(viewed=True)
        CommentLikesViewed.objects.filter(
            comment__article_id = i.id).update(viewed=True)
        CommentDislikesViewed.objects.filter(
            comment__article_id = i.id).update(viewed=True)
        KarmaPositiveViewed.objects.filter (
            profile_author=request.user.pk).update(viewed=True)
        KarmaNegativeViewed.objects.filter (
            profile_author=request.user.pk).update (viewed=True)


    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def target_mark_as_viewed(request, target, pk):
    if target == 'comment':
        Comment.objects.filter(id=pk).update(viewed=True)
    elif target == 'answered_you':
        Comment.objects.filter(id=pk).update(viewed=True)
    elif target == 'like':
        LikesViewed.objects.filter(id=pk).update(viewed=True)
    elif target == 'dislike':
        DislikesViewed.objects.filter(id=pk).update(viewed=True)
    elif target == 'comment_like':
        CommentLikesViewed.objects.filter(id=pk).update(viewed=True)
    elif target == 'comment_dislike':
        CommentDislikesViewed.objects.filter(id=pk).update(viewed=True)
    elif target == 'like_karma':
        KarmaPositiveViewed.objects.filter(id=pk).update(viewed=True)
    elif target == 'dislike_karma':
        KarmaNegativeViewed.objects.filter(id=pk).update(viewed=True)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def all_notification(request):
    current_articles = Article.get_by_author (author_pk=request.user.pk)
    all_notification, current_all_notification = [], []
    for itm_article in current_articles:
        likes = LikesViewed.objects.filter(article_id=itm_article.id)
        dislikes = DislikesViewed.objects.filter(article_id=itm_article.id)
        comments = Comment.get_comments(itm_article.id).exclude(author_id=request.user.pk)
        answered_you = Comment.get_comments(itm_article.id).filter(
                    parent__author_id=request.user.pk)
        likes_karma = KarmaPositiveViewed.objects.filter(profile_author=request.user.pk)
        dislikes_karma = KarmaNegativeViewed.objects.filter (
            profile_author=request.user.pk)
        comment_likes = CommentLikesViewed.objects.filter (
            comment__author_id=request.user.pk)
        comment_dislikes = CommentDislikesViewed.objects.filter (
            comment__author_id=request.user.pk)

        for answer in answered_you:
            all_notification.append (("answered_you", answer))
        for comment in comments:
            all_notification.append (("comment", comment))
        for like in likes:
            all_notification.append (("like", like))
        for dislike in dislikes:
            all_notification.append (("dislike", dislike))
        for like_karma in likes_karma:
            all_notification.append (("like_karma", like_karma))
        for dislike_karma in dislikes_karma:
            all_notification.append (("dislike_karma", dislike_karma))
        for comment_like in comment_likes:
            all_notification.append (("comment_like", comment_like))
        for comment_dislike in comment_dislikes:
            all_notification.append (("comment_dislike", comment_dislike))
        current_all_notification = list(set(all_notification))

    return current_all_notification

