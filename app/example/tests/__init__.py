# Example tests package
from .example_of_model_tests import (
    ExampleOfArticleModelTest,
    ExampleOfFetchLogModelTest,
    ExampleOfSummaryModelTest
)
from .example_of_serializer_tests import (
    ExampleOfCustomValidationSerializerTest,
    ExampleOfReadonlySerializerTest,
    ExampleOfModelSerializerTest
)
from .example_of_service_tests import (
    ExampleOfExternalApiServiceTest,
    ExampleOfAiServiceTest
)
from .example_of_integration_tests import ExampleOfIntegrationTest

__all__ = [
    'ExampleOfArticleModelTest',
    'ExampleOfFetchLogModelTest',
    'ExampleOfSummaryModelTest',
    'ExampleOfCustomValidationSerializerTest',
    'ExampleOfReadonlySerializerTest',
    'ExampleOfModelSerializerTest',
    'ExampleOfExternalApiServiceTest',
    'ExampleOfAiServiceTest',
    'ExampleOfIntegrationTest',
] 