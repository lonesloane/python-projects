##@package temisxmlparser
# __Script used to extract classification annotations from the xml files
# produced by the Luxid workflow.__
#

import os
import ConfigParser
#import xml.etree.cElementTree
from lxml import etree

##  Read the xml file, extract the file name and the annotations
# and append this information to the csv file of the corresponding
# corpus.
#
#        @param output_folder The folder where the output files are stored
#        @param xmlfile name of the xml file containing the annotations
def convert_classif_xml_to_csv(output_folder, xmlfile):
    tree = etree.ElementTree(file=os.path.join(output_folder, xmlfile))
    enrichment = tree.getroot()
    # Loop over xml structure
    for annotation in enrichment:
        long_filename = annotation.attrib["file"].split('\\')
        filename = long_filename[len(long_filename) - 1]
        corpus = long_filename[len(long_filename) - 3]
        print "corpus: " + corpus
        #Debug Code
        #        if corpus != "_Agriculture_food_and_fisheries":
        #            return
        #End Debug
        doctype = long_filename[len(long_filename) - 2]
        print "doctype: " + doctype
        filename = filename[0:len(filename) - 1:1]
        print "filename: " + filename
        # Append results to csv file
        # Create folder if not yet created
        if not os.path.isdir(os.path.join(output_folder, corpus)):
            os.mkdir(os.path.join(output_folder, corpus))
        # Open csv file in append mode. (File created on first access)
        with open(os.path.join(output_folder, corpus,
                               "Annotations.csv"), 'ab') as csv_annotations:
            if annotation.tag == "annotation":
                for node in annotation:
                    csv_annotations.write(
                        "{filename}{sep}{uri}{sep}{text}{end}".format(
                            sep='|',
                            filename=filename,
                            uri=node.attrib["uri"].encode("utf-8"),
                            text=node.text.encode("utf-8"),
                            end=u"\n"))


## __Runs the extraction of the classification's annotations__
#
#  Change the value of the parameter `outputFolder` in the configuration
#  file `config.ini` to point to the folder where the annotations are stored
#
#  Upon extraction, the resulting annotations are stored in csv files which are
#  stored in dedicated folders based on the corpus identified in the
#  annotation xml:
#~~~~~xml
#      <enrichment>
#          <annotation cartridgeName='Metadata' file='[E:\Input\_Golden_corpora\_Agriculture_food_and_fisheries\Official_documents\EN_AGR-CA-M-2005-2_JT00187347.pdf]'>
#            <coverage uri='http://kim.oecd.org/Taxonomy/GeographicalAreas#Paris'>Paris</coverage>
#            <coverage uri='http://kim.oecd.org/Taxonomy/GeographicalAreas#Pretoria'>Pretoria</coverage>
#            ...
#~~~~~
#  Here, the corpus is `_Agriculture_food_and_fisheries`
#
#  One sub-folder per identified corpus is created.
def main():
    _config = ConfigParser.SafeConfigParser()
    _config_file_path = os.path.join(os.getcwd(), 'config.ini')
    _config.read(_config_file_path)

    # Folder where temis xml files from the workflow are stored
    _output_folder = _config.get('global', 'outputFolder')

    for _xml_file in os.listdir(_output_folder):
        if os.path.isfile(os.path.join(_output_folder, _xml_file)):
            extension = _xml_file.split(".")[1]
            if extension != "xml":
                # skip any "alien" file
                # which could also be in the folder
                continue
            # For each xml file, extract the annotations
            # and put them in a single csv file per corpus
            convert_classif_xml_to_csv(_output_folder, _xml_file)


if __name__ == '__main__':
    main()
