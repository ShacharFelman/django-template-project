from django.test import TestCase
from django.utils import timezone
from example.models import ExampleOfArticle, ExampleOfFetchLog, ExampleOfSummary
from example.serializers import (
    ExampleOfCustomValidationSerializer,
    ExampleOfReadonlySerializer,
    ExampleOfModelSerializer
)
from django.contrib.auth import get_user_model

User = get_user_model()

class ExampleOfCustomValidationSerializerTest(TestCase):
    def setUp(self):
        self.article_data = {
            'title': 'Test Article',
            'content': 'Test content',
            'url': 'http://example.com/test',
            'published_date': timezone.now(),
            'author': 'Test Author',
            'source': 'Test Source',
            'example_source': 'Test Client'
        }

    def test_valid_data(self):
        serializer = ExampleOfCustomValidationSerializer(data=self.article_data)
        self.assertTrue(serializer.is_valid())

    def test_future_date_validation(self):
        self.article_data['published_date'] = timezone.now() + timezone.timedelta(days=1)
        serializer = ExampleOfCustomValidationSerializer(data=self.article_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('published_date', serializer.errors)

    def test_title_validation(self):
        self.article_data['title'] = 'ab'  # Too short
        serializer = ExampleOfCustomValidationSerializer(data=self.article_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)

    def test_title_stripping(self):
        self.article_data['title'] = '  Test Title  '
        serializer = ExampleOfCustomValidationSerializer(data=self.article_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['title'], 'Test Title')


class ExampleOfReadonlySerializerTest(TestCase):
    def setUp(self):
        self.fetch_log = ExampleOfFetchLog.objects.create(
            source="Test Source",
            status=ExampleOfFetchLog.Status.SUCCESS,
            items_fetched=10,
            items_saved=8,
            started_at=timezone.now() - timezone.timedelta(minutes=5),
            completed_at=timezone.now()
        )

    def test_serializer_fields(self):
        serializer = ExampleOfReadonlySerializer(self.fetch_log)
        data = serializer.data
        
        self.assertIn('source', data)
        self.assertIn('status', data)
        self.assertIn('duration', data)
        self.assertIn('success_rate', data)

    def test_duration_calculation(self):
        serializer = ExampleOfReadonlySerializer(self.fetch_log)
        duration = serializer.data['duration']
        self.assertIsNotNone(duration)
        self.assertGreater(duration, 0)

    def test_success_rate_calculation(self):
        serializer = ExampleOfReadonlySerializer(self.fetch_log)
        success_rate = serializer.data['success_rate']
        self.assertEqual(success_rate, 80.0)  # 8/10 * 100

    def test_success_rate_zero_items(self):
        self.fetch_log.items_fetched = 0
        self.fetch_log.save()
        serializer = ExampleOfReadonlySerializer(self.fetch_log)
        success_rate = serializer.data['success_rate']
        self.assertEqual(success_rate, 0.0)


class ExampleOfModelSerializerTest(TestCase):
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
            status="completed",
            summary_text="Test summary",
            word_count=5,
            processing_cost=0.005,
            requested_by=self.user
        )

    def test_serializer_fields(self):
        serializer = ExampleOfModelSerializer(self.summary)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('processing_model', data)
        self.assertIn('status', data)
        self.assertIn('summary_text', data)
        self.assertIn('word_count', data)
        self.assertIn('processing_cost', data)
        self.assertIn('created_at', data)

    def test_readonly_fields(self):
        serializer = ExampleOfModelSerializer(self.summary)
        data = serializer.data
        
        # All fields should be readonly
        self.assertIn('id', data)
        self.assertIn('created_at', data)
        self.assertIn('completed_at', data) 