import datetime

from ckeditor_uploader.fields import RichTextUploadingField
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import ValidationError


class Hub(models.Model):
    hub = models.CharField(max_length=100)

    class Meta:
        verbose_name = "хаб"
        verbose_name_plural = "хабы"

    @staticmethod
    def get_all_hubs():
        """
        Returns all hubs as dict
        """
        hubs_menu = []
        hubs = Hub.objects.all()
        for itm in hubs:
            itm_menu = {"id": itm.id, "hub": itm.hub}
            hubs_menu.append(itm_menu)
        return hubs_menu

    # для отображения названий вместо id в админке
    def __str__(self):
        return f"{self.hub}"


class Tag(models.Model):
    tag = models.CharField(max_length=100)

    class Meta:
        verbose_name = "тег"
        verbose_name_plural = "теги"


class Article(models.Model):
    # title = models.CharField(max_length=240, verbose_name="заголовок")
    title = models.TextField(verbose_name="заголовок")
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               related_name='author_article',
                               on_delete=models.CASCADE)
    hub = models.ForeignKey(Hub, verbose_name="хаб", default=False,
                            on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
    body = RichTextUploadingField()
    image = models.ImageField(
        upload_to="img_articles/", blank=True, verbose_name="главная картинка"
    )
    link_to_original = models.URLField(blank=True,
                                       verbose_name="ссылка на оригинал")

    created = models.DateTimeField(verbose_name="создана", auto_now_add=True)
    updated = models.DateTimeField(verbose_name="обновлена", auto_now=True)
    published = models.DateTimeField(
        verbose_name="дата публикации", default=timezone.now
    )

    draft = models.BooleanField(verbose_name="черновик", default=True)
    is_active = models.BooleanField(verbose_name="удалена", default=True)

    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="лайки",
        related_name="likes",
        through="LikesViewed",
        blank=True,
    )
    dislikes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="дизлайки",
        related_name="dislikes",
        through="DislikesViewed",
        blank=True,
    )
    views = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="просмотры",
        related_name="views",
        blank=True,
    )
    bookmarks = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="заметки",
        related_name="bookmarks",
        blank=True,
    )
    rating = models.IntegerField(verbose_name="рейтинг", default=0)

    class Meta:
        verbose_name = "статья"
        verbose_name_plural = "статьи"
        ordering = ("-published",)

    def __str__(self):
        return self.title

    @staticmethod
    def get_last_articles(articles_current_page):
        """
        last articles (right block) of current page articles
        """
        len_last_articles = 3
        # если статей нет
        if not articles_current_page.exclude():
            return None
        # если статей меньше 3, то изменить переменную количества
        elif articles_current_page.count() < 3:
            len_last_articles = articles_current_page.count()
        last_articles_set = articles_current_page.values("id",
                                                         "title",
                                                         "published"
                                                         )[0:len_last_articles]
        last_articles = [{} for _ in range(len_last_articles)]
        for i in range(len_last_articles):
            last_articles[i]["id"] = last_articles_set[i]["id"]
            last_articles[i]["title"] = last_articles_set[i]["title"]
            # TODO эту логику перенести на сторону клиента
            if (
                    last_articles_set[i]["published"].date()
                    != datetime.datetime.now().date()
            ):
                last_articles[i]["date"] = \
                    last_articles_set[i]["published"].date()
            else:
                last_articles[i]["date"] = "сегодня"
            last_articles[i]["time"] = \
                last_articles_set[i]["published"].strftime("%H:%M")
        return last_articles

    @staticmethod
    def get_articles():
        """
        Returns all published articles
        # and last articles (right block)
        """
        hub_articles = Article.objects.filter(draft=False, is_active=True)
        return hub_articles

    @staticmethod
    def get_search_articles(request_dict):
        ''' функция отвечает за поиск соответсвий в бд по имени и содержимого статьи '''
        search_string = request_dict.get('search')

        by_date = request_dict.get('searchdate')
        if by_date == 'month':
            fromdate = datetime.date.today() - datetime.timedelta(days=30)
        elif by_date == 'week':
            fromdate = datetime.date.today() - datetime.timedelta(days=7)
        elif by_date == 'today':
            fromdate = datetime.datetime(datetime.date.today().year,
                                         datetime.date.today().month,
                                         datetime.date.today().day)
        else:
            fromdate = None

        by_rate = request_dict.get('searchrate')
        if by_rate == 'any':
            by_rate = False

        hubs_list = request_dict.getlist('hubscheck')

        result = Article.get_articles()
        # проверяем по искомому слову
        if search_string:
            result = Article.get_articles().filter(
                Q(title__icontains=search_string) | Q(body__icontains=search_string)
            )
            if not result:
                result = Article.get_articles().filter(
                    Q(title__iexact=search_string) | Q(body__iexact=search_string)
                )
            if not result:
                result = Article.get_articles()
                search_query = search_string.lower()
                for el in result.values():
                    if search_query in el['title'].lower() or search_query in \
                            el['body'].lower():
                        pass
                    else:
                        result = result.exclude(pk=el['id'])
        # проверяем по временному интервалу
        if fromdate:
            try:
                result = result.filter(published__gte=fromdate)
            except ValidationError:
                pass
        # проверяем на положительный рейтинг
        if by_rate:
            try:
                result = result.filter(rating__gt=0)
            except (ValidationError, ValueError):
                pass
        # проверяем по указанным хабам
        if hubs_list:
            try:
                result = result.filter(hub_id__in=[item.pk for item in Hub.objects.filter(hub__in=hubs_list)])
            except (ValidationError, ValueError):
                pass
        return result

    @staticmethod
    def get_article(id_article):
        """
        Returns article
        """
        article = get_object_or_404(Article, id=id_article)
        # если удалена
        if article.is_active is False:
            article = None
        return article

    @staticmethod
    def get_annotation(word_count: int) -> tuple:
        """
        Return a dictionary, where the key is pk, and the value is the
        first 'word_count' words of the article.
        """
        annotation = []
        articles = Article.get_articles()[0]
        for article in articles:
            body_list = article.body.split(" ")[:word_count]
            itm_annotation = {
                "body": " ".join(body_list),
                "title": article.title,
                "id": article.id,
                "published": article.published,
                "username": article.author,
            }
            annotation.append(itm_annotation)

        # собипраем хабы для отображения кликабельного меню хабов
        hubs_menu = Hub.get_all_hubs()
        return annotation, hubs_menu

    @staticmethod
    def get_by_tag(tag: str):
        """
        Returns articles with the set tag
        """
        return Article.get_articles()[0].filter(tags=tag, draft=False)

    @staticmethod
    def get_by_hub(hub_id: int):
        """
        Returns articles with the set hub
        """
        return Article.get_articles().filter(hub=hub_id, draft=False)

    @staticmethod
    def get_by_author(author_pk: int, draft=None):
        """
        Returns articles with the set author
        """
        if draft is None:
            return Article.objects.filter(
                author_id__pk=author_pk).order_by("-updated")
        return (
            Article.objects.filter(author_id__pk=author_pk)
                .filter(draft=draft)
                .order_by("-updated")
        )

    @staticmethod
    def get_bookmarks(id_user):
        objects = Article.bookmarks.through.objects.filter(
            habruser_id=id_user,
            article_id__is_active=True  # удалённые и забаненные не показывать
        )
        bookmarks = []
        for i in objects:
            bookmarks.append(Article.get_article(i.article_id))
        return bookmarks

    @staticmethod
    def del_article(id_article):
        """
        delete(is_active = False) article
        """
        art = Article.objects.get(id=id_article)
        art.is_active = False
        art.save()

    @staticmethod
    def draft_article(id_article):
        """
        turn draft article(True/False)
        """
        art = Article.objects.get(id=id_article)
        if art.draft is False:
            art.draft = True
        else:
            art.draft = False
        art.save()



class LikesViewed(models.Model):
    """
    Расширение промежуточной таблицы дополнением
    поля просмотра уведомления
     """
    article = models.ForeignKey(Article,
                                on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    viewed = models.BooleanField(default=False, verbose_name='просмотрено')
    date = models.DateTimeField (verbose_name="дата", auto_now_add=True)

    def get_likes(request):
        result = LikesViewed.objects.filter(user = request.user)
        return result

class DislikesViewed(models.Model):
    """
    Расширение промежуточной таблицы дополнением
    поля просмотра уведомления
     """
    article = models.ForeignKey(Article,
                                on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    viewed = models.BooleanField(default=False, verbose_name='просмотрено')
    date = models.DateTimeField (verbose_name="дата", auto_now_add=True)



if __name__ == "__main__":
    hub = Hub(hub="development")


