#!/usr/bin/env python
#
# wtime unit tests
#
import sys
from wtime3 import wtime
import unittest

class TestStringMethods(unittest.TestCase):

    def test_getTimes(self):
        t1,t2,t3,t4 = wtime.getTimes("wtime3")
        self.assertEquals((t1, t2, t3, t4),
                          (None, None, None, None))

    def test_wt(self):
        wt = wtime(t1=None,t2=None,t3=None,t4=None) 
        self.assertFalse(wt is None)

    def test_calc2(self):
        wt = wtime(t1=None,t2=None,t3=None,t4=None) 
        out = wt.calc2()
        self.assertTrue(out is not None)

if __name__ == '__main__':
    unittest.main()

