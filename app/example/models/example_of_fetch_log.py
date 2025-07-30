"""Example of a logging model with status tracking."""
from django.db import models
from django.utils import timezone


class ExampleOfFetchLog(models.Model):
    """Example of a logging model with status tracking and metadata."""

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        SUCCESS = 'SUCCESS', 'Success'
        ERROR = 'ERROR', 'Error'

    source = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="The example source used for this operation"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        help_text="Current status of the operation"
    )
    started_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the operation started"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the operation completed"
    )
    items_fetched = models.IntegerField(
        default=0,
        help_text="Number of items fetched from the source"
    )
    items_saved = models.IntegerField(
        default=0,
        help_text="Number of items successfully saved"
    )
    error_message = models.TextField(
        blank=True,
        help_text="Error message if the operation failed"
    )
    query_params = models.JSONField(
        default=dict,
        help_text="Parameters used for the operation"
    )
    metadata = models.JSONField(
        default=dict,
        help_text="Additional metadata about the operation"
    )
    raw_data_file = models.CharField(
        max_length=255,
        blank=True,
        help_text="Path to the raw JSON data file"
    )

    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['status', '-started_at']),
        ]
        verbose_name = "Example Fetch Log"
        verbose_name_plural = "Example Fetch Logs"

    def __str__(self):
        return f"{self.source if self.source else 'Unknown'} - {self.status} - {self.started_at}"

    def complete(self, status: Status, **kwargs):
        """Mark the operation as complete with additional data."""
        self.status = status
        self.completed_at = timezone.now()

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        self.save() 