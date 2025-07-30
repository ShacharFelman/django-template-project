from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch, MagicMock
from example.models import ExampleOfArticle, ExampleOfFetchLog, ExampleOfSummary
from example.services import ExampleOfExternalApiService, ExampleOfAiService
from django.contrib.auth import get_user_model

User = get_user_model()

class ExampleOfExternalApiServiceTest(TestCase):
    def setUp(self):
        self.service = ExampleOfExternalApiService()

    def test_service_initialization(self):
        self.assertIsNotNone(self.service.api_key)
        self.assertEqual(self.service.base_url, 'https://api.example.com/v1/data')

    @patch('example.services.ExampleOfExternalApiService._fetch_data')
    def test_fetch_and_save_success(self, mock_fetch):
        # Mock the fetch response
        mock_fetch.return_value = {
            'status': 'ok',
            'totalResults': 2,
            'items': [
                {
                    'title': 'Test Item 1',
                    'content': 'Test content 1',
                    'url': 'http://example.com/item1',
                    'publishedAt': timezone.now().isoformat(),
                    'author': 'Test Author',
                    'source': {'name': 'Test Source'},
                    'urlToImage': 'http://example.com/image1.jpg',
                    'description': 'Test description 1'
                },
                {
                    'title': 'Test Item 2',
                    'content': 'Test content 2',
                    'url': 'http://example.com/item2',
                    'publishedAt': timezone.now().isoformat(),
                    'author': 'Test Author',
                    'source': {'name': 'Test Source'},
                    'urlToImage': 'http://example.com/image2.jpg',
                    'description': 'Test description 2'
                }
            ]
        }

        result = self.service.fetch_and_save()
        
        # Check that items were created
        self.assertEqual(ExampleOfArticle.objects.count(), 2)
        self.assertEqual(result['totalResults'], 2)
        self.assertEqual(result['items_saved'], 2)

    def test_fetch_log_creation(self):
        with patch('example.services.ExampleOfExternalApiService._fetch_data') as mock_fetch:
            mock_fetch.return_value = {
                'status': 'ok',
                'totalResults': 0,
                'items': []
            }
            
            self.service.fetch_and_save()
            
            # Check that fetch log was created
            fetch_logs = ExampleOfFetchLog.objects.all()
            self.assertEqual(fetch_logs.count(), 1)
            self.assertEqual(fetch_logs[0].status, ExampleOfFetchLog.Status.SUCCESS)


class ExampleOfAiServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.article = ExampleOfArticle.objects.create(
            title="Test Article",
            content="This is a test article with some content to process.",
            url="http://example.com/test",
            published_date=timezone.now(),
            source="Test Source",
            example_source="Test Client"
        )
        self.service = ExampleOfAiService()

    def test_service_initialization(self):
        self.assertIsNotNone(self.service.ai_api_key)
        self.assertEqual(self.service.default_model, "example-model-v1")

    def test_process_item_success(self):
        summary = self.service.process_item(
            item_id=self.article.id,
            processing_model="example-model-v1",
            user=self.user,
            max_words=50
        )
        
        self.assertIsNotNone(summary)
        self.assertEqual(summary.status, "completed")
        self.assertIsNotNone(summary.summary_text)
        self.assertIsNotNone(summary.processing_cost)
        self.assertEqual(summary.example_item, self.article)

    def test_process_item_duplicate(self):
        # Process the same item twice
        summary1 = self.service.process_item(
            item_id=self.article.id,
            processing_model="example-model-v1",
            user=self.user
        )
        summary2 = self.service.process_item(
            item_id=self.article.id,
            processing_model="example-model-v1",
            user=self.user
        )
        
        # Should return the same summary
        self.assertEqual(summary1.id, summary2.id)

    def test_process_item_nonexistent(self):
        with self.assertRaises(ExampleOfArticle.DoesNotExist):
            self.service.process_item(
                item_id=99999,
                processing_model="example-model-v1",
                user=self.user
            )

    def test_get_item_summary(self):
        # Create a completed summary
        summary = ExampleOfSummary.objects.create(
            example_item=self.article,
            processing_model="example-model-v1",
            status="completed",
            summary_text="Test summary",
            word_count=5,
            processing_cost=0.005,
            requested_by=self.user
        )
        
        retrieved_summary = self.service.get_item_summary(
            item_id=self.article.id,
            processing_model="example-model-v1"
        )
        
        self.assertEqual(retrieved_summary, summary)

    def test_get_item_summaries(self):
        # Create multiple summaries
        summary1 = ExampleOfSummary.objects.create(
            example_item=self.article,
            processing_model="example-model-v1",
            status="completed",
            summary_text="Summary 1",
            requested_by=self.user
        )
        summary2 = ExampleOfSummary.objects.create(
            example_item=self.article,
            processing_model="example-model-v2",
            status="completed",
            summary_text="Summary 2",
            requested_by=self.user
        )
        
        summaries_data = self.service.get_item_summaries(item_id=self.article.id)
        
        self.assertEqual(summaries_data['item_id'], self.article.id)
        self.assertEqual(len(summaries_data['summaries']), 2) 