import urllib2
import pprint
import base64
from HTMLParser import HTMLParser
import xml.etree.ElementTree as eT

DEBUG = True
VERBOSE = False

ns = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
      'default': 'http://oecd.metastore.ingenta.com/ns/'}

service_url = "http://discovery-service.oecdcode.org/metadata/1.0/book/"
authKey = base64.standard_b64encode(b'KV3ITN:KV3ITN')
headers = {"Content-Type": "application/json", "Authorization": "Basic: " + authKey}

booksList = []
doi_keywords_dict = {}


class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr in attrs:
                if attr[1] != '../':
                    booksList.append(attr[1])


def load_doi_keywords_dict():
    with open('keywords.csv') as f:
        for line in f:
            key, values = line.split('|')
            doi_keywords_dict[key] = values


def populate_books_list():
    request = urllib2.Request(service_url)
    request.set_proxy('wsg-proxy.oecd.org', 'http')
    for key, val in headers.items():
        request.add_header(key, val)
    response = urllib2.urlopen(request)
    content = response.read()
    parser = MyHTMLParser()
    parser.feed(content)


def get_book_xml(book):
    request = urllib2.Request(service_url+book)
    request.set_proxy('wsg-proxy.oecd.org', 'http')
    for key, val in headers.items():
        request.add_header(key, val)
    response = urllib2.urlopen(request)
    content = response.read()
    return content


def get_book_dois(xml):
    book_dois = []
    root = eT.fromstring(xml)
    for doi_elem in root.findall('default:doi', ns):
        #print "doi: ", doi_elem.attrib['{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource']
        book_dois.append(doi_elem.attrib['{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource'])
    for doi_elem in root.findall('default:isPartOf/default:Serial/default:doi', ns):
        #print "doi: ", doi_elem.attrib['{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource']
        book_dois.append(doi_elem.attrib['{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource'])

    return book_dois


def get_keywords_for_doi(doi):
    match = False
    keywords = ''
    if doi in doi_keywords_dict.keys():
        match = True
        keywords = doi_keywords_dict[doi]
    return (match, keywords)


def enrich_books_xml():
    for book in booksList[0:100]:
        print "Book: ", book
        book_xml = get_book_xml(book)
        book_dois = get_book_dois(book_xml)
        for doi in book_dois:
            match, keywords = get_keywords_for_doi(doi)
            if match:
                print 'Match found:', keywords
                break


if __name__ == '__main__':
    load_doi_keywords_dict()
    #if DEBUG: pprint.pprint(doi_keywords_dict)
    populate_books_list()
    #if DEBUG: pprint.pprint(booksList)
    enrich_books_xml()