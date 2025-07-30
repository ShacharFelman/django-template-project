from django.core.management.base import BaseCommand
from celery import current_app
from example.tasks import example_test_task


class ExampleOfCeleryCommand(BaseCommand):
    help = 'Example of a management command that checks Celery worker and beat status'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Checking Celery status...'))

        # Check if Celery workers are running
        try:
            inspect = current_app.control.inspect()
            stats = inspect.stats()

            if stats:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Found {len(stats)} active Celery worker(s)')
                )
                for worker, info in stats.items():
                    self.stdout.write(f'  - {worker}: {info.get("pool", {}).get("max-concurrency", "N/A")} processes')
            else:
                self.stdout.write(
                    self.style.ERROR('✗ No active Celery workers found')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error checking workers: {e}')
            )

        # Test task execution
        self.stdout.write('\nTesting example task execution...')
        try:
            result = example_test_task.delay()
            self.stdout.write(
                self.style.SUCCESS(f'✓ Example test task queued with ID: {result.task_id}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error queuing example test task: {e}')
            )

        # Check scheduled tasks
        self.stdout.write('\nChecking scheduled tasks...')
        try:
            scheduled = inspect.scheduled()
            if scheduled:
                for worker, tasks in scheduled.items():
                    self.stdout.write(f'  - {worker}: {len(tasks)} scheduled tasks')
            else:
                self.stdout.write('  - No scheduled tasks found')
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Could not check scheduled tasks: {e}')
            )

        # Check registered tasks
        self.stdout.write('\nChecking registered tasks...')
        try:
            registered = inspect.registered()
            if registered:
                for worker, tasks in registered.items():
                    self.stdout.write(f'  - {worker}: {len(tasks)} registered tasks')
                    # Show some example tasks
                    example_tasks = [task for task in tasks if 'example' in task]
                    if example_tasks:
                        self.stdout.write(f'    Example tasks: {", ".join(example_tasks[:3])}')
            else:
                self.stdout.write('  - No registered tasks found')
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Could not check registered tasks: {e}')
            ) 