import unittest
import numpy as np
import pandas as pd
from changepoint import changepoint
from optimize import best_index, smooth, robust_index
import audit
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


class TestRobust(unittest.TestCase):
    def test_one_scenario_matches_the_plain_best_date(self):
        risk = [0.9 - 0.01 * i for i in range(80)]
        for w in (0.0, 0.01, 0.03):
            idx, regret, own = robust_index([risk], w)
            self.assertEqual(idx, best_index(risk, w))
            self.assertEqual(regret, 0)

    def test_identical_scenarios_agree_with_one(self):
        risk = [0.8 - 0.012 * i for i in range(60)]
        self.assertEqual(robust_index([risk, risk, risk], 0.02)[0], robust_index([risk], 0.02)[0])

    def test_conflicting_scenarios_land_between_their_best_dates(self):
        early = [abs(i - 10) / 40 for i in range(60)]       # safest around day 10
        late = [abs(i - 40) / 40 for i in range(60)]        # safest around day 40
        idx, regret, own = robust_index([early, late], 0.0)
        self.assertLess(own[0], idx); self.assertLess(idx, own[1])
        self.assertGreater(regret, 0)

    def test_worst_case_regret_is_no_worse_than_either_own_best(self):
        early = [abs(i - 10) / 40 for i in range(60)]
        late = [abs(i - 40) / 40 for i in range(60)]
        idx, regret, own = robust_index([early, late], 0.0)
        # picking either scenario's own best date would give at least this much worst-case regret
        for pick in own:
            s = [smooth(early), smooth(late)]
            worst = max(s[0][pick] - min(s[0]), s[1][pick] - min(s[1]))
            self.assertGreaterEqual(worst + 1e-9, regret)


def _cmp(daily=0.8, five=0.9, yearly=0.9, shift_n=20, shift_o=20, drop_n=-10, drop_o=-10, mean_n=1600, mean_o=1600, p_n=0.01, p_o=0.01):
    return {"daily_correlation": daily, "five_day_correlation": five, "yearly_total_correlation": yearly,
            "onset_year_correlation": 0.8, "onset_mean_abs_diff_days": 3,
            "mean_annual_mm": {"nasa": mean_n, "other": mean_o},
            "nasa": {"shift_days": shift_n, "annual_change_pct": drop_n, "step_p": p_n},
            "other": {"shift_days": shift_o, "annual_change_pct": drop_o, "step_p": p_o}}


class TestAudit(unittest.TestCase):
    def test_close_agreement_is_strong(self):
        r = audit.assess(_cmp())
        self.assertEqual(r["level"], "strong"); self.assertEqual(r["flags"], [])

    def test_your_real_pattern_is_weak(self):
        # the Enugu numbers from the first real comparison
        r = audit.assess(_cmp(daily=0.37, five=0.54, yearly=0.06, shift_n=21, shift_o=3, drop_n=-20, drop_o=-6,
                              mean_n=1623, mean_o=1594, p_n=0.007, p_o=0.918))
        self.assertEqual(r["level"], "weak")
        text = " ".join(r["flags"])
        self.assertIn("Yearly totals barely agree", text)
        self.assertIn("The later start differs", text)
        self.assertIn("Only NASA POWER shows a statistically significant jump", text)

    def test_middle_case_is_moderate(self):
        r = audit.assess(_cmp(yearly=0.7, shift_n=20, shift_o=14, drop_n=-10, drop_o=-8))
        self.assertEqual(r["level"], "moderate")

    def test_big_difference_in_average_rain_is_flagged(self):
        r = audit.assess(_cmp(mean_n=1900, mean_o=1200))
        self.assertTrue(any("Average yearly rain differs" in f for f in r["flags"]))

    def test_summary_wording(self):
        weak = {k: {"level": "weak"} for k in "abc"}
        self.assertIn("weakly at all 3", audit.summary_text(weak))
        self.assertIn("unconfirmed", audit.summary_text(weak))
        strong = {k: {"level": "strong"} for k in "abc"}
        self.assertIn("agree well at all 3", audit.summary_text(strong))


if __name__ == "__main__":
    unittest.main()
