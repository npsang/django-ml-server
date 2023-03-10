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
    ListDocumentSerializer,
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
            # res = JSONRenderer().render(res, renderer_context={'indent': 4})
        except Exception as e:
            print(f'POST - searchinternet. Maybe because of : {e}')

        return Response(res,status=status.HTTP_201_CREATED)
        # return HttpResponse(res,status=status.HTTP_201_CREATED)

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
            # res = JSONRenderer().render(res, renderer_context={'indent': 4})
        except Exception as e:
            res = None
            print(e)
        
        return Response(res,status=status.HTTP_201_CREATED)
        # return HttpResponse(res,status=status.HTTP_201_CREATED)

# Many vs Many
class ComputesViewSet(APIView):
    
    def post(self, request):
        res = _compute_many_with_many(
            req=request.data,
            pipelines=registry.models
        )
        return Response(res, status=status.HTTP_201_CREATED)

class MLModelViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = MLModel.objects.filter(active=True)
    serializer_class = MLModelSerializer

    def get_permissions(self):
        return [permissions.AllowAny()]

class ListDocumentViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Document.objects.filter(active=True)
    serializer_class = ListDocumentSerializer

class DocumentViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = Document.objects.filter(active=True)
    serializer_class = DocumentSerializer

class SentenceViewSet(viewsets.ViewSet, generics.RetrieveAPIView, generics.ListAPIView):
    queryset = Sentence.objects.filter(active=True)
    serializer_class = SentenceSerializer

