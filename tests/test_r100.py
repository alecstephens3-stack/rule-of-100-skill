"""Tests for the Rule of 100 tracker. Run: python3 -m unittest discover tests"""
import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "rule-of-100" / "scripts" / "r100.py"


def r(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True)


class TrackerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.run_dir = Path(self.tmp.name) / "demo"
        out = r("init", self.run_dir, "--action", "warm reach-outs", "--unit", "actions", "--start", "2020-01-01")
        self.assertEqual(out.returncode, 0, out.stderr)

    def tearDown(self):
        self.tmp.cleanup()

    def status(self, today):
        out = r("status", self.run_dir, "--today", today, "--json")
        self.assertEqual(out.returncode, 0, out.stderr)
        return json.loads(out.stdout)

    def log(self, day, count, *extra):
        return r("log", self.run_dir, "--date", day, "--count", count, *extra)

    def test_init_sets_day_100(self):
        run = json.loads((self.run_dir / "run.json").read_text())
        self.assertEqual(run["end"], "2020-04-09")  # 2020 is a leap year
        self.assertEqual(run["target"], 100)

    def test_init_never_overwrites(self):
        out = r("init", self.run_dir, "--action", "x", "--unit", "actions")
        self.assertNotEqual(out.returncode, 0)

    def test_hit_short_and_missed_days(self):
        self.log("2020-01-01", 100)
        self.log("2020-01-02", 100)
        self.log("2020-01-03", 40)
        # 2020-01-04 has no row
        self.log("2020-01-05", 100)
        s = self.status("2020-01-06")
        self.assertEqual((s["days_hit"], s["days_partial"], s["days_missed"]), (3, 1, 1))
        self.assertEqual(s["short_or_missed_dates"], ["2020-01-03", "2020-01-04"])
        self.assertEqual(s["total_done"], 340)

    def test_streak_resets_on_a_miss(self):
        for day in ("2020-01-01", "2020-01-02", "2020-01-03"):
            self.log(day, 100)
        self.log("2020-01-05", 100)
        self.log("2020-01-06", 100)
        s = self.status("2020-01-06")
        self.assertEqual(s["current_streak"], 2)
        self.assertEqual(s["longest_streak"], 3)

    def test_extra_on_one_day_does_not_repair_another(self):
        self.log("2020-01-01", 0)
        self.log("2020-01-02", 240)
        s = self.status("2020-01-03")
        self.assertEqual(s["days_hit"], 1)
        self.assertEqual(s["days_missed"], 1)

    def test_today_is_open_until_it_ends(self):
        self.log("2020-01-01", 100)
        self.log("2020-01-02", 30)
        s = self.status("2020-01-02")
        self.assertEqual(s["days_partial"], 0)  # today can still be finished
        self.assertEqual(s["today_left"], 70)
        self.assertEqual(s["current_streak"], 1)

    def test_add_accumulates_and_replace_overwrites(self):
        self.log("2020-01-01", 60)
        self.log("2020-01-01", 40, "--add")
        self.assertEqual(self.status("2020-01-01")["today_count"], 100)
        self.log("2020-01-01", 10)
        self.assertEqual(self.status("2020-01-01")["today_count"], 10)

    def test_refuses_dates_outside_the_run_and_in_the_future(self):
        self.assertNotEqual(self.log("2019-12-31", 5).returncode, 0)
        self.assertNotEqual(self.log("2020-04-10", 5).returncode, 0)
        self.assertNotEqual(self.log("2999-01-01", 5).returncode, 0)
        self.assertNotEqual(self.log("2020-01-01", -1).returncode, 0)

    def test_lead_measure_and_source_are_kept(self):
        self.log("2020-01-01", 100, "--lead", 3, "--source", "seen")
        self.log("2020-01-02", 100, "--lead", 2)
        s = self.status("2020-01-02")
        self.assertEqual(s["lead_total"], 5)
        self.assertEqual(s["reported_by_person_days"], 1)
        with (self.run_dir / "log.csv").open() as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(rows[0]["source"], "seen")

    def test_finished_run(self):
        s = self.status("2021-01-01")
        self.assertEqual(s["state"], "finished")
        self.assertEqual(s["day"], 100)
        self.assertEqual(s["days_missed"], 100)

    def test_adapted_number(self):
        other = Path(self.tmp.name) / "thirty"
        r("init", other, "--action", "x", "--unit", "minutes", "--target", 30, "--start", "2020-01-01")
        r("log", other, "--date", "2020-01-01", "--count", 30)
        out = json.loads(r("status", other, "--today", "2020-01-02", "--json").stdout)
        self.assertEqual(out["days_hit"], 1)

    def test_done_refuses_a_second_first_contact(self):
        self.assertEqual(r("done", self.run_dir, "--who", "Sam Lee", "--date", "2020-01-01", "--medium", "text").returncode, 0)
        again = r("done", self.run_dir, "--who", "  sam   LEE ", "--date", "2020-01-02")
        self.assertNotEqual(again.returncode, 0)
        self.assertIn("already contacted", again.stderr)
        follow = r("done", self.run_dir, "--who", "Sam Lee", "--date", "2020-01-02", "--follow-up")
        self.assertEqual(follow.returncode, 0, follow.stderr)
        self.assertIn("CONTACTED 2", r("check", self.run_dir, "--who", "sam lee").stdout)
        self.assertIn("NEW", r("check", self.run_dir, "--who", "Someone Else").stdout)

    def test_follow_up_needs_a_first_contact(self):
        self.assertNotEqual(r("done", self.run_dir, "--who", "Nobody", "--date", "2020-01-01", "--follow-up").returncode, 0)

    def test_blocked_people_are_refused(self):
        r("block", self.run_dir, "--who", "Pat Doe", "--reason", "said no")
        out = r("done", self.run_dir, "--who", "pat doe", "--date", "2020-01-01")
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("BLOCKED", r("check", self.run_dir, "--who", "Pat Doe").stdout)

    def test_log_from_done_counts_first_contacts_only(self):
        for name in ("A", "B", "C"):
            r("done", self.run_dir, "--who", name, "--date", "2020-01-01")
        r("done", self.run_dir, "--who", "D", "--date", "2020-01-02")
        r("done", self.run_dir, "--who", "A", "--date", "2020-01-02", "--follow-up")
        r("log", self.run_dir, "--from-done", "--date", "2020-01-01")
        r("log", self.run_dir, "--from-done", "--date", "2020-01-02")
        with (self.run_dir / "log.csv").open() as fh:
            rows = {x["date"]: x for x in csv.DictReader(fh)}
        self.assertEqual(rows["2020-01-01"]["count"], "3")
        self.assertEqual(rows["2020-01-02"]["count"], "1")
        self.assertEqual(rows["2020-01-01"]["source"], "seen")

    def test_late_report_of_a_past_day_is_allowed(self):
        self.assertEqual(self.status("2020-01-02")["days_missed"], 1)
        self.log("2020-01-01", 100)
        s = self.status("2020-01-02")
        self.assertEqual((s["days_hit"], s["days_missed"]), (1, 0))
        self.assertEqual(s["reported_by_person_days"], 1)

    def test_results_and_replies_add_up_over_days(self):
        self.log("2020-01-01", 100, "--lead", 10)
        r("log", self.run_dir, "--date", "2020-01-01", "--count", 0, "--add", "--lead", 12, "--result", 1)
        s = self.status("2020-01-01")
        self.assertEqual((s["today_count"], s["lead_total"], s["result_total"]), (100, 22, 1))

    def test_finish_stops_the_clock(self):
        out = r("finish", self.run_dir, "--reason", "list ran out")
        self.assertEqual(out.returncode, 0, out.stderr)
        run = json.loads((self.run_dir / "run.json").read_text())
        self.assertTrue(run["finished"])
        s = self.status("2999-01-01")
        self.assertEqual(s["state"], "stopped early")
        self.assertNotEqual(r("finish", self.run_dir).returncode, 0)

    def test_bad_inputs_give_a_plain_message(self):
        out = r("log", self.run_dir, "--date", "yesterday", "--count", 5)
        self.assertNotEqual(out.returncode, 0)
        self.assertNotIn("Traceback", out.stderr)
        bad = subprocess.run([sys.executable, str(SCRIPT), "status", str(self.run_dir)], capture_output=True, text=True,
                             env={**__import__("os").environ, "R100_TZ": "Not/AZone"})
        self.assertNotEqual(bad.returncode, 0)
        self.assertNotIn("Traceback", bad.stderr)


if __name__ == "__main__":
    unittest.main()
