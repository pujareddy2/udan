# Job Seeker Dashboard — API Integration Map

**Document Version**: 1.0  
**Phase**: Phase 7 — Frontend–Backend Integration Planning  
**Frontend File**: `scripts_decoded/b7e1da8a-a516-4d12-aab4-e9383c107ecf.js`  
**Frontend Component**: `JobSeekerSections` (lines 442–955)  
**Supporting Components**: `AlertCenterDrawer` (lines 960–1005), `VoiceChatDialog` (lines 1010–1147)  
**Status**: All components use hardcoded data. No live API calls exist for Job Seeker features.

---

## Summary Table

| # | Component | Endpoint | Method | Loading State | Error Handling | Keep Fallback |
|---|-----------|----------|:------:|:-------------:|:--------------:|:-------------:|
| 1 | Profile Summary Strip | `/api/v1/dashboard/jobseeker/{user_id}` | GET | ✅ Yes | ✅ Yes | ✅ Yes |
| 2 | Missed Opportunity Banner | `/api/v1/lifecycle/missed-opportunities` | GET | ✅ Yes | ✅ Yes | ✅ Yes |
| 3 | Eligibility Decoder | `/api/v1/eligibility/run` | POST | ✅ Yes | ✅ Yes | ✅ Yes |
| 4 | Scam Shield | `/api/v1/scam/check` (NEW) | POST | ✅ Yes | ✅ Yes | ✅ Yes |
| 5 | Readiness Ring + Free Scheme Fix | `/api/v1/readiness` | GET | ✅ Yes | ✅ Yes | ✅ Yes |
| 6 | Document Readiness Panel | `/api/v1/jobseeker/documents/summary` | GET | ✅ Yes | ✅ Yes | ✅ Yes |
| 7 | Priority Ranking + Sorting | `/api/v1/jobseeker/opportunities/ranked` (NEW) | GET | ✅ Yes | ✅ Yes | ✅ Yes |
| 8 | Trust / Source Chips | Embedded in Opportunity Ranked response | GET | ❌ No (same call as #7) | ❌ No (same call as #7) | ✅ Yes |
| 9 | Roadmap / Next Steps Card | `/api/v1/lifecycle/recovery-plan` | GET | ✅ Yes | ✅ Yes | ✅ Yes |
| 10 | Alert Center Drawer | `/api/v1/notifications` + `/api/v1/deadlines/upcoming` | GET | ✅ Yes | ✅ Yes | ✅ Yes |
| 11 | Voice Input Support | `/api/v1/voice/chat` | POST | ✅ Yes | ✅ Yes | ❌ No |

---

## Component Integration Details

---

### 1. Profile Summary Strip

**Component Name**: Profile Summary Strip  
**Frontend File / Section**: `JobSeekerSections` — Section rendered at lines 594–620 inside `return ()`  
**Frontend State Variable**: `profile` (useState object, lines 443–454)

**Current Hardcoded State**:
```js
const [profile, setProfile] = useState({
  name: "Aanya Kumar",
  qualification: "B.Tech in Computer Science",
  experience: "1 Year",
  role: "Junior Software Engineer",
  state: "Telangana",
  district: "Hyderabad",
  category: "OBC",
  age: 23,
  skills: ["Python", "SQL", "HTML", "CSS"],
  hasCasteCert: false
});
const profileCompletion = 85; // hardcoded
```

**Existing Backend Endpoint**: `/api/v1/dashboard/jobseeker/{user_id}` *(requires modification)*  
**New Backend Endpoint Required**: No  
**HTTP Method**: `GET`  
**Auth**: `Authorization: Bearer <token>` required

**Fields Required by Frontend**:

| Frontend Field | Source in API Response | Notes |
|----------------|----------------------|-------|
| `profile.name` | `profile.full_name` | Rename on map |
| `profile.qualification` | `profile.qualification` | Maps from `education_level` |
| `profile.experience` | `profile.years_of_experience` | Needs string format (`"1 Year"`) |
| `profile.role` | `profile.preferred_job_role` | Direct map |
| `profile.state` | `profile.state` | Direct map |
| `profile.district` | `profile.district` | Direct map |
| `profile.category` | `profile.category` | Direct map |
| `profile.age` | `profile.age` | Direct map |
| `profile.skills` | `profile.skills` | Array — direct map |
| `profileCompletion` | `stats.completion_percentage` | Integer 0–100 |

**Loading State Required**: Yes  
- Show a skeleton strip with blurred name and "Loading profile..." text while fetching.

**Error Handling Required**: Yes  
- If API fails: keep existing hardcoded values as fallback state. Show no error UI (silent degradation).
- Log error to `console.error`.

**Fallback Hardcoded State Should Remain**: ✅ Yes  
- The current `useState` default values serve as the fallback until the API response is received.

**Integration Point in Code**:
```js
// ADD inside JobSeekerSections, after useState declarations (approx line 461):
useEffect(() => {
  const userId = localStorage.getItem("user_id");
  const token  = localStorage.getItem("token");
  if (!userId || !token) return;
  fetch(`http://localhost:8000/api/v1/dashboard/jobseeker/${userId}`, {
    headers: { "Authorization": `Bearer ${token}` }
  })
  .then(r => r.ok ? r.json() : null)
  .then(data => {
    if (!data) return;
    const p = data.profile || {};
    setProfile({
      name:          p.full_name        || profile.name,
      qualification: p.qualification    || profile.qualification,
      experience:    `${p.years_of_experience || 1} Year(s)`,
      role:          p.preferred_job_role || profile.role,
      state:         p.state            || profile.state,
      district:      p.district         || profile.district,
      category:      p.category         || profile.category,
      age:           p.age              || profile.age,
      skills:        p.skills           || profile.skills,
      hasCasteCert:  false              // from documents API (feature #6)
    });
    setProfileCompletion(data.stats?.completion_percentage ?? 85);
  })
  .catch(console.error);
}, []);
```

---

### 2. Missed Opportunity Banner

**Component Name**: Missed Opportunity Banner  
**Frontend File / Section**: `JobSeekerSections` — Conditional section rendered at lines 622–638  
**Frontend State Variable**: `uploadedCasteCert` (boolean) — banner shown when `!currentHasCasteCert`

**Current Hardcoded State**:
```jsx
{/* Banner always appears if hasCasteCert is false */}
<strong>National Merit Scholarship 2025 (₹12,000 value)</strong>
{/* Deadline: 31 Jan 2026, cause: Caste Certificate */}
```

**Existing Backend Endpoint**: `/api/v1/lifecycle/missed-opportunities` *(requires modification)*  
**New Backend Endpoint Required**: No  
**HTTP Method**: `GET`  
**Auth**: `Authorization: Bearer <token>` required

**Fields Required by Frontend**:

| Frontend Field | Source in API Response | Notes |
|----------------|----------------------|-------|
| Opportunity title | `[0].title` | First missed item shown in banner |
| Missed value (₹) | `[0].missed_value` | Formatted as `₹{value}` |
| Root cause | `[0].root_cause` | Used as explanation text in banner |
| Missed date | `[0].missed_at` | Human-readable format |
| Recovery action | `[0].recovery_action` | Text for fix button label |
| Future value at risk | `[0].future_value_at_risk` | Optional display field |

**Loading State Required**: Yes  
- During load: hide the banner entirely (display none). Render only after API responds.

**Error Handling Required**: Yes  
- If API fails or returns empty array: hide the banner entirely. Do not show a hardcoded past-missed record for a real user.

**Fallback Hardcoded State Should Remain**: ✅ Yes  
- The hardcoded banner (National Merit Scholarship) is the visual fallback while the backend is unimplemented.  
- **Replace hardcoded content** with a new `missedOpp` state variable once backend is ready.

**Integration Point in Code**:
```js
// ADD new state variable (approx line 461):
const [missedOpp, setMissedOpp] = useState(null); // null = no missed opp to show

