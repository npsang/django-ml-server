import pickle
import requests
import ssl
import concurrent.futures
import urllib.request

from googlesearch import search
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from translate import translate_en2vi, translate_vi2en

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

def download_pdf(url):
  filename=urllib.parse.unquote(str(url).split('/')[-1])
  if str(filename[-4:]) != str('.pdf'):
    filename+='.pdf'
  downloadPath = 'C:/Users/Sang Nguyen Desktop/Downloads/' + filename
  try:
    urllib.request.urlretrieve(url, downloadPath)
    print(url)
    return downloadPath, url
  except Exception as E:
    pass
  
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
            print('exception:', E)
            pass
      except Exception as E:
        print('exception:', E)
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
  print(downloaded_file_path)
  print(f'output: {output}')
  return output 

x=['Bạn đang tìm kiếm công cụ giúp bạn kiểm tra xem bài viết của mình hay của bạn bè có phải bị đánh giá là đạo văn hay không?',
   'Hãy theo dõi bài viết để biết thêm 7 phần mềm, web kiểm tra đạo văn miễn phí và chính xác nhất.',]

ex=search_downloadPDF(x,'vi',num_of_keyword=2,num_of_result=3,is_cross=1,timeout=5)
print(ex)