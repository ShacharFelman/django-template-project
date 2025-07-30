# Django Template Project

## Overview

A comprehensive Django template project that provides examples of common web application patterns and features. This template includes authentication, API endpoints, background tasks, external service integration, and more - all implemented as reusable examples.

---

## Project Structure

```
django-template-project/
├── app/
│   ├── core/           # Core settings and common functionality
│   ├── example/        # Feature examples with "example_of_xxx" naming
│   └── users/          # Authentication system (unchanged)
├── docs/               # Documentation
├── docker-compose.yml  # Docker services configuration
└── requirements.txt    # Python dependencies
```

---

## Features

### Core Features
- **User Management:** Register, authenticate, and manage users (email-based login)
- **API Documentation:** Auto-generated with drf-spectacular (Swagger/OpenAPI)
- **Dockerized:** Full Docker setup for app, Postgres, Redis, Celery worker/beat/flower
- **CORS Support:** Configurable CORS headers for cross-origin requests
- **Redis Caching:** Redis is used for both Celery and API caching

### Example Features (in `example` app)
- **CRUD Operations:** Complete CRUD with caching and custom permissions
- **External API Integration:** Example service for external API calls
- **AI/ML Processing:** Example service for AI/ML integration
- **Background Tasks:** Periodic and async task examples
- **Admin Interface:** Advanced admin with custom actions and filters
- **Management Commands:** Custom commands and Celery monitoring
- **Comprehensive Testing:** Model, serializer, service, and integration tests

---

## Architecture

- **Django REST Framework** for API endpoints
- **Celery** for background tasks
- **PostgreSQL** as the database
- **Redis** as the Celery broker and API cache
- **Docker** for containerized development and deployment

---

## Getting Started

### Prerequisites
- Docker & Docker Compose
- (For local dev) Python 3.10+ and PostgreSQL/Redis if not using Docker

### Environment Variables
Create a `.env` file in the project root with the following variables:
```
DB_HOST=db
DB_NAME=template_db
DB_USER=template_user
DB_PASS=template_pass
EXAMPLE_API_KEY=your_example_api_key
EXAMPLE_AI_API_KEY=your_example_ai_key
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
REDIS_URL=redis://redis:6379/0
```

---

## Running with Docker

1. **Build and start all services:**
   ```sh
   docker-compose up --build
   ```
   This will start:
   - Django app (http://localhost:8000)
   - PostgreSQL (localhost:5432)
   - Redis (localhost:6379)
   - Celery worker, beat, and Flower (http://localhost:5555)

2. **Access the API docs:**
   - Swagger UI: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
   - OpenAPI schema: [http://localhost:8000/api/schema](http://localhost:8000/api/schema)

3. **Create a superuser (for admin access):**
   ```sh
   docker-compose exec app python manage.py createsuperuser
   ```

---

## Example API Endpoints

### Authentication
- `POST /api/users/create/` — Register a new user
- `POST /api/users/token/` — Obtain auth token
- `GET /api/users/me/` — Get current user info

### Example CRUD Operations
- `GET /api/example/items/` — List example items
- `POST /api/example/items/` — Create example item
- `GET /api/example/items/{id}/` — Retrieve example item
- `PUT /api/example/items/{id}/` — Update example item
- `DELETE /api/example/items/{id}/` — Delete example item
- `GET /api/example/items/{id}/process/` — Process example item

### Example Services
- `POST /api/example/fetch/` — Trigger external API fetch (admin only)
- `POST /api/example/process/` — Trigger async processing (admin only)
- `GET /api/example/status/{item_id}/` — Check processing status (admin only)

---

## Example API Requests & Responses

### 1. Register User
**Request:**
```http
POST /api/users/create/
Content-Type: application/json
{
  "email": "user@example.com",
  "name": "User Name",
  "password": "password123"
}
```
**Response:**
```json
{
  "email": "user@example.com",
  "name": "User Name"
}
```

### 2. List Example Items
**Request:**
```http
GET /api/example/items/
Authorization: Token <auth_token>
```
**Response:**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Example Item",
      "content": "Example content...",
      "url": "http://example.com/item",
      "published_date": "2025-01-09T12:00:00Z",
      "author": "Example Author",
      "source": "Example Source",
      "example_source": "Example Client",
      "created_at": "2025-01-09T12:00:00Z"
    }
  ]
}
```

### 3. Trigger External API Fetch
**Request:**
```http
POST /api/example/fetch/
Authorization: Token <admin_token>
Content-Type: application/json
{
  "query_params": {"category": "example"}
}
```
**Response:**
```json
{
  "message": "Example fetch and save completed successfully."
}
```

---

## Example Features Documentation

### Models
- **ExampleOfArticle:** Basic model with relationships and common fields
- **ExampleOfFetchLog:** Logging model with status tracking and metadata
- **ExampleOfSummary:** Model with async status tracking and relationships

### Views
- **ExampleOfCachedListView:** CRUD operations with caching and custom permissions
- **ExampleOfManualTriggerView:** Manual trigger for external services
- **ExampleOfAsyncProcessingView:** Async processing with status checking

### Services
- **ExampleOfExternalApiService:** External API integration with error handling
- **ExampleOfAiService:** AI/ML service integration with async processing

### Admin
- **ExampleOfBasicAdmin:** Basic admin customization
- **ExampleOfAdvancedAdmin:** Advanced admin with filters and computed fields
- **ExampleOfCustomActionsAdmin:** Admin with custom bulk actions

### Management Commands
- **ExampleOfCustomCommand:** Custom command with async/sync options
- **ExampleOfCeleryCommand:** Celery status monitoring command

### Tests
- **Model Tests:** Validation, constraints, and relationships
- **Serializer Tests:** Custom validation and computed fields
- **Service Tests:** External API and AI service integration
- **Integration Tests:** Complete workflow testing

---

## Customization Guide

### Adding Your Own Models
1. Create models in your app following the `ExampleOf*` pattern
2. Add admin classes following the admin examples
3. Create serializers with custom validation as needed
4. Add tests for your models

### Adding External API Integration
1. Use `ExampleOfExternalApiService` as a template
2. Implement your API client following the same pattern
3. Add error handling and logging
4. Create corresponding tasks for background processing

### Adding AI/ML Services
1. Use `ExampleOfAiService` as a template
2. Implement your AI client following the same pattern
3. Add async processing capabilities
4. Create status tracking for long-running operations

### Adding Background Tasks
1. Use the task examples in `example/tasks/`
2. Follow the retry and error handling patterns
3. Add logging for monitoring
4. Create management commands for manual triggers

---

## Development & Testing

### Running Tests
```sh
# Run all tests
python manage.py test

# Run specific test files
python manage.py test example.tests.example_of_model_tests
python manage.py test example.tests.example_of_integration_tests
```

### Management Commands
```sh
# Test custom command
python manage.py example_of_custom_command --async

# Check Celery status
python manage.py example_of_celery_command
```

### Celery Tasks
```sh
# Start Celery worker
celery -A core worker --loglevel=info

# Start Celery beat (scheduler)
celery -A core beat --loglevel=info

# Monitor with Flower
celery -A core flower --port=5555
```

---

## API Documentation
- **Swagger UI:** [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- **OpenAPI schema:** [http://localhost:8000/api/schema](http://localhost:8000/api/schema)

---

## Contributing

This template is designed to be a starting point for Django projects. Feel free to:
1. Copy and modify the examples for your specific use case
2. Add new example patterns
3. Improve the documentation
4. Submit issues or pull requests

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.