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
from file_handle.download_by_url import download_file, url1
from file_handle.read_file import readPDFFile

# Create your views here.
class ComputeViewSet(APIView):
    
    def _compute(self, test_path, templates_path, mlmodel_id=1):
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
        test_sentences, test_sentences_tokenized = pipeline.preprocessing(readPDFFile(test_path))
        test_embedding = pipeline.embedding(test_sentences_tokenized)
        res['testFile'].append({
            'id': '0',
            'name': test_path.split('/')[-1],
            'data': [
                {
                    'id': str(i),
                    'content': sentence,
                    'matchId': None,

                } for i, sentence in enumerate(test_sentences)
            ]
            })
        for i, template_path in enumerate(templates_path):
            template_sentences, template_sentences_tokenized = pipeline.preprocessing(readPDFFile(template_path))
            template_embedding = pipeline.embedding(template_sentences_tokenized)
            res['templateFile'].append(
                {
                    'id': str(i+1),
                    'name': template_path.split('/')[-1],
                    'data': [
                        {
                            'id': i,
                            'content': sentence,
                            'matchId': None,

                        } for i, sentence in enumerate(template_sentences)
                    ]
                })
            score, cosin_matrix, positions = pipeline.compute(test_embedding, template_embedding)
            for test_sentence_id, pos_in_template in enumerate(positions):
                res['testFile'][0]['data'][test_sentence_id]['matchId'] = pos_in_template
                res['templateFile'][0]['data'][pos_in_template]['matchId'] = test_sentence_id
                res['templateFile'][0]['data'][pos_in_template]['score'] = cosin_matrix[test_sentence_id][pos_in_template]

                print(f"Cau {test_sentence_id} cua {res['testFile'][0]['name']} tuong dong voi")
                print(f"Cau {pos_in_template} cua {res['templateFile'][0]['name']}")
                print(f"voi so diem la {cosin_matrix[test_sentence_id][pos_in_template]}")
        return res

        

    def post(self, request):
        """
        request.data = {
            "test_path": "/home/sangnguyendesktop/Public/2021_Binh_Huong_2021_VCAA.pdf",
            "templates_path": [
                "/home/sangnguyendesktop/Public/2021_Binh_Huong_2021_VCAA.pdf",
                "/home/sangnguyendesktop/Public/20Hien_Thang_YdinhNCKHSV_2021_paper.pdf"
            ]
        }
        """
        try:
            
            res = self._compute(
                test_path=request.data['test_path'],
                templates_path=request.data['templates_path'],
                mlmodel_id=request.data['mlmodel_id'] if 'mlmodel_id' in request.data else 1
            )
        except Exception as e:
            res = None
            print(e) 

        return Response(res,status=status.HTTP_201_CREATED)