class UserViewSet(viewsets.ViewSet, generics.CreateAPIView,
                    generics.ListAPIView, generics.RetrieveAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer

# Many vs Many
def _compute_many_with_many(req, pipelines):
    # Get data from request
    _test_files_path = req['testFile']
    _templates_files_path = req['templateFile']
    _user_name = req['user']
    _threshold = float(req['threshold'])

    _res = {'testFile': [], 'templateFile': []}
    # test_files and template_files must be type of list
    _templates_data_to_compute = []
    for _template_file_path in _templates_files_path:
        _template_success, _template_document_id, _template_document_name, _template__document_url, _template_sentences_id, _template_sentences, \
            _template_tokenized_sentences, _template_language, _template_embeddings = None, None, None, None, None, None, None, None, None
        # prepare template
        _template_success, _template_document_id, _template_document_name, _template__document_url, _template_sentences_id, _template_sentences, \
            _template_tokenized_sentences, _template_language, _template_embeddings = __prepare_data(_template_file_path, _user_name, pipelines)
        if not _template_success:
            print(f'Error when preprare template file: {_template_file_path}')
            continue
        else:
            _templates_data_to_compute.append(
                {
                    'language': _template_language,
                    'embeddings': _template_embeddings,
                    'document_id': _template_document_id,
                    'sentences_id': _template_sentences_id,
                    'name': _template_document_name
                }
            )

        # make respone
        __do_template_respone(_res, _template_success, _template_document_id, _template_document_name,
                            _template__document_url, _template_sentences_id, _template_sentences)

    
    for _test_file_path in _test_files_path:
        _test_success, _test_document_id, _test_document_name, _test_document_url, _test_sentences_id, _test_sentences, \
            _test_tokenized_sentences, _test_language, _test_embeddings, _1many_result = None, None, None, None, None, None, None, None, None, None
        _templates_id, _templates_score, _templates_quantity, _compute_type, _templates_name = [], [], [], [], []
        # Prepare test
        _test_success, _test_document_id, _test_document_name,  _test_document_url, _test_sentences_id, _test_sentences, \
            _test_tokenized_sentences, _test_language, _test_embeddings = __prepare_data(_test_file_path, _user_name, pipelines)

        if not _test_success:
            print(f'Error when preprare test file: {_test_file_path}')
            continue
        # compute stuff
        for _template_data in _templates_data_to_compute:
            _type, __test_embedding, __template_embedding, __template_language, __template_embeddings,\
                __template_document_id, __template_sentences_id, _11_result = None, None, None, None, None, None, None, None
            
            __template_language = _template_data['language']
            __template_embeddings = _template_data['embeddings']
            __template_document_id = _template_data['document_id']
            __template_sentences_id = _template_data['sentences_id']
            __template_document_name = _template_data['name']

            if _test_language == 'vi' and __template_language == 'vi':
                _type = 'vi'
            elif _test_language == 'en' and __template_language == 'en':
                _type = 'en'
            else:
                _type = 'cross'
            
            _pipeline = pipelines[_type]
            __test_embedding = next(item for item in _test_embeddings if item['type'] == _type)['embedding']
            __template_embedding = next(item for item in __template_embeddings if item['type'] == _type)['embedding']

            _score, _cosin_matrix, _positisions = _pipeline.compute(
                doc_a=__test_embedding,
                doc_b=__template_embedding
            )
            _11_result = __make_res_compute_score(_score, _cosin_matrix, _positisions, __template_document_id, __template_sentences_id)
            
            _templates_id.append(__template_document_id)
            _templates_score.append(_score)
            _templates_quantity.append(len([item for item in _11_result if float(item['score']) > _threshold]))
            _compute_type.append(_type)
            _templates_name.append(__template_document_name)
            if not _1many_result:
                _1many_result = [[item] for item in _11_result]
            else:
                _1many_result = [[*_1many_result[i], item] for i, item in enumerate(_11_result)]
        # make respone for testFile
        __do_test_respone(_res, _test_success, _test_document_id, _test_document_name, _test_document_url, _test_sentences_id, _test_sentences, \
            _1many_result, _templates_id, _templates_name, _templates_score, _templates_quantity, _compute_type)

    return _res

# Search on internet
def _search_on_internet(req, pipelines):
    # Get data from request
    _test_files_path = req['testFile']
    _user_name = req['user']
    _threshold = float(req['threshold'])
    _number_of_keyword = req['number_of_keyword']
    _number_of_result = req['number_of_result']

    _res = {'testFile': [], 'templateFile': []}
    # test_files must be type of list
    for _test_file_path in _test_files_path:
        _test_success, _test_document_id, _test_document_name, _test_sentences_id, _test_sentences, \
            _test_tokenized_sentences, _test_language, _test_embeddings, _1many_result = None, None, None, None, None, None, None, None, None
        _templates_id, _templates_score, _templates_quantity, _compute_type, _templates_name = [], [], [], [], []
        _templates_path, _templates_url = None, None
        # Prepare test
        _test_success, _test_document_id, _test_document_name,  _test_document_url, _test_sentences_id, _test_sentences, \
            _test_tokenized_sentences, _test_language, _test_embeddings = __prepare_data(_test_file_path, _user_name, pipelines)
        if not _test_success:
            print(f'Error when preprare test file: {_test_file_path}')
            continue

        # Search and download file as template from internet
        _templates_path, _templates_url = search_downloadPDF(
            sents=_test_tokenized_sentences,
            langOfText=_test_language,
            num_of_keyword=_number_of_keyword,
            num_of_result=_number_of_result,
        )

        # Prepare template
        for _template_file_path, _template_file_url in zip(_templates_path, _templates_url):
            _template_success, _template_document_id, _template_document_name, _template_sentences_id, _template_sentences, \
                _template_tokenized_sentences, _template_language, _template_embeddings = None, None, None, None, None, None, None, None
            _pipeline = None
            # prepare template
            _template_success, _template_document_id, _template_document_name, _template_document_url, _template_sentences_id, _template_sentences, \
                _template_tokenized_sentences, _template_language, _template_embeddings = __prepare_data(_template_file_path, _user_name, pipelines, _template_file_url)
            if not _template_success:
                print(f'Error when preprare template file: {_template_file_path}')
                continue

            # make respone
            __do_template_respone(_res, _template_success, _template_document_id, _template_document_name,
                    _template_document_url, _template_sentences_id, _template_sentences)

            # Compute
            if _test_language == 'vi' and _template_language == 'vi':
                _type = 'vi'
            elif _test_language == 'en' and _template_language == 'en':
                _type = 'en'
            else:
                _type = 'cross'

            _pipeline = pipelines[_type]
            _test_embedding = next(item for item in _test_embeddings if item['type'] == _type)['embedding']
            _template_embedding = next(item for item in _template_embeddings if item['type'] == _type)['embedding']
            _score, _cosin_matrix, _positisions = _pipeline.compute(
                doc_a=_test_embedding,
                doc_b=_template_embedding
            )
            _11_result = __make_res_compute_score(_score, _cosin_matrix, _positisions, _template_document_id, _template_sentences_id)
            _templates_id.append(_template_document_id)
            _templates_score.append(_score)
            _templates_quantity.append(len([item for item in _11_result if float(item['score']) > _threshold]))
            _compute_type.append(_type)
            _templates_name.append(_template_document_name)
            if not _1many_result:
                _1many_result = [[item] for item in _11_result]
            else:
                _1many_result = [[*_1many_result[i], item] for i, item in enumerate(_11_result)]
        # make reponse for testFile
        __do_test_respone(_res, _test_success, _test_document_id, _test_document_name,_test_document_url, _test_sentences_id, _test_sentences, \
            _1many_result, _templates_id, _templates_name, _templates_score, _templates_quantity, _compute_type)

    return _res

# inner function
def __make_res_compute_score(score, cosin_matrix, positisions, template_document_id, template_sentences_id):
    try:
        _res_score = []
        for test_sentence_id, pos_in_template in enumerate(positisions):
            _res_score.append(
                {
                            'document_id': template_document_id,
                            'score': str(round(cosin_matrix[test_sentence_id][pos_in_template].item(), 3)),
                            'sentence_id': template_sentences_id[pos_in_template]
                }
            )
        return _res_score
    except Exception as e:
        print(f'Err: __do_template_respone(). Maybe caused of {e}')

def __do_template_respone(res, success, document_id, document_name, document_url, sentences_id, sentences):
    if not success:
        return
    try:
        res['templateFile'].append(
            {
                'id': document_id,
                'name': document_name,
                'url': document_url,
                'data': [
                    {
                        'id': _id,
                        'content': _content
                    } for _id, _content  in zip(sentences_id, sentences)
                ]
            }
        )
    except Exception as e:
        print(f'Err: __do_template_respone(). Maybe caused of {e}')

def __do_test_respone(res, success, document_id, document_name, document_url, sentences_id, sentences, sentences_score, \
    templates_id, templates_name, templates_score, templates_quantity, compute_type):
    if not success:
        return
    try:
        res['testFile'].append(
            {
                'id': document_id,
                'name': document_name,
                'url': document_url,
                'data': [
                    {
                        'id': _id,
                        'content': _content,
                        'matchId': _i,
                        'score': score
                    } for _i, (_id, _content, score) in enumerate(zip(sentences_id, sentences, sentences_score))
                ],
                'info': [
                    {
                        'threshold': 0.8,
                        'id': _id,
                        'name': _name,
                        'score': str(round(_score.item(), 3)),
                        'type': _type,
                        'quantity': _quantity,
                    } for _id, _name, _score, _quantity, _type in zip(templates_id, templates_name, templates_score, templates_quantity, compute_type)
                ]
            }
        )
    except Exception as e:
        print(f'Error at __do_test_respone. Maybe cause of: {e}')

def __prepare_data(path, user_name, pipelines, url=''):
    _path = path
    _name = _path.split('/')[-1]
    _document_url = ''
    if not url:
        _document, _create = Document.objects.get_or_create(
            path=_path,
            name=_name,
            user=User.objects.get_or_create(username=user_name)[0]
        )
    else:
        _document, _create = Document.objects.get_or_create(
            path=_path,
            name=_name,
            user=User.objects.get_or_create(username=user_name)[0],
            url=url
        )
    if _create:
        _success, _sentences_id, _sentences, _tokenized_sentences, _language, _embeddings = \
            __after_created_new_document_object(_document, pipelines)
    else:
        _success, _sentences_id, _sentences, _tokenized_sentences, _language, _embeddings = \
            __get_document_object_data(_document)
    if _document.url:
        _document_url = _document.url
    return _success, _document.id, _document.name, _document_url, _sentences_id, _sentences, _tokenized_sentences, _language, _embeddings

def __after_created_new_document_object(document, pipelines):
    """
    after get_or_create if create == true that method will create a new document object
    this function will preprocess new data and store to this new document object
    and return good things
    """
    _success = False
    _sentences_id, _sentences, _sentences_tokenized, _lang, _embeddings = None, None, None, None, None
    # READ DOCUMENT AND DO SENTENCES TOKENIZE
    try:
        _text, _lang = read_file(document.path, get_language=True)
        document.language = _lang
        _sentences_id, _sentences, _sentences_tokenized  = __create_sentence_object_by_processing_document(document, _text, _lang, pipelines)
        _embeddings = []
        # If language='vi' encode two times, once for vietnamese encode, once for cross encode
            # ENCODE THE DOCUMENT sentences_tokenized, language, pipelines)
        if _lang == 'vi': # vietnamese
            _embedding_vi = __processand_store_embedding(document,_sentences_tokenized, language='vi', pipelines=pipelines)
            _embeddings.append(
                {
                    'type': 'vi',
                    'embedding': _embedding_vi,
                }
            )
        elif _lang == 'en': # english
            _embedding_en = __processand_store_embedding(document,_sentences_tokenized, language='en', pipelines=pipelines)
            _embeddings.append(
                {
                    'type': 'en',
                    'embedding': _embedding_en,
                }
            )
        else:   # different languages 
            pass
        _embedding_cross = __processand_store_embedding(document,_sentences_tokenized, language='cross', pipelines=pipelines)
        _embeddings.append(
            {
                'type': 'cross',
                'embedding': _embedding_cross,
            }
        )
        document.save()
        _success = True
    except Exception as e:
        print('__after_created_new_document_object', e)
    # READ DOCUMENT AND DO SENTENCES TOKENIZE
    return _success, _sentences_id, _sentences, _sentences_tokenized, _lang, _embeddings

def __get_document_object_data(document):
    _success = False
    _sentences_id, _sentences, _sentences_tokenized, _lang, _embeddings = None, None, None, None, None
    try:
        _sentence_objects = [sentence for sentence in Sentence.objects.filter(document_id=document.id)]
        _sentences = [sentence.content for sentence in _sentence_objects]
        _sentences_tokenized = [sentence.content_tokenized for sentence in _sentence_objects]
        _lang = document.language
        _sentences_id = [sentence.id for sentence in _sentence_objects]
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
        if document.is_en_encode:
            _en_np_bytes = base64.b64decode(document.en_encode)
            _embedding_en = pickle.loads(_en_np_bytes)
            _embeddings.append(
                {
                    'type': 'en',
                    'embedding': _embedding_en,
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
        _success = True
    except Exception as e:
        print(f'Get : {e}')
    return _success, _sentences_id, _sentences, _sentences_tokenized, _lang, _embeddings

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
    _sentences_id, _sentences, _sentences_tokenized = None, None, None
    _pipeline = None
    if language == 'vi':
        _pipeline = pipelines['vi']
    elif language == 'en':
        _pipeline = pipelines['cross']
    try:
        if _pipeline is not None:
            _sentences, _sentences_tokenized = _pipeline.preprocessing(text)
            _sentences_id = []
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
                    _id = sentence_serializer.save()
                    _sentences_id.append(_id)
                else:
                    print(sentence_serializer.errors)
        else:
            print('BUG: _pipeline not found')
    except Exception as e:
        print(f'Create sentence object by processing document: {document.name}')
    return _sentences_id, _sentences, _sentences_tokenized

def __processand_store_embedding(document, sentences_tokenized, language, pipelines):
    """
    params:
        document (object): document object
        sentences_tokenized (list): sentences tokenized list of document
        language (str): language of document
        pipelines (dict): pipelines dict {'vi': VietnameseComputeSimilarity(class instance),
                                        'en': EnglishComputeSimilarity (class instance)
                                        'cross': ViEnCrossSimilarity (class instance)}
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
        _pipeline = pipelines['en']
        _embedding = _pipeline.embedding(sentences_tokenized)
        if _embedding.any():
            document.is_en_encode = True
            __np_bytes = pickle.dumps(_embedding)
            __np_base64 = base64.b64encode(__np_bytes)
            document.en_encode = __np_base64
        document.save()
        return _embedding
    elif language == 'cross':
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
        _success, _test_sentences_id, _test_sentences, _, _test_language, _test_embeddings = \
            __after_created_new_document_object(_test_document, pipelines)
    else:
        _success, _test_sentences_id, _test_sentences, _, _test_language, _test_embeddings = \
            __get_document_object_data(_test_document)

    if _success == False:
        print('Error when process document data')
        return res
    # add test respone
    res['testFile'].append(
        {
            'id': _test_document.id,
            'name': _test_document.name,
            'url': None,
            'data': [
                {
                    'id': _id,
                    'content': _content,
                    'matchId': None,
                    'score': []
                } for _id, _content  in zip(_test_sentences_id, _test_sentences)
            ]
        }
    )
    # Preparing template
    count = 0
    for _path in req['templateFile']:
        count += 1
        print(f'\n---------------------------------\nProcessing {_path}, total: {count}//{len(req["templateFile"])}')
        _pipeline = None
        _test_embedding = None
        _embedding = None

        
        _template_document, _is_create = Document.objects.get_or_create(
            path=_path,
            name=_path.split('/')[-1],
            user=User.objects.get_or_create(username=req['user'])[0],
        )
        if _is_create:
            print('Creat new object: Processing Data')
            __success, __sentences_id, __sentences, __sentences_tokenized, __language, __embeddings = __after_created_new_document_object(
                _template_document, pipelines)
        else:
            print('Getting processed data from object')
            __success, __sentences_id, __sentences, __sentences_tokenized, __language, __embeddings = __get_document_object_data(_template_document)

        if __success == False:
            res['templateFile'].append(
                {
                    'id': _template_document.id,
                    'name': _template_document.name,
                    'score': None,
                    'url': None,
                    'data': [
                        {
                            'id': None,
                            'content': None
                        }
                    ]
                }
            )
            continue
        # DO COMPUTE
        # compute shit
        if _test_language == 'vi' and __language == 'vi':
            """
            test_language == template_language == 'vi'. Using vietnamese compute similarity pipeline
            Using vietnamese embedding
            """
            print('Use Vietnamese compute similarity pipeline')
            _type = 'vi'
        else:
            """
            different language files. Using cross language similarity pipeline
            Using cross embedding
            """      
            print('Use Cross compute similarity pipeline')
            _type = 'cross'

        print(f'Computing: ... {_template_document.name}', end=' ')
        _pipeline = pipelines[_type]
        print(f'pipeline: {_pipeline}')
        print(_test_embeddings)
        _test_embedding = next(item for item in _test_embeddings if item['type'] == _type)['embedding']
        _embedding = next(item for item in __embeddings if item['type'] == _type)['embedding']
        print('--------------------------')
        score, cosin_matrix, positions = _pipeline.compute(_test_embedding, _embedding)
        print('Done!!')
        print(f'score: {score} - len(position): {len(positions)}')
        print('Return respone...')
        # Return respone
        res['templateFile'].append(
            {
                'id': _template_document.id,
                'name': _template_document.name,
                'score': score,
                'url': None,
                'data': [
                    {
                        'id': _id,
                        'content': _content
                    } for _id, _content  in zip(__sentences_id, __sentences)
                ]
            }
        )
        _test_file = res['testFile'][0]['data']
        for test_sentence_id, pos_in_template in enumerate(positions):
            print(f'{test_sentence_id} - {pos_in_template}')
            # print(f'Processing at sentence_{test_sentence_id} of testFile - Pair with sentence_{pos_in_template} of templateFile')
            # GET testFile from res
            _test_file[test_sentence_id]['matchId'] = test_sentence_id
            _test_file[test_sentence_id]['score'].append({
                'document_id': _template_document.id,
                'score': cosin_matrix[test_sentence_id][pos_in_template],
                'sentence_id': __sentences_id[pos_in_template]
                }
            )
    return res
