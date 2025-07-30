from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from example.models import ExampleOfArticle, ExampleOfFetchLog, ExampleOfSummary
from example.services import ExampleOfExternalApiService, ExampleOfAiService
from unittest.mock import patch
from django.utils import timezone

User = get_user_model()

class ExampleOfIntegrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True,
            is_superuser=True
        )
        
        # Create test article
        self.article = ExampleOfArticle.objects.create(
            title="Test Article",
            content="This is a test article with some content to process.",
            url="http://example.com/test",
            published_date=timezone.now(),
            source="Test Source",
            example_source="Test Client"
        )

    def test_full_workflow(self):
        """Test the complete workflow from API to processing."""
        
        # 1. Test external API service
        with patch('example.services.ExampleOfExternalApiService._fetch_data') as mock_fetch:
            mock_fetch.return_value = {
                'status': 'ok',
                'totalResults': 1,
                'items': [{
                    'title': 'API Test Item',
                    'content': 'API test content',
                    'url': 'http://example.com/api-test',
                    'publishedAt': timezone.now().isoformat(),
                    'author': 'API Author',
                    'source': {'name': 'API Source'},
                    'urlToImage': 'http://example.com/api-image.jpg',
                    'description': 'API test description'
                }]
            }
            
            service = ExampleOfExternalApiService()
            result = service.fetch_and_save()
            
            self.assertEqual(result['items_saved'], 1)
            self.assertEqual(ExampleOfArticle.objects.count(), 2)  # Original + new

        # 2. Test AI processing service
        ai_service = ExampleOfAiService()
        summary = ai_service.process_item(
            item_id=self.article.id,
            processing_model="example-model-v1",
            user=self.user
        )
        
        self.assertEqual(summary.status, "completed")
        self.assertIsNotNone(summary.summary_text)

        # 3. Test API endpoints
        self.client.force_authenticate(user=self.admin_user)
        
        # Test CRUD endpoint
        response = self.client.get(reverse('example-item-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

        # Test service endpoint
        response = self.client.post(reverse('example-fetch'), {
            'query_params': {'source': 'test'}
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test async processing endpoint
        response = self.client.post(reverse('example-process'), {
            'item_id': self.article.id,
            'processing_model': 'example-model-v1'
        })
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_api_authentication(self):
        """Test API authentication and permissions."""
        
        # Test unauthenticated access
        response = self.client.get(reverse('example-item-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test authenticated access
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('example-item-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test admin-only endpoints
        response = self.client.post(reverse('example-fetch'), {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test admin access
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(reverse('example-fetch'), {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_error_handling(self):
        """Test error handling in the workflow."""
        
        # Test processing non-existent item
        ai_service = ExampleOfAiService()
        with self.assertRaises(ExampleOfArticle.DoesNotExist):
            ai_service.process_item(
                item_id=99999,
                processing_model="example-model-v1",
                user=self.user
            )

        # Test API endpoint with invalid data
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(reverse('example-process'), {
            'item_id': 99999
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_data_consistency(self):
        """Test data consistency across the system."""
        
        # Create summary
        summary = ExampleOfSummary.objects.create(
            example_item=self.article,
            processing_model="example-model-v1",
            status="completed",
            summary_text="Test summary",
            word_count=5,
            processing_cost=0.005,
            requested_by=self.user
        )

        # Test that relationships are maintained
        self.assertEqual(summary.example_item, self.article)
        self.assertEqual(summary.requested_by, self.user)
        self.assertEqual(self.article.summaries.count(), 1)

        # Test fetch log creation
        fetch_log = ExampleOfFetchLog.objects.create(
            source="Test Source",
            status=ExampleOfFetchLog.Status.SUCCESS,
            items_fetched=5,
            items_saved=3
        )

        # Test fetch log completion
        fetch_log.complete(
            status=ExampleOfFetchLog.Status.SUCCESS,
            items_saved=4
        )
        
        self.assertEqual(fetch_log.status, ExampleOfFetchLog.Status.SUCCESS)
        self.assertEqual(fetch_log.items_saved, 4)
        self.assertIsNotNone(fetch_log.completed_at) 