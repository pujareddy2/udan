# Job Seeker Dashboard - API Validation Report

This report reviews the **Job Seeker Dashboard** requirements against:
1. The **actual running FastAPI OpenAPI/Swagger specification** (Port 8000).
2. The **Udaan AI Flask backend** (Port 5000), which contains the core rule-based engines.

It details the existing endpoints, implementation feasibility on the frontend, missing response fields, and required backend changes for each of the 11 target features.

---

## 🔍 OpenAPI Spec & Inventory Discrepancy Note

Before detailing the features, we highlight critical discrepancies found in the codebase compared to previous assumptions:
* **Authentication**: `/api/v1/auth/login` uses a JSON body (`LoginRequest` containing `email` and `password`), NOT url-encoded form data.
* **Missing Endpoints**: The endpoints `/api/v1/opportunities/eligible`, `/api/v1/opportunities/recommended`, `/api/v1/opportunities/{opportunity_id}`, and `/api/v1/wallet/documents` **do not exist** in the actual FastAPI routes.
* **Voice Agent Routing**: The voice chatbot endpoint is `/api/v1/voice/chat`, not `/api/v1/voice_agent/chat`.

---

## 📋 Feature-by-Feature API Gap Analysis

### 1. Profile Summary Strip
* **Feature Name**: Profile Summary Strip
* **Existing Endpoint(s)**: 
  * FastAPI: `/api/v1/dashboard/jobseeker/{user_id}` (GET)
* **Can Frontend Implement Immediately?**: No.
* **Missing Response Fields**: 
  * Specific demographic profile details (e.g. `full_name`, `age`, `gender`, `category`, `state`, `district`, `preferred_language`) are missing from the response.
  * It returns a static mock summary (`user_name: "User"`, `completion_percentage: 84`, `readiness_score: 82`, etc.) and does not fetch dynamic profile status from the database.
* **Whether Backend Modification is Required**: Yes. The FastAPI backend must be modified to query SQLModel tables (`UserProfile` and `JobSeekerProfile`) to return the actual user data and dynamically calculate completion percentage and readiness score.
* **Whether a Completely New Endpoint is Required**: No. The existing `/api/v1/dashboard/jobseeker/{user_id}` route can be modified.

---

### 2. Missed Opportunity Banner
* **Feature Name**: Missed Opportunity Banner
* **Existing Endpoint(s)**: 
  * FastAPI: `/api/v1/lifecycle/missed-opportunities` (GET)
  * Flask: `/api/opportunities/match` (POST)
* **Can Frontend Implement Immediately?**: No.
* **Missing Response Fields**: 
  * The FastAPI endpoint `/api/v1/lifecycle/missed-opportunities` returns a static mock list with a single post-matric scholarship entry. It does not compute missed opportunities dynamically for the logged-in jobseeker.
  * The Flask endpoint `/api/opportunities/match` calculates `missed` items dynamically, but it requires a POST request with the user's full profile context.
