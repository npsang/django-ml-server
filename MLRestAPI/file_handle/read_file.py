from underthesea import sent_tokenize
import pypdfium2 as pdfium 
from langdetect import detect
from underthesea import text_normalize
import docx2txt
import os 


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

def read_file(docPath, get_language=False):
  if os.stat(docPath).st_size !=0:
    typeOfFile = docPath.split('.')[-1]
    text = ""
    try:
        if typeOfFile == 'pdf':
          text = readPDFFile(docPath)
        elif typeOfFile == 'docx':
          text = readDOCXFile(docPath)
        elif typeOfFile == 'txt':
          text = readTXTFile(docPath)
        else:
          try:
            text=readPDFFile(docPath)
          except:
            pass
          try:
            text = readDOCXFile(docPath)
          except:
            pass
          try:
            text = readTXTFile(docPath)
          except:
            pass

        output=text_normalize(text)

        if get_language:
          langOfText = detect(text)
          return output, langOfText
        return output
    except Exception as E:
        print(E)
        pass 
  else:
    print('Empty File')
    pass 