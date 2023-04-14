import logging
import os
import sys

from django.core.management.base import BaseCommand
from recipes.models import Ingredient, Unit

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Use:
        python manage.py clear_table tablename <table name>
    For delete all tables use:
        python manage.py clear_table tablename all
    For help:
        python manage.py clear_table help
    """

    def add_arguments(self, parser):

        parser.add_argument('arguments', nargs='+', type=str)

    def handle(self, *args, **options):

        initialize_logger()

        if not options['arguments']:
            return
        if options['arguments'][0] == 'help':
            log_params = {__class__.__doc__}
            logger.info(
                'Справка по функции: '
                f'{log_params} '
            )
            return

        if options['arguments'][0] == 'tablename':
            if options['arguments'][1] == 'all':
                tables = [
                    'recipes_ingredient',
                    'recipes_unit',
                ]
            else:
                tables = [options['arguments'][1], ]

            for table in tables:
                self.tablename = table
                self.clear_table()
                logger.info(f'table {self.tablename} is cleared')
            return
        else:
            logger.info(__class__.__doc__)

    def clear_table(self):
        table = self.tablename

        if table == 'recipes_ingredient':
            Ingredient.objects.all().delete()
        else:
            Unit.objects.all().delete()


def initialize_logger():
    """
    Инициализурует логгер модуля приложения.
    """

    file_dir = os.path.dirname(os.path.abspath(__file__))
    file_handler = logging.FileHandler(
        filename=os.path.join(file_dir, 'main.log'),
        encoding='utf-8',
    )
    message_format = (
        '%(asctime)s : %(levelname)s'
        ' : %(name)s : LN=%(lineno)d'
        ' : pathname=%(pathname)s : %(message)s'
    )
    stdout_handler = logging.StreamHandler(stream=sys.stdout,)
    handlers = [file_handler, stdout_handler]
    formatter = logging.Formatter(
        message_format,
        '%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    stdout_handler.setFormatter(formatter)
    logging.basicConfig(
        level=logging.INFO,
        handlers=handlers,
        format=message_format,
    )
