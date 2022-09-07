from django.core.management.base import BaseCommand

from wagtail.models import Page


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("from_id", type=int)
        parser.add_argument("to_id", type=int)

    def handle(self, *args, **options):
        # Get pages
        from_page = Page.objects.get(id=options["from_id"])
        to_page = Page.objects.get(id=options["to_id"])

        # Move pages
        from_page.move(to_page, pos='last-child')
