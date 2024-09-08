import logging
import unittest
import datetime
import BARS
import os

from dotenv import load_dotenv
load_dotenv()

class IndependentTests(unittest.TestCase):

    def setUp(self):
        self.client = BARS.BClient(os.getenv('SESSIONID'))
        self.pupilid = int(os.getenv('PUPILID'))
        self.today = str(datetime.date.today())

    def test_get_diary(self):
        diary = self.client.get_diary(self.today)
        self.assertIsInstance(diary, list)

    def test_get_schedule(self):
        schedule_week = self.client.get_week_schedule(self.today)
        schedule_month = self.client.get_month_schedule(self.today)

        self.assertIsInstance(schedule_week, list)
        self.assertIsInstance(schedule_month, list)

    def test_get_schedule_report_link(self):
        report_link = self.client.get_schedule_report_link(self.today)
        assert report_link.startswith('https://xn--80atdl2c.xn--33-6kcadhwnl3cfdx.xn--p1ai/media/downloads/reports/Печать_расписания_на_')

    def test_get_summary_marks(self):
        self.client.get_summary_marks(self.today)

    def test_get_total_marks(self):
        self.client.get_total_marks()

    def test_get_account_info(self):
        account_info = self.client.get_account_info()
        self.assertEqual(self.pupilid, account_info.pupilid)

    def test_get_attendace_data(self):
        self.client.get_attendace_data(self.pupilid, "2000-01-01", "3000-01-01")

    def test_get_progress_data(self):
        self.client.get_progress_data(self.pupilid, "2000-01-01", "3000-01-01")

    def test_get_school_info(self):
        self.client.get_school_info()

    def test_get_class_info(self):
        self.client.get_class_info()

if __name__ == '__main__':
    unittest.main()
