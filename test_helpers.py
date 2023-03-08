import unittest
import helpers

# TO RUN THESE TESTS: python -m unittest test_helpers.py

class TestServer(unittest.TestCase):

    def test_write_data(self):
        test_data = ['a', 'b', 'c', 'd']
        # write data to test file
        self.assertEqual(helpers.write_data("test.csv", test_data), test_data)
    
    def test_init_log(self):
        port1, port2, port3 = 1000, 2000, 3000
        portDict = {'port1':1000, 'port2':2000,'port3':3000}
        filenameTickspeeds = ["1", "2", "3", "4", "5", "6"]
        tickspeeds = [1,2,3,4,5,6]
        # check port identification is correct
        self.assertEqual(helpers.init_log(port1, portDict)[0].split("_")[0], "1")
        self.assertEqual(helpers.init_log(port2, portDict)[0].split("_")[0], "2")
        self.assertEqual(helpers.init_log(port3, portDict)[0].split("_")[0], "3")
        # check clock rate roll is within correct bounds and entered into filename correctly
        self.assertIn(helpers.init_log(port1, portDict)[0].split("_")[1], filenameTickspeeds)
        self.assertIn(helpers.init_log(port2, portDict)[0].split("_")[1], filenameTickspeeds)
        self.assertIn(helpers.init_log(port3, portDict)[0].split("_")[1], filenameTickspeeds)
        # check clock rate roll is within correct bounds
        self.assertIn(helpers.init_log(port1, portDict)[1], tickspeeds)
        self.assertIn(helpers.init_log(port2, portDict)[1], tickspeeds)
        self.assertIn(helpers.init_log(port3, portDict)[1], tickspeeds)
    