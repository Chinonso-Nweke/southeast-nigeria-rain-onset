import unittest
import pandas as pd
import onset


def make_year(year=2001):
    idx = pd.date_range(f"{year}-01-01", f"{year}-12-31")
    return pd.Series(0.0, index=idx)


def steady_rain(rain, start, end, mm=2.0, every=3):
    days = pd.date_range(start, end)
    for i, d in enumerate(days):
        if i % every == 0:
            rain[d] = mm


class TestOnset(unittest.TestCase):
    def setUp(self):
        onset.WET_MM, onset.WET_DAYS = 20, 3
        onset.DRY_MM, onset.DRY_SPELL_DAYS, onset.LOOKAHEAD_DAYS = 1, 7, 30

    def test_longest_dry_spell(self):
        self.assertEqual(onset.longest_dry_spell(pd.Series([0, 0, 5, 0, 0, 0])), 3)
        self.assertEqual(onset.longest_dry_spell(pd.Series([5, 5, 5])), 0)
        self.assertEqual(onset.longest_dry_spell(pd.Series([], dtype=float)), 0)

    def test_clean_onset(self):
        rain = make_year()
        rain["2001-04-10":"2001-04-12"] = 7
        steady_rain(rain, "2001-04-13", "2001-05-25")
        day, false_start = onset.onset_for_year(rain, 2001)
        self.assertEqual(day, pd.Timestamp("2001-04-12"))
        self.assertFalse(false_start)

    def test_false_start_then_real_onset(self):
        rain = make_year()
        rain["2001-03-10":"2001-03-12"] = 7     # early wet spell, then a long dry spell
        rain["2001-04-20":"2001-04-22"] = 7
        steady_rain(rain, "2001-04-23", "2001-06-01")
        day, false_start = onset.onset_for_year(rain, 2001)
        self.assertEqual(day, pd.Timestamp("2001-04-22"))
        self.assertTrue(false_start)

    def test_no_rain_at_all(self):
        day, false_start = onset.onset_for_year(make_year(), 2001)
        self.assertIsNone(day)
        self.assertFalse(false_start)

    def test_only_a_false_start(self):
        rain = make_year()
        rain["2001-03-10":"2001-03-12"] = 7
        day, false_start = onset.onset_for_year(rain, 2001)
        self.assertIsNone(day)
        self.assertTrue(false_start)

    def test_rain_before_march_is_ignored(self):
        rain = make_year()
        rain["2001-02-10":"2001-02-12"] = 7
        steady_rain(rain, "2001-02-13", "2001-03-25")
        day, _ = onset.onset_for_year(rain, 2001)
        self.assertIsNone(day)

    def test_dry_spell_of_six_days_is_allowed_seven_is_not(self):
        onset.LOOKAHEAD_DAYS = 10
        rain6 = make_year()
        rain6["2001-04-10":"2001-04-12"] = 7
        rain6["2001-04-19"] = 3                  # 6 dry days (13-18), then rain
        steady_rain(rain6, "2001-04-20", "2001-05-30")
        self.assertEqual(onset.onset_for_year(rain6, 2001)[0], pd.Timestamp("2001-04-12"))
        rain7 = make_year()
        rain7["2001-04-10":"2001-04-12"] = 7
        rain7["2001-04-20"] = 3                  # 7 dry days (13-19), then rain
        steady_rain(rain7, "2001-04-21", "2001-05-30")
        self.assertNotEqual(onset.onset_for_year(rain7, 2001)[0], pd.Timestamp("2001-04-12"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
