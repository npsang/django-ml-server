from rest_framework import viewsets, generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
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
from file_handle.read_file import read_file

# Create your views here.
class SearchOnInternetViewSet(APIView):
    
    def post(self, request):
        """
        UBUNBU PATH EXAMPLE
        request.data = {
            "test_path": "/home/sangnguyendesktop/Public/2021_Binh_Huong_2021_VCAA.pdf",
            "templates_path": [
                "/home/sangnguyendesktop/Public/2021_Binh_Huong_2021_VCAA.pdf",
                "/home/sangnguyendesktop/Public/20Hien_Thang_YdinhNCKHSV_2021_paper.pdf"
            ]
        }
        WINDOW PATH EXAMPLE
        request.data = {
            "test_path": "C:/Users/Sang Nguyen Desktop/Downloads/2021_Binh_Huong_2021_VCAA.pdf",
            "templates_path": [
                "C:/Users/Sang Nguyen Desktop/Downloads/20Hien_Thang_YdinhNCKHSV_2021_paper.pdf"
            ]
        }
        """
        try:
            
            res = _compute(
                test_path=request.data['test_path'],
                templates_path=request.data['templates_path'],
                mlmodel_id=request.data['mlmodel_id'] if 'mlmodel_id' in request.data else 1
            )
        except Exception as e:
            res = None
            print(e) 

        return Response(res,status=status.HTTP_201_CREATED)

class ComputeViewSet(APIView):

    def post(self, request):
        """
        UBUNBU PATH EXAMPLE
        request.data = {
            "test_path": "/home/sangnguyendesktop/Public/2021_Binh_Huong_2021_VCAA.pdf",
            "templates_path": [
                "/home/sangnguyendesktop/Public/2021_Binh_Huong_2021_VCAA.pdf",
                "/home/sangnguyendesktop/Public/20Hien_Thang_YdinhNCKHSV_2021_paper.pdf"
            ]
        }
        WINDOW PATH EXAMPLE
        request.data = {
            "test_path": "C:/Users/Sang Nguyen Desktop/Downloads/2021_Binh_Huong_2021_VCAA.pdf",
            "templates_path": [
                "C:/Users/Sang Nguyen Desktop/Downloads/20Hien_Thang_YdinhNCKHSV_2021_paper.pdf"
            ]
        }
        """
        try:
            
            res = _compute(
                test_path=request.data['test_path'],
                templates_path=request.data['templates_path'],
                mlmodel_id=request.data['mlmodel_id'] if 'mlmodel_id' in request.data else 1
            )
        except Exception as e:
            res = None
            print(e) 

        return Response(res,status=status.HTTP_201_CREATED)

class ComputeCreateViewSet(APIView):
    
    def post(self, request):
        """
        UBUNBU PATH EXAMPLE
        request.data = {
            "test_path": "/home/sangnguyendesktop/Public/2021_Binh_Huong_2021_VCAA.pdf",
            "templates_path": [
                "/home/sangnguyendesktop/Public/2021_Binh_Huong_2021_VCAA.pdf",
                "/home/sangnguyendesktop/Public/20Hien_Thang_YdinhNCKHSV_2021_paper.pdf"
            ]
        }
        WINDOW PATH EXAMPLE
        request.data = {
            "user": "npsang"
            "test_path": ["C:/Users/Sang Nguyen Desktop/Downloads/2021_Binh_Huong_2021_VCAA.pdf"],
            "templates_path": [
                "C:/Users/Sang Nguyen Desktop/Downloads/20Hien_Thang_YdinhNCKHSV_2021_paper.pdf"
            ]
        }
        """
        try:
            
            res = _compute_create_document_object(
                user=request.data['user'],
                test_path=request.data['test_path'],
                templates_path=request.data['templates_path'],
                mlmodel_id=request.data['mlmodel_id'] if 'mlmodel_id' in request.data else 1
            )
        except Exception as e:
            res = None
            print(e) 

        return Response(res,status=status.HTTP_201_CREATED)

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


