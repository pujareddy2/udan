import unittest
from unittest.mock import patch
from backend.integrations.profile_agent import parse_profile, profile_from_form
from backend.integrations.explain import explain
from backend.logic.scam_shield import check_scam
from backend.logic.skill_to_scheme import free_fix
from backend.logic.missed_and_alerts import missed, alerts
from backend.logic.eligibility import check_eligibility
from backend.server import app


class TestProfileAgent(unittest.TestCase):
    @patch("backend.integrations.profile_agent.call_gemini")
    def test_parse_profile_success(self, mock_call_gemini):
        mock_call_gemini.return_value = """
        ```json
        {
            "name": "Sree",
            "age": 25,
            "gender": "female",
            "category": "OBC",
            "state": "Telangana",
            "qualification": "graduate",
            "income": 50000,
            "skills": ["typing", "excel"],
            "interests": ["reading"]
        }
        ```
        """
        result = parse_profile("I am Sree, 25 years old OBC female from Telangana...", "jobseeker")
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Sree")
        self.assertEqual(result["age"], 25)
        self.assertEqual(result["gender"], "female")
        self.assertEqual(result["category"], "OBC")
        self.assertEqual(result["state"], "Telangana")
        self.assertEqual(result["qualification"], "graduate")
        self.assertEqual(result["income"], 50000)
        self.assertEqual(result["skills"], ["typing", "excel"])
        self.assertEqual(result["interests"], ["reading"])
        self.assertEqual(result["module"], "jobseeker")

    @patch("backend.integrations.profile_agent.call_gemini")
    def test_parse_profile_invalid_json(self, mock_call_gemini):
        mock_call_gemini.return_value = "This is not JSON at all."
        result = parse_profile("invalid text", "jobseeker")
        self.assertIsNone(result)

    @patch("backend.integrations.profile_agent.call_gemini")
    def test_parse_profile_validation_failure(self, mock_call_gemini):
        mock_call_gemini.return_value = """
        {
            "name": "Sree",
            "age": [25],
            "gender": "female",
            "module": "jobseeker"
        }
        """
        result = parse_profile("invalid text", "jobseeker")
        self.assertIsNone(result)

    def test_profile_from_form(self):
        form = {
            "name": "Ravi",
            "age": "30",
            "gender": "male",
            "category": "general",
            "state": "Telangana",
            "qualification": "post-graduate",
            "income": "120000",
            "skills": "typing",   # raw string — should be normalised to list
            "interests": None
        }
        result = profile_from_form(form, "jobseeker")
        self.assertEqual(result["name"], "Ravi")
        self.assertEqual(result["age"], 30)
        self.assertEqual(result["gender"], "male")
        self.assertEqual(result["category"], "general")
        self.assertEqual(result["state"], "Telangana")
        self.assertEqual(result["qualification"], "post-graduate")
        self.assertEqual(result["income"], 120000)
        self.assertEqual(result["skills"], ["typing"])
        self.assertEqual(result["interests"], [])
        self.assertEqual(result["module"], "jobseeker")


class TestExplain(unittest.TestCase):
    @patch("backend.integrations.explain.call_gemini")
    def test_explain_success(self, mock_call_gemini):
        mock_call_gemini.return_value = (
            '["Kondapalli toy making is a traditional skill.", "You need an Aadhaar card."]'
        )
        engine_result = {
            "verdict": "partial",
            "reasons": ["Skill is Kondapalli toy making.", "Must have Aadhaar card."],
            "missing_documents": ["aadhaar"],
            "missing_skills": ["kondapalli_toys"],
            "readiness": 50
        }
        result = explain(engine_result, "en")

        self.assertEqual(result["verdict"], "partial")
        self.assertEqual(result["readiness"], 50)
        self.assertEqual(result["missing_documents"], ["aadhaar"])
        self.assertEqual(result["missing_skills"], ["kondapalli_toys"])
        self.assertEqual(result["reasons_plain"], [
            "Kondapalli toy making is a traditional skill.",
            "You need an Aadhaar card."
        ])

    @patch("backend.integrations.explain.call_gemini")
    def test_explain_failure_fallback(self, mock_call_gemini):
        mock_call_gemini.return_value = None
        engine_result = {
            "verdict": "not_eligible",
            "reasons": ["Age must be under 30."],
            "missing_documents": [],
            "missing_skills": [],
            "readiness": 0
        }
        result = explain(engine_result, "te")
        self.assertEqual(result["verdict"], "not_eligible")
        self.assertEqual(result["readiness"], 0)
        self.assertEqual(result["reasons_plain"], ["Age must be under 30."])

    @patch("backend.integrations.explain.call_gemini")
    def test_explain_wrong_length_fallback(self, mock_call_gemini):
        mock_call_gemini.return_value = '["Only one sentence returned."]'
        engine_result = {
            "verdict": "partial",
            "reasons": ["Reason one.", "Reason two."],
            "missing_documents": [],
            "missing_skills": [],
            "readiness": 80
        }
        result = explain(engine_result, "hi")
        self.assertEqual(result["verdict"], "partial")
        self.assertEqual(result["readiness"], 80)
        self.assertEqual(result["reasons_plain"], ["Reason one.", "Reason two."])

    @patch("backend.integrations.explain.call_gemini")
    def test_explain_verdict_unchanged(self, mock_call_gemini):
        """Verdict and readiness must never change regardless of LLM output."""
        mock_call_gemini.return_value = '["translated reason"]'
        engine_result = {
            "verdict": "eligible",
            "reasons": ["You meet age limit."],
            "missing_documents": [],
            "missing_skills": [],
            "readiness": 95
        }
        result = explain(engine_result, "te")
        self.assertEqual(result["verdict"], "eligible")
        self.assertEqual(result["readiness"], 95)