// ADD new useEffect for missed opportunities fetch:
useEffect(() => {
  const token = localStorage.getItem("token");
  if (!token) return;
  fetch("http://localhost:8000/api/v1/lifecycle/missed-opportunities", {
    headers: { "Authorization": `Bearer ${token}` }
  })
  .then(r => r.ok ? r.json() : [])
  .then(data => { if (data.length > 0) setMissedOpp(data[0]); })
  .catch(console.error);
}, []);

// IN JSX — replace hardcoded banner text with missedOpp fields:
// {missedOpp && <section>...{missedOpp.title}...₹{missedOpp.missed_value}...</section>}
```

---

### 3. Eligibility Decoder

**Component Name**: Eligibility Decoder Modal  
**Frontend File / Section**: `JobSeekerSections` — Fixed-position modal at lines 888–951  
**Frontend State Variable**: `decoderOpp` (useState, line 458) — set by clicking "Check Eligibility" on any card

**Current Hardcoded State**:  
Each opportunity in the `opportunities` array contains:
```js
{
  categoryAgeRelaxation: "3 years relaxation for OBC applied...",
  requiredDocs: ["Aadhaar", "Graduation Certificate"],
  missingDocs: [],
  missingSkills: [],
  reasoning: "You meet the graduation requirement..."
}
```

**Existing Backend Endpoint**: `/api/v1/eligibility/run` *(requires modification)*  
**New Backend Endpoint Required**: No  
**HTTP Method**: `POST`  
**Auth**: `Authorization: Bearer <token>` required

**Fields Required by Frontend**:

| Frontend Field | Source in API Response | Notes |
|----------------|----------------------|-------|
| Age & Category row | `criteria[0].reasoning_en` | Where `criterion == 'Age Limit'` |
| Age relaxation text | `criteria[1].reasoning_en` | Where `criterion == 'Age Relaxation Applied'` |
| Education row | `criteria[2].reasoning_en` | Where `criterion == 'Education Level'` |
| Skills row | `criteria[5]` `passed`, `missing_skills` | Show missing skills list |
| Documents row | `criteria[6]` `passed`, `missing_docs` | Show missing docs list |
| AI Summary | `ai_summary` | Shown in the "AI Match Summary Reason" box |
| `missingDocs` | `missing_docs` | For card badge count |
| `missingSkills` | `missing_skills` | For card badge count |
| `readiness` (match %) | `match_score` | Shown as "Eligibility Match: X%" |

**Loading State Required**: Yes  
- When "Check Eligibility" is clicked: show a spinner/loading state inside the modal (open modal immediately with loading content, then replace with results).

**Error Handling Required**: Yes  
- If API fails: fall back to the static data already stored on the opportunity object (`opp.reasoning`, `opp.missingDocs`, etc.) — these remain valid hardcoded fallbacks.

**Fallback Hardcoded State Should Remain**: ✅ Yes  
- Each opportunity object's `categoryAgeRelaxation`, `missingDocs`, `missingSkills`, `reasoning` fields remain as the pre-computed fallback.  
- The modal renders these when live API is unavailable.

**Integration Point in Code**:
```js
// REPLACE handleScamCheck pattern — add a separate handler for decoder:
const [decoderLoading, setDecoderLoading] = useState(false);

