# создание быстрых команд для выполнения частых задач ($: python manage.py make_fill_db )
# если из json файла в базу добавляется в поле с  UNIQUE=True уже имеющееся значение, то будет ошибка
import json
import os
from random import randint

from django.conf import settings
from django.core.management import BaseCommand
from mimesis import Person, Text

from apps.articles.models import Article, Hub, Tag
from apps.authorization.models import HabrUser

path_json = os.path.join(settings.BASE_DIR, "json")  # путь к json папке


def load_from_json(file_name):
    """
    :param file_name: имя необходимого json файла
    :return: выводит содержимое
    """
    with open(
        os.path.join(path_json, file_name + ".json"), "r", encoding="utf-8"
    ) as file_json:
        return json.load(file_json)


count_users = 20


def get_user(number):
    """
    Creates random user data
    :param number: number of users
    """
    for i in range(number):
        person = Person("ru")
        user = HabrUser(
            username=person.username(template="U_d"),
            email=person.email(domains=("yandex.ru", "gmail.com")),
            password=person.password(),
        )
        user.save()


count_articles = 50


def get_article():
    """
    Creates random text article
    """
    quantity = randint(200, 500)
    text = Text("ru")
    article = {
        "title": text.title(),
        "body": text.text(quantity=quantity),
        "draft": False,
    }
    return article


class Command(BaseCommand):  # свой класс унаследуем от BaseCommand
    def handle(self, *args, **options):  # с обязательным методом handle

        # users = load_from_json("authors")
        # for itm in users:
        #     # распаковка словаря соответственно модели и распред. по ключам с
        #     # одновременным сохр. в базу( .save() )
        #     HabrUser.objects.create(**itm)

        # автогенерация библиотекой mimesis
        get_user(count_users)

        tags = load_from_json("tags")
        for itm in tags:
            Tag.objects.create(tag=itm)

        hubs = load_from_json("hubs")
        for itm in hubs:
            Hub.objects.create(hub=itm)

        count_authors = HabrUser.objects.count()
        count_tags = Tag.objects.count()
        count_hubs = Hub.objects.count()

        # articles = load_from_json("test_articles")
        for itm in range(count_articles):
            #  выбираем случайные теги,хабы, авторы
            id_author = randint(1, count_authors)
            id_tag = randint(1, count_tags)
            id_hub = randint(1, count_hubs)

            # создаём и заполняем статьи
            dict_article = get_article()

            # добавляем автора
            dict_article["author"] = HabrUser.objects.get(id=id_author)

            #  пишем в таблицу
            itm_article = Article.objects.create(**dict_article)

            # (ManyToMany) добавляем отношения к тэгам и хабам
            itm_article.hub.add(Hub.objects.get(id=id_hub))
            itm_article.tags.add(Tag.objects.get(id=id_tag))
