from rest_framework import viewsets, generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
import json
import pickle
import base64
from .models import (
    User,
    Document,
    Sentence,
    MLModel
)
from .serializers import (
    UserSerializer,
    DocumentSerializer,
    SentenceSerializer,
    MLModelSerializer
)

from MLRestAPI.wsgi import registry 
# from ml.registry import MLRegistry
# from ..ml.registry import MLRegistry
from file_handle.download_by_url import download_file, url1
from file_handle.read_file import readPDFFile

# Create your views here.
class ComputeViewSet(APIView):
    
    def post(self, request):
        """
        {
            "mlmodel: mlmodel_id,
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
        res = {
            'testFile': [],
            'templateFile': [],
        }
        # TestFile
        # 1. CREATE DOCUMENT OBJECT
        user_id = request.data['user']
        # mlmodel_id = request.data['mlmodel']
        mlmodel_id = 1
        pipeline = registry.model[mlmodel_id]

        test_file = request.data['testFile'][0]
        test_file['user'] = user_id
        test_file['name'] = 'test.pdf'
        test_file['file_type'] = 'pdf'
        # 2. download file 
        document = download_file(url=url1, filename=test_file['name']) # Change later: url, filename from post request)
        test_file['document'] = document
        # 2. readfile
        content = readPDFFile(document)
        # 3. preprocessinng
        #   3.1 text normalize
        content =  pipeline.text_normalize(content)
        test_file['content'] = content
        #   3.2 save Document Object
        test_file_serializer = DocumentSerializer(data=test_file)
        if DocumentSerializer.is_valid(test_file_serializer):
            """
            IF DOCUMENT IS VALID, CREATE SENTENCES OBJECTS OF THIS DOCUMENT
            Inner task: PREPROCESSING annd CREATE SENTENCE OBJECT
            """
            # save Document Object and get document_id
            document_id = test_file_serializer.save()
            res['testFile'].append({'document_id': document_id})
            # sentence tokenizing and get sentences list
            sentences = pipeline.sent_tokenize(content)
            for i, sentence in enumerate(sentences):
                # preprocessing
                content = sentence
                is_tokenized = False
                content_tokenized = ''
                is_encode = False
                encode = None
                # word tokenized
                try:
                    content_tokenized = pipeline.word_tokenize(content)
                    is_tokenized = True
                except Exception as e:
                    print('Tokenizing:',e)
                # embedding for transformer
                if is_tokenized:
                    try:
                        encode = pipeline.embedding(content_tokenized)
                        # TODO: Change encode(type is np.array) to binary
                        encode_bytes = pickle.dumps(encode)
                        encode_base64 =  base64.b64encode(encode_bytes)
                        is_encode = True
                    except Exception as e:
                        print('Encoding:',e)



                """  
                # 1. set the field to Django BinaryField
                from django.db import models
                np_field = models.BinaryField()
                # 2. transform numpy array to python byte using pickle dumps, then encoded by base64
                # np_bytes = pickle.dumps(np_array)
                np_base64 = base64.b64encode(np_bytes)
                model.np_field = np_base64
                # 3. get the numpy array from django model
                np_bytes = base64.b64decode(model.np_field)
                np_array = pickle.loads(np_bytes)
                """
                sentence_obj = {
                    'document': document_id,
                    'content': content,
                    'is_tokenized': is_tokenized,
                    'content_tokenized': content_tokenized,
                    'is_encode': is_encode,
                    'encode': encode_base64,
                }

                if i < 5 or  i > len(sentences)-5:
                    print(sentence_obj)
                    # print(type(encode))

                print(sentence_obj['encode'])
                sentence_serializer = SentenceSerializer(data=sentence_obj)
                if SentenceSerializer.is_valid(sentence_serializer):
                    sentence_id = sentence_serializer.save()
                    if is_encode:
                        Sentence.objects.get(pk=sentence_id).encode = encode_base64
                        # sentence_.encode = encode_base64
            # Test 
            # print(Sentence.objects.get(pk=1))
            # res['testFile'].append(json.dumps(Document.objects.get(pk=output)))







        # TemplateFile
        # Case 1: TemplateFile chi co mot file
        # Case 2: TemplateFile co nhieu hon mot file
        template_files = request.data['templateFile']
        for template_file in template_files:
            template_file['user'] = user_id
            template_file['name'] = 'test.pdf'
            template_file['file_type'] = 'pdf'
            template_file_serializer = DocumentSerializer(data=template_file)

            if DocumentSerializer.is_valid(template_file_serializer):
                output = template_file_serializer.save()
                res['templateFile'].append({'document_id': output})
        
        

        # serializer = DocumentSerializer(data=request.data)
        return Response(res,status=status.HTTP_201_CREATED)

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


class SentenceViewSet(viewsets.ViewSet, generics.RetrieveAPIView, generics.ListAPIView):
    queryset = Sentence.objects.filter(active=True)
    serializer_class = SentenceSerializer


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView,
                    generics.ListAPIView, generics.RetrieveAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer


class MLModelWSGI(APIView):

    def get(self, request):
        return Response('hello world')
        # return Response(str(registry.model), status=status.HTTP_200_OK)
