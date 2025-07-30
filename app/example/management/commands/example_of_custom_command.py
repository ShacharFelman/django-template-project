from django.core.management.base import BaseCommand
from example.tasks import example_of_periodic_fetch_task


class ExampleOfCustomCommand(BaseCommand):
    help = 'Example of a custom management command that triggers periodic tasks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--async',
            action='store_true',
            help='Run the task asynchronously through Celery'
        )
        parser.add_argument(
            '--source',
            type=str,
            default='example',
            help='Source to fetch data from (default: example)'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting example fetch...'))

        # Example query parameters
        query_params = {
            'source': options['source'],
            'category': 'example',
            'limit': 10
        }

        if options['async']:
            # Run through Celery
            result = example_of_periodic_fetch_task.delay(query_params)
            self.stdout.write(
                self.style.SUCCESS(f'Task queued with ID: {result.task_id}')
            )
        else:
            # Run synchronously
            result = example_of_periodic_fetch_task(query_params)
            self.stdout.write(
                self.style.SUCCESS(f'Task completed: {result}')
            ) 