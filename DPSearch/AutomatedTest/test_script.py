# filter Types: countries, topics, datasets, indicators, publications
import urllib2
import pprint
import xml.etree.ElementTree as eT
import datetime
import os
import io

DEBUG = False
VERBOSE = False
FUZZY_SEARCH = True
SAVE_XML = True

SEARCH_TERMS = 0
LANG = 1
FILTER = 2
ns = {'exalead': 'exa:com.exalead.search.v10'}
# metadata_keys contains the metadata fields used for the match
metadata_keys = ['description', 'ispartof_serial_description_en', 'indicator_group_title']
RESULT_PATH = 'TestResults'

def buildSearchUrl(searchTerms, filterType=None, lang=None, doFuzzy=False):
    """build valid search url based on input parameters

    :param searchTerms:
    :param filterType:
    :param doFuzzy:
    :return: search url to submit to Exalead search API
    """
    if lang is None:
        languageFilter = '&r=f/language/en'
    else:
        languageFilter = '&r=f/language/{lang}'.format(lang=lang)

    if filterType is None or len(filterType) == 0:
        typeFilter = ''
    else:
        typeFilter = '&r=%2Bf%2Ftype%2F{filter}'.format(filter=filterType)

    if len(searchTerms)>1:
        sexp = '+'.join(searchTerms)
    else:
        sexp = searchTerms[0]
    if not doFuzzy:
        searchParam = '&q={s}'.format(s=sexp)
    else:
        nbfuzzy = len(searchTerms)-1
        searchParam = '&q=FUZZYAND%2F-{n}({s})'.format(s=sexp, n=nbfuzzy)

    queryUrl = 'http://t4-pub-1:97/search-api-dev/?hf=10&b=0{languageFilter}{typeFilter}{searchParam}&sl=sl_dp&st=st_dp&l=en'\
        .format(typeFilter=typeFilter, languageFilter=languageFilter, searchParam=searchParam)
    return queryUrl


def isEmpty(s):
    """

    :param s:
    :return:
    """
    if len(s) > 0:
        return False
    return True


def getSearchResults(queryUrl):
    """Calls Exalead search API and retrieves search results

    :param queryUrl:
    :return: array of search hits
    """
    response = urllib2.urlopen(queryUrl)
    content = response.read()
    root = eT.fromstring(content)

    hits = []

    if root.find('exalead:hits', ns) is None:  # Sometimes, we find nothing at all !!!
        return hits

    for hit in root.find('exalead:hits', ns).findall('exalead:Hit', ns):
        metas = {}
        for meta in hit.find('exalead:metas', ns).findall('exalead:Meta', ns):
            meta_name = meta.attrib['name']
            meta_value = ''
            meta_string = meta.find('exalead:MetaString', ns)
            if meta_string is not None:
                meta_value = meta_string.text
            else:
                meta_text = meta.find('exalead:MetaText', ns)
                if meta_text is not None:
                    text = ''
                    for text_seg in meta_text.findall('{exa:com.exalead.search.v10}TextSeg'):
                        text += text_seg.text
                    meta_value = text
            metas[meta_name] = meta_value
        hits.append(metas)
    return hits


def validatePublicUrl(results, expectedUrl, tstNb):
    """Check if expectedUrl is found in the array results

    Returns a score based on the position of the match compared to the expected position tstNb

    :param results: array of hits (Exalead)
    :param expectedUrl: expected publicurl of the hit
    :param tstNb: rank of the expected hit
    :return: score  (from 10 for exact match to 0 for no match)
    """
    for rank in range(len(results)):  # a query can return less than 10 results
        if VERBOSE: print 'publicurl', results[rank]['publicurl']
        if results[rank]['publicurl'] in expectedUrl:
            if VERBOSE: print 'Found result at rank', rank, 'expected rank', tstNb
            return 10 - abs(tstNb-rank)
    return 0  # result not found on first page, this is the worst case


