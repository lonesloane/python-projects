##@package manualtagsimport
# __Script used to copy the csv files containing "manual" annotations
# in the respective corpus folders for comparison with the cartridge.__
#

import os
import ConfigParser
import shutil

## Copies the annotation file to the corresponding corpus folder.
#
# @param manualtags_folder Path where the manual annotations files are stored
# @param csv_file Name of the annotation file.
# From this name, the corpus is extracted. For example:
# `TMX to CSV_Agriculture_food_and_fisheries.csv` gives
# `_Agriculture_food_and_fisheries`
# @param outputFolder Destination folder
def copy_csvfile_to_corpus_folder(manualtags_folder, csv_file, outputfolder):
    # TMX to CSV_Agriculture_food_and_fisheries.csv
    # ==> Agriculture_food_and_fisheries
    _corpus = csv_file.split('.')[0][10:]

    src_file_path = os.path.join(manualtags_folder, csv_file)
    dest_file_path = os.path.join(outputfolder, _corpus, 'ManualTags.csv')
    open(dest_file_path, 'w')
    # print src_file
    #     print dest_file
    shutil.copyfile(src_file_path, dest_file_path)


## Module entry point.
# Loops through all available csv file in the folder
# `manualTagsFolder` and copies to the folder
# `outputFolder`
#
# Remember to update the `config.ini` file accordingly.
def main():
    _config = ConfigParser.SafeConfigParser()
    _config_file_path = os.path.join(os.getcwd(), 'config.ini')
    _config.read(_config_file_path)

    # Folder where manual tags are stored
    _manualtags_folder = _config.get('global', 'manualTagsFolder')
    _outputFolder = _config.get('global', 'outputFolder')

    for _csv_file in os.listdir(_manualtags_folder):
        if os.path.isfile(os.path.join(_manualtags_folder, _csv_file)):
            extension = _csv_file.split(".")[1]
            if extension != "csv":
                # skip any "alien" file
                # which could also be in the folder
                continue
            # Copy each csv file into the corpus folder
            copy_csvfile_to_corpus_folder(_manualtags_folder, _csv_file, _outputFolder)


if __name__ == '__main__':
    main()
