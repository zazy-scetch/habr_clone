from django.apps import AppConfig


class CommentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.comments"


class UserArticlesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.user_articles"
