from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LostReportViewSet,
    FoundReportViewSet,
    CategoryListView, LocationListView, Index
)

router = DefaultRouter()
router.register(r'lost', LostReportViewSet, basename='lost-report')
router.register(r'found', FoundReportViewSet, basename='found-report')

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='categories'),
    path('locations/', LocationListView.as_view(), name='locations'),
    path('', include(router.urls)),
]