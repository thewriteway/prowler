import uuid

from django.db import transaction, connection
from rest_framework.exceptions import NotAuthenticated
from rest_framework.filters import SearchFilter
from rest_framework_json_api import filters
from rest_framework_json_api.serializers import ValidationError
from rest_framework_json_api.views import ModelViewSet

from api.filters import CustomDjangoFilterBackend


class BaseViewSet(ModelViewSet):
    filter_backends = [
        filters.QueryParameterValidationFilter,
        filters.OrderingFilter,
        CustomDjangoFilterBackend,
        SearchFilter,
    ]

    filterset_fields = []
    search_fields = []

    ordering_fields = "__all__"
    ordering = ["id"]

    def get_queryset(self):
        raise NotImplementedError


class BaseRLSViewSet(BaseViewSet):
    def initial(self, request, *args, **kwargs):
        # Ideally, this logic would be in the `.setup()` method but DRF view sets don't call it
        # https://docs.djangoproject.com/en/5.1/ref/class-based-views/base/#django.views.generic.base.View.setup
        if "X-Tenant-ID" not in request.headers:
            # This will return a 403 until we implement authentication/authorization
            # https://www.django-rest-framework.org/api-guide/authentication/#unauthorized-and-forbidden-responses
            raise NotAuthenticated("X-Tenant-ID header is required")

        tenant_id = request.headers["X-Tenant-ID"]

        try:
            uuid.UUID(tenant_id)
        except ValueError:
            raise ValidationError("X-Tenant-ID header must be a valid UUID")

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SET api.tenant_id = %s", [tenant_id])
            return super().initial(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        tenant_id = self.request.headers.get("X-Tenant-ID")
        context["tenant_id"] = tenant_id
        return context