const openDecoderModal = async (opp) => {
  setDecoderOpp(opp);              // open modal with existing data immediately
  setDecoderLoading(true);
  try {
    const token = localStorage.getItem("token");
    const userId = localStorage.getItem("user_id");
    const res = await fetch("http://localhost:8000/api/v1/eligibility/run", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
      body: JSON.stringify({ user_id: parseInt(userId), opportunity_id: opp.dbId })
    });
    if (res.ok) {
      const data = await res.json();
      setDecoderOpp(prev => ({
        ...prev,
        missingDocs:           data.missing_docs   || prev.missingDocs,
        missingSkills:         data.missing_skills || prev.missingSkills,
        categoryAgeRelaxation: data.criteria?.find(c => c.criterion === "Age Relaxation Applied")?.reasoning_en || prev.categoryAgeRelaxation,
        reasoning:             data.ai_summary     || prev.reasoning,
        readiness:             data.match_score    ?? prev.readiness
      }));
    }
  } catch (e) { console.error(e); }
  finally { setDecoderLoading(false); }
};
// CHANGE: onClick={() => setDecoderOpp(opp)}  →  onClick={() => openDecoderModal(opp)}
```

---

### 4. Scam Shield

**Component Name**: Scam Shield Guard  
**Frontend File / Section**: `JobSeekerSections` — Section at lines 756–785  
**Frontend State Variables**: `scamText` (input), `scamResult` (output), both useState (lines 459–460)  
**Current Logic**: Entirely client-side keyword pattern matching in `handleScamCheck()` (lines 559–589)

**Existing Backend Endpoint**: None in FastAPI *(Flask only: `/api/scam/check` on port 5000)*  
**New Backend Endpoint Required**: ✅ Yes — `/api/v1/scam/check` (NEW)  
**HTTP Method**: `POST`  
**Auth**: Not required (public endpoint — no user data sent)

**Fields Required by Frontend**:

| Frontend Field | Source in API Response | Notes |
|----------------|----------------------|-------|
| `scamResult.safe` | `is_safe` (boolean) | Controls icon + colour scheme |
| `scamResult.level` | Derived: `is_safe ? "Safe Profile ✓" : "High Risk Alert 🚨"` | Or use `risk_level` field |
| `scamResult.reasons` | `flags[].description` (array of strings) | Rendered as `<ul><li>` list |
| Risk level label | `risk_level` (SAFE / LOW / MEDIUM / HIGH / CRITICAL) | Used to colour-code the result |
| Safe indicators | `safe_indicators` | Optional "positive signals" display |

**Loading State Required**: Yes  
- Between clicking "Scan for Scams" and receiving the response: show a spinner animation or pulse on the shield icon.

**Error Handling Required**: Yes  
- If API call fails: fall back to the existing client-side `handleScamCheck()` logic immediately. The user sees results from the local engine without knowing the API failed.

**Fallback Hardcoded State Should Remain**: ✅ Yes  
- The current `handleScamCheck()` function (lines 559–589) is a complete, working local fallback.  
- **Do not remove it.** Use it as the fallback when the new endpoint is unavailable.

**Integration Point in Code**:
```js
// REPLACE handleScamCheck with an async version that calls the API:
const handleScamCheck = async () => {
  if (!scamText.trim()) return;
  setScamLoading(true);  // new state variable
  try {
    const res = await fetch("http://localhost:8000/api/v1/scam/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: scamText })
    });
    if (res.ok) {
      const data = await res.json();
      setScamResult({
        safe:    data.is_safe,
        level:   data.is_safe ? "Safe Profile ✓" : `${data.risk_level} Risk Alert 🚨`,
        reasons: data.flags.map(f => f.description)
      });
      return;
    }
  } catch (e) { console.error(e); }
  // FALLBACK: run local keyword engine if API unavailable
  runLocalScamCheck(scamText);  // extract current logic into named function
  setScamLoading(false);
};
```

---

### 5. Readiness Ring + Free Scheme Fix

**Component Name**: Application Readiness Ring + AI Free Scheme Fix Upgrade  
**Frontend File / Section**: `JobSeekerSections` — Left column of 3-column grid, lines 643–683  
**Frontend State Variables**:  
- `profileCompletion = 85` (hardcoded, line 466)  
- `documentScore` (derived from `currentHasCasteCert`, line 467)  
- `skillsScore` (derived from `registeredCourse`, line 468)  
- `overallReadiness` (computed average, line 469)  
- `registeredCourse` (boolean, line 456)

**Existing Backend Endpoint**: `/api/v1/readiness` *(requires modification)*  
**New Backend Endpoint Required**: No  
**HTTP Method**: `GET`  
**Auth**: Query param `user_id` or JWT  

**Fields Required by Frontend**:

| Frontend Field | Source in API Response | Notes |
|----------------|----------------------|-------|
| `profileCompletion` | `breakdown.profile_score` | Integer 0–100 |
| `documentScore` | `breakdown.document_score` | Integer 0–100 |
| `skillsScore` | `breakdown.skills_score` | Integer 0–100 |
| `overallReadiness` | `overall_readiness` | Integer 0–100 |
| Free fix scheme title | `free_scheme_fixes[0].fix_scheme_title` | For the "Free Scheme Fix" card |
| Missing skill name | `free_scheme_fixes[0].missing_skill` | Displayed in description |
| Fix benefit value | `free_scheme_fixes[0].benefit_if_fixed` | Shown as unlock value |
| Enroll URL | `free_scheme_fixes[0].enroll_url` | For "Enroll Free Upgrade" button |

**Loading State Required**: Yes  
- While fetching: show the SVG ring with a neutral grey fill and a `--` placeholder inside instead of the percentage.

**Error Handling Required**: Yes  
- If API fails: retain computed values from `profileCompletion`, `documentScore`, `skillsScore` defaults (85, 70, 80).

**Fallback Hardcoded State Should Remain**: ✅ Yes  
- `profileCompletion = 85`, `documentScore = 70`, `skillsScore = 80` remain as defaults.  
- The PMKVY Free Scheme Fix card's hardcoded "Java Programming" messaging is the fallback.

**Integration Point in Code**:
```js
// ADD new state variables (approx line 461):
const [readinessData, setReadinessData] = useState(null);

