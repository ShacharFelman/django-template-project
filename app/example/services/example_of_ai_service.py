import logging
import os
from typing import Dict, Optional
from django.conf import settings
from django.utils import timezone

from example.models import ExampleOfSummary, ExampleOfArticle

logger = logging.getLogger(__name__)

class ExampleOfAiService:
    """Example of a service for AI/ML processing using external models."""

    def __init__(self):
        # Prepare model mapping for future flexibility
        self.model_map = {
            "example-model-v1": "example-model-v1",
            "example-model-v2": "example-model-v2",
            "example-model-pro": "example-model-pro",
            "example-model-lite": "example-model-lite",
        }
        self.default_model = "example-model-v1"
        self.ai_api_key = os.environ.get("EXAMPLE_AI_API_KEY", "example-ai-key")

        if not self.ai_api_key:
            raise ValueError("EXAMPLE_AI_API_KEY must be set in Django settings")

    def _get_ai_client(self, model_name: str = None):
        """Example of getting an AI client for processing."""
        model = self.model_map.get(model_name, self.default_model)
        # In real implementation, this would return an actual AI client
        # For example purposes, we'll return a mock client
        return {
            'model': model,
            'api_key': self.ai_api_key,
            'temperature': 0.3,
        }

    def process_item(
        self,
        item_id: int,
        processing_model: str = None,
        user=None,
        max_words: int = 150,
    ) -> ExampleOfSummary:
        """
        Process an item using AI/ML.
        """
        try:
            item = ExampleOfArticle.objects.get(id=item_id)
            model_key = processing_model or self.default_model

            # Check for existing completed summary
            summary = (
                ExampleOfSummary.objects.filter(example_item=item, processing_model=model_key, status="completed").first()
            )

            if summary:
                logger.info(f"Processing summary exists for item {item_id}")
                return summary

            # Create or reuse a summary record
            summary, _ = ExampleOfSummary.objects.get_or_create(
                example_item=item,
                processing_model=model_key,
                defaults={"status": "pending", "requested_by": user},
            )

            # Generate summary using AI service
            summary_text, processing_cost = self._generate_summary(
                title=item.title,
                content=item.content,
                processing_model=model_key,
                max_words=max_words,
            )
            logger.info(f"Processing item {item_id} with model {model_key}")

            # Save result
            summary.summary_text = summary_text
            summary.processing_cost = processing_cost
            summary.word_count = len(summary_text.split())
            summary.status = "completed"
            summary.completed_at = timezone.now()
            summary.save()
            return summary

        except ExampleOfArticle.DoesNotExist:
            logger.error(f"Example item {item_id} not found")
            raise
        except Exception as e:
            logger.error(f"Error processing item {item_id}: {e}")
            if "summary" in locals():
                summary.status = "failed"
                summary.error_message = str(e)
                summary.save()
            raise

    def _generate_summary(
        self,
        title: str,
        content: str,
        processing_model: str,
        max_words: int,
    ) -> tuple[str, float]:
        """Example of AI/ML processing for summarization."""
        ai_client = self._get_ai_client(processing_model)
        
        # Simulate AI processing for example purposes
        # In real implementation, this would call an actual AI service
        summary_text = f"This is an example summary of '{title}' with approximately {max_words} words. The content has been processed using {processing_model}."
        
        # Simulate processing cost (in credits)
        processing_cost = 0.001 * len(content.split())  # 0.001 credits per word

        return summary_text.strip(), processing_cost

    def process_item_async(self, item_id: int, processing_model: str = None, user=None, max_words: int = 150) -> ExampleOfSummary:
        """
        Asynchronously process an item by enqueuing a Celery task.
        Returns the ExampleOfSummary object (status will be 'pending' or 'in_progress').
        """
        model_key = processing_model or self.default_model
        # Ensure the item exists, or raise ExampleOfArticle.DoesNotExist
        try:
            item = ExampleOfArticle.objects.get(id=item_id)
        except ExampleOfArticle.DoesNotExist:
            logger.error(f"Example item {item_id} not found (async)")
            raise
        # Check for existing completed summary
        summary = ExampleOfSummary.objects.filter(example_item=item, processing_model=model_key, status="completed").first()
        if summary:
            return summary
        summary, created = ExampleOfSummary.objects.get_or_create(
            example_item=item,
            processing_model=model_key,
            defaults={
                'status': 'pending',
                'requested_by': user
            }
        )
        # If already being processed or completed, return existing summary
        if not created and summary.status in ['pending', 'in_progress', 'completed']:
            return summary
        from example.tasks import example_of_async_processing_task
        example_of_async_processing_task.delay(item_id, model_key, user.id if user else None, max_words)
        return summary

    def get_item_summary(self, item_id: int, processing_model: str = None) -> Optional[ExampleOfSummary]:
        model_key = processing_model or self.default_model
        return ExampleOfSummary.objects.filter(
            example_item_id=item_id,
            processing_model=model_key,
            status="completed"
        ).first()

    def get_item_summaries(self, item_id: int) -> Dict:
        summaries = ExampleOfSummary.objects.filter(example_item_id=item_id)
        return {
            "item_id": item_id,
            "summaries": [
                {
                    "id": s.id,
                    "processing_model": s.processing_model,
                    "status": s.status,
                    "summary_text": s.summary_text,
                    "word_count": s.word_count,
                    "processing_cost": s.processing_cost,
                    "created_at": s.created_at,
                    "completed_at": s.completed_at,
                    "error_message": s.error_message,
                }
                for s in summaries
            ],
        } 