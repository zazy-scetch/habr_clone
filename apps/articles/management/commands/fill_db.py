import os

from django.core.management import BaseCommand


class Command(BaseCommand):

    help = "Наполняем базу данных"

    def add_arguments(self, parser):
        parser.add_argument(
            "num_users", type=int, help="Количество создаваемых пользователей"
        )

        parser.add_argument(
            "num_articles",
            type=int,
            help="Количество создаваемых статей",
        )

    def handle(self, *args, **options):
        num_users = options["num_users"]
        num_articles = options["num_articles"]

        os.system(f"python3 manage.py create_user {num_users}")
        os.system(f"python3 manage.py create_article {num_articles}")
