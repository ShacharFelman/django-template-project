from django.db import models
from django.conf import settings


class ExampleOfSummary(models.Model):
    """Example of a model with async status tracking and relationships."""

    SUMMARY_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    example_item = models.ForeignKey(
        'ExampleOfArticle',
        on_delete=models.CASCADE,
        related_name='summaries',
        help_text="The example item being processed"
    )

    summary_text = models.TextField(
        blank=True,
        null=True,
        help_text="The processed summary text"
    )

    processing_model = models.CharField(
        max_length=50,
        default='example-model-v1',
        help_text="The processing model used"
    )

    status = models.CharField(
        max_length=20,
        choices=SUMMARY_STATUS_CHOICES,
        default='pending',
        help_text="Current status of the processing"
    )

    word_count = models.IntegerField(
        blank=True,
        null=True,
        help_text="Number of words in the summary"
    )

    processing_cost = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        blank=True,
        null=True,
        help_text="Cost of processing in credits"
    )

    error_message = models.TextField(
        blank=True,
        null=True,
        help_text="Error message if processing failed"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the processing request was created"
    )

    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the processing was completed"
    )

    # Optional: Track who requested the processing
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="User who requested the processing"
    )

    def __str__(self):
        return f"Summary for: {self.example_item.title[:50]}..."

    @property
    def is_completed(self):
        return self.status == 'completed'

    @property
    def is_failed(self):
        return self.status == 'failed'

    @property
    def is_pending(self):
        return self.status == 'pending'

    @property
    def is_in_progress(self):
        return self.status == 'in_progress'

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Example Summary"
        verbose_name_plural = "Example Summaries"
        # Prevent duplicate summaries for the same item and model
        unique_together = ['example_item', 'processing_model'] 