from django.core.management.base import BaseCommand
from mimesis import Person, Business, Datetime, Address

from apps.authorization.models import HabrUser, HabrUserProfile


class Command(BaseCommand):
    help = (
        "Created random article data. Format python manage.py create_article "
        "number_article First create user"
    )

    def add_arguments(self, parser):
        parser.add_argument("number", type=int, help="Количество создаваемых " "статей")

    def handle(self, *args, **options):
        """
        Creates random the article data
        """
        person = Person("ru")
        business = Business("ru")
        datetime = Datetime("ru")
        address = Address("ru")
        number = options["number"]
        for i in range(number):
            user = HabrUser(
                username=person.username(template="U_d"),
                email=person.email(domains=("yandex.ru", "gmail.com")),
                password=person.password(length=8, hashed=False),
            )
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f"Successfully created user " f"{user.username}")
            )

            profile = HabrUserProfile.objects.get(user=user)
            # profile.avatar = person.avatar(size=256)
            profile.full_name = person.full_name(gender=None, reverse=False)
            profile.place_of_work = business.company()
            profile.specialization = person.occupation()
            profile.gender = 'M' if person.gender(iso5218=False, symbol=False) == 'Муж.' else 'Ж'
            profile.birth_date = datetime.date(start=1950, end=2018)
            profile.country = address.country(allow_random=False)
            profile.region = address.region()
            profile.city = address.city()

            profile.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created " f"profile " f"{profile.full_name}"
                )
            )
