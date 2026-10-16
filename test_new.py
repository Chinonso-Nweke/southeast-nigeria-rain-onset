import unittest
import numpy as np
import pandas as pd
from changepoint import changepoint
from optimize import best_index, smooth
import check_data


class TestChangepoint(unittest.TestCase):
    def test_finds_a_clear_step(self):
        rng = np.random.default_rng(1)
        years = np.arange(1981, 2025)
        x = np.where(years < 2001, 95.0, 117.0) + rng.normal(0, 6, len(years))
        r = changepoint(years, x, n_perm=500)
        self.assertTrue(abs(r["change_year"] - 2001) <= 1)
        self.assertLess(r["p_perm"], 0.01)
        self.assertGreater(r["r2_step"], r["r2_line"])
        self.assertAlmostEqual(r["mean_after"] - r["mean_before"], 22, delta=6)

    def test_pure_noise_is_not_significant(self):
        rng = np.random.default_rng(2)
        years = np.arange(1981, 2025)
        r = changepoint(years, rng.normal(100, 15, len(years)), n_perm=500)
        self.assertGreater(r["p_perm"], 0.05)

    def test_steady_trend_prefers_the_line(self):
        years = np.arange(1981, 2025)
        x = 90 + 1.0 * (years - 1981) + np.random.default_rng(3).normal(0, 2, len(years))
        r = changepoint(years, x, n_perm=200)
        self.assertGreater(r["r2_line"], 0.8)


class TestOptimizer(unittest.TestCase):
    def test_free_waiting_picks_the_safest_date(self):
        risk = [0.9, 0.7, 0.4, 0.2, 0.1, 0.3, 0.5]
        self.assertEqual(best_index(risk * 1, 0.0), smooth(risk).index(min(smooth(risk))))

    def test_costly_waiting_picks_an_earlier_date(self):
        risk = [0.9 - 0.02 * i for i in range(60)]          # risk falls slowly
        free = best_index(risk, 0.0)
        costly = best_index(risk, 0.2)
        self.assertGreater(free, costly)
        self.assertEqual(costly, 0)

    def test_tie_goes_to_the_earlier_date(self):
        self.assertEqual(best_index([0.5] * 10, 0.0), 0)

    def test_one_odd_year_cannot_pick_the_date(self):
        risk = [0.5] * 40
        risk[20] = 0.0                                        # a single spike down
        self.assertLess(smooth(risk)[20], 0.5)
        self.assertGreater(smooth(risk)[20], 0.3)


class TestDataChecks(unittest.TestCase):
    def _run(self, series, tmp_name="zz_test"):
        import os
        series.to_csv(f"rain_{tmp_name}.csv")
        try:
            return check_data.check(tmp_name)
        finally:
            os.remove(f"rain_{tmp_name}.csv")

    def _clean(self):
        idx = pd.date_range("1981-01-01", "2020-12-31")
        return pd.Series(np.random.default_rng(0).gamma(0.4, 6, len(idx)), index=idx)

    def test_clean_data_has_no_problems(self):
        self.assertEqual(self._run(self._clean())["problems"], [])

    def test_many_missing_days_is_a_problem(self):
        s = self._clean(); s.iloc[:300] = np.nan
        self.assertTrue(self._run(s)["problems"])

    def test_negative_values_are_a_problem(self):
        s = self._clean(); s.iloc[10] = -5
        self.assertTrue(self._run(s)["problems"])

    def test_missing_dates_count_as_missing(self):
        s = self._clean().drop(pd.date_range("1990-01-01", "1990-12-31"))
        self.assertTrue(self._run(s)["problems"])


if __name__ == "__main__":
    unittest.main()
