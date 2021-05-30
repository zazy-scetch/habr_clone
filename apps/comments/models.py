from django.conf import settings
from django.db import models
import abc

from apps.articles.models import Article
from apps.authorization.models import HabrUser, HabrUserProfile


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE,
                                related_name="article")
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE)
    parent = models.ForeignKey("self", null=True, blank=True,
                               related_name="comment_parent",
                               on_delete=models.CASCADE,
                               )
    body = models.TextField(verbose_name="текст комментария")
    date = models.DateTimeField(verbose_name="дата", auto_now_add=True)
    is_active = models.BooleanField(verbose_name="удален", default=True)

    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="лайки",
        related_name="comment_likes",
        through="CommentLikesViewed",
        blank=True,
    )
    dislikes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="дизлайки",
        related_name="comment_dislikes",
        through="CommentDislikesViewed",
        blank=True,
    )
    viewed = models.BooleanField(default=False, verbose_name='просмотрено')

    def __str__(self):
        return f"{self.article.title}-{self.author.username}"

    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "комментарии"

    @staticmethod
    def create_comment(article_pk: int, comment_pk: int, username,
                       text_comment):
        try:
            parent_comment = Comment.objects.get(pk=comment_pk)
        except ValueError:
            parent_comment = None
        author = username
        article = Article.objects.get(pk=article_pk)
        comment = Comment(
            body=text_comment, article=article, author=author,
            parent=parent_comment
        )
        comment.save()

    @staticmethod
    def get_comments(article_pk):
        comments = Comment.objects.filter(
            article__pk=article_pk).order_by("date")
        return comments

    @staticmethod
    def get_comment(parent_id):
        """ получение родительского комментария """
        comment = Comment.objects.get(id=parent_id)
        return comment

    @staticmethod
    def get_all_comments_hub(pk):
        articles = Article.get_articles().filter(hub=pk, draft=False)

    @staticmethod
    def get_liked_comments_by_user(id_comment, id_user):
        """Проверка всех комментариев, на лайк от пользователя(для отметки
        в шаблоне, что текущий юзер уже лайкнул комментарий)"""
        liked_comments = []
        for itm in LikesCommentViewed.objects.filter(user=id_user):
            liked_comments.append(itm.comment.id)
        return liked_comments

    @staticmethod
    def get_disliked_comments_by_user(id_comment, id_user):
        """Проверка всех комментариев, на дизлайк от пользователя(для отметки
        в шаблоне, что текущий юзер уже дизлайкнул комментарий)"""
        disliked_comments = []
        for itm in DislikesCommentViewed.objects.filter(user=id_user):
            disliked_comments.append(itm.comment.id)
        return disliked_comments

