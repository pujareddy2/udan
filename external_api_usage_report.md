# Job Seeker Dashboard Feature Audit: External API & Backend Usage Report

This report presents an audit of the newly implemented **Job Seeker Dashboard** features in the UDAAN platform, analyzing their current interactions with backend logic, database queries, and external APIs (specifically GROQ and SERPER).

---

## 📊 Feature Audit: API & Logic Usage

Currently, all 11 newly implemented features in the standalone frontend client ([UDAAN AI (standalone).html](file:///c:/Users/CHINNI/OneDrive/Desktop/Udaan/udan/UDAAN%20AI%20(standalone).html)) are implemented using **hardcoded mock states and client-side heuristics**. They do not perform live HTTP requests to the backend or external APIs.

The table below audits each feature's current implementation and details if equivalent backend or external API logic exists.

| Feature Name | Uses Internal Backend Logic? | Uses Database Queries? | Uses GROQ API? | Uses SERPER API? | Available Backend / External API Support (Gaps & Opportunities) |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Profile Summary Strip** | ❌ No | ❌ No | ❌ No | ❌ No | **Available**: `/api/v1/auth/{user_id}/profile` saves baseline details, and `/api/v1/profile/{user_id}/jobseeker` updates seeker details in the SQLite DB. |
| **Missed Opportunity Banner** | ❌ No | ❌ No | ❌ No | ❌ No | **Available**: `/api/v1/lifecycle/missed-opportunities` lists expired schemes and regret reasons from the database. |
| **Eligibility Decoder** | ❌ No | ❌ No | ❌ No | ❌ No | **Available**: `backend/logic/eligibility.py` calculates limits and categories. However, the exact age-relaxation reasoning strings (e.g. OBC 3-year relaxation) are client-side only and not exposed in the API schema. |
| **Scam Shield** | ❌ No | ❌ No | ❌ No | ❌ No | **No Endpoint**: Python logic exists in `backend/logic/scam_shield.py` (which runs regex filters on fees and domain names), but **no REST API endpoint** exists in the FastAPI or Flask servers to expose it. |
| **Readiness Ring + Free Scheme Fix**| ❌ No | ❌ No | ❌ No | ❌ No | **Partial**: `/api/v1/readiness` retrieves the overall score. However, there is no backend endpoint to support simulating/submitting a skill upgrade (like PMKVY Java Course enrollment) to update the score. |
| **Document Readiness Panel** | ❌ No | ❌ No | ❌ No | ❌ No | **Available**: `/api/v1/wallet/documents` lists verified/missing documents. No endpoint exists to trigger a mock document upload/verification. |
| **Priority Ranking with sorting** | ❌ No | ❌ No | ❌ No | ❌ No | **No**: Sorting and priority score calculations (based on deadline, readiness, and benefit amount) are fully calculated client-side using `getPriorityScore`. |
| **Trust / Source Chips** | ❌ No | ❌ No | ❌ No | ❌ No | **No**: Opportunity schemas returned by `/api/v1/opportunities/eligible` do not include trust scores, source URLs, or government flags. |
| **Roadmap / Next Steps Card** | ❌ No | ❌ No | ❌ No | ❌ No | **Partial**: `/api/v1/lifecycle/recovery-plan` returns a list of action items, but it does not map directly to the UI roadmap milestone checklist. |
| **Alert Center Drawer** | ❌ No | ❌ No | ❌ No | ❌ No | **Partial**: Backend has notification data access (`notification_db.py`), but there is no API endpoint that exposes these alerts to the frontend. |
| **Voice Chat Coach** | ❌ No | ❌ No | ❌ No | ❌ No | **Available**: `/api/v1/voice_agent/chat` processes natural language voice transcripts and routes to the LLM agent via GROQ API. The UI dialog currently uses a client-side hardcoded fallback. |

---

## 🔑 External API Key References

The UDAAN platform utilizes environment keys configured via the `.env` file and managed by Pydantic settings. Below is the reference map of where `GROQ_API_KEY` and `SERPER_API_KEY` are used in the codebase.

### 1. GROQ_API_KEY References

The `GROQ_API_KEY` is used to authenticate requests to the Groq Cloud API for natural language understanding, profile parsing, and conversational guidance.

* **[backend/integrations/llm.py](file:///c:/Users/CHINNI/OneDrive/Desktop/Udaan/udan/backend/integrations/llm.py#L12-L14)**:
  Loads the key using `os.getenv("GROQ_API_KEY")` with a fallback to `LLM_API_KEY` to initialize LLM chat clients.
* **[app/core/config.py](file:///c:/Users/CHINNI/OneDrive/Desktop/Udaan/udan/app/core/config.py#L19)**:
  Declares `GROQ_API_KEY: str = ""` as part of the Pydantic Settings class for the FastAPI configuration.
* **[app/api/routers/voice_agent.py](file:///c:/Users/CHINNI/OneDrive/Desktop/Udaan/udan/app/api/routers/voice_agent.py#L59)**:
  Accesses `settings.GROQ_API_KEY` to configure the conversation and routing agent.
* **[app/api/routers/test_integration.py](file:///c:/Users/CHINNI/OneDrive/Desktop/Udaan/udan/app/api/routers/test_integration.py#L17-L19)**:
  Validates if the environment variable is active and performs health checks against the Groq API.
* **[scripts/demo_flow.py](file:///c:/Users/CHINNI/OneDrive/Desktop/Udaan/udan/scripts/demo_flow.py#L89-L101)**:
  Checks for the key on startup; if missing, falls back to a simulated LLM parser to allow demo validation.
* **[test_apis.py](file:///c:/Users/CHINNI/OneDrive/Desktop/Udaan/udan/test_apis.py#L8)**:
  A standalone testing script that validates connection capability with the Groq API endpoint.

### 2. SERPER_API_KEY References

The `SERPER_API_KEY` is used to query the Google Search API (via Serper.dev) for discovering new government schemes and job listings dynamically from the web.

* **[app/core/config.py](file:///c:/Users/CHINNI/OneDrive/Desktop/Udaan/udan/app/core/config.py#L18)**:
  Declares `SERPER_API_KEY: str = ""` as a configuration setting.
* **[app/api/routers/test_integration.py](file:///c:/Users/CHINNI/OneDrive/Desktop/Udaan/udan/app/api/routers/test_integration.py#L119-L121)**:
  References `settings.SERPER_API_KEY` to execute integration health tests for organic and image web queries on `https://google.serper.dev/search`.
* **[test_apis.py](file:///c:/Users/CHINNI/OneDrive/Desktop/Udaan/udan/test_apis.py#L35)**:
  Validates Serper API connectivity and parses the result counts.
* **[app/services/internet_discovery.py](file:///c:/Users/CHINNI/OneDrive/Desktop/Udaan/udan/app/services/internet_discovery.py)**:
  Main service class that handles query generation and parses web results. It uses a mock implementation (`_call_serper_api`) in local testing to save credits.

---

## 🚨 Features Lacking Backend or External API Support

While the UDAAN backend contains highly sophisticated engines for profile extraction and eligibility matching, the audit reveals the following **structural gaps** where frontend features have **no corresponding backend endpoints or schemas**:

1. **Scam Shield API Endpoint**:
   - *Status*: The backend contains a robust heuristic scanner (`backend/logic/scam_shield.py`), but there is no FastAPI or Flask router endpoint exposing this function.
   - *Impact*: The frontend must rely entirely on duplicate client-side keyword checks until a POST endpoint is created.
2. **Opportunities Enrichment Fields (Trust Score & Source Domains)**:
   - *Status*: The `/api/v1/opportunities/eligible` schema lacks fields for `trust_score`, `is_govt`, and `source` domain names.
   - *Impact*: These chips cannot be populated dynamically from the current backend database model.
3. **Interactive Skill/Course Upgrades**:
   - *Status*: There is no backend endpoint to support enrolling in training schemes (like PMKVY) or dynamically registering a course completion.
   - *Impact*: Upgrading readiness remains a non-persistent, client-side simulation.
