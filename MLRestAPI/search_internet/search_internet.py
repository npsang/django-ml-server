import pickle
import requests
import concurrent.futures
import urllib.request
import time
import os
import random

from googlesearch import search
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

from MLRestAPI.wsgi import registry

translator = registry.models['translate']

CWD = os.getcwd()
STOPWORDS_PATH = CWD + '/search_internet/stopwords.pk'
DOWNLOAD_PATH = CWD + '/storage/'

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
        stopwords = pickle.load(open(STOPWORDS_PATH, 'rb'))
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
def getContentOnWebsite_save2txt(url):
    # open with GET method
    user_agents = [
                    "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",
                    "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
                    "Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
                  ]
    random_user_agent = random.choice(user_agents)
    headers = {
                'User-Agent': random_user_agent
              }

    text = '' # ???
    # http_respone 200 means OK status
    #socket.setdefaulttimeout(5)
    try:    
      resp = requests.get(url, headers=headers)
      if resp.status_code == 200:
        soup = BeautifulSoup(resp.text,'lxml')
        text = soup.body.get_text(' ', strip=True)
        #print(text)
    except Exception as E:
        return None
    if text!= '':
      #print(text)
      savePath=DOWNLOAD_PATH+(str(url).split('//')[-1]).replace('/','_').replace('.','_').replace('\\','_').replace(':','_').replace('*','_').replace('?','_').replace('<','_').replace('>','_').replace('|','_')+'.txt'
      txt_file=open(savePath,'w',encoding='utf-8')
      txt_file.write(text)
      txt_file.close()
      print(url)
      return savePath,url
    else:
      print('loi')

def download_pdf(url):
  filename=urllib.parse.unquote(str(url).split('/')[-1])
  downloadPath = DOWNLOAD_PATH + filename
  #socket.setdefaulttimeout(2)
  try:
    urllib.request.urlretrieve(url, downloadPath)
    # print(url)
    return downloadPath, url
  except Exception as E:
    pass
  
def search_downloadPDF(sents, langOfText, num_of_keyword=3, num_of_result=10, is_cross=1, timeout=5):      #input list các câu
  downloaded_file_path=[]
  website_content_file=[]
  output=[]
  if is_cross==1:           #xuyên ngữ
    if langOfText=='vi':
      text=' '.join(x for x in sents) 
      keywords=extractKeyWord(text,langOfText, num_of_keyword)
      query = ' '.join(keywords).replace("_", " ")
      query_pdf = query + ' filetype:pdf'
      query_docx = query + ' filetype:docx'
      query_list=[query_pdf,query_docx]
      print(query)
      try:
        listLinks=search(query,lang='vi',num_results=num_of_result)
        try:
          with concurrent.futures.ThreadPoolExecutor() as executor:
            website_content_file=executor.map(getContentOnWebsite_save2txt,listLinks,timeout=timeout)
        except Exception as E:
          print(E)
      except Exception as E:
        print(E)
      try:
        listLinks_1_pdf = search(query_pdf, lang='vi', num_results = num_of_result)
        time.sleep(2)
        listLinks_1_docx = search(query_docx, lang='vi', num_results = num_of_result)
        time.sleep(2)
        #listLinks_2_pdf = search(translator.translate_vi2en(query_pdf), lang='en', num_results = num_of_result)
        time.sleep(2)
        #listLinks_2_docx = search(translator.translate_vi2en(query_docx), lang='en', num_results = num_of_result)
        #listLinks=[*listLinks_1_pdf,*listLinks_1_docx,*listLinks_2_pdf,*listLinks_2_docx]
        listLinks=[*listLinks_1_pdf,*listLinks_1_docx]
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
      query_pdf = query + ' filetype:pdf'
      query_docx = query + ' filetype:docx'
      try:
        listLinks=search(query,lang='vi',num_results=num_of_result)
        try:
          with concurrent.futures.ThreadPoolExecutor() as executor:
            website_content_file=executor.map(getContentOnWebsite_save2txt,listLinks,timeout=timeout)
        except Exception as E:
          print(E)
      except Exception as E:
        print(E)
      try:
        listLinks_1_pdf = search(query_pdf, lang='vi', num_results = num_of_result)
        time.sleep(2)
        listLinks_1_docx = search(query_docx, lang='vi', num_results = num_of_result)
        time.sleep(2)
        #listLinks_2_pdf = search(translator.translate_en2vi(query_pdf), lang='en', num_results = num_of_result)
        time.sleep(2)
        #listLinks_2_docx = search(translator.translate_en2vi(query_docx), lang='en', num_results = num_of_result)
        #listLinks=[*listLinks_1_pdf,*listLinks_1_docx,*listLinks_2_pdf,*listLinks_2_docx]
        listLinks=[*listLinks_1_pdf,*listLinks_1_docx]
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
    query_pdf = query + ' filetype:pdf'
    query_docx = query + ' filetype:docx'
    query_txt = query + ' filetype:txt'
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
  for path in downloaded_file_path:
    if path!=None:
      output.append(path)
  for path in website_content_file:
    if path!=None:
      output.append(path)
  savepath_output=[]
  url_output=[]
  for i in output:
    savepath_output.append(i[0])
    url_output.append(i[1])
  return savepath_output,url_output 
'''
x=['Bạn đang tìm kiếm công cụ giúp bạn kiểm tra xem bài viết của mình hay của bạn bè có phải bị đánh giá là đạo văn hay không?',
    'Hãy theo dõi bài viết để biết thêm 7 phần mềm, web kiểm tra đạo văn miễn phí và chính xác nhất.',]

ex=search_downloadPDF(x,'vi',num_of_keyword=2,num_of_result=3,is_cross=1,timeout=5)
print(ex)
'''