* **Whether Backend Modification is Required**: Yes. The FastAPI backend must be updated to dynamically evaluate missed opportunities (e.g., matching the user's profile against jobs/schemes that have expired or where requirements were missed) using the database and background logic.
* **Whether a Completely New Endpoint is Required**: No. The existing `/api/v1/lifecycle/missed-opportunities` endpoint can be modified.

---

### 3. Eligibility Decoder (with Age Relaxation Reasoning)
* **Feature Name**: Eligibility Decoder (with Age Relaxation Reasoning)
* **Existing Endpoint(s)**: 
  * FastAPI: `/api/v1/eligibility/run` (POST)
  * Flask: `/api/opportunities/match` (POST)
* **Can Frontend Implement Immediately?**: No.
* **Missing Response Fields**: 
  * The FastAPI `/api/v1/eligibility/run` endpoint is a static placeholder returning mock counts and stubs. It does not evaluate age criteria, category-based relaxations, or state residency, nor does it return age relaxation reasoning or multilingual explanations (`reasons_plain`).
  * The Flask matching endpoint evaluates eligibility and returns multilingual `reasons` dynamically, but it requires integration with the FastAPI spec.
* **Whether Backend Modification is Required**: Yes. The FastAPI eligibility router must be integrated with the rule-based eligibility calculation engine (incorporating age, category, state, education) and return detailed multilingual descriptions for each criterion, including specific age relaxation reasons.
* **Whether a Completely New Endpoint is Required**: No. The existing `/api/v1/eligibility/run` endpoint can be modified.

---

### 4. Scam Shield
* **Feature Name**: Scam Shield
* **Existing Endpoint(s)**: 
  * Flask: `/api/scam/check` (POST)
  * FastAPI: None.
* **Can Frontend Implement Immediately?**: No.
* **Missing Response Fields**: None (the Flask endpoint is fully functional, but it is not exposed on the primary FastAPI Swagger specification).
* **Whether Backend Modification is Required**: Yes. A route must be introduced in the FastAPI backend to expose this capability.
* **Whether a Completely New Endpoint is Required**: Yes, a new endpoint (e.g., `/api/v1/scam/check`) is required on the FastAPI backend.

---

### 5. Readiness Ring + Free Scheme Fix
* **Feature Name**: Readiness Ring + Free Scheme Fix
* **Existing Endpoint(s)**: 
  * FastAPI: `/api/v1/readiness` (GET)
  * Flask: `/api/opportunities/match` (POST)
* **Can Frontend Implement Immediately?**: No.
* **Missing Response Fields**: 
  * The FastAPI `/api/v1/readiness` endpoint only returns a single overall user `readiness_score` (mocked). It does not provide per-opportunity readiness breakdown, missing skills, or course/skill upgrades (such as PMKVY free course fixes).
  * The Flask matching endpoint calculates `upgrades` and `missing_skills` dynamically but is hosted on a separate port and requires POSTing the full profile.
* **Whether Backend Modification is Required**: Yes. The FastAPI backend must be modified to calculate per-opportunity readiness and map missing skills to free course upgrades (similar to the Flask backend's `upgrades` and `missing_skills` integration).
* **Whether a Completely New Endpoint is Required**: No. The existing `/api/v1/readiness` endpoint can be modified or we can return these fields inside the opportunity/match endpoints.

---

### 6. Document Readiness Panel
* **Feature Name**: Document Readiness Panel
* **Existing Endpoint(s)**: 
  * FastAPI: `/api/v1/{module}/documents/summary` (GET)
* **Can Frontend Implement Immediately?**: No.
* **Missing Response Fields**: 
  * The FastAPI `/api/v1/{module}/documents/summary` returns a static mock list with generic counts. It does not inspect the database or verify the user's uploaded documents against their matched opportunities.
  * Note: `/api/v1/wallet/documents` which was previously listed does not actually exist in the FastAPI OpenAPI spec.
* **Whether Backend Modification is Required**: Yes. The FastAPI backend must query the user's document wallet and the eligibility rules of matched opportunities to determine verified, missing, and expiring documents.
* **Whether a Completely New Endpoint is Required**: No. The existing `/api/v1/{module}/documents/summary` endpoint can be modified.

---

### 7. Priority Ranking
* **Feature Name**: Priority Ranking
* **Existing Endpoint(s)**: 
  * FastAPI: `/api/v1/opportunity-health/{opportunity_id}` (GET)
* **Can Frontend Implement Immediately?**: No.
* **Missing Response Fields**: 
  * There is no bulk priority ranking endpoint. The `/api/v1/opportunity-health/{opportunity_id}` endpoint only returns a static mock status ("Apply Immediately", score 95) for a single opportunity.
* **Whether Backend Modification is Required**: Yes. The backend must compute priority scores dynamically across all matched opportunities based on factors like deadline, benefit value, and readiness.
* **Whether a Completely New Endpoint is Required**: Yes, a new endpoint for batch priority ranking (or embedding priority fields directly within the opportunities list payload) is required.

---

### 8. Trust / Source Chips
* **Feature Name**: Trust / Source Chips
* **Existing Endpoint(s)**: 
  * FastAPI: `/api/v1/trust/{opportunity_id}` (GET)
* **Can Frontend Implement Immediately?**: Yes, partially, if the source URL is provided in the opportunity payload (e.g. checking for `.gov.in` domain).
* **Missing Response Fields**: 
  * The FastAPI `/api/v1/trust/{opportunity_id}` endpoint returns a static mock score (100) and type ("Government").
  * There is no dynamic trust engine or source categorization for all opportunities.
* **Whether Backend Modification is Required**: Yes. The backend needs to return trust metadata and domain verification flags within the list of matched opportunities.
* **Whether a Completely New Endpoint is Required**: No. The existing `/api/v1/trust/{opportunity_id}` can be made dynamic, or these flags should be embedded in the matching/eligible opportunity schema.

---

### 9. Roadmap / Next Steps Card
* **Feature Name**: Roadmap / Next Steps Card
* **Existing Endpoint(s)**: 
  * FastAPI: `/api/v1/lifecycle/recovery-plan` (GET)
* **Can Frontend Implement Immediately?**: No.
* **Missing Response Fields**: 
  * The FastAPI `/api/v1/lifecycle/recovery-plan` returns static text and hardcoded action items. It doesn't dynamically calculate the steps/milestones or direct links for the user's missing items.
* **Whether Backend Modification is Required**: Yes. The backend needs to calculate the recovery checklist items and milestones dynamically based on user profile state.
* **Whether a Completely New Endpoint is Required**: No. The existing `/api/v1/lifecycle/recovery-plan` endpoint can be modified to return dynamic data.

---

### 10. Alert Center
* **Feature Name**: Alert Center
* **Existing Endpoint(s)**: 
  * FastAPI: `/api/v1/deadlines/upcoming` (GET)
  * FastAPI: `/api/v1/notifications` (GET)
* **Can Frontend Implement Immediately?**: No.
* **Missing Response Fields**: 
  * `/api/v1/deadlines/upcoming` returns hardcoded farmer/agriculture deadlines and days remaining. It does not return actual jobseeker opportunity deadlines.
  * `/api/v1/notifications` returns general hardcoded notifications.
* **Whether Backend Modification is Required**: Yes. These endpoints must be updated to dynamically query jobseeker-specific records and matched opportunities.
* **Whether a Completely New Endpoint is Required**: No. The existing endpoints can be modified.

---

### 11. Voice Input Support
* **Feature Name**: Voice Input Support
* **Existing Endpoint(s)**: 
  * FastAPI: `/api/v1/voice/chat` (POST) (Note: it is `/api/v1/voice/chat`, NOT `/api/v1/voice_agent/chat` as previously reported)
  * Flask: `/api/profile/parse` (POST)
* **Can Frontend Implement Immediately?**: Yes, using the Web Speech API on the client side to transcribe audio to text, and calling the FastAPI/Flask parsing and chat endpoints.
* **Missing Response Fields**: None.
* **Whether Backend Modification is Required**: No.
* **Whether a Completely New Endpoint is Required**: No.

---

## 📊 Summary Matrix

| # | Feature Name | FastAPI Endpoint(s) | Reusable Immediately? | Missing Fields / Gaps | Backend Mod Required? | New Route Required? |
|---|---|---|---|---|---|---|
| 1 | Profile Summary Strip | `/api/v1/dashboard/jobseeker/{user_id}` | No (Mocked) | Needs real demographic details from DB | Yes | No |
| 2 | Missed Opportunity Banner | `/api/v1/lifecycle/missed-opportunities` | No (Mocked) | Needs dynamic expired scheme logic matching user profile | Yes | No |
| 3 | Eligibility Decoder | `/api/v1/eligibility/run` | No (Mocked) | Needs age relaxation explanations and state/category rules | Yes | No |
| 4 | Scam Shield | None | No | Not present in FastAPI specification (exists on Flask) | Yes | Yes |
| 5 | Readiness Ring + Fix | `/api/v1/readiness` | No (Mocked) | Needs opportunity breakdown, missing skills, and PMKVY course fixes | Yes | No |
| 6 | Document Readiness Panel | `/api/v1/{module}/documents/summary` | No (Mocked) | Needs verification comparison with user's uploaded document list | Yes | No |
| 7 | Priority Ranking | `/api/v1/opportunity-health/{opportunity_id}` | No (Mocked) | Needs bulk priority ranking of all schemes | Yes | Yes |
| 8 | Trust / Source Chips | `/api/v1/trust/{opportunity_id}` | Yes (Partial) | Returns mock score; needs dynamic verification tags | Yes | No |
| 9 | Roadmap / Next Steps | `/api/v1/lifecycle/recovery-plan` | No (Mocked) | Needs personalized document/skill recovery action items | Yes | No |
| 10| Alert Center | `/api/v1/deadlines/upcoming` | No (Mocked) | Returns farmer deadlines; needs jobseeker specific alerts | Yes | No |
| 11| Voice Input Support | `/api/v1/voice/chat` | Yes | None | No | No |