class TestScamShield(unittest.TestCase):
    def test_scam_posting(self):
        result = check_scam("Pay Rs 5000 to confirm your government job, limited seats!")
        self.assertTrue(result["is_scam"])
        self.assertIn("Money/fee/payment requested", result["flags"])
        self.assertIn("Urgency language used", result["flags"])

    def test_legit_posting(self):
        result = check_scam("SSC CGL 2026 notification released, apply on ssc.gov.in")
        self.assertFalse(result["is_scam"])
        self.assertEqual(result["flags"], [])

    def test_fake_govt_domain(self):
        result = check_scam("Get a guaranteed government job at sarkari-naukri.com")
        self.assertTrue(result["is_scam"])
        self.assertTrue(any("non-official domain" in f for f in result["flags"]))

    def test_otp_requested(self):
        result = check_scam("Send your OTP to verify your government application")
        self.assertTrue(result["is_scam"])
        self.assertIn("Financial/account details requested", result["flags"])

    def test_empty_input(self):
        result = check_scam("")
        self.assertFalse(result["is_scam"])
        self.assertEqual(result["flags"], [])


class TestFreeFixT5(unittest.TestCase):
    """T5 — Skill → free-scheme map tests."""

    def test_typing_returns_pmkvy(self):
        """free_fix(["typing"]) must return the PMKVY entry."""
        result = free_fix(["typing"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["skill"], "typing")
        self.assertIn("PMKVY", result[0]["scheme"])
        self.assertEqual(result[0]["url"], "https://pmkvyofficial.org")

    def test_quantitative_aptitude(self):
        result = free_fix(["quantitative_aptitude"])
        self.assertEqual(len(result), 1)
        self.assertIn("NIELIT", result[0]["scheme"])

    def test_spoken_english(self):
        result = free_fix(["spoken_english"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["skill"], "spoken_english")

    def test_open_source(self):
        result = free_fix(["open_source"])
        self.assertEqual(len(result), 1)
        self.assertIn("NASSCOM", result[0]["scheme"])

    def test_computer_basics(self):
        result = free_fix(["computer_basics"])
        self.assertEqual(len(result), 1)
        self.assertIn("PMGDISHA", result[0]["scheme"])

    def test_unknown_skill_skipped(self):
        """Skills not in the map are silently skipped."""
        result = free_fix(["some_unknown_skill_xyz"])
        self.assertEqual(result, [])

    def test_mixed_known_and_unknown(self):
        result = free_fix(["typing", "unknown_xyz", "spoken_english"])
        self.assertEqual(len(result), 2)
        skills_returned = [r["skill"] for r in result]
        self.assertIn("typing", skills_returned)
        self.assertIn("spoken_english", skills_returned)

    def test_normalises_spaces_and_hyphens(self):
        """Input with spaces or hyphens should still match."""
        result = free_fix(["computer basics", "spoken-english"])
        self.assertEqual(len(result), 2)

    def test_empty_list(self):
        self.assertEqual(free_fix([]), [])

    def test_case_insensitive(self):
        result = free_fix(["Typing", "SPOKEN_ENGLISH"])
        self.assertEqual(len(result), 2)


class TestMissedOpportunities(unittest.TestCase):
    """T6 — missed() tests."""

    def _make_opp(self, title, is_active, close_date=None, **kwargs):
        return {"title": title, "is_active": is_active,
                "close_date": close_date, **kwargs}

    def _engine_eligible(self, profile, opp):
        return {"verdict": "eligible", "readiness": 80}

    def _engine_not_eligible(self, profile, opp):
        return {"verdict": "not_eligible", "readiness": 10}

    def test_missed_returns_inactive_eligible(self):
        """An inactive+eligible opportunity must appear in missed()."""
        opps = [
            self._make_opp("SSC CGL 2023", is_active=False),
        ]
        result = missed({}, opps, self._engine_eligible)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "SSC CGL 2023")
        self.assertIn("_eligibility", result[0])

    def test_missed_skips_active(self):
        """Active opportunities must NOT appear in missed()."""
        opps = [
            self._make_opp("SSC CGL 2026", is_active=True),
        ]
        result = missed({}, opps, self._engine_eligible)
        self.assertEqual(result, [])

    def test_missed_skips_not_eligible(self):
        """Inactive but NOT eligible → must not appear."""
        opps = [
            self._make_opp("TSPSC Group 4 2022", is_active=False),
        ]
        result = missed({}, opps, self._engine_not_eligible)
        self.assertEqual(result, [])

    def test_missed_multiple_mixed(self):
        """Only inactive+eligible rows surface."""
        opps = [
            self._make_opp("Past Eligible", is_active=False),
            self._make_opp("Past Not Eligible", is_active=False),
            self._make_opp("Active Eligible", is_active=True),
        ]
        def engine(profile, opp):
            if opp["title"] == "Past Not Eligible":
                return {"verdict": "not_eligible"}
            return {"verdict": "eligible"}

        result = missed({}, opps, engine)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Past Eligible")

    def test_missed_string_is_active_false(self):
        """String 'false' for is_active must be treated as inactive."""
        opps = [self._make_opp("Old Scheme", is_active="false")]
        result = missed({}, opps, self._engine_eligible)
        self.assertEqual(len(result), 1)

    def test_missed_engine_exception_skipped(self):
        """If engine raises, that opportunity is silently skipped."""
        def bad_engine(profile, opp):
            raise RuntimeError("engine error")
        opps = [self._make_opp("Bad Opp", is_active=False)]
        result = missed({}, opps, bad_engine)
        self.assertEqual(result, [])

    def test_missed_empty_opportunities(self):
        self.assertEqual(missed({}, [], self._engine_eligible), [])


class TestAlerts(unittest.TestCase):
    """T6 — alerts() tests."""

    def _today(self):
        from datetime import date
        return date.today()

    def _opp(self, title, is_active, days_offset):
        """Create opp with close_date = today + days_offset."""
        from datetime import date, timedelta
        close = (self._today() + timedelta(days=days_offset)).isoformat()
        return {"title": title, "is_active": is_active, "close_date": close}

    def test_alerts_within_window(self):
        """Active opp closing in 10 days must appear in alerts(within_days=30)."""
        opps = [self._opp("SSC CHSL 2026", is_active=True, days_offset=10)]
        result = alerts({}, opps, within_days=30)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "SSC CHSL 2026")
        self.assertEqual(result[0]["days_left"], 10)
        self.assertIn("message", result[0])

    def test_alerts_outside_window_excluded(self):
        """Opp closing in 60 days must NOT appear in a 30-day window."""
        opps = [self._opp("Far Future Scheme", is_active=True, days_offset=60)]
        result = alerts({}, opps, within_days=30)
        self.assertEqual(result, [])

    def test_alerts_inactive_excluded(self):
        """Inactive (past) opportunities must never appear in alerts."""
        opps = [self._opp("Old Scheme", is_active=False, days_offset=5)]
        result = alerts({}, opps, within_days=30)
        self.assertEqual(result, [])

    def test_alerts_already_expired_excluded(self):
        """Opportunities with close_date in the past must be excluded."""
        opps = [self._opp("Expired Scheme", is_active=True, days_offset=-3)]
        result = alerts({}, opps, within_days=30)
        self.assertEqual(result, [])

    def test_alerts_no_close_date_excluded(self):
        """Opportunities without a close_date must be excluded."""
        opps = [{"title": "Open Ended", "is_active": True, "close_date": None}]
        result = alerts({}, opps, within_days=30)
        self.assertEqual(result, [])

    def test_alerts_sorted_by_days_left(self):
        """Results must be sorted by days_left ascending (soonest first)."""
        opps = [
            self._opp("Later", is_active=True, days_offset=20),
            self._opp("Sooner", is_active=True, days_offset=5),
            self._opp("Middle", is_active=True, days_offset=12),
        ]
        result = alerts({}, opps, within_days=30)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["title"], "Sooner")
        self.assertEqual(result[1]["title"], "Middle")
        self.assertEqual(result[2]["title"], "Later")

    def test_alerts_closing_today(self):
        """Opp closing today must say 'TODAY' in message."""
        opps = [self._opp("Urgent Scheme", is_active=True, days_offset=0)]
        result = alerts({}, opps, within_days=30)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["days_left"], 0)
        self.assertIn("TODAY", result[0]["message"])

    def test_alerts_empty_opportunities(self):
        self.assertEqual(alerts({}, [], within_days=30), [])


