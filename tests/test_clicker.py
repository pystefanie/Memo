import unittest
from clicker import ClickSchedule


class ScheduleTests(unittest.TestCase):
    def test_interval_and_no_catchup_burst(self):
        clicks = []
        schedule = ClickSchedule(0.1)
        schedule.start(10)
        self.assertFalse(schedule.tick(9, lambda: clicks.append(9)))
        self.assertTrue(schedule.tick(10, lambda: clicks.append(10)))
        self.assertFalse(schedule.tick(10.05, lambda: clicks.append(10.05)))
        self.assertTrue(schedule.tick(15, lambda: clicks.append(15)))
        self.assertFalse(schedule.tick(15, lambda: clicks.append(15)))
        self.assertEqual(clicks, [10, 15])

    def test_limit_stops_exactly(self):
        clicks = []
        schedule = ClickSchedule(0.1, limit=3)
        schedule.start(0)
        for now in range(10):
            schedule.tick(now, lambda: clicks.append(True))
        self.assertEqual(len(clicks), 3)
        self.assertFalse(schedule.running)

    def test_stop_and_restart(self):
        schedule = ClickSchedule(0.1)
        schedule.start(0)
        schedule.tick(0, lambda: None)
        schedule.stop()
        self.assertFalse(schedule.tick(1, lambda: self.fail('clicked after stop')))
        schedule.start(2)
        self.assertEqual(schedule.count, 0)
        self.assertTrue(schedule.tick(2, lambda: None))

    def test_failed_click_not_counted(self):
        schedule = ClickSchedule(0.1)
        schedule.start(0)
        def fail():
            raise RuntimeError('input blocked')
        with self.assertRaises(RuntimeError):
            schedule.tick(0, fail)
        self.assertEqual(schedule.count, 0)


if __name__ == '__main__':
    unittest.main()
