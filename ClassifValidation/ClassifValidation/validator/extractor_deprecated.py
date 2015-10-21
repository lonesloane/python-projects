"""
Created on Jul 18, 2014

@author: Stephane VARIN
"""
import os
import xml.etree.cElementTree
import ConfigParser


## @deprecated see temisxmlparser instead
def convert_classif_xml_to_csv(xmlfile_folder, xmlfile):
    """ convert_classif_xml_to_csv:
    """
    tree = xml.etree.cElementTree.ElementTree(file=os.path.join(xmlfile_folder,
                                                                xmlfile))
    enrichment = tree.getroot()
    # Loop over xml structure
    for annotation in enrichment:
        long_filename = annotation.attrib["file"].split('\\')
        filename = long_filename[len(long_filename) - 1]
        filename = filename[0:len(filename) - 1:1]
        # Append results to csv file
        with open(os.path.join(xmlfile_folder,
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


## @deprecated see temisxmlparser instead
def main():
    """main:
    """
    _config = ConfigParser.SafeConfigParser()
    _config_file_path = os.path.join(os.getcwd(), 'config.ini')
    _config.read(_config_file_path)

    _output_folder = _config.get('global', 'outputFolder')

    for _corpus_folder in os.listdir(_output_folder):
        _xml_file_folder = os.path.join(_output_folder, _corpus_folder)
        if os.path.isdir(_xml_file_folder):
            print "Processing corpus_folder: " + _corpus_folder
            for _xml_file in os.listdir(_xml_file_folder):
                extension = _xml_file.split(".")[1]
                if extension != "xml":
                    continue  # We care only for xml files
                convert_classif_xml_to_csv(_xml_file_folder, _xml_file)


if __name__ == '__main__':
    main()
