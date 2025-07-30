from celery import shared_task
from django.utils import timezone
from example.models import ExampleOfSummary
from example.models import ExampleOfArticle
from example.services import ExampleOfAiService
import logging
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def example_of_async_processing_task(self, item_id, processing_model=None, user_id=None, max_words=150):
    """
    Example of a Celery task to process an item using AI/ML in the background.
    Delegates all ExampleOfSummary model handling to the service layer.
    """
    from django.contrib.auth import get_user_model
    user = None
    if user_id:
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            user = None
    try:
        service = ExampleOfAiService()
        service.process_item(
            item_id=item_id,
            processing_model=processing_model,
            user=user,
            max_words=max_words
        )
        logger.info(f"Processing completed for item {item_id}")
    except ExampleOfArticle.DoesNotExist:
        logger.error(f"Example item {item_id} not found for processing task.")
        # The service should handle status update if needed
    except Exception as e:
        logger.error(f"Error in example_of_async_processing_task for item {item_id}: {e}")
        raise self.retry(exc=e, countdown=60) 