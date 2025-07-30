from celery import shared_task
from django.utils import timezone
from django.db import transaction
from example.services import ExampleOfExternalApiService, ExampleServiceError
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def example_of_periodic_fetch_task(self, query_params=None):
    """
    Example of a Celery task to fetch data from external API and save to database.
    This task will run periodically based on the schedule defined in celery.py
    """
    start_time = timezone.now()

    try:
        logger.info("Starting periodic example fetch task")

        # Initialize the service
        service = ExampleOfExternalApiService()

        # Fetch and save items
        result = service.fetch_and_save(query_params)
        items_fetched = result.get('totalResults', 0)

        logger.info(f"Successfully completed example fetch task. Total items: {items_fetched}")

        return {
            'status': 'success',
            'items_count': items_fetched,
            'fetch_time': start_time.isoformat()
        }

    except ExampleServiceError as e:
        error_msg = f"Service error: {str(e)}"
        logger.error(error_msg)

        # Retry the task
        try:
            raise self.retry(countdown=60, exc=e)
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for example fetch task: {error_msg}")
            return {
                'status': 'failed',
                'error': error_msg,
                'fetch_time': start_time.isoformat()
            }

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)

        # Retry the task
        try:
            raise self.retry(countdown=60, exc=e)
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for example fetch task: {error_msg}")
            return {
                'status': 'failed',
                'error': error_msg,
                'fetch_time': start_time.isoformat()
            }

@shared_task
def example_test_task():
    """Example test task to verify Celery is working correctly."""
    logger.info("Example test task executed successfully")
    return "Example test task completed" 