// ADD useEffect:
useEffect(() => {
  const userId = localStorage.getItem("user_id");
  if (!userId) return;
  fetch(`http://localhost:8000/api/v1/readiness?user_id=${userId}`)
  .then(r => r.ok ? r.json() : null)
  .then(data => { if (data) setReadinessData(data); })
  .catch(console.error);
}, []);

// REPLACE hardcoded scores in JSX:
// profileCompletion  → readinessData?.breakdown?.profile_score  ?? 85
// documentScore      → readinessData?.breakdown?.document_score ?? (currentHasCasteCert ? 100 : 70)
// skillsScore        → readinessData?.breakdown?.skills_score   ?? (registeredCourse ? 100 : 80)
// overallReadiness   → readinessData?.overall_readiness         ?? Math.round(...)
// Free fix card      → readinessData?.free_scheme_fixes?.[0]
```

---

### 6. Document Readiness Panel

**Component Name**: Document Verification Wallet  
**Frontend File / Section**: `JobSeekerSections` — Middle column of 3-column grid, lines 685–718  
**Frontend State Variable**: `uploadedCasteCert` (boolean, line 457) — controls Caste Certificate status

**Current Hardcoded State**:
```jsx
{/* Always-verified documents */}
"Aadhaar Identity Card"    → ✓ Verified (hardcoded)
"Graduation Certificate"   → ✓ Verified (hardcoded)
"Caste Certificate (OBC)"  → status from uploadedCasteCert state
"Income Certificate"       → Optional (hardcoded)
```

**Existing Backend Endpoint**: `/api/v1/jobseeker/documents/summary` *(requires modification)*  
**New Backend Endpoint Required**: No  
**HTTP Method**: `GET`  
**Auth**: `Authorization: Bearer <token>` required

**Fields Required by Frontend**:

| Frontend Field | Source in API Response | Notes |
|----------------|----------------------|-------|
| Document name | `documents[].document_name` | Display label |
| Document status | `documents[].status` | `Verified` / `Missing` / `Expiring` / `Optional` |
| Verified indicator (✓ / ⚠) | Derived from `status` | Green for Verified, Amber for Missing |
| Upload button visibility | `status === "Missing"` | Show "Upload" button only for missing |
| `hasCasteCert` | `documents` array `status === "Verified"` where name = "Caste Certificate" | Must also update `profile.hasCasteCert` |
| Official apply link | `documents[].official_apply_link` | For "How to Get" link on missing docs |

**Loading State Required**: Yes  
- While fetching: show 4 skeleton rows with a shimmer animation.

**Error Handling Required**: Yes  
- If API fails: retain the current hardcoded list as fallback. The Caste Certificate "Missing" state should remain the default.

**Fallback Hardcoded State Should Remain**: ✅ Yes  
- The 4-item hardcoded list remains as the fallback render state.

**Integration Point in Code**:
```js
// ADD new state (approx line 461):
const [documents, setDocuments] = useState(null); // null = use hardcoded fallback

