import datetime

from django.core.mail import send_mail
from django.db import models, transaction
from django.utils.timezone import now

from apps.articles.models import Article
from apps.authorization.models import HabrUser
from apps.comments.models import Comment
from habr import settings


class Moderator(models.Model):
    """Модератор"""
    staff = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name = "модератор"
        verbose_name_plural = "модераторы"

    @staticmethod
    def is_moderator(id_user: int) -> bool:
        """Проверка юзера явлляется ли он модератором"""
        return Moderator.objects.filter(staff=id_user).exists()


class BannedUser(models.Model):
    """Забаненный пользователь"""
    offender = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 on_delete=models.DO_NOTHING)
    date_ban = models.DateField(auto_now_add=True,
                                verbose_name='дата блокировки')
    is_forever = models.BooleanField(default=False,
                                     verbose_name='Блокировка навсегда')
    num_days = models.IntegerField(verbose_name='дней блокировки',
                                   blank=True, default=0)
    is_active = models.BooleanField(default=False)
    reason = models.TextField(verbose_name='причина блокировки')

    class Meta:
        verbose_name = "нарушитель"
        verbose_name_plural = "нарушители"
        ordering = ('-date_ban',)

    def get_remaining_days(self):
        remaining_days = None
        if not self.is_forever:
            num_days = self.num_days
            date_ban = self.date_ban
            end_date = date_ban + datetime.timedelta(days=num_days)
            current_date = datetime.date.today()
            remaining_days = (end_date - current_date).days
            if remaining_days <= 0:
                self.is_active = False
                self.save()
                self.unset_ban_email()
        return remaining_days

    def delete(self):
        self.is_active = False
        self.save()

    def set_ban_email(self):
        """
        Функция отправляет письмо с оповещением о блокировке аккаунта.
        """
        user = HabrUser.objects.get(username=self.offender)
        subject = f'Блокировка пользователя {user.username}'
        message = f'Здравствуйте!\nВаш аккаунт был заблокирован' \
                  f' {"навсегда" if self.is_forever else f"на {self.num_days} дней"}\n' \
                  f'по причине: {self.reason}\n' \
                  f'Есть жалобы и замечания? Отправляйте их по адресу: sputnik-seven@yandex.ru'
        return send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)

    def unset_ban_email(self):
        """
        Функция отправляет письмо с оповещением о снятии бана.
        """
        user = HabrUser.objects.get(username=self.offender)
        subject = f'Снятие блокировки пользователя {user.username}'
        message = 'Здравствуйте!\nСрок блокировки вашего аккаунта истёк, доступ к нему вновь разрешён.'
        return send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)


class ComplainToComment(models.Model):
    """Жалоба на комментарий"""
    comment = models.ForeignKey(Comment, related_name="related_comment",
                                on_delete=models.DO_NOTHING)
    status = models.BooleanField(null=True,
                                 verbose_name="статус проверки",
                                 help_text="None - комментарий в процессе "
                                           "проверки,True - одобрение(бан) "
                                           "комментария,"
                                           " False - отказ(оставить)")
    text_complain = models.TextField(blank=False,
                                     verbose_name="Текст жалобы")
    text_reason = models.TextField(default=False,
                                   verbose_name="Текст причины бана")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name="Пожаловался",
                             on_delete=models.DO_NOTHING)
    created = models.DateTimeField(verbose_name="дата", auto_now_add=True)

    @staticmethod
    def send_complain_to_comment(id_comment, text, id_user):
        """отправка комментария на модерацию"""
        if not ComplainToComment.objects.filter(comment=id_comment,
                                                status=None).exists():
            ComplainToComment.objects.create(
                comment=Comment.objects.get(id=id_comment),
                status=None,
                text_complain=text,
                user=HabrUser.objects.get(id=id_user)
            )

    @staticmethod
    def get_all_complaints():
        return ComplainToComment.objects.filter(status=None)

    @staticmethod
    def get_complaints_of_article(id_article):
        """жалобы на комментарии текущей статьи"""

        return ComplainToComment.objects.filter(status=None,
                                                comment__article=id_article)

    @staticmethod
    def allow_comment(id_complain):
        """отклонить жалобу"""
        if ComplainToComment.objects.filter(id=id_complain).exists():
            ComplainToComment.objects.filter(id=id_complain) \
                .delete()

    @staticmethod
    @transaction.atomic()
    def reject_comment(id_complain):
        """забанить"""
        if ComplainToComment.objects.filter(id=id_complain).exists():
            ComplainToComment.objects.filter(id=id_complain) \
                .update(status=True)
            Comment.objects.filter(related_comment=id_complain) \
                .update(is_active=False)

    class Meta:
        verbose_name = "Жалоба на комментарий"
        verbose_name_plural = "Жалобы на  комментарии"


