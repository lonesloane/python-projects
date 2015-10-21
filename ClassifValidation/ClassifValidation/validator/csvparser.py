## @package csvparser
# __Script used to parse the annotations csv files
# and compare between manual and Luxid annotations.__
#

import os
import ConfigParser
import datetime

SEP = "|"
END = "\n"
DEFAULTMANUAL = "1"
DEFAULTCOMMON = "1"
DEFAULTTEMIS = "0"
MANUAL = 0
COMMON = 1
TEMISONLY = 2
INCLUDEORGS = False


class Parser(object):
    """Parser:
    """

    def __init__(self, corpus_folder, manualtags_filename, temistags_filename):
        """__init__:
        """
        self.config = ConfigParser.SafeConfigParser()
        self.config_file_path = os.path.join(os.getcwd(), 'config.ini')
        self.config.read(self.config_file_path)
        self.output_folder = self.config.get('global', 'outputFolder')
        self.working_folder = os.path.join(self.output_folder, corpus_folder)
        self.output_filename = self.config.get("global", "outputFileName")
        self.manualtags_filepath = os.path.join(self.working_folder,
                                                manualtags_filename + ".csv")
        self.temistags_filepath = os.path.join(self.working_folder,
                                               temistags_filename + ".csv")
        _datetime = "{dattetime}".format(dattetime=datetime.datetime.now())
        self.output_filepath = os.path.join(self.working_folder,
                                            corpus_folder + self.output_filename + " " + _datetime + ".csv")

        self.tags = {}

    def parse_tags(self):
        """parse_tags:
        """
        # Read Manual tags
        self.parse_manual_tags()
        # Read Temis tags
        self.parse_temis_tags()
        # Export results
        self.write_csv()

    @staticmethod
    def build_csv_line(key, manual_tag, common_tag, temis_tag,
                       manualcorrect="", commoncorrect="", commonincorrect="",
                       temiscorrect="", temisincorrect=""):
        """build_csv_line:
        """
        csvline = ("{key}{sep}{manual}{sep}{manualcorrect}{sep}{common}{sep}"
                   "{commoncorrect}{sep}{commonincorrect}{sep}{temis}{sep}"
                   "{temiscorrect}{sep}{temisincorrect}{sep}{end}").format(
            key=key,
            manual=str(manual_tag).strip(),
            manualcorrect=manualcorrect,
            common=str(common_tag).strip(),
            commoncorrect=commoncorrect,
            commonincorrect=commonincorrect,
            temis=str(temis_tag).strip(),
            temiscorrect=temiscorrect,
            temisincorrect=temisincorrect,
            sep=SEP,
            end=END)
        return csvline

    def write_csv(self):
        """write_csv:
        """
        with open(self.output_filepath, "wb") as csv_file:
            csv_file.write("File|Manual Only|Correct|Common|Correct|Incorrect"
                           "|Temis Only|Correct|Incorrect|\n")
            for key in self.tags:
                for manual_tag in self.tags[key][MANUAL]:
                    csv_file.write(self.build_csv_line(key=key,
                                                       manual_tag=manual_tag,
                                                       common_tag="",
                                                       temis_tag="",
                                                       manualcorrect=DEFAULTMANUAL))
                for common_tag in self.tags[key][COMMON]:
                    csv_file.write(self.build_csv_line(key=key,
                                                       manual_tag="",
                                                       common_tag=common_tag,
                                                       temis_tag="",
                                                       commoncorrect=DEFAULTCOMMON))
                for temis_tag in self.tags[key][TEMISONLY]:
                    if "Organisations" in temis_tag and not INCLUDEORGS:
                        continue
                    else:
                        csv_file.write(self.build_csv_line(key=key,
                                                           manual_tag="",
                                                           common_tag="",
                                                           temis_tag=temis_tag,
                                                           temiscorrect=DEFAULTTEMIS))
                csv_file.write(self.build_csv_line("", "", "", "", "",
                                                   "", "", "", ""))

    def parse_manual_tags(self):
        """parse_manual_tags:
        """
        with open(self.manualtags_filepath) as manualtags_file:
            for values in manualtags_file:
                # Ignore column headers
                if "Annotation" in values:
                    continue
                if "Document" in values:
                    continue
                tags = values.split(",")
                # if new entry, create empty arrays
                try:
                    self.tags[tags[0]]
                except:
                    self.tags[tags[0]] = [[], [], []]
                # By default, all tags go into the "manual" array
                self.tags[tags[0]][MANUAL].append(
                    self.concat_manual_tags(tags[1],
                                            tags[2]))

    def concat_manual_tags(self, tag_type, manual_tag):
        """concat_manual_tags:
        """
        # [Topics]: Climate Action Network
        return "[{tag_type}]: {tagValue}".format(
            tag_type=self.clean_manual_types(tag_type),
            tagValue=self.clean_tag(manual_tag))

    def concat_temis_tags(self, tag_type, temis_tag):
        """concat_temis_tags:
        """
        return "[{tag_type}]: {tagValue}".format(
            tag_type=self.clean_temis_types(tag_type),
            tagValue=self.clean_tag(temis_tag))


    def get_manualtags_forfile(self, filename):
        """get_manualtags_forfile:
        """
        if self.tags.has_key(filename):
            return self.tags[filename][MANUAL]
        else:
            self.tags[filename] = [[], [], []]
            return self.tags[filename][MANUAL]

    def parse_temis_tags(self):
        """parse_temis_tags:
        """
        with open(self.temistags_filepath) as temis_tagsfile:
            for values in temis_tagsfile:
                temistags = values.split("|")
                filename = temistags[0]
                manualtags = self.get_manualtags_forfile(filename)
                temistag = self.concat_temis_tags(temistags[1], temistags[2])

                if temistag in manualtags:
                    # if tag found both in manual and temis tag files,
                    # move tag from manual to common array
                    manualtags.remove(temistag)
                    self.tags[filename][COMMON].append(temistag)
                else:
                    self.tags[filename][TEMISONLY].append(temistag)

    @staticmethod
    def clean_manual_types(manual_type):
        """clean_manual_types
        """
        # /Entity/KIMTaxo/GeographicalAreas ==> GeographicalAreas
        results = manual_type.split("/")
        result = results[len(results) - 1]
        return result

    @staticmethod
    def clean_temis_types(temis_type):
        """clean_temis_types
        """
        # http://kim.oecd.org/Taxonomy/GeographicalAreas#Paris
        # ==> GeographicalAreas
        results = temis_type.split("/")
        result = results[len(results) - 1].split("#")
        return result[0]

    @staticmethod
    ## Removes leading and trailing whitespaces in `tag`
    #
    # @param tag string to clean up.
    def clean_tag(tag):
        # Climate Action Network\n ==> Climate Action Network
        # return tag[0:len(tag)-1:1]
        return str(tag).strip()


## Module entry point
#
# Loops through all available sub-folders (i.e. corpuses) in `outputFolder`
# and compares manual annotations (`manualTagsFileName`)
# with annotations coming from Temis (`temisTagsFileName`)
#
# Temis annotations are generated from xml files using __temisxmlparser__
# Manual annotations are copied in the respective corpus folders using
# __manualtagsimport__
#
# Remember to update the `config.ini` file accordingly.
def main():
    _config = ConfigParser.SafeConfigParser()
    _config_file_path = os.path.join(os.getcwd(), 'config.ini')
    _config.read(_config_file_path)

    _output_folder = _config.get('global', 'outputFolder')
    _manualtags_filename = _config.get('global', 'manualTagsFileName')
    _temistags_filename = _config.get('global', 'temisTagsFileName')

    for _corpus_folder in os.listdir(_output_folder):
        _working_folder = os.path.join(_output_folder, _corpus_folder)
        if os.path.isdir(_working_folder):
            print "Processing " + _working_folder
            _parser = Parser(_corpus_folder, _manualtags_filename,
                             _temistags_filename)
            # Go !!!
            _parser.parse_tags()


if __name__ == '__main__':
    main()