// ADD useEffect:
useEffect(() => {
  const userId = localStorage.getItem("user_id");
  const token  = localStorage.getItem("token");
  if (!userId || !token) return;
  fetch(`http://localhost:8000/api/v1/jobseeker/documents/summary?user_id=${userId}`, {
    headers: { "Authorization": `Bearer ${token}` }
  })
  .then(r => r.ok ? r.json() : null)
  .then(data => {
    if (!data) return;
    setDocuments(data.documents);
    // sync hasCasteCert state:
    const casteCert = data.documents.find(d => d.document_name.toLowerCase().includes("caste"));
    if (casteCert?.status === "Verified") setUploadedCasteCert(true);
  })
  .catch(console.error);
}, []);

// IN JSX: render (documents ?? hardcodedDocList).map(doc => ...)
```

---

### 7. Priority Ranking + Sorting

**Component Name**: Matched Opportunities & Priority Ranking Feed  
**Frontend File / Section**: `JobSeekerSections` — Section at lines 787–886 (includes sort select + card grid)  
**Frontend State Variables**:  
- `opportunities` — hardcoded array (lines 471–543)  
- `sortBy` — `useState("priority")` (line 461)  
- `sortedOpps` — derived sorted array (lines 552–557)  
- `getPriorityScore()` — local composite formula (lines 545–550)

**Existing Backend Endpoint**: None (only `/api/v1/opportunity-health/{id}` which is single + mocked)  
**New Backend Endpoint Required**: ✅ Yes — `/api/v1/jobseeker/opportunities/ranked` (NEW)  
**HTTP Method**: `GET`  
**Auth**: `Authorization: Bearer <token>` required  
**Query Parameters**: `user_id`, `sort_by` (priority | deadline | benefit | readiness)

**Fields Required by Frontend**:

| Frontend Field | Source in API Response | Notes |
|----------------|----------------------|-------|
| `opp.id` | `opportunities[].id` | Used as React key |
| `opp.name` | `opportunities[].title` | Rename on map |
| `opp.amount` | `opportunities[].amount_display` | Pre-formatted string |
| `opp.deadline` | `opportunities[].deadline_date` | Format as "DD Mon YYYY" |
| `opp.deadlineDays` | `opportunities[].days_remaining` | Integer |
| `opp.tag` | `opportunities[].tag` | Category chip |
| `opp.benefitVal` | `opportunities[].benefit_value` | Numeric for sorting |
| `opp.readiness` | `opportunities[].readiness_pct` | Integer 0–100 |
| `opp.missingDocs` | `opportunities[].missing_docs` | Array of strings |
| `opp.missingSkills` | `opportunities[].missing_skills` | Array of strings |
| `opp.upgradeAvailable` | `opportunities[].upgrade_available` | Boolean |
| `opp.categoryAgeRelaxation` | `opportunities[].category_age_relaxation` | String or null |
| `opp.reasoning` | `opportunities[].reasoning` | For eligibility decoder |
| `opp.dbId` | `opportunities[].id` | Needed for eligibility decoder API call |
| Trust chip data | `opportunities[].trust` | Sub-object (see feature #8) |

**Loading State Required**: Yes  
- Show 3 skeleton cards with shimmer animation while fetching.  
- The sort select should be disabled during loading.

**Error Handling Required**: Yes  
- If API fails: render the hardcoded `opportunities` array. Sort operations still work client-side.

**Fallback Hardcoded State Should Remain**: ✅ Yes  
- The 4-item hardcoded opportunity array (SSC CGL, NATS, PMKVY, RRB NTPC) remains the fallback.  
- Client-side `getPriorityScore()` and `sortedOpps` logic remain as the fallback sort mechanism.

**Integration Point in Code**:
```js
// ADD new state (approx line 461):
const [liveOpps, setLiveOpps] = useState(null); // null = use hardcoded fallback
const [oppsLoading, setOppsLoading] = useState(false);

// ADD useEffect — re-fetch when sortBy changes:
useEffect(() => {
  const userId = localStorage.getItem("user_id");
  const token  = localStorage.getItem("token");
  if (!userId || !token) return;
  setOppsLoading(true);
  fetch(`http://localhost:8000/api/v1/jobseeker/opportunities/ranked?user_id=${userId}&sort_by=${sortBy}`, {
    headers: { "Authorization": `Bearer ${token}` }
  })
  .then(r => r.ok ? r.json() : null)
  .then(data => {
    if (data?.opportunities) setLiveOpps(data.opportunities);
  })
  .catch(console.error)
  .finally(() => setOppsLoading(false));
}, [sortBy]);

