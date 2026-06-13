# Job Seeker Dashboard Features: Dependency Matrix

This document defines the dependency matrix for all 11 newly implemented features on the **Job Seeker Dashboard** in UDAAN. It maps each frontend feature component to its corresponding backend API requirements, logic dependencies, external services, and current implementation status.

---

## 📋 Dependency Matrix Table

| # | Feature Name | Frontend Component | Existing Backend Endpoint | New Backend Endpoint Required | Internal Rules Engine Dependency | GROQ LLM Dependency | SERPER Web Search Dependency | Current Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **1** | **Profile Summary Strip** | `JobSeekerSections` | `GET /api/v1/profile/{user_id}/jobseeker` | None | SQLite DB Profile Schema | ❌ No | ❌ No | **Ready** |
| **2** | **Missed Opportunity Banner** | `JobSeekerSections` | `GET /api/v1/lifecycle/missed-opportunities` | None | Regret Calculator (`missed_and_alerts.py`) | ❌ No | ❌ No | **Ready** |
| **3** | **Eligibility Decoder** | `JobSeekerSections` | `GET /api/v1/opportunities/{opportunity_id}` | None (Modify existing details schema to include OBC age relaxations) | Eligibility Engine (`eligibility.py`) & Explain logic (`explain.py`) | **Yes** (Multilingual explanation routing) | ❌ No | **Needs Backend Work** |
| **4** | **Scam Shield** | `JobSeekerSections` | None | `POST /api/v1/scam-shield/check` | Scam Check Rules (`scam_shield.py`) | ❌ No | ❌ No | **Needs Backend Work** |
| **5** | **Readiness Ring + Free Scheme Fix** | `JobSeekerSections` | `GET /api/v1/readiness` | `POST /api/v1/profile/skills/add` | Readiness Engine (`app/api/routers/readiness.py`) | ❌ No | ❌ No | **Needs Backend Work** |
| **6** | **Document Readiness Panel** | `JobSeekerSections` | `GET /api/v1/wallet/documents` | `POST /api/v1/wallet/documents/upload` | Document Wallet Engine (`app/api/routers/documents.py`) | ❌ No | ❌ No | **Needs Backend Work** |
| **7** | **Priority Ranking** | `JobSeekerSections` | `GET /api/v1/opportunities/eligible` | None | None (Handled via client sorting) | ❌ No | ❌ No | **Ready** |
| **8** | **Trust / Source Chips** | `JobSeekerSections` | `GET /api/v1/opportunities/eligible` | None (Modify eligible schema to include source/trust scores) | None | ❌ No | ❌ No | **Needs Backend Work** |
| **9** | **Roadmap / Next Steps Card** | `JobSeekerSections` | `GET /api/v1/lifecycle/recovery-plan` | None (Modify response to match UI milestones) | Recovery Planning Engine (`app/api/routers/timeline.py`) | ❌ No | ❌ No | **Needs Backend Work** |
| **10** | **Alert Center Drawer** | `AlertCenterDrawer` | None | `GET /api/v1/notifications/active` | Notification System (`notification_db.py`) | ❌ No | ❌ No | **Needs Backend Work** |
| **11** | **Voice Input support in Chat** | `VoiceChatDialog` | `POST /api/v1/voice_agent/chat` | None | AI Coach Conversational Router (`voice_agent.py`) | **Yes** | **Yes** (For web discovery) | **Ready** (Needs wiring) |

---

## 🔍 Detailed Component & API Mapping

### 1. Profile Summary Strip
* **Frontend Component**: `JobSeekerSections` (lines 594-620)
* **Status**: **Ready**
* **Mapping**: Can consume the payload returned by `GET /api/v1/profile/{user_id}/jobseeker` directly.

### 2. Missed Opportunity Banner
* **Frontend Component**: `JobSeekerSections` (lines 622-639)
* **Status**: **Ready**
* **Mapping**: Displayed conditionally when `GET /api/v1/lifecycle/missed-opportunities` returns list items indicating missed deadlines (e.g. missing Caste Certificate for National Merit Scholarship).

### 3. Eligibility Decoder
* **Frontend Component**: `JobSeekerSections` (lines 880-914)
* **Status**: **Needs Backend Work**
* **Mapping**: Needs the `GET /api/v1/opportunities/{opportunity_id}` endpoint to return structural fields such as `category_age_relaxation` details, which are generated dynamically using LLMs (GROQ API) inside `backend/integrations/explain.py` for Telugu/Hindi translation reasoning.

### 4. Scam Shield
* **Frontend Component**: `JobSeekerSections` (lines 780-820)
* **Status**: **Needs Backend Work**
* **Mapping**: Requires exposing `backend/logic/scam_shield.py` via a new FastAPI REST router endpoint `POST /api/v1/scam-shield/check` so that description inputs can be validated against security heuristics on the server.

### 5. Readiness Ring + Free Scheme Fix
* **Frontend Component**: `JobSeekerSections` (lines 641-692)
* **Status**: **Needs Backend Work**
* **Mapping**: To enable the "Fix" action (enrolling in PMKVY Java Developer Course), the client needs to POST the skill addition to the backend, which will persist the new skill (`"Java Programming"`) in `udaan_v2.db` and trigger a recalculation of the readiness score.

### 6. Document Readiness Panel
* **Frontend Component**: `JobSeekerSections` (lines 694-734)
* **Status**: **Needs Backend Work**
* **Mapping**: A upload route (`POST /api/v1/wallet/documents/upload`) is required to update the document status (e.g., verifying Caste Certificate) in the backend wallet, which in turn triggers eligibility changes on RRB NTPC.

### 7. Priority Ranking
* **Frontend Component**: `JobSeekerSections` (lines 545-557, 736-778)
* **Status**: **Ready**
* **Mapping**: Standard sorting is calculated entirely client-side using benefit amounts, deadlines, and readiness values.

### 8. Trust / Source Chips
* **Frontend Component**: `JobSeekerSections` (within Opportunity Feed Cards)
* **Status**: **Needs Backend Work**
* **Mapping**: The backend schema for opportunities must be modified to return metadata fields `trust_score: int`, `is_govt: bool`, and `source: str`.

### 9. Roadmap / Next Steps Card
* **Frontend Component**: `JobSeekerSections` (lines 822-878)
* **Status**: **Needs Backend Work**
* **Mapping**: Requires modifying `/api/v1/lifecycle/recovery-plan` to return structured recovery checklist milestones.

### 10. Alert Center Drawer
* **Frontend Component**: `AlertCenterDrawer` (lines 923-968)
* **Status**: **Needs Backend Work**
* **Mapping**: Requires exposing a REST endpoint `GET /api/v1/notifications/active` to return current real-time alerts.

### 11. Voice Input in Chat
* **Frontend Component**: `VoiceChatDialog` (lines 973-1110)
* **Status**: **Ready** (needs wiring)
* **Mapping**: Needs to route text query outputs to `POST /api/v1/voice_agent/chat` and play back the resulting `response_text` via browser speech synthesis. This endpoint depends directly on the GROQ API key for routing queries.