def validateContains(results, testScenario, minOccurence=0):
    """Check if results contain a metadata "key" with given "value"

    :param results:
    :param key:
    :param value:
    :param minOccurence: minimum number of match expected
    :return: score
    """
    keys = []
    key, value = testScenario.split('{contains}')
    value = value.lower()
    if VERBOSE: print "Validate contains"
    if VERBOSE: print "key, value: ", key, value
    if key == 'metadata':  #  metadata regroups several metadata fields
        keys.extend(metadata_keys)
    else:  # simple case such as title
        keys.append(key)

    _score = 0
    for key in keys:
        _keyfound = False
        for rank in range(len(results)):  # a query can return less than 10 results
            if key not in results[rank]:
                continue
            _keyfound = True
            if VERBOSE: print u'looking for value:{2} / received results[{0}][{3}]: {1}'.format(
                rank,
                results[rank][key][0:120]+'(...)',
                value,
                key)
            if value in results[rank][key].lower():
                if VERBOSE: print 'match key:value found'
                _score += 1
        if _score == 0 and _keyfound:
            _score = 0  # result not found on first page, this is the worst case
            if DEBUG: print 'value {0} not found'.format(value)
    if VERBOSE: print 'validate contains score:', _score
    return _score


def validateSorted(results, sortField):
    _score = 0
    sortedValues = []
    if VERBOSE: print 'validateSorted on:', sortField
    for rank in range(len(results)):
        if 'publicationdate' not in results[rank]:
            if DEBUG: print 'No publication date available'
        if VERBOSE: print 'publication_date:', results[rank]['publicationdate']
        _date = datetime.datetime.strptime(results[rank]['publicationdate'], '%m/%d/%Y %H:%M:%S')
        sortedValues.append(_date)
    if VERBOSE: pprint.pprint(sortedValues)
    for i in range(len(sortedValues)-1):
        if VERBOSE: print 'sortedValues[i], sortedValues[i+1]:', sortedValues[i], sortedValues[i+1]
        if sortedValues[i] - sortedValues[i+1] > datetime.timedelta(seconds=1):
            _score += 1
    if VERBOSE: print 'validate sorted score:', _score
    return _score


def validate(results, testScenario, tstNb):
    """ Validate test scenario based on the results
    :param results:
    :param testScenario:
    :param tstNb:
    :return:
    """
    containScenario = None
    sortScenario = None
    expectedUrl = None
    score = 0
    keys = []
    if 'publicurl' in testScenario:
        # look for exact result in hits
        expectedUrl = testScenario.split("=")[1]
        if VERBOSE: print 'ExpectedUrl: ', expectedUrl
    elif 'AND' in testScenario:
        # multiple conditions to take into account (e.g. title contains "xxx" + sort by date)
        if DEBUG: print "multiple conditions"
        scenario1, scenario2 = testScenario.split('AND')
        if DEBUG: print "scenario1: {0}, scenario2: {1}".format(scenario1, scenario2)
        if 'contains' in scenario1:
            containScenario = scenario1
            if 'sort' in scenario2:
                sortField = scenario2[6:]
                sortScenario = scenario2
        elif 'contains' in scenario2:
            containScenario = scenario2
            if 'sort' in scenario1:
                sortField = scenario1[6:]
                sortScenario = scenario1
    elif 'contains' in testScenario:  # simple 'contains' scenario.
        containScenario = testScenario
    elif 'sort' in testScenario:  # only checking the results are sorted by date
        sortField = testScenario[6:]
        sortScenario = testScenario

    if expectedUrl is not None:
        score += validatePublicUrl(results, expectedUrl, tstNb)
    if containScenario is not None:
        score += validateContains(results, containScenario)
    if sortScenario is not None:
        score += validateSorted(results, sortField)

    if DEBUG: print '{testScenario} => score: {score}'.format(testScenario=testScenario, score=score)
    return score


def rundate(f):
    dt = f.split('.')[0][9:]
    dt_run = datetime.datetime.strptime(dt,'%Y-%m-%d_%H-%M-%S')
    return dt_run


def loadRunResults(opt=None):
    # get list of files in TestResults
    lst = [(f, rundate(f)) for f in os.listdir(RESULT_PATH) if os.path.isfile(os.path.join(RESULT_PATH, f))]
    lst.sort(reverse=True)
    if VERBOSE: print 'list of TestResult files:', lst
    if opt == 'beforelast':
        if not len(lst) > 1:
            return None
        runfile = lst[1][0]
    else:
        runfile = lst[0][0]

    return runfile