class TestEligibilityEngine(unittest.TestCase):
    """T10 — check_eligibility tests."""

    def test_eligible_perfect_match(self):
        profile = {
            "age": 25,
            "category": "general",
            "state": "Telangana",
            "qualification": "graduate",
            "skills": ["typing"]
        }
        opp = {
            "title": "SSC CGL",
            "min_age": 18,
            "max_age_general": 32,
            "qualifications": '["graduate"]',
            "categories": '["general"]',
            "states": '[]',
            "required_documents": '[]',
            "required_skills": '["typing"]'
        }
        res = check_eligibility(profile, opp)
        self.assertEqual(res["verdict"], "eligible")
        self.assertEqual(res["readiness"], 100)
        self.assertEqual(res["missing_skills"], [])

    def test_partial_missing_skills_and_docs(self):
        profile = {
            "age": 25,
            "category": "general",
            "state": "Telangana",
            "qualification": "graduate",
            "skills": []
        }
        opp = {
            "title": "SSC CGL",
            "min_age": 18,
            "max_age_general": 32,
            "qualifications": '["graduate"]',
            "categories": '["general"]',
            "states": '[]',
            "required_documents": '["degree_certificate"]',
            "required_skills": '["typing"]'
        }
        res = check_eligibility(profile, opp)
        self.assertEqual(res["verdict"], "partial")
        self.assertIn("typing", res["missing_skills"])
        self.assertIn("degree_certificate", res["missing_documents"])
        self.assertTrue(0 < res["readiness"] < 100)

    def test_not_eligible_age_too_high(self):
        profile = {
            "age": 35,
            "category": "general",
            "state": "Telangana",
            "qualification": "graduate"
        }
        opp = {
            "title": "SSC CGL",
            "min_age": 18,
            "max_age_general": 32
        }
        res = check_eligibility(profile, opp)
        self.assertEqual(res["verdict"], "not_eligible")
        self.assertTrue(any("exceeds" in r for r in res["reasons"]))

    def test_age_relaxation_obc(self):
        """OBC user age 34 should be eligible if general max is 32 and OBC max is 35."""
        profile = {
            "age": 34,
            "category": "obc",
            "state": "Telangana",
            "qualification": "graduate"
        }
        opp = {
            "title": "SSC CGL",
            "min_age": 18,
            "max_age_general": 32,
            "max_age_obc": 35
        }
        res = check_eligibility(profile, opp)
        # category match is open to all if categories is not defined, or matches obc
        self.assertEqual(res["verdict"], "eligible")

    def test_state_restricted(self):
        """Domicile state mismatch should fail core eligibility."""
        profile = {
            "age": 25,
            "category": "general",
            "state": "Andhra Pradesh",
            "qualification": "graduate"
        }
        opp = {
            "title": "TSPSC Group 4",
            "states": '["Telangana"]'
        }
        res = check_eligibility(profile, opp)
        self.assertEqual(res["verdict"], "not_eligible")
        self.assertTrue(any("state" in r or "Domicile" in r for r in res["reasons"]))