class ComputeViewSetTODO(APIView):
    
    def _create_document_object(self, data=None, pipeline=None, compute=False,test_document_dict=None):
        document_id = None
        document_object = None
        teamplate_nparrays = []
        compute_output = {}

        if compute == True:
            try:
                # test_bytes = [base64.b64decode((sentence_data['encode'])) for sentence_data in test_document_dict['sentences_data']]
                # test_nparrays = [pickle.loads(test_byte) for test_byte in test_bytes]

                test_byte = base64.b64encode(b'VrUGlrbWdyNHdtZEk4V2xZRFBjR0dUVDQ1VUpVK0VlaVlQdGNoU0Q3QW5wVzhwNE9TUFFqOG5qNyswNGE5R3NmWXZ0WkJDTDVTTmltKyt3a0JQMk5WSEwxQTE0WStmVTJndnF1WHpEdlRBYUErQXJhQVBnTzhEejlDM1EyK3k2eTdQdEMwR0wwWXZiVTk5OUVrdm40TnBUME5Ma2crWXZkNVBCUUo3VHRVc29RK0lnbE9QcjE0WDc0dkZjMisrdzJzdm0yZGtqNmNYSkMrczJ5R1BZSHVsVDFtais2K0ZTQzJ2V3hLNWI3eHkxYTlSY1crdm13YlJEMHdxcWk4VkltWVBmeHlDVDlmWkVFL2ZZL0t2aG0rcTc2dzNFbTk2NTAvUGlSS25UNDQxVXcrS3cxblBzZUxPRDRTZnBnK09PbWN2ckhEcno1Mm5sbStRc0JNdnNnWCtMMGk5S0ErNHJwVXZqeTl4ejJlb2VhODVvQ1BQbjdGQUwzcFkrbSszMWpJdkgyd09MNVNXenUrTURxZ3ZzMU1YcjVpT011K0d6U1p2bXpmamo1c252cStiRlQyUFd0UXN6NXcrSnU5V25wK3ZqMEZOVDYrUGZVOVNpL1pQdHJBNkwwMStGMCtiaWE2dlpHSXBMNzVpZ1c5ckNGSnZtNXRIeit4eWNhK0ZlVml2bjJFb0QyaDExaStnaG53UFdJU2c3ek5Kd2cvTy8wZU94V2xhcjVlVWZrOW9ycUN2cllQcEx4NU11aTk2VU5hUFRCTzFEMHdUT2krTGdsbFB1Y3pyejZMK2EyKy9jTjh2MkxKZHI1SGM1ZStTVjhXdlVNdkRqMFZPa2UrTCtxT1BtZXZxRDVkSzhHOWg0b0VQdWErdFQwaTJJRSswVFFVUHBRYnlMelFjN2krZVUyS1B2UFgwNzE5d1l5OFZlbW5QZXlFeHI0bjJ3aytQcVFJUGtqU2NELytyZ085aEZHSVByYXhsRDZYRlJ1L3VkU0V2ZzJsdTd6a1lERStuSThjUGpodXpEeUNYbzArVnBHL1BrTGF5RHE1Q3JZK2dtRWdQZ2VOMXo1TFZkdzlsV0JKdmtEVXByMFNVYmE5V1lWQ3Zwb0hXTDFDdjVhK0ZQVmJQdXJlcFQ1WjhrazkzMk5oUEUzQjBqNjQxK1ErU2k4RVB5dlBaYjU0ZlVrK1hzRGJQcXVCaEQ0a2x1ZytFNzRjUHpqUFFMc3hjVjArOXYycnZWRGRBcjVDZW5NOXZDU1F2b2VnQnI5VVVSQStoVmtVUCtOYUpMNXJpakM5Y2ZxWFBzcGkxcjZwUFFNK2xTYlJQVXlMTWo1WjhiQytIRjJPUFIvSHV6M0t4MVUrMzNHUlBrcHhlajZOQkhXK0luaGx2bDVVazc2SHM5SStHQ1lWdnNCVjJydDVzYUUrbjB0M3ZlbVYvRDBrbk5TOE1Jd0tQMUN6T0QzKzdPRThlY3RuUG5XTU83NHhSTDg5YkkyU1B1cDBJVDcvQXJJK3ZvemxQaFA0cDcxMjBJNDl4cDBqUFVqTVlEMHhFYUUrZHMvTXZmalhuejBpdFJjK0E5QlR2bzJtMkQ3dTZ1USs1bzRpdnNEbit6NXZMbEUrRWl3OHZSQ051VDdlQ0RJK05TQ2hQczh1Z2I0ZXpsRSt6NHZ4dlRFSWhiNjE0VWkrdlIzTlBrTDlhRDcyckg2K1Rka092bytLVzc2c2Q1TzlWVXA5dlRQeGtqNUFJMkM5TEV0T3Zrd3pPcjVDb1hTK0VJSUhQOHhQbjcwVXJrUTlPUHk4UFFKWE1yMDlVS3MrZ0cxd1BRb01RVDVmQUhZKzJvemRQYVh4Uzc2M1RzSTk4dExRdnNOYkJ6NkhlcHk3YTVJOVBqU0xvNzVuNFpnK2E5VlR2Y3BVT0x5UUtEQS9RUlNJdmVOZUJiK1VkSlJpTGc9PQ=="')
                test_nparray = pickle.loads(test_byte)
            except Exception as e:
                print('# compute with test file:', e)


        if data:
            document_data_dict = data
            # download file 
            document = download_file(url=url1, filename=document_data_dict['name']) # Change later: url, filename from post request)
            document_data_dict['document'] = document
            # readfile
            content = readPDFFile(document)
            # text normalize
            if pipeline:
                content =  pipeline.text_normalize(content)
                document_data_dict['content'] = content
            # preprocessing
            document_data_dict['pre_processing'] = False
            document_serializer = DocumentSerializer(data=document_data_dict)
            if DocumentSerializer.is_valid(document_serializer):
                """
                IF DOCUMENT IS VALID, CREATE SENTENCES OBJECTS OF THIS DOCUMENT
                Inner task: PREPROCESSING annd CREATE SENTENCE OBJECT
                """
                # save Document Object and get document_id
                document_id, document_object = document_serializer.save()
                # sentence tokenizing and get sentences list
                sentences = pipeline.sent_tokenize(content)
                for i, sentence in enumerate(sentences):
                    print(f'Processing at sentence_{i+1}/{len(sentences)} of document_{document_id}\n---------------*--------------')
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

                            # COMPUTE:
                            if compute == True:
                                teamplate_nparrays.append(encode)
                        except Exception as e:
                            print('Encoding:',e)

                    sentence_serializer = SentenceSerializer(data={
                        'document': document_id,
                        'content': content,
                        'is_tokenized': is_tokenized,
                        'content_tokenized': content_tokenized,
                        'is_encode': is_encode,
                        'encode': encode_base64,
                    })
                    if SentenceSerializer.is_valid(sentence_serializer):
                        _ = sentence_serializer.save()

                if compute == True:
                    compute_output['score'], compute_output['cosin_array'] = pipeline.compute(test_nparrays, teamplate_nparrays)

            else:
                print(document_serializer.errors)
        res = DocumentSerializer(document_object).data
        res['sentences_data'] = [SentenceSerializer(sentence_object).data for sentence_object in Sentence.objects.filter(document_id=document_id)]
        
        if compute_output == True:
            print(compute_output)
            res['compute_output'] = compute_output
        return res

    
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
        user_id = request.data['user']
        # mlmodel_id = request.data['mlmodel']
        mlmodel_id = 1
        print(registry)
        pipeline = registry.model[mlmodel_id]

        # TEST FILE
        try:  
            res['testFile']  = self._create_document_object(
                data={
                    'user': user_id,
                    'name': 'test.pdf',
                    'file_type': 'pdf',
                    'url': request.data['testFile'][0]['url'],
                },
                pipeline=pipeline
            )
        except Exception as e:
            print('_create_document_object', e)
        
        # TEMPALTE FILES
        try:  
            for template in request.data['templateFile']:
                pass
                res['templateFile'].append(self._create_document_object(
                    data={
                        'user': user_id,
                        'name': 'template.pdf',
                        'file_type': 'pdf',
                        'url': template['url'],
                    },
                    pipeline=pipeline,
                    compute=True,
                    test_document_dict=res['testFile']
                ))
        except Exception as e:
            print('_create_document_object', e)        

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
