'''
Created on Aug 1, 2014

@author: stephane
'''
import unittest
from validator import excelgenerator as excgen

class TestExcelGenerator(unittest.TestCase):
    """TestExcelGenerator:
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_is_row_empty(self):
        """test_is_row_empty:
        """
        row1 = "La|nature|est|un|temple"
        self.assertFalse(excgen.ExcelGenerator.is_row_empty(row1),
                         "Should return False. row is not empty!")

        row2 = "||||"
        self.assertTrue(excgen.ExcelGenerator.is_row_empty(row2),
                         "Should return True. row is empty!")

        row3 = "||||\n"
        self.assertTrue(excgen.ExcelGenerator.is_row_empty(row3),
                         "Should return True. row is empty!")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
