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
from search_internet.search_internet import search_downloadPDF

# Create your views here.
class SearchOnInternetViewSet(APIView):
    
    def post(self, request):
        """
        UBUNBU PATH EXAMPLE
        request.data = {
            "testFile": "/home/sangnguyendesktop/Public/2021_Binh_Huong_2021_VCAA.pdf",
            "templateFile": [
                "/home/sangnguyendesktop/Public/2021_Binh_Huong_2021_VCAA.pdf",
                "/home/sangnguyendesktop/Public/20Hien_Thang_YdinhNCKHSV_2021_paper.pdf"
            ]
        }
        WINDOW PATH EXAMPLE
        request.data = {
            "testFile": "C:/Users/Sang Nguyen Desktop/Downloads/2021_Binh_Huong_2021_VCAA.pdf"
        }
        """
        res = None
        try: 
            res = _search_on_internet(
                req=request.data,
                pipelines=registry.models
            )
        except Exception as e:
            print(f'POST - searchinternet. Maybe because of : {e}')

        return Response(res,status=status.HTTP_201_CREATED)

# 1 vs 1
class ComputeViewSet(APIView):

    def post(self, request):
        """
        UBUNBU PATH EXAMPLE
        request.data = {
            "testFile": "/home/sangnguyendesktop/Public/2021_Binh_Huong_2021_VCAA.pdf",
            "templateFile": [
                "/home/sangnguyendesktop/Public/2021_Binh_Huong_2021_VCAA.pdf",
                "/home/sangnguyendesktop/Public/20Hien_Thang_YdinhNCKHSV_2021_paper.pdf"
            ]
        }
        WINDOW PATH EXAMPLE
        request.data = {
            "testFile": "C:/Users/Sang Nguyen Desktop/Downloads/2021_Binh_Huong_2021_VCAA.pdf",
            "templateFile": [
                "C:/Users/Sang Nguyen Desktop/Downloads/20Hien_Thang_YdinhNCKHSV_2021_paper.pdf"
            ]
        }
        """
        try:
            
            res = _compute(
                test_path=request.data['testFile'],
                templates_path=request.data['templateFile'],
                mlmodel_id=request.data['mlmodel_id'] if 'mlmodel_id' in request.data else 1
            )
        except Exception as e:
            res = None
            print(e) 

        return Response(res,status=status.HTTP_201_CREATED)
# 1 vs many
class ComputeCreateViewSet(APIView):
    
    def post(self, request):
        """
        UBUNBU PATH EXAMPLE
        request.data = {
            "testFile": "/home/sangnguyendesktop/Public/2021_Binh_Huong_2021_VCAA.pdf",
            "templateFile": [
                "/home/sangnguyendesktop/Public/2021_Binh_Huong_2021_VCAA.pdf",
                "/home/sangnguyendesktop/Public/20Hien_Thang_YdinhNCKHSV_2021_paper.pdf"
            ]
        }
        WINDOW PATH EXAMPLE
        request.data = {
            "user": "npsang"
            "testFile": ["C:/Users/Sang Nguyen Desktop/Downloads/2021_Binh_Huong_2021_VCAA.pdf"],
            "templateFile": [
                "C:/Users/Sang Nguyen Desktop/Downloads/20Hien_Thang_YdinhNCKHSV_2021_paper.pdf"
            ]
        }
        """
        try:
            
            res = _compute_create_document_object(
                req=request.data,
                pipelines=registry.models
            )
            print(res)
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

# 1 vs 1
def _compute(test_path, templates_path, mlmodel_id=1, is_cross=0):
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
    pipeline_cross=registry.crossmodel[mlmodel_id]
    test_text, test_lang = read_file(test_path, get_language=True)
    if test_text:
        test_sentences, test_sentences_tokenized = pipeline.preprocessing(test_text)
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
                    'lang' : test_lang

                } for i, sentence in enumerate(test_sentences)
            ]
            })
        for i, template_path in enumerate(templates_path):
            if res['testFile']['lang']=='vi'and res['templateFile']['lang']=='vi':
                template_text, template_lang = read_file(template_path, get_language=True)
                template_sentences, template_sentences_tokenized = pipeline.preprocessing(template_text)
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
                                'lang' : template_lang

                            } for i, sentence in enumerate(template_sentences)
                        ]
                    }
                )
            else:
                template_text, template_lang = read_file(template_path)
                template_sentences, template_sentences_tokenized = pipeline_cross.preprocessing(template_text)
                template_embedding = pipeline_cross.embedding(template_sentences_tokenized)
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
                                'lang' : template_lang

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

