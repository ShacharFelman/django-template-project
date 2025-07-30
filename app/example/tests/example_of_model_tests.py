from django.test import TestCase
from django.utils import timezone
from example.models import ExampleOfArticle, ExampleOfFetchLog, ExampleOfSummary
from django.contrib.auth import get_user_model

User = get_user_model()

class ExampleOfArticleModelTest(TestCase):
    def setUp(self):
        self.article = ExampleOfArticle.objects.create(
            title="Test Example Article",
            content="Some example content",
            url="http://example.com/article",
            published_date=timezone.now(),
            author="Example Author",
            source="Test Source",
            example_source="Test Client"
        )

    def test_str_representation(self):
        self.assertEqual(str(self.article), self.article.title)

    def test_ordering(self):
        article2 = ExampleOfArticle.objects.create(
            title="Second Example Article",
            content="More example content",
            url="http://example.com/article2",
            published_date=timezone.now() + timezone.timedelta(days=1),
            author="Example Author 2",
            source="Source 2",
            example_source="Client 2"
        )
        articles = ExampleOfArticle.objects.all()
        self.assertEqual(articles[0], article2)
        self.assertEqual(articles[1], self.article)

    def test_field_constraints(self):
        # url must be unique
        with self.assertRaises(Exception):
            ExampleOfArticle.objects.create(
                title="Duplicate URL",
                content="Content",
                url="http://example.com/article",
                published_date=timezone.now(),
                author="Author",
                source="Source",
                example_source="Client"
            )


class ExampleOfFetchLogModelTest(TestCase):
    def setUp(self):
        self.fetch_log = ExampleOfFetchLog.objects.create(
            source="Test Source",
            status=ExampleOfFetchLog.Status.PENDING,
            items_fetched=5,
            items_saved=3
        )

    def test_str_representation(self):
        expected = f"{self.fetch_log.source} - {self.fetch_log.status} - {self.fetch_log.started_at}"
        self.assertEqual(str(self.fetch_log), expected)

    def test_complete_method(self):
        self.fetch_log.complete(
            status=ExampleOfFetchLog.Status.SUCCESS,
            items_saved=4,
            error_message=""
        )
        self.assertEqual(self.fetch_log.status, ExampleOfFetchLog.Status.SUCCESS)
        self.assertEqual(self.fetch_log.items_saved, 4)
        self.assertIsNotNone(self.fetch_log.completed_at)


class ExampleOfSummaryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.article = ExampleOfArticle.objects.create(
            title="Test Article",
            content="Test content",
            url="http://example.com/test",
            published_date=timezone.now(),
            source="Test Source",
            example_source="Test Client"
        )
        self.summary = ExampleOfSummary.objects.create(
            example_item=self.article,
            processing_model="example-model-v1",
            status="pending",
            requested_by=self.user
        )

    def test_str_representation(self):
        expected = f"Summary for: {self.article.title[:50]}..."
        self.assertEqual(str(self.summary), expected)

    def test_status_properties(self):
        self.assertTrue(self.summary.is_pending)
        self.assertFalse(self.summary.is_completed)
        self.assertFalse(self.summary.is_failed)

        self.summary.status = "completed"
        self.assertTrue(self.summary.is_completed)
        self.assertFalse(self.summary.is_pending)

    def test_unique_constraint(self):
        # Should not be able to create duplicate summary for same item and model
        with self.assertRaises(Exception):
            ExampleOfSummary.objects.create(
                example_item=self.article,
                processing_model="example-model-v1",
                status="pending"
            ) 