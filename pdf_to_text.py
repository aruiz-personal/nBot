#!/usr/bin/env python3
#_*_ coding: utf8 _*_

import PyPDF2

def convertir(ruta):
    pdfFileObj = open(ruta, 'rb')
    # pdf reader object
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    #number of pages in pdf
    # a page object
    texto=''
    for page in pdfReader.pages:
        texto= texto + page.extractText()
    
    pdfFileObj.close()
    return texto
