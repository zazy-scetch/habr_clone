from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import HttpResponseRedirect, get_object_or_404
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.conf import settings
from django.template.loader import render_to_string

from apps.articles.models import Article, Hub
from .forms import CommentCreateForm
from .models import Comment


@login_required
@transaction.atomic
def comment_create(request, pk):
    current_article = get_object_or_404(Article, id=pk)
    form_comment = CommentCreateForm(request.POST or None)
    if request.method == 'POST':
        if form_comment.is_valid():
            new_comment = form_comment.save(commit=False)
            new_comment.author = request.user
            new_comment.article = current_article
            new_comment.body = form_comment.cleaned_data["body"]
            new_comment.parent = None
            new_comment.is_child = False
            new_comment.save()
            #если в js стоит функция location.reload();, то return JsonResponse не нужен
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required
@transaction.atomic
def child_comment_create(request, pk, id_parent_comment):
    current_article = get_object_or_404(Article, id=pk)
    form_comment = CommentCreateForm(request.POST or None)
    if request.method == 'POST':
        if form_comment.is_valid():
            new_comment = form_comment.save(commit=False)
            new_comment.author = request.user
            new_comment.article = current_article
            new_comment.body = form_comment.cleaned_data["body"]
            new_comment.parent = Comment.get_comment(id_parent_comment)
            new_comment.is_child = True
            new_comment.save()
            #если в js стоит функция location.reload();, то return JsonResponse не нужен
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def like_dislike_ajax(request):
    if request.is_ajax() and request.user.is_authenticated:
        field = request.GET.get("field")
        comment = request.GET.get("comment").split("-")[1]
        comment = Comment.objects.get(pk=comment)
        if request.user != comment.author:
            if field == "like":
                if comment.likes.filter(pk=request.user.pk).exists():
                    comment.likes.remove(request.user)
                    comment.author.habruserprofile.rating -= 1 * 0.5
                elif comment.dislikes.filter(pk=request.user.pk).exists():
                    comment.likes.add(request.user)
                    comment.dislikes.remove(request.user)
                    comment.author.habruserprofile.rating += 2 * 0.5
                else:
                    comment.likes.add(request.user)
                    comment.author.habruserprofile.rating += 1 * 0.5
            elif field == "dislike":
                if comment.dislikes.filter(pk=request.user.pk).exists():
                    comment.dislikes.remove(request.user)
                    comment.author.habruserprofile.rating += 1 * 0.5
                elif comment.likes.filter(pk=request.user.pk).exists():
                    comment.dislikes.add(request.user)
                    comment.likes.remove(request.user)
                    comment.author.habruserprofile.rating -= 2 * 0.5
                else:
                    comment.dislikes.add(request.user)
                    comment.author.habruserprofile.rating -= 1 * 0.5
            comment.author.habruserprofile.save()
        return JsonResponse(
            {
                "id": comment.pk,
                "likes": comment.likes.count(),
                "dislikes": comment.dislikes.count(),
                "like": comment.likes.filter(pk=request.user.pk).exists(),
                "dislike": comment.dislikes.filter(pk=request.user.pk).exists(),
            }
        )
