# import PyPDF2
import docx2txt
import pypdfium2 as pdfium
from underthesea import text_normalize
from langdetect import detect


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
    typeOfFile = docPath.split('.')[-1]
    text = ""
    if typeOfFile == 'pdf':
      text = readPDFFile(docPath)
    elif typeOfFile == 'docx' or typeOfFile == 'doc':
      text = readDOCXFile(docPath)
    else:
      text = readTXTFile(docPath)
    
    output=text_normalize(text)
    if get_language:
      langOfText = detect(text)
      return output, langOfText
    else:
      return output 