// REPLACE sortedOpps reference in JSX:
// const displayOpps = liveOpps
//   ? (sortBy === "priority" ? liveOpps : localSort(liveOpps, sortBy))
//   : sortedOpps;  // keep current sort logic as fallback
```

---

### 8. Trust / Source Chips

**Component Name**: Trust / Source Chips (embedded within Opportunity Cards)  
**Frontend File / Section**: `JobSeekerSections` — Inside opportunity card map, lines 827–864  
**Frontend Data Source**: Properties on each opportunity object: `opp.source`, `opp.trustScore`, `opp.isGovt`

**Current Hardcoded State**:
```js
source: "ssc.nic.in"        // hardcoded per opportunity
trustScore: 100              // hardcoded integer
isGovt: true                 // hardcoded boolean
```

**Existing Backend Endpoint**: Embedded within `/api/v1/jobseeker/opportunities/ranked` (Feature #7)  
**New Backend Endpoint Required**: No (data arrives as part of ranked opportunities response)  
**HTTP Method**: GET (same call as Feature #7)  
**Auth**: Same as Feature #7

**Fields Required by Frontend**:

| Frontend Field | Source in API Response | Notes |
|----------------|----------------------|-------|
| `opp.source` | `opportunities[].trust.source_domain` | Rename on map |
| `opp.trustScore` | `opportunities[].trust.trust_score` | Integer 0–100 |
| `opp.isGovt` | `opportunities[].trust.is_govt` | Boolean |
| Provider type label | `opportunities[].trust.provider_type` | Used for display text |
| Govt department | `opportunities[].trust.govt_department` | Optional tooltip |

**Trust Chip Colour Logic (already implemented in frontend)**:
```js
// Colour logic at lines 844–850 — no frontend change needed:
trustScore >= 90 → green  (#7fe0a0)
trustScore >= 70 → amber  (#ffd27a)
trustScore <  70 → red    (#ff6b6b)
```

**Loading State Required**: ❌ No — chips load as part of the opportunity card (Feature #7 handles loading state)

**Error Handling Required**: ❌ No — if `trust` object is absent from API response, the hardcoded `trustScore`/`source`/`isGovt` fields on each opportunity already serve as the fallback

**Fallback Hardcoded State Should Remain**: ✅ Yes  
- `source`, `trustScore`, `isGovt` on each hardcoded opportunity object remain valid fallbacks when the ranked API is unavailable.

**Integration Point in Code**:
```js
// In the API response mapping for Feature #7, add trust field extraction:
const mappedOpp = {
  ...apiOpp,
  source:     apiOpp.trust?.source_domain ?? "official source",
  trustScore: apiOpp.trust?.trust_score   ?? 80,
  isGovt:     apiOpp.trust?.is_govt       ?? false,
};
// No other frontend changes needed — chips already render from these fields
```

---

### 9. Roadmap / Next Steps Card

**Component Name**: Personalized Seeker Roadmap  
**Frontend File / Section**: `JobSeekerSections` — Right column of 3-column grid, lines 720–753  
**Frontend State Variables**: `currentHasCasteCert`, `registeredCourse` — used as checkbox states

**Current Hardcoded State**:
```jsx
Step 1: "Complete profile registration (100%)" — always ✓ done
Step 2: "Obtain Caste Certificate"              — checked = currentHasCasteCert
Step 3: "Complete Java Skill Fix Course"        — checked = registeredCourse
Step 4: "Apply for SSC CGL 2026"               — always unchecked
```

**Existing Backend Endpoint**: `/api/v1/lifecycle/recovery-plan` *(requires modification)*  
**New Backend Endpoint Required**: No  
**HTTP Method**: `GET`  
**Auth**: `Authorization: Bearer <token>` required

**Fields Required by Frontend**:

| Frontend Field | Source in API Response | Notes |
|----------------|----------------------|-------|
| Step title | `roadmap_steps[].title` | Bold label |
| Step description | `roadmap_steps[].description` | Sub-label (smaller text) |
| Step status | `roadmap_steps[].status` | `completed` / `pending` / `blocked` |
| Step checkbox checked | `status === "completed"` | Maps to `checked` prop |
| Action detail | `roadmap_steps[].action_detail` | Shows where/how to complete step |
| Deadline | `roadmap_steps[].deadline` | Appended as "closes DD Mon YYYY" |
| Unlocks value | `roadmap_steps[].unlocks_value` | Shows "Unlocks ₹X" motivator |

**Loading State Required**: Yes  
- While fetching: show 3 skeleton rows in the Roadmap card.

**Error Handling Required**: Yes  
- If API fails: retain the 4 hardcoded steps. Their checked states remain driven by `currentHasCasteCert` and `registeredCourse` booleans.

**Fallback Hardcoded State Should Remain**: ✅ Yes  
- The 4-item hardcoded roadmap remains as the visual fallback.

**Integration Point in Code**:
```js
// ADD new state (approx line 461):
const [roadmapSteps, setRoadmapSteps] = useState(null); // null = use hardcoded fallback

// ADD useEffect:
useEffect(() => {
  const token = localStorage.getItem("token");
  if (!token) return;
  fetch("http://localhost:8000/api/v1/lifecycle/recovery-plan", {
    headers: { "Authorization": `Bearer ${token}` }
  })
  .then(r => r.ok ? r.json() : null)
  .then(data => { if (data?.roadmap_steps) setRoadmapSteps(data.roadmap_steps); })
  .catch(console.error);
}, []);

// IN JSX: render (roadmapSteps ?? hardcodedSteps).map(step => ...)
// Map: status === "completed" → checked={true}; pending/blocked → checked={false}
```

---

### 10. Alert Center Drawer

**Component Name**: Alert Center Drawer  
**Frontend File / Section**: `AlertCenterDrawer` component — lines 960–1005  
**Frontend State Variable**: `alertsOpen` in parent `Dashboard` (line 35); drawer receives `onClose` prop  
**Trigger**: Bell icon in `UdaanNav` calls `onAlertOpen()` which sets `alertsOpen = true`

**Current Hardcoded State**:
```jsx
// 3 hardcoded alerts in AlertCenterDrawer:
Alert 1: URGENT DEADLINE — RRB NTPC (22 days, Caste Certificate)
Alert 2: FREE SKILL FIX — PMKVY Java (deadline 15 July)
Alert 3: DOCUMENT REMINDER — Aadhaar mobile link
```

**Existing Backend Endpoints** *(both require modification)*:
1. `/api/v1/notifications` — for general alerts and notifications  
2. `/api/v1/deadlines/upcoming` — for deadline-based alerts

**New Backend Endpoint Required**: No  
**HTTP Method**: `GET` (both endpoints)  
**Auth**: `Authorization: Bearer <token>` required

**Fields Required by Frontend**:

| Frontend Field | Source in API Response | Notes |
|----------------|----------------------|-------|
| Priority tier colour | `alerts[].priority_tier` | CRITICAL=red, HIGH=amber, MEDIUM=blue |
| Priority label text | `alerts[].priority_tier` | "URGENT DEADLINE", "FREE SKILL FIX", etc. |
| Alert title/message | `alerts[].message` | Main body text |
| Action button label | `alerts[].action_label` | Optional CTA button |
| Unread badge count | `unread_count` | Bell icon dot indicator in nav |
| Deadline alert message | `deadlines[].opportunity_title` + `deadlines[].days_remaining` | For deadline-type alerts |

**Loading State Required**: Yes  
- When drawer opens: show 3 skeleton alert cards while fetching.

**Error Handling Required**: Yes  
- If both APIs fail: show the 3 hardcoded fallback alerts. Never show an empty Alert Center.

**Fallback Hardcoded State Should Remain**: ✅ Yes  
- The 3 hardcoded alerts remain as fallback content when APIs are unavailable.

**Integration Point in Code**:
```js
// MODIFY AlertCenterDrawer to accept and display live alerts:
// ADD new state inside AlertCenterDrawer:
const [liveAlerts, setLiveAlerts] = useState(null); // null = show hardcoded fallback
const [alertsLoading, setAlertsLoading] = useState(true);

useEffect(() => {
  const token = localStorage.getItem("token");
  if (!token) { setAlertsLoading(false); return; }
  Promise.all([
    fetch("http://localhost:8000/api/v1/notifications",      { headers: { Authorization: `Bearer ${token}` } }).then(r => r.ok ? r.json() : null),
    fetch("http://localhost:8000/api/v1/deadlines/upcoming", { headers: { Authorization: `Bearer ${token}` } }).then(r => r.ok ? r.json() : null),
  ])
  .then(([notifs, deadlines]) => {
    const combined = [
      ...(notifs?.alerts     || []),
      ...(deadlines?.deadlines?.map(d => ({
        priority_tier: d.urgency,
        message: `${d.opportunity_title} deadline in ${d.days_remaining} days`,
        action_label: "View Opportunity"
      })) || [])
    ].sort((a, b) => ["CRITICAL","HIGH","MEDIUM","LOW"].indexOf(a.priority_tier) - ["CRITICAL","HIGH","MEDIUM","LOW"].indexOf(b.priority_tier));
    if (combined.length > 0) setLiveAlerts(combined);
  })
  .catch(console.error)
  .finally(() => setAlertsLoading(false));
}, []);
```

---

### 11. Voice Input Support

**Component Name**: UDAAN AI Seeker Coach (Voice Chat Dialog)  
**Frontend File / Section**: `VoiceChatDialog` component — lines 1010–1147  
**Frontend State Variables**: `lang`, `inputText`, `messages`, `isListening`, `statusText`  
**Trigger**: FAB chat button (floating, bottom-right) → `setChatOpen(true)` in `Dashboard`

**Current Hardcoded State**:
```js
// Voice recognition: uses browser Web Speech API (already live — no hardcoded data)
// AI responses: rule-based keyword matching (lines 1044–1062)
// e.g. "ssc" in query → hardcoded SSC CGL eligibility reply
```

**Existing Backend Endpoint**: `/api/v1/voice/chat` *(reusable — no modification needed)*  
**New Backend Endpoint Required**: No  
**HTTP Method**: `POST`  
**Auth**: Not required (public inference endpoint)

**Fields Required by Frontend**:

| Frontend Field | Source in API Response | Notes |
|----------------|----------------------|-------|
| AI reply text | `response_text` | Appended to `messages` array |
| Audio payload | `audio_payload` (optional base64) | Play via `<audio>` element if present |
| Actions | `actions[]` | Optional — navigate or highlight dashboard features |

**Loading State Required**: Yes  
- After sending a message: show typing indicator (e.g. animated "..." bubble) in the message list while waiting for the API response.  
- The current `setTimeout(800ms)` simulating delay is replaced by the actual API latency.

**Error Handling Required**: Yes  
- If API call fails: fall back to the local keyword-based response engine (current `handleSend` logic at lines 1044–1062).  
- Show no error to user — the fallback engine is seamless.

**Fallback Hardcoded State Should Remain**: ❌ No (partial)  
- The browser **Web Speech API** for voice input is already live and real — keep it.  
- The **hardcoded keyword response engine** (setTimeout fake AI) should be fully replaced by the backend call.  
- Unlike other features, there is no value in permanently keeping the keyword stub — the live API is better in all cases.  
- However, the keyword engine remains as a **network-error-only fallback**.

**Integration Point in Code**:
```js
// REPLACE the setTimeout AI response stub in handleSend():
const handleSend = async () => {
  const query = inputText.trim();
  if (!query) return;
  const userMsg = { role: "user", text: query };
  setMessages(prev => [...prev, userMsg]);
  setInputText("");
  setStatusText("AI is thinking...");

  try {
    const res = await fetch("http://localhost:8000/api/v1/voice/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, language: lang })
    });
    if (res.ok) {
      const data = await res.json();
      const reply = data.response_text;
      setMessages(prev => [...prev, { role: "assistant", text: reply }]);
      // optional TTS:
      const utterance = new SpeechSynthesisUtterance(reply);
      utterance.lang = lang.split("-")[0];
      synth.speak(utterance);
    } else throw new Error("API error");
  } catch (e) {
    // FALLBACK to local keyword engine:
    const fallbackReply = getLocalFallbackReply(query); // extract current setTimeout logic
    setMessages(prev => [...prev, { role: "assistant", text: fallbackReply }]);
  } finally {
    setStatusText("");
  }
};
```

---

## Integration Execution Order for Phase 8

The following order minimises blocking dependencies:

```
Phase 8A — Data foundations (no UI changes):
  1. Feature #1  — Profile Summary Strip   (dashboard summary API)
  2. Feature #11 — Voice Chat             (simplest, API already exists)

Phase 8B — Opportunity data (drives #7, #8, #3):
  3. Feature #7  — Priority Ranking       (new ranked endpoint — core data source)
  4. Feature #8  — Trust/Source Chips     (embedded in #7 response, zero extra work)
  5. Feature #3  — Eligibility Decoder    (uses opportunity.dbId from #7)

Phase 8C — Readiness & documents:
  6. Feature #5  — Readiness Ring         (readiness endpoint)
  7. Feature #6  — Document Panel         (documents/summary endpoint)

Phase 8D — Lifecycle & alerts:
  8. Feature #2  — Missed Opportunity     (missed-opportunities endpoint)
  9. Feature #9  — Roadmap Card           (recovery-plan endpoint)
  10. Feature #10 — Alert Center          (notifications + deadlines endpoints)

Phase 8E — Security:
  11. Feature #4 — Scam Shield            (new scam/check endpoint)
```

---

## Global Frontend Changes Required (All Features)

The following changes apply to `JobSeekerSections` globally and are needed before any individual feature integration:

1. **Add `userId` and `token` extraction** at the top of `JobSeekerSections`:
   ```js
   const userId = localStorage.getItem("user_id");
   const token  = localStorage.getItem("token");
   ```

2. **Add a global `apiLoading` state** to track whether any initial data fetch is in progress.

3. **Add a shared `apiFetch` helper** to centralise Bearer token attachment:
   ```js
   const apiFetch = (url, opts = {}) => fetch(url, {
     ...opts,
     headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json", ...(opts.headers || {}) }
   });
   ```

4. **Convert `profileCompletion` from a `const` to a `useState`** to allow the API to update it:
   ```js
   const [profileCompletion, setProfileCompletion] = useState(85);
   ```

5. **All fallback hardcoded data remains in place** as `useState` default values. API responses overwrite them via `setState` calls inside `useEffect` hooks.

---

## Files to be Modified in Phase 8

| File | Change Type | Scope |
|------|-------------|-------|
| [b7e1da8a-a516-4d12-aab4-e9383c107ecf.js](file:///c:/Users/CHINNI/OneDrive/Desktop/Udaan/udan/scripts_decoded/b7e1da8a-a516-4d12-aab4-e9383c107ecf.js) | Major edit | `JobSeekerSections` + `AlertCenterDrawer` + `VoiceChatDialog` |
| [UDAAN AI (standalone).html](file:///c:/Users/CHINNI/OneDrive/Desktop/Udaan/udan/UDAAN%20AI%20(standalone).html) | Repack | Re-encode updated JS into gzip+base64 bundle |

> [!IMPORTANT]
> The standalone HTML must be repacked after **every** JS edit using `update_bundle.py` already present in the project root.

> [!NOTE]
> No new component files need to be created. All integration is within the existing `JobSeekerSections`, `AlertCenterDrawer`, and `VoiceChatDialog` components.

> [!TIP]
> Trust/Source Chips (Feature #8) require **zero additional work** in Phase 8 — they are automatically populated once the Priority Ranking API (Feature #7) returns the `trust` sub-object.

> [!WARNING]
> The `/api/v1/opportunities/eligible` and `/api/v1/opportunities/recommended` endpoints listed in Swagger **do not exist** in the router. Use `/api/v1/jobseeker/opportunities/ranked` exclusively for the opportunity feed.
