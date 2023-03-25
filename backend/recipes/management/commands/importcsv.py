import csv

from django.core.management import BaseCommand
from django.utils import timezone
from recipes.models import Ingredient


class Command(BaseCommand):
    """Загружает модели в базу данных из файла CSV.\n
    Текст команды:
    'python manage.py importcsv D:/Dev/foodgram-project-react/data/
    (ваш путь к папке с файлами CSV)'
    """

    def add_arguments(self, parser):
        parser.add_argument("csv_folder_path", type=str)

    def handle(self, *args, **options):
        start_time = timezone.now()
        folder_path = options["csv_folder_path"]

        # Импортируем ингредиенты
        with open(
            f'{folder_path}ingredients.csv', "r", encoding='utf-8'
        ) as csv_file:
            data = list(csv.reader(csv_file, delimiter=","))
            for row in data[:]:
                Ingredient.objects.create(
                    name=row[0],
                    measurement_unit=row[1]
                )

        self.stdout.write(
            self.style.SUCCESS("Sucess importing ingredients.csv.")
        )

        end_time = timezone.now()
        self.stdout.write(
            self.style.SUCCESS(
                f"Loading CSV took: {(end_time-start_time).total_seconds()}"
                " seconds."
            )
        )
