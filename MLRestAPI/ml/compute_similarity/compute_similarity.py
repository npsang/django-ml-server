from sentence_transformers import SentenceTransformer, util
import numpy as np
import os

cwd = os.getcwd() # /home/sangnguyendesktop/Code/project/plagiarism

class ComputeSimilarity:
    def __init__(self):
        path_to_artifacts = cwd+"/ml/compute_similarity/models/"
        print(path_to_artifacts)
        self.model = SentenceTransformer(
            path_to_artifacts + 'make-multilingual-sys-2023-01-12_01-42-22')

    def preprocessing(self, input_data):
        pass

    def embedding(self, docs): #docs: list of lists of tokenized sentences
        output = []
        for doc in docs:
            encode_doc = self.model.encode(doc)
            output.append(encode_doc)
        return output

    def post_processing(self):
        pass

    def compute(self, doc_a, doc_b): #doc_a, doc_b : list of tokenized sentences of doc_a, doc_b
        res=util.cos_sim(doc_a,doc_b)
        temp=np.argmax(res,axis=1)
        sum_max=0.0
        for i in range(len(doc_a)):
            sum_max+=res[i][temp[i]]
        avg_cos_sim=sum_max/float(len(doc_a))
        return avg_cos_sim, res       #return: cos_sim trung bình giữa doc_a với doc_b, array kết quả cos_sim giữa các câu
