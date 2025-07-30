"""Example of external API service implementation with logging integration."""
import os
import json
from typing import Dict, Any, Tuple
import httpx
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from example.models import ExampleOfFetchLog, ExampleOfArticle


class ExampleServiceError(Exception):
    """Exception raised for errors in the example service."""
    pass


class ConfigurationError(Exception):
    """Exception raised for configuration errors."""
    pass


class ExampleOfExternalApiService():
    """
    Example of a flexible fetcher for external APIs, driven by JSON config.
    Implements external API integration with logging support.
    """
    def __init__(self, config: Dict[str, Any] = None):
        # Support both environment variable and config parameter
        api_key = None
        if config and 'api_key' in config:
            api_key = config['api_key']
        else:
            api_key = os.environ.get('EXAMPLE_API_KEY', 'example-key')

        if not api_key:
            raise ConfigurationError("Missing api_key for ExampleOfExternalApiService. Provide it in environment or config.")

        self.api_key = api_key
        self.base_url = 'https://api.example.com/v1/data'
        self.config = config or {}

    def _get_query_params(self) -> Dict[str, Any]:
        """
        Returns the default query parameters for the external API endpoint.
        This can be overridden by passing custom parameters to the fetch method.
        """
        default_params = {
            'language': 'en',
            'category': 'example',
        }

        # Override with config if provided
        if self.config:
            default_params.update({
                k: v for k, v in self.config.items()
                if k not in ['api_key']  # Exclude api_key from query params
            })

        return default_params

    def _create_fetch_log(self, source: str = 'ExampleService',
                         query_params: Dict[str, Any] = None) -> ExampleOfFetchLog:
        """Create a new ExampleOfFetchLog entry for this fetch operation."""
        return ExampleOfFetchLog.objects.create(
            source=source,
            status=ExampleOfFetchLog.Status.PENDING,
            query_params=query_params or {},
            metadata={'service_class': 'ExampleOfExternalApiService'}
        )

    def _save_raw_data(self, fetch_log: 'ExampleOfFetchLog', raw_data: Dict[str, Any]) -> None:
        """Save raw response data to file and update fetch log."""
        if not raw_data:
            return

        try:
            # Create a filename based on fetch log ID and timestamp
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            filename = f"example_raw_{fetch_log.id}_{timestamp}.json"

            # You might want to configure this path in settings
            raw_data_dir = os.path.join('media', 'raw_data')
            os.makedirs(raw_data_dir, exist_ok=True)

            file_path = os.path.join(raw_data_dir, filename)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(raw_data, f, indent=2, ensure_ascii=False)

            fetch_log.raw_data_file = file_path
            fetch_log.save(update_fields=['raw_data_file'])

        except Exception as e:
            print(f"Warning: Could not save raw data file: {e}")

    def _fetch_data(self, query_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform the API call and return the raw response data from external API.
        Ensures the api_key is included in the request parameters.
        """
        if not query_params:
            query_params = self._get_query_params()

        url = self.base_url
        query_params['apiKey'] = self.api_key

        try:
            # Simulate API call for example purposes
            # In real implementation, this would be an actual HTTP request
            response_data = {
                'status': 'ok',
                'totalResults': 5,
                'items': [
                    {
                        'title': 'Example Item 1',
                        'content': 'This is example content for item 1.',
                        'url': 'https://example.com/item1',
                        'publishedAt': timezone.now().isoformat(),
                        'author': 'Example Author',
                        'source': {'name': 'Example Source'},
                        'urlToImage': 'https://example.com/image1.jpg',
                        'description': 'Example description for item 1.'
                    },
                    {
                        'title': 'Example Item 2',
                        'content': 'This is example content for item 2.',
                        'url': 'https://example.com/item2',
                        'publishedAt': timezone.now().isoformat(),
                        'author': 'Example Author',
                        'source': {'name': 'Example Source'},
                        'urlToImage': 'https://example.com/image2.jpg',
                        'description': 'Example description for item 2.'
                    }
                ]
            }
            return response_data
        except Exception as e:
            raise ExampleServiceError(f"Failed to fetch from external API: {e}")

    def _process_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the raw response data from external API and return a structured format.
        """
        if 'items' not in response_data:
            raise ExampleServiceError("Invalid response format from external API: 'items' key missing")

        items = response_data['items']
        return {
            'status': response_data.get('status', 'unknown'),
            'totalResults': response_data.get('totalResults', 0),
            'items': items
        }

    def _save_items(self, items_data: list) -> Tuple[int, int]:
        """
        Save the fetched items to the database.
        Skip items that already exist (based on URL).

        Returns:
            Tuple[int, int]: (items_processed, items_saved)
        """
        items_processed = 0
        items_saved = 0

        for item_data in items_data:
            items_processed += 1
            try:
                # Skip if item with this URL already exists
                if ExampleOfArticle.objects.filter(url=item_data.get('url')).exists():
                    continue

                ExampleOfArticle.objects.create(
                    title=item_data.get('title', ''),
                    content=item_data.get('content', ''),
                    url=item_data.get('url', ''),
                    published_date=parse_datetime(item_data.get('publishedAt')),
                    author=item_data.get('author'),
                    source=item_data.get('source', {}).get('name', 'Unknown'),
                    image_url=item_data.get('urlToImage'),
                    description=item_data.get('description'),
                    example_source='ExampleAPI'
                )
                items_saved += 1

            except Exception as e:
                print(f"Error saving item: {e}")

        return items_processed, items_saved

    def fetch_and_save(self, query_params: Dict[str, Any] = None,
                      source: str = 'ExampleService'):
        """
        Fetch items from external API, save them to the database, and return the processed data.
        Optionally accepts custom query parameters to override defaults.
        Includes comprehensive logging integration.
        """
        # Use provided query params or get defaults
        if not query_params:
            query_params = self._get_query_params()

        # Create fetch log entry
        fetch_log = self._create_fetch_log(source, query_params)

        try:
            # Update status to in progress
            fetch_log.status = ExampleOfFetchLog.Status.IN_PROGRESS
            fetch_log.save(update_fields=['status'])

            # Fetch data from API
            response_data = self._fetch_data(query_params)
            if not response_data:
                raise ExampleServiceError("No data returned from external API")

            # Save raw data to file
            # self._save_raw_data(fetch_log, response_data)

            # Process the response
            processed_data = self._process_response(response_data)

            # Update fetch log with fetched count
            fetch_log.items_fetched = len(processed_data['items'])
            fetch_log.save(update_fields=['items_fetched'])

            # Save items to the database and get counts
            items_processed, items_saved = self._save_items(processed_data['items'])

            # Add save statistics to the result
            processed_data['items_processed'] = items_processed
            processed_data['items_saved'] = items_saved
            processed_data['duplicates_skipped'] = items_processed - items_saved

            # Update fetch log metadata with additional info
            metadata = {
                'service_class': 'ExampleOfExternalApiService',
                'api_status': processed_data.get('status'),
                'total_results': processed_data.get('totalResults'),
                'duplicates_skipped': processed_data['duplicates_skipped']
            }

            # Complete the fetch log with success status
            fetch_log.complete(
                status=ExampleOfFetchLog.Status.SUCCESS,
                items_saved=items_saved,
                metadata=metadata
            )

            return processed_data

        except Exception as e:
            # Log the error and mark fetch as failed
            error_message = str(e)
            fetch_log.complete(
                status=ExampleOfFetchLog.Status.ERROR,
                error_message=error_message,
                metadata={'service_class': 'ExampleOfExternalApiService', 'error_type': type(e).__name__}
            )

            # Re-raise the exception to maintain existing behavior
            raise e 