from sentence_transformers import SentenceTransformer, util
import numpy as np
import os
from underthesea import text_normalize, sent_tokenize, word_tokenize

cwd = os.getcwd() # /home/sangnguyendesktop/Code/project/plagiarism

class ViEnCrossSimilarity:
    def __init__(self):
        path_to_artifacts = cwd+"/ml/compute_similarity/models/"
        self.text_normalize = text_normalize
        self.sent_tokenize = sent_tokenize
        self.model = SentenceTransformer(
            path_to_artifacts + 'ViEnCrossModel')

    def word_tokenize(self, input_data):
        return word_tokenize(input_data, format='text')

    def preprocessing(self, input_data):
        """
        1. Text Normalize
        2. Sentence tokenize
        3. Word tokenize
        """
        sentences = []
        sentences_w_word_tokenized = []
        normalized = self.text_normalize(input_data)
        for sentence in self.sent_tokenize(normalized):
            sentences_w_word_tokenized.append(self.word_tokenize(sentence))
            sentences.append(sentence)
        return sentences, sentences_w_word_tokenized


    def embedding(self, sentences): #sentences: list of tokenized sentences
        try:
            sentences = np.array(sentences)
            encode_sentences = self.model.encode(sentences)
            return encode_sentences
        except Exception as e:
            print(f'Embedding error: {e}')
            return None 

    def post_processing(self):
        pass

    def compute(self, doc_a, doc_b): #doc_a, doc_b : list of tokenized sentences of doc_a, doc_b
        res=util.cos_sim(doc_a,doc_b)
        temp=np.argmax(res,axis=1)
        sum_max=0.0
        for i in range(len(doc_a)):
            sum_max+=res[i][temp[i]]
        avg_cos_sim=sum_max/float(len(doc_a))
        return avg_cos_sim, res, temp       #return: cos_sim trung bình giữa doc_a với doc_b, array kết quả cos_sim giữa các câu, temp vi tri cac cau diem cao
