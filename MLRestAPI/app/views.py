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

from MLRestAPI.wsgi import registry
# from ml.registry import MLRegistry
# from ..ml.registry import MLRegistry

# Create your views here.
class ComputeViewSet(APIView):
    
    def post(self, request):
        """
        {
            "user": "user_id",
            "testFile": [
                {
                    "url": "https://test.file.example.com"
                }
            ],
            "templateFile": [
                {
                    "url": "https://template1.file.example.com"
                },
                {
                    "url": "https://template2.file.example.com"
                }
            ]
        }
        
        """
        # CREATE DOCUMENT OBJECT
        user_id = request.data['user']
        # TestFile
        test_file = request.data['testFile'][0]
        test_file['user'] = user_id
        test_file['name'] = 'test.pdf'
        test_file['file_type'] = 'pdf'

    
        # TemplateFile
        # Case 1: TemplateFile chi co mot file
        # Case 2: TemplateFile co nhieu hon mot file
        template_files = request.data['templateFile']
        for template_file in template_files:
            template_file['user'] = user_id
            template_file['name'] = 'test.pdf'
            template_file['file_type'] = 'pdf'

        test_file_serializer = DocumentSerializer(data=test_file)

        hello = 'test'
        if DocumentSerializer.is_valid(test_file_serializer):
            hello = test_file_serializer.save()

        serializer = DocumentSerializer(data=request.data)
        return Response(hello,status=status.HTTP_201_CREATED)

    def get(self, request):
        input_data1 = request.data['doc1']
        input_data2 = request.data['doc2']

        my_alg = registry.model[int(request.data['model_id'])]

        emb1 = my_alg.embedding([input_data1])
        emb2 = my_alg.embedding([input_data2])

        # print(type(emb1), emb1)
        avg_cos_sim, res = my_alg.compute(emb1, emb2)
        print(avg_cos_sim)
        print(res)

        return Response(avg_cos_sim, status=status.HTTP_200_OK)

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


class MLModelWSGI(APIView):

    def get(self, request):
        return Response('hello world')
        # return Response(str(registry.model), status=status.HTTP_200_OK)
