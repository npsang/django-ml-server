from django.http import Http404

from rest_framework import viewsets, generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser

from .models import (
    User,
    Document,
    MLModel
)
from .serializers import (
    UserSerializer,
    DocumentSerializer,
    MLModelSerializer
)

# from plagiarism.wsgi import registry
# from ml.registry import MLRegistry
# from ..ml.registry import MLRegistry

# Create your views here.
class ComputeViewSet(APIView):
    pass

#     def get(self, request):
#         input_data1 = request.data['doc1']
#         input_data2 = request.data['doc2']

#         my_alg = registry.model[int(request.data['model_id'])]

#         emb1 = my_alg.embedding([input_data1])
#         emb2 = my_alg.embedding([input_data2])

#         # print(type(emb1), emb1)
#         avg_cos_sim, res = my_alg.compute(emb1, emb2)
#         print(avg_cos_sim)
#         print(res)

#         return Response(avg_cos_sim, status=status.HTTP_200_OK)

class MLModelViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = MLModel.objects.filter(active=True)
    serializer_class = MLModelSerializer

    def get_permissions(self):
        return [permissions.AllowAny()]



class DocumentViewSet(viewsets.ViewSet, generics.CreateAPIView,
                        generics.RetrieveAPIView, generics.ListAPIView):
    queryset = Document.objects.filter(active=True)
    serializer_class = DocumentSerializer

    def get_permissions(self):
        return [permissions.AllowAny()]



class UserViewSet(viewsets.ViewSet, generics.CreateAPIView,
                    generics.ListAPIView, generics.RetrieveAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'get_current_user':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class MLModelWSGI(APIView):

    def get(self, request):
        return Response('hello world')
        # return Response(str(registry.model), status=status.HTTP_200_OK)