# 1 vs many        
def _compute_create_document_object(req, pipelines):

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
    # Preparing test
    _test_document, _create= Document.objects.get_or_create(
        path=req['testFile'],
        name=req['testFile'].split('/')[-1],
        user=User.objects.get_or_create(username=req['user'])[0]
    )
    if _create:
        _test_sentences, _test_sentences_tokenized, _test_language, _test_embeddings = __after_created_new_document_object(
            _test_document, pipelines)
    else:
        _test_sentences, _test_sentences_tokenized, _test_language, _test_embeddings = __get_document_object_data(_test_document)

    # HANDLE EMPTY TEXT FILE
    if _test_sentences is None:
        return res

    # add test respone
    res['testFile'].append(
        {
            'id': _test_document.id,
            'name': _test_document.name,
            'data': [
                {
                    'id': sentence.id,
                    'content': sentence.content,
                    'matchId': None,
                    'score': []
                } for sentence in Sentence.objects.filter(document_id=_test_document.id)
            ]
        }
    )
    # Preparing template

    for _path in req['templateFile']:
        print(f'{_path}')
        _template_file_matchID_score = {}
        _pipeline = None
        _test_embedding = None
        _embedding = None

        
        _template_document, _is_create = Document.objects.get_or_create(
            path=_path,
            name=_path.split('/')[-1],
            user=User.objects.get_or_create(username=req['user'])[0],
        )
        if _is_create:
            __sentences, __sentences_tokenized, __language, __embeddings = __after_created_new_document_object(
                _template_document, pipelines)
        else:
            __sentences, __sentences_tokenized, __language, __embeddings = __get_document_object_data(_template_document)

        # HANDLE EMPTY TEXT FILE
        if __sentences is None:
            continue
        # DO COMPUTE
        # compute shit
        if _test_language == 'vi' and __language == 'vi':
            """
            test_language == template_language == 'vi'. Using vietnamese compute similarity pipeline
            Using vietnamese embedding
            """
            _type = 'vi'
        else:
            """
            different language files. Using cross language similarity pipeline
            Using cross embedding
            """           
            _type = 'cross'

        _pipeline = pipelines[_type]
        _test_embedding = next(item for item in _test_embeddings if item['type'] == _type)['embedding']
        _embedding = next(item for item in __embeddings if item['type'] == _type)['embedding']

        score, cosin_matrix, positions = _pipeline.compute(_test_embedding, _embedding)
        
        # Return respone
        _test_file = res['testFile'][0]['data']
        for test_sentence_id, pos_in_template in enumerate(positions):
            # GET testFile from res
            _test_file[test_sentence_id]['matchId'] = test_sentence_id
            _test_file[test_sentence_id]['score'].append({
                'document_id': _template_document.id,
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
            
            res['templateFile'].append(
                {
                    'id': _template_document.id,
                    'name': _template_document.name,
                    'score': score,
                    'data': [
                        {
                            'id': sentence.id,
                            'content': sentence.content,
                            'matchId': _template_file_matchID_score['matchId'],
                            'score': _template_file_matchID_score['score']
                        } for sentence in Sentence.objects.filter(document_id=_template_document.id)
                    ]
                }
            )

    return res

def _search_on_internet(req, pipelines):
    """"
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
    # Preparing test
    _test_document, _create= Document.objects.get_or_create(
        path=req['testFile'],
        name=req['testFile'].split('/')[-1],
        user=User.objects.get_or_create(username=req['user'])[0]
    )
    if _create:
        _test_sentences, _test_sentences_tokenized, _test_language, _test_embeddings = __after_created_new_document_object(
            _test_document, pipelines)
    else:
        _test_sentences, _test_sentences_tokenized, _test_language, _test_embeddings = __get_document_object_data(_test_document)

    # HANDLE EMPTY TEXT FILE
    if _test_sentences is None:
        return res
    # add test respone
    res['testFile'].append(
        {
            'id': _test_document.id,
            'name': _test_document.name,
            'data': [
                {
                    'id': sentence.id,
                    'content': sentence.content,
                    'matchId': None,
                    'score': []
                } for sentence in Sentence.objects.filter(document_id=_test_document.id)
            ]
        }
    )

    # Preparing template
    # Use sentences tokenize to make search query and search on internet using Google Search API
    _template_path, _template_url = search_downloadPDF(
        sents=_test_sentences_tokenized,
        langOfText=_test_language,
        num_of_keyword=req['number_of_keyword'],
        num_of_result=req['number_of_result'],
    )
    print(len(_template_path), len(_template_url))
    for _path, _url in zip(_template_path, _template_url):
        print(f'{_path} - {_url}')
        _template_file_matchID_score = {}
        _pipeline = None
        _test_embedding = None
        _embedding = None

        
        _template_document, _is_create = Document.objects.get_or_create(
            path=_path,
            name=_path.split('/')[-1],
            user=User.objects.get_or_create(username=req['user'])[0],
            url=_url
        )
        if _is_create:
            __sentences, __sentences_tokenized, __language, __embeddings = __after_created_new_document_object(
                _template_document, pipelines)
        else:
            __sentences, __sentences_tokenized, __language, __embeddings = __get_document_object_data(_template_document)

        # HANDLE EMPTY TEXT FILE
        if __sentences is None:
            continue
        # DO COMPUTE
        # compute shit
        if _test_language == 'vi' and __language == 'vi':
            """
            test_language == template_language == 'vi'. Using vietnamese compute similarity pipeline
            Using vietnamese embedding
            """
            _type = 'vi'
        else:
            """
            different language files. Using cross language similarity pipeline
            Using cross embedding
            """            
            _type = 'cross'

        _pipeline = pipelines[_type]
        _test_embedding = next(item for item in _test_embeddings if item['type'] == _type)['embedding']
        _embedding = next(item for item in __embeddings if item['type'] == _type)['embedding']
        score, cosin_matrix, positions = _pipeline.compute(_test_embedding, _embedding)

        # Return respone
        _test_file = res['testFile'][0]['data']
        for test_sentence_id, pos_in_template in enumerate(positions):
            # GET testFile from res
            _test_file[test_sentence_id]['matchId'] = test_sentence_id
            _test_file[test_sentence_id]['score'].append({
                'document_id': _template_document.id,
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
            
            res['templateFile'].append(
                {
                    'id': _template_document.id,
                    'name': _template_document.name,
                    'score': score,
                    'url': _template_document.url,
                    'data': [
                        {
                            'id': sentence.id,
                            'content': sentence.content,
                            'matchId': _template_file_matchID_score['matchId'],
                            'score': _template_file_matchID_score['score']
                        } for sentence in Sentence.objects.filter(document_id=_template_document.id)
                    ]
                }
            )

    return res

def __after_created_new_document_object(document, pipelines):
    """
    after get_or_create if create == true that method will create a new document object
    this function will preprocess new data and store to this new document object
    and return good things
    """
    _sentences, _sentences_tokenized, _lang, _embeddings = None, None, None, None
    # READ DOCUMENT AND DO SENTENCES TOKENIZE
    _text, _lang = read_file(document.path, get_language=True)
    if _text:
        document.language = _lang
        _sentences, _sentences_tokenized  = __create_sentence_object_by_processing_document(document, _text, _lang, pipelines)
        _embeddings = []
        # If language='vi' encode two times, once for vietnamese encode, once for cross encode
            # ENCODE THE DOCUMENT sentences_tokenized, language, pipelines)
        if _lang == 'vi':
            _embedding_vi = __processand_store_embedding(document,_sentences_tokenized, language='vi', pipelines=pipelines)
            _embeddings.append(
                {
                    'type': 'vi',
                    'embedding': _embedding_vi,
                }
            )

        _embedding_cross = __processand_store_embedding(document,_sentences_tokenized, language='en', pipelines=pipelines)
        _embeddings.append(
            {
                'type': 'cross',
                'embedding': _embedding_cross,
            }
        )
        document.save()
        return _sentences, _sentences_tokenized, _lang, _embeddings
    return _sentences, _sentences_tokenized, _lang, _embeddings


def __get_document_object_data(document):
    _sentences, _sentences_tokenized, _lang, _embeddings = None, None, None, None
    try:
        _sentence_objects = [sentence for sentence in Sentence.objects.filter(document_id=document.id)]
        if len(_sentence_objects) > 0 :
            _sentences = [sentence.content for sentence in _sentence_objects]
            _sentences_tokenized = [sentence.content_tokenized for sentence in _sentence_objects]
            _lang = document.language

            _embeddings = []
            if document.is_vi_encode:
                _vi_np_bytes = base64.b64decode(document.vi_encode)
                _embedding_vi = pickle.loads(_vi_np_bytes)
                _embeddings.append(
                    {
                        'type': 'vi',
                        'embedding': _embedding_vi,
                    }
                )

            _cross_np_bytes = base64.b64decode(document.cross_encode)
            _embedding_cross = pickle.loads(_cross_np_bytes)
            _embeddings.append(
                {
                    'type': 'cross',
                    'embedding': _embedding_cross,
                }
            )

    except Exception as e:
        print(f'Get : {e}')
    return _sentences, _sentences_tokenized, _lang, _embeddings

def __create_sentence_object_by_processing_document(document, text, language, pipelines):
    """"
    params:
        document (object): document object
        text (str): text extract from the document file
        language (str): 'vi' or 'en' stand for vietnamese document or english document
        pipelines (dict): pipelines dict {'vi': VietnameseComputeSimilarity(class),
                                    'cross': ViEnCrossSimilarity (class)}
    return
        _sentences (list): list sentence which had sentence tokenized by pipeline
        _sentences_tokenized (list): list sentence which had sentence tokenized and word tokenized by pipeline
    """
    _pipeline = None
    if language == 'vi':
        _pipeline = pipelines['vi']
    elif language == 'en':
        _pipeline = pipelines['cross']
    if _pipeline:
        try:
            _sentences, _sentences_tokenized = _pipeline.preprocessing(text)
            ## CREATE SENTENCE OBJECT
            for _sentence, _sentence_tokenized in zip(_sentences, _sentences_tokenized):
                sentence_serializer = SentenceSerializer(
                    data={
                        'document': document.id,
                        'content': _sentence,
                        'content_tokenized': _sentence_tokenized,
                        'is_tokenized': True if _sentence_tokenized else False,
                    }
                )
                if SentenceSerializer.is_valid(sentence_serializer):
                    sentence_serializer.save()
                else:
                    print(sentence_serializer.errors)
            return _sentences, _sentences_tokenized
        except Exception as e:
            print(f'Create sentence object by processing document: {document.name}')
        
    return None

def __processand_store_embedding(document, sentences_tokenized, language, pipelines):
    """
    params:
        document (object): document object
        sentences_tokenized (list): sentences tokenized list of document
        language (str): language of document
        pipelines (dict): pipelines dict {'vi': VietnameseComputeSimilarity(class),
                                        'cross': ViEnCrossSimilarity (class)}
    return:
        _embedding (numpy array): embedding of document by pipeline
    """
    if language == 'vi':
        _pipeline = pipelines['vi']
        _embedding = _pipeline.embedding(sentences_tokenized)
        if _embedding.any():
            document.is_vi_encode = True
            __np_bytes = pickle.dumps(_embedding)
            __np_base64 = base64.b64encode(__np_bytes)
            document.vi_encode = __np_base64
        document.save()
        return _embedding

    elif language == 'en':
        _pipeline = pipelines['cross']
        _embedding = _pipeline.embedding(sentences_tokenized)
        if _embedding.any():
            document.is_cross_encode = True
            __np_bytes = pickle.dumps(_embedding)
            __np_base64 = base64.b64encode(__np_bytes)
            document.cross_encode = __np_base64
        document.save()
        return _embedding
    else:
        print(f'__processand_store_embedding: invalid language {language}')
        return None