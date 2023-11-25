import csv

from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient, Tag

CSV_PATH_INGREDIENTS = './data/ingredients.csv'
CSV_PATH_TAGS = './data/tags.csv'


class Command(BaseCommand):
    help = 'Загружает данные об ингредиентах из csv файла в базу данных.'

    def handle(self, *args, **kwargs):
        try:
            self.load_ingredients()
            self.load_tags()
        except Exception as error:
            CommandError(error)
        print('Данные об ингредиентах и теги успешно загружены в базу данных!')

    def load_ingredients(self):
        with open(CSV_PATH_INGREDIENTS, newline='', encoding='utf-8') as file:
            ingredients = []
            for row in csv.reader(file, delimiter=','):
                ingredients.append(
                    Ingredient(name=row[0], measurement_unit=row[1])
                )
            Ingredient.objects.bulk_create(ingredients)

    def load_tags(self):
        with open(CSV_PATH_TAGS, newline='', encoding='utf-8') as file:
            tags = []
            for row in csv.reader(file, delimiter=','):
                tags.append(
                    Tag(name=row[0], color=row[1], slug=row[2])
                )
            Tag.objects.bulk_create(tags)
