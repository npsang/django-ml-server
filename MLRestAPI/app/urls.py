from rest_framework import routers
from django.urls import path, include

from . import views

router = routers.DefaultRouter()
router.register("users", views.UserViewSet, "user")
router.register("documents", views.DocumentViewSet, "document")
router.register("mlmodels", views.MLModelViewSet, "mlmodel")

urlpatterns = [
    path('', include(router.urls)),
    path('mlmodelwsgi/', views.MLModelWSGI.as_view()),
    path('compute/', views.ComputeViewSet.as_view()),
]
