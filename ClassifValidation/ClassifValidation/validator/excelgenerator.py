## @package excelgenerator
# __Script used to generate excel files based on the results
# of comparison between manual and Luxid annotations.__
#

import xlwt
import xlrd
import ConfigParser
import codecs
import os
import datetime


class ExcelGenerator(object):
    """ExcelGenerator:
    """
    # Annotations column numbers
    FILE = 0
    MANUAL_ONLY = 1
    MANUAL_CORRECT = 2
    COMMON = 3
    COMMON_CORRECT = 4
    COMMON_INCORRECT = 5
    TEMIS_ONLY = 6
    TEMIS_CORRECT = 7
    TEMIS_INCORRECT = 8
    CRLF = 9
    # Report column numbers
    MISSED = 0
    CORRECT = 1
    INCORRECT = 2
    PRECISION = 3
    RECALL = 4
    FMEASURE = 5

    def __init__(self, working_folder, corpus_folder):
        """__init__:
        """
        self.working_folder = working_folder
        self.corpus_folder = corpus_folder

        self.csv_validation_files = {}
        self.get_list_csv_validation_files(self.working_folder,
                                           self.corpus_folder)

        self.xls_validation_files = {}
        self.get_list_xls_validation_files(self.working_folder,
                                           self.corpus_folder)

    def get_list_csv_validation_files(self, working_folder,
                                      corpus_name):
        """get_list_csv_validation_files:
        """
        for csvfile in os.listdir(working_folder):
            if (corpus_name in csvfile and "csv" in csvfile
                and not "~" in csvfile):
                elems = csvfile.split(" ")
                # _corpusName_classif_check 2014-07-29 14:56:12.411799.csv
                csv_datetime = datetime.datetime.strptime(
                    "{date} {time}".format(
                        date=elems[1],
                        time=elems[2][0:len(elems[2]) - 4]),
                    "%Y-%m-%d %H:%M:%S.%f")
                self.csv_validation_files[csvfile] = [csv_datetime]

    def get_list_xls_validation_files(self, working_folder, corpus_name):
        """get_list_xls_validation_files:
        """
        for xlsfile in os.listdir(working_folder):
            if (corpus_name in xlsfile and ".xls" in xlsfile
                and not "~" in xlsfile):
                elems = xlsfile.split(" ")
                # _Agriculture_food_and_fisheries_classif_verification 1.xls
                xls_filenumber = int([elems[1][0:len(elems[1]) - 4]][0])
                self.xls_validation_files[xlsfile] = xls_filenumber

    def process(self):
        """process:
        """
        if len(self.xls_validation_files) > 0:
            print ("Found previous validation. "
                   "Creating new validation with previous values.")
            csv_filepath = self.get_latest_csv()
            xls_filepath, xls_filenumber = self.get_latest_xls()
            print "latest csv file: " + csv_filepath
            print "latest xls file: " + xls_filepath
            self.build_excel_file(csv_filepath, xls_filepath, xls_filenumber)
        else:
            print ("No previous validation found."
                   "Creating first validation with default values.")
            csv_filepath = self.get_latest_csv()
            self.build_excel_file(csv_filepath)

    def get_latest_xls(self):
        """get_latest_xls:
        """
        if not len(self.xls_validation_files) > 0:
            raise Exception("No XSL validation file found.")
        latest_xslname = ""
        latest_xlsnumber = 0

        for xlsname, xlsnumber in self.xls_validation_files.iteritems():
            if xlsnumber > latest_xlsnumber:
                latest_xlsnumber = xlsnumber
                latest_xslname = xlsname

        return os.path.join(self.working_folder, latest_xslname), latest_xlsnumber

    def get_latest_csv(self):
        """get_latest_csv
        """
        if not len(self.csv_validation_files) > 0:
            raise Exception("No CSV validation file found.")
        latest_csvname = ""
        latest_csvdate = datetime.datetime.strptime("1900-01-01", "%Y-%m-%d")

        for csvname, csvdatetime in self.csv_validation_files.iteritems():
            if csvdatetime[0] > latest_csvdate:
                latest_csvdate = csvdatetime[0]
                latest_csvname = csvname

        return os.path.join(self.working_folder, latest_csvname)

    @staticmethod
    def fill_default_values(csvfile, sheetannotations):
        """fill_default_values:
        """
        # Define Style of the first row
        header_style = xlwt.easyxf(
            "font: bold true, color black, height 240;"
            "pattern: pattern solid, fore_colour gray25;")
        # Fill in the data
        rowindex = 0
        column_index = 0
        with codecs.open(csvfile, "r", "utf-8") as csv_inputfile:
            for row in csv_inputfile:
                for cell_value in row.split("|"):
                    if column_index == ExcelGenerator.CRLF:
                        continue  # avoid the carriage return in the last cell
                    if rowindex == 0:
                        sheetannotations.write(rowindex, column_index,
                                               cell_value, header_style)
                    else:
                        column_index_of_value = column_index in [
                            ExcelGenerator.MANUAL_CORRECT,
                            ExcelGenerator.COMMON_CORRECT,
                            ExcelGenerator.COMMON_INCORRECT,
                            ExcelGenerator.TEMIS_CORRECT,
                            ExcelGenerator.TEMIS_INCORRECT
                        ]
                        if cell_value and column_index_of_value:
                            sheetannotations.write(rowindex, column_index,
                                                   int(cell_value))
                        else:
                            sheetannotations.write(rowindex, column_index,
                                                   cell_value)
                    column_index += 1
                column_index = 0
                rowindex += 1

    @staticmethod
    def is_row_empty(row):
        """is_row_empty:
        """
        for cell in row.split("|"):
            if cell and cell != u'\n':
                return False
        return True

    def insert_missing_correct(self, sheet_annotations, previous_workbook,
                               csv_file, current_filename, current_row_index):
        """insert_missing_correct:
        """
        # Style of missing values
        missed_style = xlwt.easyxf(
            "font: bold true, color black; "
            "pattern: pattern fine_dots, fore_colour red;")
        correct_rows = []
        previous_sheet = previous_workbook.sheet_by_index(0)
        # Find the annotation marked as correct in common or Temis
        # missing from current csv
        for previous_row_index in range(previous_sheet.nrows):
            previous_row = previous_sheet.row_values(previous_row_index, 0, 9)
            is_samefile = previous_row[ExcelGenerator.FILE] == current_filename
            if not is_samefile:
                continue
            if self.is_row_in_sheet(previous_row, csv_file):
                continue
            is_commoncorrect = (previous_row[ExcelGenerator.COMMON_CORRECT] == 1)
            is_temiscorrect = (previous_row[ExcelGenerator.TEMIS_CORRECT] == 1)
            if is_commoncorrect or is_temiscorrect:
                correct_rows.append(previous_row)
        # If we found missed values, append at the end of the section
        if len(correct_rows) > 0:
            column_index = 0
            for row in correct_rows:
                row[ExcelGenerator.MANUAL_CORRECT] = 1
                if row[ExcelGenerator.COMMON_CORRECT] == 1:
                    row[ExcelGenerator.COMMON_CORRECT] = 0
                if row[ExcelGenerator.TEMIS_CORRECT] == 1:
                    row[ExcelGenerator.TEMIS_CORRECT] = 0
                for cell_value in row:
                    # avoid the carriage return in the last cell
                    if column_index == ExcelGenerator.CRLF:
                        continue
                    sheet_annotations.write(current_row_index, column_index,
                                            cell_value, missed_style)
                    column_index += 1
                column_index = 0
                current_row_index += 1
        return current_row_index

    @staticmethod
    def is_row_in_sheet(previousrow, csvfile):
        """is_row_in_sheet:
        """
        with codecs.open(csvfile, "r", "utf-8") as csvinputfile:
            for row in csvinputfile:
                currentrow = row.split("|")
                is_same_file = (currentrow[ExcelGenerator.FILE] ==
                                previousrow[ExcelGenerator.FILE])
                is_same_common = (currentrow[ExcelGenerator.COMMON] ==
                                  previousrow[ExcelGenerator.COMMON])
                is_same_temis = (currentrow[ExcelGenerator.TEMIS_ONLY] ==
                                 previousrow[ExcelGenerator.TEMIS_ONLY])
                if is_same_file and is_same_common and is_same_temis:
                    return True
            return False

    def fill_values(self, xls_file_path, csv_file, sheet_annotations):
        """fill_values:
        """
        # Open previous excel file
        previous_workbook = xlrd.open_workbook(xls_file_path)
        # Style of the first row
        header_style = xlwt.easyxf(
            "font: bold true, color black, height 240;"
            "pattern: pattern solid, fore_colour gray25;")
        # Style of new annotations
        newvalue_style = xlwt.easyxf("pattern: pattern fine_dots,"
                                     "fore_colour orange;")
        # Fill in the data
        row_index = 0
        column_index = 0
        current_filename = ''
        with codecs.open(csv_file, "r", "utf-8") as csv_input_file:
            for row in csv_input_file:
                # detect gap between annotation sections (per file)
                # and add any missing correct annotation from previous iteration
                if self.is_row_empty(row):
                    row_index = self.insert_missing_correct(sheet_annotations,
                                                            previous_workbook,
                                                            csv_file,
                                                            current_filename,
                                                            row_index)
                # proceed with main loop
                cell_values = row.split("|")
                previous_values = self.get_previous_values(previous_workbook,
                                                           cell_values)
                # print previous_values
                for cell_value in cell_values:
                    # avoid the carriage return in the last cell
                    if column_index == ExcelGenerator.CRLF:
                        continue
                    if row_index == 0:
                        sheet_annotations.write(row_index, column_index,
                                                cell_value, header_style)
                    else:
                        if column_index in [ExcelGenerator.MANUAL_CORRECT,
                                            ExcelGenerator.COMMON_CORRECT,
                                            ExcelGenerator.COMMON_INCORRECT,
                                            ExcelGenerator.TEMIS_CORRECT,
                                            ExcelGenerator.TEMIS_INCORRECT]:
                            if previous_values:
                                sheet_annotations.write(
                                    row_index, column_index,
                                    previous_values[column_index])
                            elif cell_value:
                                print row_index, column_index, cell_value
                                sheet_annotations.write(
                                    row_index, column_index,
                                    int(cell_value), newvalue_style)
                        else:
                            sheet_annotations.write(row_index, column_index,
                                                    cell_value)
                    column_index += 1
                column_index = 0
                current_filename = cell_values[0]
                row_index += 1

    @staticmethod
    def get_previous_values(previous_workbook, cell_values):
        """get_previous_values:
        Scan previous_workbook to find a row matching the given cell_values
        Note: only based on annotation values, not on validation values
        """
        previous_values = None
        sheet = previous_workbook.sheet_by_index(0)
        for row_index in range(sheet.nrows):
            previous_values = sheet.row_values(row_index, 0, 9)
            is_samefile = (previous_values[ExcelGenerator.FILE] ==
                           cell_values[ExcelGenerator.FILE])
            is_samemanual = (previous_values[ExcelGenerator.MANUAL_ONLY] ==
                             cell_values[ExcelGenerator.MANUAL_ONLY])
            is_samecommon = (previous_values[ExcelGenerator.COMMON] ==
                             cell_values[ExcelGenerator.COMMON])
            is_sametemis = (previous_values[ExcelGenerator.TEMIS_ONLY] ==
                            cell_values[ExcelGenerator.TEMIS_ONLY])
            if is_samefile and is_samemanual and is_samecommon and is_sametemis:
                break
            else:
                previous_values = None
        return previous_values

    def build_excel_file(self, csv_file, xls_filepath="", xls_filenumber=0):
        """build_excel_file:
        """
        print "Building new excel file."
        book = xlwt.Workbook()
        sheet_annotations = book.add_sheet('Annotations')
        sheet_report = book.add_sheet('Report')
        self.build_format_annotation_sheet(sheet_annotations)

        if xls_filenumber == 0:
            self.fill_default_values(csv_file, sheet_annotations)
        else:
            self.fill_values(xls_filepath, csv_file, sheet_annotations)

        # Fill in the formulas
        self.build_report_worksheet(sheet_report)
        # Save the file as :
        # ***path***/***corpus_folder***_classif_verification ***number***.xls
        book.save(os.path.join(
            self.working_folder,
            "{corpus_folder}_classif_verification {nb}.xls".format(
                corpus_folder=self.corpus_folder,
                nb=xls_filenumber + 1)))

    @staticmethod
    def build_format_annotation_sheet(sheet_annotations):
        """build_format_annotation_sheet:
        """
        # Freeze first row
        sheet_annotations.panes_frozen = True
        sheet_annotations.remove_splits = True
        sheet_annotations.vert_split_pos = 0
        sheet_annotations.horz_split_pos = 1
        sheet_annotations.vert_split_first_visible = 0
        sheet_annotations.horz_split_first_visible = 1

        # Set default columns width
        sheet_annotations.col(ExcelGenerator.FILE).width = 256 * 30
        sheet_annotations.col(ExcelGenerator.MANUAL_ONLY).width = 256 * 35
        sheet_annotations.col(ExcelGenerator.MANUAL_CORRECT).width = 256 * 9
        sheet_annotations.col(ExcelGenerator.COMMON).width = 256 * 35
        sheet_annotations.col(ExcelGenerator.COMMON_CORRECT).width = 256 * 9
        sheet_annotations.col(ExcelGenerator.COMMON_INCORRECT).width = 256 * 11
        sheet_annotations.col(ExcelGenerator.TEMIS_ONLY).width = 256 * 35
        sheet_annotations.col(ExcelGenerator.TEMIS_CORRECT).width = 256 * 9
        sheet_annotations.col(ExcelGenerator.TEMIS_INCORRECT).width = 256 * 11

        sheet_annotations.height_mismatch = 1
        sheet_annotations.height = 300

    @staticmethod
    def build_report_worksheet(sheet_report):
        """build_report_worksheet:
        """
        # Define Style of the reports
        report_style = xlwt.easyxf(
            "font: bold true, color black;"
            " pattern: pattern solid, fore_colour gray25;")
        sheet_report.write(1, ExcelGenerator.MISSED, "Missed", report_style)
        sheet_report.write(1, ExcelGenerator.CORRECT, "Correct", report_style)
        sheet_report.write(1, ExcelGenerator.INCORRECT, "Incorrect", report_style)
        sheet_report.write(1, ExcelGenerator.PRECISION, "Precision", report_style)
        sheet_report.write(1, ExcelGenerator.RECALL, "Recall", report_style)
        sheet_report.write(1, ExcelGenerator.FMEASURE, "F-Measure", report_style)

        sheet_report.write(2, ExcelGenerator.MISSED,
                           xlwt.Formula("SUM('Annotations'!C$1:C$65536)"))
        sheet_report.write(2, ExcelGenerator.CORRECT,
                           xlwt.Formula("SUM('Annotations'!E$1:E$65536)+"
                                        "SUM('Annotations'!H$1:H$65536)"))
        sheet_report.write(2, ExcelGenerator.INCORRECT,
                           xlwt.Formula("SUM('Annotations'!F$1:F$65536)+"
                                        "SUM('Annotations'!I$1:I$65536)"))
        sheet_report.write(2, ExcelGenerator.PRECISION,
                           xlwt.Formula("B3/(B3+C3)*100"))
        sheet_report.write(2, ExcelGenerator.RECALL,
                           xlwt.Formula("B3/(B3+A3)*100"))
        sheet_report.write(2, ExcelGenerator.FMEASURE,
                           xlwt.Formula("2*(D3*E3)/(D3+E3)"))


def main():
    """main:
    """
    _config = ConfigParser.SafeConfigParser()
    _config_file_path = os.path.join(os.getcwd(), 'config.ini')
    _config.read(_config_file_path)
    _output_folder = _config.get('global', 'outputFolder')
    for _corpus_folder in os.listdir(_output_folder):
        _working_folder = os.path.join(_output_folder, _corpus_folder)
        if os.path.isdir(_working_folder):
            print "Processing " + _working_folder
            _excelgenerator = ExcelGenerator(_working_folder, _corpus_folder)
            _excelgenerator.process()


if __name__ == '__main__':
    main()