def _compute(test_path, templates_path, mlmodel_id=1):
    """
    1. Read text from pdf file
    2. Preprocessing this text to embedding
    3. Embedding preprocessed text to input of compute
    4. Compute and return
    Return
    res = {
        'testFile': [
            {
                "id": "document_id",
                "name": "string",
                "data": [
                    {
                        "id": "sentence_id",
                        "content": "sentence 1",
                        "matchId": "other_document_sentence_id"
                    }
                ]
            }
        ],
        'templateFile: [
            {
                "id": "document_id",
                "name": "string",
                "data": [
                    {
                        "id": "sentence_id",
                        "name": "string",
                        "data": [
                            {
                                "id": "sentence_id",
                                "content": "sentence 1",
                                "matchId": "other_document_sentence_id"
                            }
                        ]
                    }
                ]
                
        
            }
            ...
            ,
            ]
        
    }
    
    """
    res = {'testFile': [], 'templateFile': []}
    pipeline = registry.model[mlmodel_id]
    test_sentences, test_sentences_tokenized = pipeline.preprocessing(read_file(test_path))
    test_embedding = pipeline.embedding(test_sentences_tokenized)
    res['testFile'].append({
        'id': '0',
        'name': test_path.split('/')[-1],
        'data': [
            {
                'id': str(i),
                'content': sentence,
                'matchId': None,
                'score': None,

            } for i, sentence in enumerate(test_sentences)
        ]
        })
    for i, template_path in enumerate(templates_path):
        template_sentences, template_sentences_tokenized = pipeline.preprocessing(read_file(template_path))
        template_embedding = pipeline.embedding(template_sentences_tokenized)
        res['templateFile'].append(
            {
                'id': str(i+1),
                'name': template_path.split('/')[-1],
                'data': [
                    {
                        'id': str(i),
                        'content': sentence,
                        'matchId': None,
                        'score': None,

                    } for i, sentence in enumerate(template_sentences)
                ]
            }
        )
        score, cosin_matrix, positions = pipeline.compute(test_embedding, template_embedding)
        for test_sentence_id, pos_in_template in enumerate(positions):
            res['testFile'][0]['data'][test_sentence_id]['matchId'] = str(test_sentence_id)
            res['testFile'][0]['data'][test_sentence_id]['score'] = cosin_matrix[test_sentence_id][pos_in_template]

            if res['templateFile'][0]['data'][pos_in_template]['matchId']:
                if res['templateFile'][0]['data'][pos_in_template]['score'] < cosin_matrix[test_sentence_id][pos_in_template]:
                    res['templateFile'][0]['data'][pos_in_template]['matchId'] = str(test_sentence_id)
                    res['templateFile'][0]['data'][pos_in_template]['score'] = cosin_matrix[test_sentence_id][pos_in_template]
                else:
                    pass
            else: 
                res['templateFile'][0]['data'][pos_in_template]['matchId'] = str(test_sentence_id)
                res['templateFile'][0]['data'][pos_in_template]['score'] = cosin_matrix[test_sentence_id][pos_in_template]
    return res
        
