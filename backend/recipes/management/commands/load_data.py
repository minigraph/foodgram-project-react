import json
import logging
import os
import sys

import api.v1.serializers as api_serializers
from django.conf import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):

        initialize_logger()

        DATA_DIR = os.path.join(
            os.path.join(settings.BASE_DIR, os.pardir),
            "data"
        )

        files = os.listdir(DATA_DIR)

        logger.info(
            'files to load:'
            f'[{[file for file in files]}]'
        )

        parameters = {
            'IngredientSerializer':
                {
                    'class': api_serializers.IngredientSerializer,
                    'file_name': 'ingredients.json',
                },
        }

        for key, value in parameters.items():
            class_name = key
            file_path = os.path.join(DATA_DIR, value['file_name'])
            class_obj = value['class']
            logger.info(
                '----------------------------\n'
                f'loading file ... {file_path}'
            )
            params = {
                class_name: {
                    'class': class_obj,
                    'file_path': file_path,
                }
            }
            parameters[class_name] = {
                'class': class_obj,
                'file_path': file_path,
            }
            self.err = False
            self.load_from_json(**params)
            if not self.err:
                logger.info('OK')

    def load_from_json(self, **kvargs):

        for key, val in kvargs.items():
            class_params = kvargs[key]
            class_obj = class_params['class']
            file_path = class_params['file_path']

            with open(file_path, encoding="utf-8") as csv_file:
                try:
                    json_list = json.load(csv_file)
                    all_units = set().union(
                        list(d['measurement_unit'] for d in json_list)
                    )
                    list_units = [{'name': name} for name in all_units]
                    serializer_units = api_serializers.UnitSerializer(
                        data=list_units, many=True
                    )
                    if serializer_units.is_valid():
                        serializer_units.save()
                    else:
                        logger.error(
                            f'serializer error:\n {serializer_units.errors}'
                        )
                        continue

                    serializer = class_obj(data=json_list, many=True)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        logger.error(
                            f'serializer error:\n {serializer.errors}'
                        )
                except Exception as e:
                    self.err = True
                    logger.error(
                        f'error while data loading, see below:\n {e}'
                    )
                    raise


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
