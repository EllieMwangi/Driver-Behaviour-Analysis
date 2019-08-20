import unittest

from api.daily_summaries import DailySummaries


class TestIdleCalculator(unittest.TestCase):
    def test_calculator(self):

        data = [0,0,0,0,0]
        data_2 = [6,7,0,2,1]
        result = DailySummaries('2017-09-07').trip_summaries.idle_time_calculator(data)
        result_2 = DailySummaries('2017-09-07').trip_summaries.idle_time_calculator(data_2)

        self.assertEqual(result, 5)
        self.assertEqual(result_2, [])

if __name__ == '__main__':
    unittest.main()