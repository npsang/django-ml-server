from webbrowser import get
from cmath import pi
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from underthesea import word_tokenize, sent_tokenize, text_normalize
import requests
from bs4 import BeautifulSoup
from langdetect import detect
from googlesearch import search
import urllib.request
import pickle
import re
import concurrent.futures
import pypdfium2 as pdfium
import docx2txt


#num_of_keyword=5

def readPDFFile(filepath):
  pdf=pdfium.PdfDocument(filepath)
  n_pages=len(pdf)
  texts=[]
  for page in pdf:
    textpage=page.get_textpage()
    text_all=textpage.get_text_range()
    texts.append(text_all)
  output=' '.join(x for x in texts)
  return output
def readTXTFile(docFilePath):
    with open(docFilePath, 'r', encoding='utf-8') as f:
        text = f.read()
    return text
def readDOCXFile(docFilePath):
    text = docx2txt.process(docFilePath)
    return text
def inputFileProcessing(docPath):
    typeOfFile = docPath.split('.')[-1]
    text = ""
    if typeOfFile == 'pdf':
        text = readPDFFile(docPath)
    elif typeOfFile == 'docx' or typeOfFile == 'doc':
        text = readDOCXFile(docPath)
    else:
        text = readTXTFile(docPath)
    langOfText = detect(text)
    output=text_normalize(text)
    return output, langOfText
# Get a list of available stop words
def getStopWords(stopWordPath):
    with open(stopWordPath, 'r', encoding='utf-8') as f:
        stopWords = []
        word = f.readline().replace(' ', '_').replace('\n', '')
        while word != '':
            stopWords.append(word)
            word = f.readline().replace(' ', '_').replace('\n', '')
    return stopWords
# Get a list of vocabularies in the document
def getVocabs(text, stopwords):
    cv = CountVectorizer(stop_words=stopwords)
    cv.fit_transform([text])
    vocabs = [v for v in cv.get_feature_names_out()]
    return vocabs
# Reference source: https://stackoverflow.com/questions/10007463/sorting-in-sparse-matrix
def sort_coo(coo_matrix):
    tuples = zip(coo_matrix.col, coo_matrix.data)
    return sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)
# Extract n words with high score
def extract_topn_from_vector(feature_names, sorted_items, topn):
    sorted_items = sorted_items[:topn]
    score_vals = []
    feature_vals = []
    for idx, score in sorted_items:
        score_vals.append(round(score, 3))
        feature_vals.append(feature_names[idx])
    results = {}
    for idx in range(len(feature_vals)):
        results[feature_vals[idx]] = score_vals[idx]
    return results
# extract key words from the text
def extractKeyWord(tokenized_text, langOfText, num_of_keyword):
    # Create a Countvectorizer variable
    cv = CountVectorizer()
    # Word tokenize
    text = tokenized_text
    # Split 2 cases: English and Vietnamese
    if langOfText == 'vi':
        # Load stop word custom
        stopwords = pickle.load(open('stopwords.pk', 'rb'))
        # General a list of vocabularies
        vocabs = getVocabs(text, stopwords)
        cv = CountVectorizer(stop_words=stopwords, vocabulary=vocabs)
    else:
        vocabs = getVocabs(text, 'english')
        cv = CountVectorizer(stop_words='english', vocabulary=vocabs)
    wcv = cv.fit_transform([text])
    tfidf = TfidfTransformer(smooth_idf=True, use_idf=True)
    tfidf.fit(wcv)
    feature_names = cv.get_feature_names_out()
    tfidf_vector = tfidf.transform(cv.transform([text]))
    sorted_items = sort_coo(tfidf_vector.tocoo())
    keywords = extract_topn_from_vector(feature_names, sorted_items, num_of_keyword)
    print(keywords)
    return keywords

# Get the content of the page on the Internet
def getContentOnWebsite(link):
    # the target we want to open
    url = link
    # open with GET method
    resp = requests.get(url)
    text = []
    # http_respone 200 means OK status
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, 'html.parser')
        for i in soup.findAll("p"):
            text.append(i.text)
        return " ".join(text)
    else:
        print("Can not access the link")
        return False

'''----------------------------------------------------------------------------------------------
Model dịch anh việt'''

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


