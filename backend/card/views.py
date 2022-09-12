from django.core.paginator import Page
from django.db.models import query
from django.db.models.query import QuerySet
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status, generics
import card
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS, IsAdminUser, BasePermission
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework import status, filters
from .serializers import CardSerializer, CardCategorySerializer, CardColorSerializer, CardStatusSerializer, CardListSerializer

from core.models import Card, CardCategory, CardColor, CardStatus
from card import serializers


class isAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        # Read permissions are allowed to any request, therefore GET, HEAD and
        # OPTIONS requests are always allowed.
        if request.method in SAFE_METHODS:
            return True

        return request.user.is_staff


class IsAdminOrReadOnly(BasePermission):
    """Object-level permission to only allow admin users to edit an object"""

    def has_permission(self, request, view):
        # Read permissions are allowed to any request, therefore GET, HEAD and
        # OPTIONS requests are always allowed.
        if request.method in SAFE_METHODS:
            return True

        # Instance must belong to an admin user
        return request.user.is_staff


# class userValidated(BasePermission):
#     def is_owner(self, request, view):
#         return request.user.


class JWTAuthenticationSage(JWTAuthentication):
    def authenticate(self, request):
        try:
            return super().authenticate(request=request)
        except InvalidToken:
            return None


class BaseCardAttrViewSet(viewsets.GenericViewSet,
                          mixins.ListModelMixin,
                          mixins.CreateModelMixin):
    """Base viewset for user owned card attributes"""
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminOrReadOnly,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        # assigned_only = bool(
        #     int(self.request.query_params.get('assigned_only', 0))
        # )
        queryset = self.queryset
        return queryset.order_by('-id').distinct()

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class StandardResultsSetPagination(PageNumberPagination):
    """Custom standard pagination class"""
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data
        })


class CardCategoryViewSet(BaseCardAttrViewSet):
    queryset = CardCategory.objects.all()
    serializer_class = serializers.CardCategorySerializer


class CardColorViewSet(BaseCardAttrViewSet):
    queryset = CardColor.objects.all()
    serializer_class = serializers.CardColorSerializer


class CardStatusViewSet(BaseCardAttrViewSet):
    queryset = CardStatus.objects.all()
    serializer_class = serializers.CardStatusSerializer


class CardViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CardSerializer
    search_fields = ['creation_date', ]
    filter_backends = (filters.SearchFilter,)
    queryset = Card.objects.all()

    def _params_to_init(self, qs):
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve the cards for current user"""
        category = self.request.query_params.get('category')
        status = self.request.query_params.get('status')
        color = self.request.query_params.get('color')
        queryset = self.queryset.filter(user_id=self.request.user.id)

        if category:
            queryset = self.queryset.filter(category_id__iexact=category)
        if status:
            queryset = self.queryset.filter(status_id__iexact=status)
        if color:
            queryset = self.queryset.filter(color_id__iexact=color)

        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.CardSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an the rif image to a supplier"""
        supplier = self.get_object()
        serializer = self.get_serializer(
            supplier,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
