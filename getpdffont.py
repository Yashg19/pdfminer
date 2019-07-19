# Refered to couple of links out there to come up with the script to extract font size
# http://www.unixuser.org/~euske/python/pdfminer/index.html#pdf2txt
# https://bayrees.wordpress.com/2018/02/08/pdfminer-extract-text-with-its-font-information/
# https://manpages.debian.org/testing/python-pdfminer/pdf2txt.1
# https://github.com/pdfminer/pdfminer.six/issues/202

#!/usr/bin/env python
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.layout import *
from pdfminer.converter import PDFPageAggregator
from os import listdir
from os.path import isfile, join
import getopt
import sys


def createPDFDoc(fpath):
    fp = open(fpath, 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser, password='')
    # Check if the document allows text extraction. If not, abort.
    if not document.is_extractable:
        raise "Not extractable"
    else:
        return document


def createDeviceInterpreter():
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    return device, interpreter


def parse_obj(objs):
    # Getting the size stats in a dictionary. The pdf might have different font size (for example, the font below the image, table, etc. could be
    # different than the size used in text. 
    size_dict = dict()
    # Initializing the max key
    max_size = None
    for obj in objs:
        if isinstance(obj, LTTextBox):
            for o in obj._objs:
                if isinstance(o,LTTextLine):
                    text=o.get_text()
                    if text.strip():
                        for c in  o._objs:
                            if isinstance(c, LTChar):
                                # Get the font size (here you can get the font name and other attributes from the LTChar class in the layout.py file
                                fs = int(round(c.fontsize))
                                if int(fs) not in size_dict:
                                    size_dict[fs] = 1
                                else:
                                    size_dict[fs]+= 1
        # if it's a container, recurse
        elif isinstance(obj, LTFigure):
            parse_obj(obj._objs)
        else:
            pass
    # Get the font size which is used for most of the text in the pdf. This can be achieved by simply iterating over the dictionary.
    if size_dict:
        max = -1
        max_size = -1
        for k, v in size_dict.iteritems():
            if v > max:
                max = v
                max_size = k

    # returning both the max key and the size dictionary for anyone to review.
    return max_size, size_dict


def get_font_stats(pdf_loc):
    fsize = None
    size_dict = dict()
    try:
        document = createPDFDoc(pdf_loc)
        device,interpreter = createDeviceInterpreter()
        pages = PDFPage.create_pages(document)
        interpreter.process_page(pages.next())
        layout = device.get_result()
        fsize, size_dict = parse_obj(layout._objs)
        print('Pdf: {0}, Font size: {1}, Different sizes used in pdf: {2}'.format(pdf_loc, fsize, size_dict))
    except Exception as e:
        print('Error processing pdf: {0}, Error: {1}'.format(pdf_loc, e))
        raise Exception(e)
    return fsize, size_dict


def get_font_stats_for_pdf_dir(local_dir):
    # get all the files in the local directory
    file_list = [f for f in listdir(local_dir) if isfile(join(local_dir, f))]
    for pdf_file in file_list:
        pdf_file_loc = local_dir + pdf_file
        get_font_stats(pdf_file_loc)


def main(argv):
    def usage():
        print ('usage: %s [-f] [-d] file ...' % argv[0])

    try:
        (opts, args) = getopt.getopt(argv[1:], 'f:d:', ['fileloc=', 'dirloc'])
    except getopt.GetoptError:
        return usage()
    
    if not opts: return usage()

    for (k, v) in opts:
        print('KeyValue = ', k, v)
        if k == '-f':
            get_font_stats(v)
        elif k == '-d':
            get_font_stats_for_pdf_dir(v)


if __name__ == '__main__': sys.exit(main(sys.argv))
    
    
        