def _compute_create_document_object(user, test_path, templates_path, mlmodel_id):
    """
    1. Creat document of object for each file_path
    2. While processing document to sentences, create sentence object
    3. Compute and return respone
        1. Read text from pdf file
    2. Preprocessing this text to embedding
    3. Embedding preprocessed text to input of compute
    4. Compute and return
    Return
    res = {
        'testFile': [
            {
                "id": "document_id",
                "name": "string",
                "data":[
                    "id": "sentence_id",
                    "content": "sentence 1",
                    "matchId": "id"
                    "score": [
                        {
                            "document_id": "string",
                            "score": score
                        },
                    ]
                ]
            }
        ],
        'templateFile': [
            {
                "id": "document_id",
                "name": "string",
                "score": score,
                "data": [
                    {
                        "id": "sentence_id",
                        "name": "string",
                        "matchId": "id",
                        "score": score,
                    },
                ]
            }
    }
    """

    res = {'testFile': [], 'templateFile': []}
    files = [*[{'test_or_template': 'test', 'path': path} for path in test_path],
            *[{'test_or_template': 'template', 'path': path} for path in templates_path]]
    pipeline = registry.model[mlmodel_id]

    
    for file in files:
        _file_path = file['path']
        _file_name = _file_path.split('/')[-1]
        # CREATE DOCUMENT OBJECTS   
        _document, _create = Document.objects.get_or_create(name=_file_name,document=_file_path,user=User.objects.get_or_create(username=user)[0])
        if _create:
            _document.file_type = _file_name.split('.')[-1]
            _document.save()

            # READ DOCUMENT AND DO SENTENCES TOKENIZE
            _sentences, _sentences_tokenized = pipeline.preprocessing(read_file(_file_path))

            ## CREATE SENTENCE OBJECT
            for sentence, sentence_tokenized in zip(_sentences, _sentences_tokenized):
                sentence_serializer = SentenceSerializer(
                    data={
                        'document': _document.id,
                        'content': sentence,
                        'content_tokenized': sentence_tokenized,
                        'is_tokenized': True if sentence_tokenized else False,
                    }
                )
                if SentenceSerializer.is_valid(sentence_serializer):
                    sentence_serializer.save()
                else:
                    print(sentence_serializer.errors)
            _embedding = pipeline.embedding(_sentences_tokenized)
            if _embedding.any():
                _document.is_encode = True
                # _document.encode = encodebase64
                _document.save()
            
        else:
            _sentences_tokenized = [sentence.content_tokenized for sentence in Sentence.objects.filter(document_id=_document.id)]
            __embedding = pipeline.embedding(_sentences_tokenized)
            __np_bytes = pickle.dumps(__embedding)
            __np_base64 = base64.b64encode(__np_bytes)
            np_bytes = base64.b64decode(__np_base64)
            _embedding = pickle.loads(np_bytes)
            

        # Return respone
        if file['test_or_template'] == 'test':
            res['testFile'].append(
                {
                    'id': _document.id,
                    'name': _document.name,
                    'data': [
                        {
                            'id': sentence.id,
                            'content': sentence.content,
                            'matchId': None,
                            'score': []
                        } for sentence in Sentence.objects.filter(document_id=_document.id)
                    ]
                }
            )
            file['enbedding'] = _embedding

        elif file['test_or_template'] == 'template':
            _template_file_matchID_score = {}
            try:
                #TODO: 
                _test = next(file_item for file_item in  files if file_item['test_or_template'] == 'test')
                score, cosin_matrix, positions = pipeline.compute(_test['enbedding'], _embedding)
                _test_file = res['testFile'][0]['data']
                for test_sentence_id, pos_in_template in enumerate(positions):
                    # GET testFile from res
                    _test_file[test_sentence_id]['matchId'] = test_sentence_id
                    _test_file[test_sentence_id]['score'].append({
                        'document_id': _document.id,
                        'score': cosin_matrix[test_sentence_id][pos_in_template]})

                    if 'matchID' in _template_file_matchID_score:
                        if _template_file_matchID_score['score'] < cosin_matrix[test_sentence_id][pos_in_template]:
                            _template_file_matchID_score['matchId'] = test_sentence_id
                            _template_file_matchID_score['score'] = cosin_matrix[test_sentence_id][pos_in_template]
                        else:
                            pass
                    else: 
                        _template_file_matchID_score['matchId'] = test_sentence_id
                        _template_file_matchID_score['score'] = cosin_matrix[test_sentence_id][pos_in_template]

            except Exception as e:
                    print(e)
            res['templateFile'].append(
                {
                    'id': _document.id,
                    'name': _document.name,
                    'score': score,
                    'data': [
                        {
                            'id': sentence.id,
                            'content': sentence.content,
                            'matchId': _template_file_matchID_score['matchId'],
                            'score': _template_file_matchID_score['score']
                        } for sentence in Sentence.objects.filter(document_id=_document.id)
                    ]
                }
            )
    return res