tokenizer_vi2en = AutoTokenizer.from_pretrained("vinai/vinai-translate-vi2en", src_lang="vi_VN")
model_vi2en = AutoModelForSeq2SeqLM.from_pretrained("vinai/vinai-translate-vi2en")
def translate_vi2en(vi_text: str) -> str:
    input_ids = tokenizer_vi2en(vi_text, return_tensors="pt").input_ids
    output_ids = model_vi2en.generate(
        input_ids,
        do_sample=True,
        top_k=100,
        top_p=0.8,
        decoder_start_token_id=tokenizer_vi2en.lang_code_to_id["en_XX"],
        num_return_sequences=1,
    )
    en_text = tokenizer_vi2en.batch_decode(output_ids, skip_special_tokens=True)
    en_text = " ".join(en_text)
    return en_text

tokenizer_en2vi = AutoTokenizer.from_pretrained("vinai/vinai-translate-en2vi", src_lang="en_XX")
model_en2vi = AutoModelForSeq2SeqLM.from_pretrained("vinai/vinai-translate-en2vi")

def translate_en2vi(en_text: str) -> str:
    input_ids = tokenizer_en2vi(en_text, return_tensors="pt").input_ids
    output_ids = model_en2vi.generate(
        input_ids,
        do_sample=True,
        top_k=100,
        top_p=0.8,
        decoder_start_token_id=tokenizer_en2vi.lang_code_to_id["vi_VN"],
        num_return_sequences=1,
    )
    vi_text = tokenizer_en2vi.batch_decode(output_ids, skip_special_tokens=True)
    vi_text = " ".join(vi_text)
    return vi_text
'''--------------------------------------------------------------------------------------------------'''
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
def download_pdf(url):
  downloadPath = '/content/' + \
              str(url).replace('/', '').replace('.', '').replace('http:', '') + '.pdf'
  try:
    urllib.request.urlretrieve(url, downloadPath)
    print(url)
    return downloadPath
  except Exception as E:
    pass
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
def search_downloadPDF(sents, langOfText, num_of_keyword=3, num_of_result=10, is_cross=0, timeout=5):      #input list các câu
  downloaded_file_path=[]
  if is_cross==1:           #xuyên ngữ
    if langOfText=='vi':
      text=' '.join(x for x in sents) 
      keywords=extractKeyWord(text,langOfText, num_of_keyword)
      query = ' '.join(keywords).replace("_", " ")
      query += ' filetype:pdf'
      print(query)
      try:
        listLinks_1 = search(query, lang='vi', num_results = num_of_result)
        listLinks_2 = search(translate_vi2en(query), lang='en', num_results = num_of_result)
        listLinks=[*listLinks_1,*listLinks_2]
        #for l in listLinks:
          #downloadPath = '/content/' + \
           #   str(l).replace('/', '').replace('.', '').replace('http:', '') + '.pdf'
        try: 
            with concurrent.futures.ThreadPoolExecutor() as executor:
                downloaded_file_path=executor.map(download_pdf, listLinks, timeout=timeout)
        except Exception as E:
            print(E)
            pass
      except Exception as E:
        print(E)
        pass
    elif langOfText=='en':
      text=' '.join(x for x in sents) 
      keywords=extractKeyWord(text,langOfText,num_of_keyword)
      query = ' '.join(keywords).replace("_", " ")
      query += ' filetype:pdf'
      print(query)
      try:
        listLinks_1 = search(query, lang='en', num_results = num_of_result)
        listLinks_2 = search(translate_en2vi(query), lang='vi', num_results = num_of_result)
        listLinks=[*listLinks_1,*listLinks_2]
        try: 
            with concurrent.futures.ThreadPoolExecutor() as executor:
                downloaded_file_path=executor.map(download_pdf, listLinks, timeout=timeout)
        except Exception as E:
            print(E)
            pass
      except Exception as E:
        print(E)
        pass
  else:
    text=' '.join(x for x in sents) 
    keywords=extractKeyWord(text,langOfText,num_of_keyword)
    query = ' '.join(keywords).replace("_", " ")
    query += ' filetype:pdf'
    print(query)
    try:
      listLinks = search(query, lang=langOfText, num_results = num_of_result)
      try: 
          with concurrent.futures.ThreadPoolExecutor() as executor:
                downloaded_file_path=executor.map(download_pdf, listLinks, timeout=timeout)
      except Exception as E:
          print(E)
          pass
    except Exception as E:
      print(E)
      pass
  output=[]
  for path in downloaded_file_path:
    if path!=None:
      output.append(path)
  return output 


x=['Bạn đang tìm kiếm công cụ giúp bạn kiểm tra xem bài viết của mình hay của bạn bè có phải bị đánh giá là đạo văn hay không?',
   'Hãy theo dõi bài viết để biết thêm 7 phần mềm, web kiểm tra đạo văn miễn phí và chính xác nhất.',
]

ex=search_downloadPDF(x,'vi',num_of_keyword=2,num_of_result=3,is_cross=1,timeout=5)
                      