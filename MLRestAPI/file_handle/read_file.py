# import PyPDF2
import docx2txt
from pdfminer.high_level import extract_text


# Read PDF file
def readPDFFile(pdfFilePath):
    text = extract_text(pdfFilePath)

    return text


# Read TXT file
def readTXTFile(docFilePath):
    with open(docFilePath, 'r', encoding='utf-8') as f:
        text = f.read()

    return text


# Read DOC/DOCX file
def readDOCXFile(docFilePath):
    text = docx2txt.process(docFilePath)

    return text
