import urllib2
import pprint
import base64
import xml.etree.ElementTree as eT
import csv

DEBUG = True
VERBOSE = False

ns = {'response': 'http://www.oecd.org/ns/lambda/schema#api-response',
      'manifest': 'http://www.oecd.org/ns/lambda/schema/'}

indicatorsList = []
doi_keywords_dict = {}


def populate_indicators_list():
    request = urllib2.Request("http://vs-pac-xml-4.main.oecd.org:10001/v1/export/t4/indicator-pages/manifest")
    base64string = base64.standard_b64encode(b'KV3ITN:KV3ITN')
    request.add_header("Authorization", "Basic %s" % base64string)
    response = urllib2.urlopen(request)
    content = response.read()
    root = eT.fromstring(content)
    for url in root.findall('response:data/manifest:manifest/manifest:url', ns):
        indicatorsList.append(url.text)


def populate_doi_keywords_dict():
    for url in indicatorsList:
        keywords = []
        request = urllib2.Request("http://vs-pac-xml-4.main.oecd.org:10001"+url)
        base64string = base64.standard_b64encode(b'KV3ITN:KV3ITN')
        request.add_header("Authorization", "Basic %s" % base64string)
        response = urllib2.urlopen(request)
        content = response.read()
        root = eT.fromstring(content)

        indicator_group_title = root.find('response:data/infoSet/indicatorGroup/title', ns)
        keywords.append(indicator_group_title.text)
        indicator_title = root.find('response:data/infoSet/indicator/title', ns)
        keywords.append(indicator_title.text)
        indicator_keywords = root.find('response:data/infoSet/indicator/keywords', ns)
        keywords.append(indicator_keywords.text)
        indicator_topic_title = root.find('response:data/infoSet/indicator/dataPortalTopic/title', ns)
        keywords.append(indicator_topic_title.text)
        doi_keywords = ",".join(keywords)
        if DEBUG: print doi_keywords

        for publication_doi in root.findall('response:data/infoSet/indicator/item[@type="relatedPublication"]/target',
                                            ns):
            if DEBUG: print "related Publication: " + publication_doi.text
            doi_keywords_dict[publication_doi.text] = doi_keywords
        for publication_doi in root.findall('response:data/infoSet/indicator/item[@type="sourcePublication"]/target',
                                            ns):
            if DEBUG: print "source Publication: " + publication_doi.text
            doi_keywords_dict[publication_doi.text] = doi_keywords

    if VERBOSE: pprint.pprint(doi_keywords_dict)


def generate_keywords_file():
    keywords_file = open('keywords.csv', mode='wb')
    csv_writer = csv.writer(keywords_file, delimiter='|', lineterminator='\n')

    for k, v in doi_keywords_dict.items():
        csv_writer.writerow([k, v.encode('utf-8')])

if __name__ == '__main__':
    populate_indicators_list()
    if DEBUG: pprint.pprint(indicatorsList)
    populate_doi_keywords_dict()
    generate_keywords_file()