def parseResultXml(xml_file_name):
    res = {}
    if VERBOSE: print 'xml_file_name:', xml_file_name
    root = eT.parse(RESULT_PATH+'/'+xml_file_name)
    for testCase in root.iter('TestCase'):
        if VERBOSE: print testCase.attrib
        for testScenario in testCase.iter('Scenario'):
            if VERBOSE: print testScenario.attrib
            res[testCase.attrib['Search_Terms']
                + testCase.attrib['Filter']
                + testScenario.attrib['Text']] = testScenario.attrib['Score']
    return res


def CompareLastRuns():
    lastrunfile = loadRunResults()
    beforelastrunfile = loadRunResults(opt='beforelast')

    if beforelastrunfile is None:
        print "No previous test run found. Comparison impossible."
        import sys
        sys.exit(0)

    lastrun = parseResultXml(lastrunfile)
    beforelastrun = parseResultXml(beforelastrunfile)
    if VERBOSE: pprint.pprint(lastrun)
    if VERBOSE: pprint.pprint(beforelastrun)

    for test in lastrun:
        if VERBOSE: print 'comparing test:',test
        if test not in beforelastrun:
            if DEBUG: print "Test not found in previous run:", test
        else:
            if VERBOSE: print "comparing test runs"
            if int(lastrun[test]) == int(beforelastrun[test]):  # same as before, nothing to report
                if DEBUG: print 'same as before, nothing to report'
                continue
            if int(lastrun[test]) > int(beforelastrun[test]):   # better than before
                print "Improved test:{0}. Previous score: {1}. Current score: {2}".format(test,
                                                                                          beforelastrun[test],
                                                                                          lastrun[test])
            if int(lastrun[test]) < int(beforelastrun[test]):   # worse than before
                print "Degraded test:{0}. Previous score: {1}. Current score: {2}".format(test,
                                                                                          beforelastrun[test],
                                                                                          lastrun[test])
            else:
                print "Something went wrong..."


# create results XML
xmlResult = eT.Element('SearchPerformanceIndex')

# Read tests definition csv file
fTest = io.open('DP_Search_test-scenarios.csv', mode='r', encoding='utf-16')
headers = fTest.readline()  # first line contains column headers

totalScore = 0
for testLine in fTest:  # 1 test scenario per line
    testScore = 0
    testLine = testLine.rstrip('\r\n')
    xmlTestCase = eT.SubElement(xmlResult, 'TestCase')
    testCase = testLine.split(',')
    searchTerms = testCase[SEARCH_TERMS].split()
    xmlTestCase.set('Search_Terms', ','.join(searchTerms))
    xmlTestCase.set('Filter', testCase[FILTER])
    xmlTestCase.set('lang', testCase[LANG])
    queryUrl = buildSearchUrl(searchTerms, filterType=testCase[FILTER], lang=testCase[LANG], doFuzzy=FUZZY_SEARCH)
    if DEBUG: print '*************************************'
    if DEBUG: print 'TestCase: ', testCase[0:120]
    if VERBOSE: print 'queryUrl: ', queryUrl
    results = getSearchResults(queryUrl)
    for i in range(10):     # go through the 10 possible 'test results' per test scenario
                            # in each line of tests definition csv file
        testScenario = testCase[i+3]
        if not isEmpty(testScenario):
            xmlTestCaseScenario = eT.SubElement(xmlTestCase, 'Scenario')
            xmlTestCaseScenario.set('Text', testScenario)
            if VERBOSE: print 'test {0}: {1}'.format(i+1, testCase[i+2])
            testScenarioScore = validate(results, testScenario, i)
            testScore += testScenarioScore
            xmlTestCaseScenario.set('Score', str(testScenarioScore))
    totalScore += testScore
    xmlTestCase.set('Score', str(testScore))
    if DEBUG: print 'Test Case score:', testScore

if DEBUG: print '\n*************************************'
if DEBUG: print 'Final test score: {score}'.format(score=totalScore)
if DEBUG: print '*************************************'
xmlResult.set('Score', str(totalScore))
xmlFileName = 'TestResults/test_run_' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.xml'
xmlResult.set('date_run', xmlFileName)
if SAVE_XML: eT.ElementTree(xmlResult).write(xmlFileName)

CompareLastRuns()

