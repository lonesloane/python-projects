'''
Created on Aug 1, 2014

@author: stephane
'''
import unittest
from excelgeneratortest import TestExcelGenerator

def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    suite.addTest(TestExcelGenerator())
    return suite

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestExcelGenerator())
    return suite
