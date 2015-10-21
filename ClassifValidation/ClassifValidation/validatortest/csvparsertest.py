'''
Created on Aug 4, 2014

@author: stephane
'''
import unittest
from validator import csvparser

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testName(self):
        pass

    def test_build_csv_line(self):
        """test_build_csv_line:
        """
        result = csvparser.Parser.build_csv_line("key",
                                                 "manual_tag",
                                                 "common_tag",
                                                 "temis_tag",
                                                 "manualcorrect",
                                                 "commoncorrect",
                                                 "commonincorrect",
                                                 "temiscorrect",
                                                 "temisincorrect")
        expected_result=("key|manual_tag|common_tag|temis_tag|manualcorrect|"
                         "commoncorrect|commonincorrect|temiscorrect|"
                         "temisincorrect|\n")
        self.assertEqual(result, expected_result, expected_result)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()