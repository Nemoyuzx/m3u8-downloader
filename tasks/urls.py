from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskHistoryViewSet, SystemLogViewSet

router = DefaultRouter()
router.register(r'history', TaskHistoryViewSet)
router.register(r'logs', SystemLogViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
