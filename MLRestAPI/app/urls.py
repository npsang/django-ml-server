from rest_framework import routers
from django.urls import path, include

from . import views

router = routers.DefaultRouter()
router.register("users", views.UserViewSet, "user")
router.register("documents", views.DocumentViewSet, "document")
router.register("mlmodels", views.MLModelViewSet, "mlmodel")
router.register('sentences', views.SentenceViewSet, 'sentence')

urlpatterns = [
    path('', include(router.urls)),
    path('mlmodelwsgi/', views.MLModelWSGI.as_view()),
    path('compute_create/', views.ComputeCreateViewSet.as_view()),
    path('compute/', views.ComputeViewSet.as_view()),
    path('search_on_internet', views.SearchOnInternetViewSet.as_view())
]
