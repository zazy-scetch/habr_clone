from django.conf import settings
from django import template


register = template.Library()


@register.filter(name="media_folder_users")
def media_folder_users(string):
    if str(string).startswith("http"):
        return string
    if not string:
        string = "avatars/default.jpg"
    return f"{settings.MEDIA_URL}{string}"


@register.filter(name="media_folder_images")
def media_folder_images(string):
    if str(string).startswith("http"):
        return string
    elif not string:
        string = "img_articles/default.jpg"
    return f"{settings.MEDIA_URL}{string}"


@register.filter(name="no_data_specified")
def no_data_specified(string):
    if not string:
        string = "не указано"
    return string