class TestServerAPI(unittest.TestCase):
    """T11 — Web server endpoints integration tests."""

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_ping(self):
        res = self.client.get("/api/ping")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json["status"], "healthy")

    def test_scam_check_endpoint(self):
        payload = {"text": "Pay Rs 5000 to confirm your government job!"}
        res = self.client.post("/api/scam/check", json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json["is_scam"])

    @patch("backend.server.parse_profile")
    def test_profile_parse_endpoint(self, mock_parse_profile):
        mock_parse_profile.return_value = {
            "name": "Sree",
            "age": 25,
            "module": "jobseeker"
        }
        payload = {"text": "I am Sree, 25 years old", "module": "jobseeker", "lang": "te"}
        res = self.client.post("/api/profile/parse", json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json["name"], "Sree")

    @patch("backend.server.explain")
    def test_opportunities_match_endpoint(self, mock_explain):
        mock_explain.return_value = {
            "verdict": "eligible",
            "readiness": 100,
            "reasons_plain": ["Age matched."],
            "missing_documents": [],
            "missing_skills": []
        }
        profile = {
            "name": "Sree",
            "age": 25,
            "category": "general",
            "state": "Telangana",
            "qualification": "graduate",
            "module": "jobseeker"
        }
        payload = {"profile": profile, "lang": "en"}
        res = self.client.post("/api/opportunities/match", json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertIn("eligible", res.json)
        self.assertIn("missed", res.json)
        self.assertIn("alerts", res.json)


if __name__ == "__main__":
    unittest.main()

