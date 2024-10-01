import csv
from typing import Any

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


def import_data():
    with open("data/ingredients.csv", encoding="utf8") as csvfile:
        reader = csv.reader(csvfile)
        reader_list = list(reader)
        objects = [
            Ingredient(name=row[0], measurement_unit=row[1])
            for row in reader_list
        ]
        Ingredient.objects.bulk_create(objects)


class Command(BaseCommand):
    help = "Import ingredients into model in DB"

    def handle(self, *args: Any, **options: Any) -> str | None:
        import_data()
        self.stdout.write(self.style.SUCCESS("Data imported succesfully"))