class ComplainToArticle(models.Model):
    """Жалоба на статью"""
    article = models.ForeignKey(Article, help_text="удалённая статья",
                                related_name="ban_article",
                                on_delete=models.CASCADE)
    status = models.BooleanField(null=True,
                                 verbose_name="статус проверки",
                                 help_text="None - статьи в процессе "
                                           "проверки,True - одобрение(бан) "
                                           "статьи, False - отказ(оставить)")
    text_complain = models.TextField(blank=False,
                                     verbose_name="Текст жалобы")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name="Пожаловался",
                             on_delete=models.DO_NOTHING)
    created = models.DateTimeField(verbose_name="дата", auto_now_add=True)

    @staticmethod
    def send_complain_to_article(id_article, text, id_user):
        """отправка жалобы на модерацию"""
        if not ComplainToArticle.objects.filter(article=id_article,
                                                status=None).exists():
            ComplainToArticle.objects.create(
                article=Article.objects.get(id=id_article),
                status=None,
                text_complain=text,
                user=HabrUser.objects.get(id=id_user)
            )

    @staticmethod
    def get_all_complaints():
        return ComplainToArticle.objects.filter(status=None)

    @staticmethod
    def allow_article(id_complain):
        """отклонить жалобу"""
        if ComplainToArticle.objects.filter(id=id_complain).exists():
            ComplainToArticle.objects.filter(id=id_complain) \
                .update(status=False)

    @staticmethod
    @transaction.atomic()
    def reject_article(id_complain):
        """забанить"""
        if ComplainToArticle.objects.filter(id=id_complain).exists():
            ComplainToArticle.objects.filter(id=id_complain) \
                .update(status=True)
            Article.objects.filter(ban_article=id_complain) \
                .update(is_active=False)

    class Meta:
        verbose_name = "Жалоба на статью"
        verbose_name_plural = "Жалобы на статьи"

    @staticmethod
    def article_is_complained(id_article):
        """Возвращает жалобу или False"""
        complain = False
        if ComplainToArticle.objects.filter(article_id=id_article,
                                            status=None).exists():
            complain = ComplainToArticle.objects.get(article_id=id_article,
                                                     status=None)
        return complain


class VerifyArticle(models.Model):
    """Проверка статьи модератором"""
    verification = models.ForeignKey(Article, help_text="статья на модерацию",
                                     on_delete=models.DO_NOTHING,
                                     related_name="verification_article")
    is_verified = models.BooleanField(null=True,
                                      verbose_name="статус проверки",
                                      help_text="None - статья в процессе "
                                                "проверки,True - одобрение "
                                                "статьи, False - отказ")
    remark = models.TextField(blank=False,
                              verbose_name="Замечание модератора")
    fixed = models.BooleanField(default=False,
                                help_text="автор исправил статью")

    @staticmethod
    @transaction.atomic
    def send_article_to_verify(pk_article, pk_author):
        """отправка статьи на проверку"""
        article = Article.objects.filter(pk=pk_article, author_id=pk_author,
                                         draft=True)
        if article.exists():
            if VerifyArticle.objects.filter(
                    verification=pk_article).exists():

                send_article = VerifyArticle.objects.filter(
                    verification=Article.objects.get(id=pk_article)
                )
                send_article.update(is_verified=None)
            else:
                send_article = VerifyArticle.objects.create(
                    verification=Article.objects.get(id=pk_article)
                )
                send_article.is_verified = None
                send_article.save()

            Article.objects.filter(id=pk_article).update(updated=now())
            return True
        else:
            return None

    @staticmethod
    def get_status_verification_article(pk_article):
        """
        запрос статуса проверки текущей статьи
        """
        status = False
        if VerifyArticle.objects.filter(verification=pk_article).exists():
            is_verified = VerifyArticle.objects.get(verification=pk_article
                                                    ).is_verified
            if is_verified is None:
                status = True

        return status

    # @staticmethod
    # def get_status_verification_articles(pk_author):
    #     """
    #     запрос статуса проверки всех статей и причин отказов
    #     в публикации автора
    #     """
    #     status = []
    #     if VerifyArticle.objects.filter(
    #             verification__author_id=pk_author).exists():
    #         for itm in VerifyArticle.objects.filter(
    #                 verification__author_id=pk_author):
    #             status.append(
    #                 (itm.verification_id, itm.is_verified, itm.remark)
    #             )
    #     else:
    #         status = None
    #     return status

    @staticmethod
    def get_articles_with_statuses(pk_author, draft=None):
        """
        Формирование объекта из статьи и текущего статуса модерации
        """
        articles_with_statuses = []
        articles = Article.get_by_author(pk_author, draft)
        for article in articles:
            if VerifyArticle.objects.filter(verification=article.pk).exists():
                articles_with_statuses.append(
                    (
                        article,
                        VerifyArticle.objects.get(
                            verification=article.pk).is_verified,
                        VerifyArticle.objects.get(
                            verification=article.pk).remark)

                )
            else:
                # если статья не отправлялась на проверку и отредактирована
                articles_with_statuses.append((article, 'not_checked'))
        return articles_with_statuses

    @staticmethod
    def get_all_articles_for_verifications():
        """получение всех статей на проверку"""
        verif_articles = VerifyArticle.objects.filter(
            is_verified=None).order_by('verification__created')
        articles_to_review = []
        for itm in verif_articles:
            articles_to_review.append(itm.verification)
        return articles_to_review

    @staticmethod
    def allow_publishing(id_article):
        """Разрешение модератором публикации статьи"""
        VerifyArticle.objects.filter(
            verification=id_article).update(is_verified=True)
        Article.objects.filter(id=id_article).update(draft=False)
        Article.objects.filter(id=id_article).update(published=now(),
                                                     updated=now())

    @staticmethod
    def return_article(text_remark, id_article):
        """отправка на доработку и с обязательной причиной отказа"""
        VerifyArticle.objects.filter(verification=id_article).update(
            is_verified=False,
            remark=text_remark
        )
        Article.objects.filter(id=id_article)

    class Meta:
        verbose_name = "статья"
        verbose_name_plural = "статьи"
