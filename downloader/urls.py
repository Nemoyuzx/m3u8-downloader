from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DownloadTaskViewSet

router = DefaultRouter()
router.register(r'tasks', DownloadTaskViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