class LikesCommentViewed(models.Model):
    """
    Расширение промежуточной таблицы дополнением
    поля просмотра уведомления
     """
    comment = models.ForeignKey(Comment,
                                on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    viewed = models.BooleanField(default=False, verbose_name='просмотрено')


class DislikesCommentViewed(models.Model):
    """
    Расширение промежуточной таблицы дополнением
    поля просмотра уведомления
     """
    comment = models.ForeignKey(Comment,
                                on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                            on_delete=models.CASCADE)
    viewed = models.BooleanField(default=False, verbose_name='просмотрено')


class Sorted(abc.ABC):
    ''' класс отвечает за сортировку  '''

    @abc.abstractclassmethod
    def get_data(self, pk=None):
        pass

    @staticmethod
    def sort(sort_type, pk=None, search_query=None, user=None):
        if user:
            TYPE = {
                '-date': SortDateUser,
                'like': SortLikeUser,
                'view': SortViewUser,
                'comments': SortCommentsUser,
            }
            return TYPE[sort_type](user)
        elif pk:
            TYPE = {
                '-date': SortDateHub,
                'like': SortLikeHub,
                'view': SortViewHub,
                'comments': SortCommentsHub,
            }
            return TYPE[sort_type](pk)
        elif search_query:
            TYPE = {
                '-date': SortDateSearch,
                'like': SortLikeSearch,
                'view': SortViewSearch,
                'comments': SortCommentsSearch,
            }
            return TYPE[sort_type](search_query)
        else:
            TYPE = {
                '-date': SortDate,
                'like': SortLike,
                'view': SortView,
                'comments': SortComments,
            }
            return TYPE[sort_type]()


class SortDate(Sorted):

    def get_data(self):
        return Article.objects.filter(draft=False).order_by('-updated')


class SortLike(Sorted):

    def get_data(self):
        return Article.objects.filter(draft=False).order_by('-rating')


class SortView(Sorted):

    def get_data(self):
        articles = Article.objects.filter(draft=False)
        result = sorted(articles, key=lambda x: x.views.count(), reverse=True)
        return result


class SortComments(Sorted):

    def get_data(self):
        comments = {}
        articles = Article.objects.filter(draft=False)
        for article in articles:
            current_comments = Comment.get_comments(article.id)
            comments[article] = current_comments.count()
        comments = sorted(comments.items(), key=lambda x: x[1], reverse=True)
        result = [i[0] for i in comments]
        return result


class SortDateHub(Sorted):

    def __init__(self, pk):
        self.pk = pk

    def get_data(self):
        return Article.objects.filter(hub=self.pk, draft=False).order_by('-updated')


class SortLikeHub(Sorted):

    def __init__(self, pk):
        self.pk = pk

    def get_data(self):
        return Article.objects.filter(hub=self.pk, draft=False).order_by('-rating')


class SortViewHub(Sorted):

    def __init__(self, pk):
        self.pk = pk

    def get_data(self):
        articles = Article.objects.filter(hub=self.pk, draft=False)
        result = sorted(articles, key=lambda x: x.views.count(), reverse=True)
        return result


class SortCommentsHub(Sorted):

    def __init__(self, pk):
        self.pk = pk

    def get_data(self):
        comments = {}
        articles = Article.objects.filter(hub=self.pk, draft=False)
        for article in articles:
            current_comments = Comment.get_comments(article.id)
            comments[article] = current_comments.count()
        comments = sorted(comments.items(), key=lambda x: x[1], reverse=True)
        result = [i[0] for i in comments]
        return result


class SortDateSearch(Sorted):

    def __init__(self, search_query):
        self.search_query = search_query

    def get_data(self):
        return self.search_query.order_by('-updated')


class SortLikeSearch(Sorted):

    def __init__(self, search_query):
        self.search_query = search_query

    def get_data(self):
        return self.search_query.order_by('-rating')


class SortViewSearch(Sorted):

    def __init__(self, search_query):
        self.search_query = search_query

    def get_data(self):
        result = sorted(self.search_query, key=lambda x: x.views.count(), reverse=True)
        return result


class SortCommentsSearch(Sorted):

    def __init__(self, search_query):
        self.search_query = search_query

    def get_data(self):
        comments = {}
        for article in self.search_query:
            current_comments = Comment.get_comments(article.id)
            comments[article] = current_comments.count()
        comments = sorted(comments.items(), key=lambda x: x[1], reverse=True)
        result = [i[0] for i in comments]
        return result


class SortDateUser(Sorted):

    def __init__(self, user):
        self.user = user

    def get_data(self):
        return Article.objects.filter(author=self.user, draft=False).order_by('-updated')


class SortLikeUser(Sorted):

    def __init__(self, user):
        self.user = user

    def get_data(self):
        return Article.objects.filter(author=self.user, draft=False).order_by('-rating')


class SortViewUser(Sorted):

    def __init__(self, user):
        self.user = user

    def get_data(self):
        articles = Article.objects.filter(author=self.user, draft=False)
        result = sorted(articles, key=lambda x: x.views.count(), reverse=True)
        return result


class SortCommentsUser(Sorted):

    def __init__(self, user):
        self.user = user

    def get_data(self):
        comments = {}
        articles = Article.objects.filter(author=self.user, draft=False)
        for article in articles:
            current_comments = Comment.get_comments(article.id)
            comments[article] = current_comments.count()
        comments = sorted(comments.items(), key=lambda x: x[1], reverse=True)
        result = [i[0] for i in comments]
        return result

class CommentLikesViewed(models.Model):
    '''Промежуточная таблица с добавлением
    поля просомтренных лайков комментариев'''
    comment = models.ForeignKey (Comment,
                                 on_delete=models.CASCADE)
    user = models.ForeignKey (settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE)
    viewed = models.BooleanField (default=False, verbose_name='просмотрено')
    date = models.DateTimeField (verbose_name="дата", auto_now_add=True)

class CommentDislikesViewed(models.Model):
    '''Промежуточная таблица с добавлением
    поля просомтренных дизлайков комментариев'''
    comment = models.ForeignKey (Comment,
                                 on_delete=models.CASCADE)
    user = models.ForeignKey (settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE)
    viewed = models.BooleanField (default=False, verbose_name='просмотрено')
    date = models.DateTimeField (verbose_name="дата", auto_now_add=True)