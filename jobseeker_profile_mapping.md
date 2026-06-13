# Job Seeker Profile Field Mapping

**Document Version**: 1.0  
**Phase**: Pre-Phase 8 — Profile Integration Analysis  
**Files Analysed**:
- Registration Form: `template.html` (view-register section)
- Profile Schema: `scripts_decoded/4f088cda-a00e-40fa-90c8-2eb2398d268b.js`
- Profile Save/Load/Build: `scripts_decoded/c33aa38d-654c-4053-bad9-41e46538669f.js`
- Profile Component: `scripts_decoded/615a609b-2f33-4430-bf48-494bb7f47957.js`
- Dashboard Component: `scripts_decoded/b7e1da8a-a516-4d12-aab4-e9383c107ecf.js` (`JobSeekerSections`, lines 442–955)

---

## Section 1 — Fields Currently Collected by the Overlay

The profile data is collected across two stages:

### Stage A — Registration Form (`template.html`, `#view-register`)

These fields are collected at first registration and seeded into `localStorage["udaan_profile"]`:

| Field ID | Label | Type | Stored As |
|----------|-------|------|-----------|
| `fullname` | Full Name | `text` | `full_name` |
| `reg-email` | Email | `email` | `email` |
| `phone` | Phone Number | `tel` | `mobile_number` |
| `reg-password` | Password | `password` | (sent to backend only) |
| `dob` | Date of Birth | `date` | `date_of_birth` |
| `gender` | Gender | `select` (Female/Male/Other) | `gender` |
| `state` | State | `text` | `state` |
| `district` | District | `text` | `district` |
| `category` | User Category | `select` (students/farmers/jobseekers/…) | `role` → determines persona |

> **Note**: The registration form does NOT capture `age` directly — only `date_of_birth`. Age must be computed from DOB.

---

### Stage B — Profile Builder Overlay (`UDAAN_PROFILE_SCHEMA` — `4f088cda-...js`)

The Profile Builder shows **common sections** (all users) plus **jobseeker-specific sections**.

#### Common Sections (all personas)

**Basic Information** (`id: "identity"`):

| Key | Label | Type |
|-----|-------|------|
| `full_name` | Full Name | text |
| `mobile_number` | Mobile Number | tel |
| `email` | Email | email |
| `date_of_birth` | Date of Birth | date |
| `gender` | Gender | select (Female/Male/Other) |

**Location Information** (`id: "location"`):

| Key | Label | Type |
|-----|-------|------|
| `state` | State | text |
| `district` | District | text |
| `village_city` | Village/Town | text |
| `urban_or_rural` | Rural / Urban | select (Urban/Rural) |

**Social Information** (`id: "social"`):

| Key | Label | Type |
|-----|-------|------|
| `category` | Category | select (General/OBC/SC/ST/EWS) |
| `annual_family_income` | Annual Family Income | text |
| `family_size` | Family Size | number |
| `special_category` | Special Category | select (None/Minority/PwD/Widow/Single Woman/Veteran Family) |

**Documents Available** (`id: "documents_available"`, type: `multi`):

| Options (multi-select) |
|------------------------|
| Aadhaar |
| PAN |
| Income Certificate |
| Caste Certificate |
| Ration Card |
| Bank Account |
| Land Passbook |

**Digital Readiness** (`id: "digital"`, type: `bool`):

| Key | Label |
|-----|-------|
| `smartphone_available` | Smartphone |
| `internet_access` | Internet Access |
| `digital_payment_access` | Digital Payments |

#### Jobseeker-Specific Section

**Education** (`id: "js_education"`, persona: `jobseekers`):

| Key | Label | Type |
|-----|-------|------|
| `qualification` | Qualification | text |
| `experience_years` | Experience (years) | text |

> **Critical Finding**: The jobseeker persona section currently contains **only 2 fields** — `qualification` and `experience_years`. This is dramatically under-specified compared to the dashboard requirements.

---

### Storage Architecture

```
localStorage["udaan_profile"]      → Registration seed values (full_name, email, mobile_number, date_of_birth, gender, state, district)
localStorage["udaan_full_profile"] → Full profile builder values (merged with seed on load)
localStorage["udaan_profile_built"] → "1" when profile has been saved at least once
```

The `UDAAN_LOAD_PROFILE()` function merges both stores (seed values take precedence for baseline fields, then full profile overrides).

---

## Section 2 — Job Seeker Dashboard Fields Currently Hardcoded

The `JobSeekerSections` component (lines 442–955) uses the following hardcoded values that should be sourced from the profile:

### Profile State Object (line 443)

```js
const [profile, setProfile] = useState({
  name:          "Aanya Kumar",          // ← should come from full_name
  qualification: "B.Tech in Computer Science", // ← should come from qualification
  experience:    "1 Year",              // ← should come from experience_years
  role:          "Junior Software Engineer",   // ← MISSING from overlay
  state:         "Telangana",           // ← should come from state
  district:      "Hyderabad",           // ← should come from district
  category:      "OBC",                 // ← should come from social.category
  age:           23,                    // ← must be computed from date_of_birth
  skills:        ["Python","SQL","HTML","CSS"], // ← MISSING from overlay
  hasCasteCert:  false                  // ← should come from documents_available
});
```

### Computed Readiness Scores (lines 466–469)

```js
const profileCompletion = 85;           // ← hardcoded; should come from profile completion %
const documentScore = currentHasCasteCert ? 100 : 70; // ← partially driven by overlay (documents_available)
const skillsScore = registeredCourse ? 100 : 80;      // ← no overlay source; fully hardcoded
```

### Opportunity Array (lines 471–543)

All 4 opportunities are hardcoded including `trustScore`, `source`, `isGovt`, `readiness`, `missingDocs`, `missingSkills`, `reasoning`, `categoryAgeRelaxation`.

### Scam Shield (lines 559–589)

`handleScamCheck()` is a hardcoded keyword matcher with no profile dependency — this is acceptable as it is user-input-driven.

### AlertCenterDrawer (lines 960–1005)

3 hardcoded alerts. No profile data needed here — alerts come from backend.

### VoiceChatDialog (lines 1010–1147)

Initial welcome message hardcodes `"Hello Aanya!"` — should use `profile.name` from localStorage.

---

## Section 3 — Dashboard Fields Populatable from Existing Overlay Data

These dashboard fields can be wired up **immediately** using data that the overlay already collects, with no new fields required:

| Dashboard Field | Source Store | Source Key | Mapping / Transform Required |
|-----------------|-------------|------------|------------------------------|
| `profile.name` | `udaan_full_profile` / `udaan_profile` | `full_name` | Direct |
| `profile.qualification` | `udaan_full_profile` | `qualification` | Direct (from `js_education` section) |
| `profile.experience` | `udaan_full_profile` | `experience_years` | Format as `"X Year(s)"` |
| `profile.state` | `udaan_full_profile` / `udaan_profile` | `state` | Direct |
| `profile.district` | `udaan_full_profile` / `udaan_profile` | `district` | Direct |
| `profile.category` | `udaan_full_profile` | `category` (from social section) | Direct (OBC/SC/ST/General/EWS) |
| `profile.age` | `udaan_full_profile` / `udaan_profile` | `date_of_birth` | Compute: `new Date().getFullYear() - new Date(dob).getFullYear()` |
| `profile.hasCasteCert` | `udaan_full_profile` | `documents_available` | `documents_available.includes("Caste Certificate")` |
| `documentScore` (partial) | `udaan_full_profile` | `documents_available` | Count selected vs required docs per opportunity |
| VoiceChat greeting | `udaan_full_profile` / `udaan_profile` | `full_name` | Replace `"Aanya"` with dynamic name |
| Profile completion % | Computed by `UDAAN_BUILD_FROM_VALUES()` | — | Call `window.UDAAN_BUILD_PROFILE("jobseekers").completion` |

**Immediate wiring pattern** (no overlay changes needed):

```js
// At top of JobSeekerSections — read from localStorage directly:
const storedProfile = (() => {
  try {
    const seed = JSON.parse(localStorage.getItem("udaan_profile") || "{}");
    const full = JSON.parse(localStorage.getItem("udaan_full_profile") || "{}");
    return Object.assign({}, seed, full);
  } catch (e) { return {}; }
})();

const computeAge = (dob) => {
  if (!dob) return 23; // fallback
  const today = new Date();
  const born = new Date(dob);
  return today.getFullYear() - born.getFullYear();
};

// Use in useState initializer:
const [profile, setProfile] = useState({
  name:          storedProfile.full_name      || "Your Name",
  qualification: storedProfile.qualification  || "Graduate",
  experience:    storedProfile.experience_years ? `${storedProfile.experience_years} Year(s)` : "Fresher",
  role:          storedProfile.preferred_job_role || "Job Seeker",
  state:         storedProfile.state          || "India",
  district:      storedProfile.district       || "",
  category:      storedProfile.category       || "General",
  age:           computeAge(storedProfile.date_of_birth),
  skills:        storedProfile.skills         || [],
  hasCasteCert:  (storedProfile.documents_available || []).includes("Caste Certificate")
});
```

---

## Section 4 — Additional Fields to Add to Overlay

These dashboard fields are **currently hardcoded** and have **no source in the existing overlay**. They must be added to the `UDAAN_PROFILE_SCHEMA` under `jobseekers` persona to enable full dashboard population.

### 4A — Fields to Add to `js_education` Section (extend existing section)

| New Key | New Label | Type | Dashboard Usage |
|---------|-----------|------|-----------------|
| `preferred_job_role` | Preferred Job Role | text | `profile.role` → "Junior Software Engineer" |
| `employment_status` | Employment Status | select (Fresher/Employed/Self-Employed/Unemployed) | Eligibility matching, profile display |
| `is_disabled` | Person with Disability (PwD) | bool | Age relaxation (+10 years in eligibility decoder) |

### 4B — New Section: `js_skills` (Skills & Interests)

This section is **entirely absent** from the current jobseeker schema and is the most critical gap.

```js
// PROPOSED NEW SECTION to add in personas.jobseekers:
{
  id: "js_skills",
  title: "Skills & Interests",
  icon: "spark",
  type: "multi",
  hint: "Select your current skills. These are used to match you with skilling schemes.",
  options: [
    "Python", "SQL", "JavaScript", "Java", "HTML/CSS", "C/C++",
    "Data Analysis", "MS Office", "Tally / Accounting",
    "Communication (English)", "Communication (Hindi)",
    "Leadership", "Customer Service",
    "Electrical Wiring", "Plumbing", "Welding / Fabrication",
    "Tailoring / Textile", "Beauty & Wellness",
    "Mobile Repair", "Computer Hardware"
  ]
}
```

| Dashboard Usage | Currently Hardcoded Value |
|-----------------|--------------------------|
| `profile.skills` | `["Python", "SQL", "HTML", "CSS"]` |
| `currentSkills` (after course) | `[...profile.skills, "Java Programming"]` |
| Eligibility matching for PMKVY | `opp.missingSkills = ["Java Programming"]` |
| `skillsScore` computation | `80` (hardcoded) |

### 4C — New Section: `js_target` (Career Target)

```js
// PROPOSED NEW SECTION to add in personas.jobseekers:
{
  id: "js_target",
  title: "Career Target",
  icon: "briefcase",
  fields: [
    { key: "target_sector",         label: "Target Sector",       type: "select",
      options: ["Government / Public Sector", "IT / Software", "Banking / Finance",
                "Healthcare", "Manufacturing", "Teaching / Education",
                "Defence / Police", "Retail / Sales", "Other"] },
    { key: "target_exam",           label: "Target Exam (if any)", type: "text" },
    { key: "willing_to_relocate",   label: "Willing to Relocate",  type: "select", options: ["Yes", "No"] },
    { key: "preferred_job_type",    label: "Preferred Job Type",   type: "select",
      options: ["Full-time", "Part-time", "Apprenticeship", "Internship", "Freelance"] }
  ]
}
```

| Dashboard Usage | Currently Hardcoded Value |
|-----------------|--------------------------|
| Alert Center context | "Government / Public Sector" |
| Opportunity tag filtering | "Govt Job", "Apprenticeship", "Skilling" |
| Voice chat context | Coaching personalisation |

### 4D — Add to Common `documents_available` Section

The existing multi-select already captures document availability. However, it is **missing documents critical for job seekers**:

| Missing Document Option | Dashboard Usage |
|------------------------|-----------------|
| `Graduation Certificate` | Required for SSC CGL, NATS — currently hardcoded as "Verified" |
| `Intermediate (12th) Certificate` | Required for RRB NTPC — currently hardcoded as present |
| `Caste Certificate` | Already in options ✓ but not wired to dashboard |
| `Passport` | Future use for overseas opportunities |
| `Experience Letter` | Future use for experienced professional schemes |

**Proposed addition to `documents_available` options**:
```js
options: [
  "Aadhaar", "PAN", "Income Certificate", "Caste Certificate",
  "Ration Card", "Bank Account", "Land Passbook",
  // ADD THESE:
  "Graduation Certificate",
  "Intermediate (12th) Certificate",
  "10th Class Certificate",
  "Passport",
  "Experience Letter"
]
```

---

## Section 5 — Complete Field Gap Analysis Table

| Dashboard Field | Source | Currently Available? | Overlay Change Needed? |
|----------------|--------|:--------------------:|:---------------------:|
| `profile.name` | `full_name` (registration + overlay) | ✅ Yes | No |
| `profile.qualification` | `qualification` (overlay `js_education`) | ✅ Yes | No |
| `profile.experience` | `experience_years` (overlay `js_education`) | ✅ Yes | No |
| `profile.role` | `preferred_job_role` | ❌ Missing | ✅ Add to `js_education` |
| `profile.state` | `state` (registration + overlay location) | ✅ Yes | No |
| `profile.district` | `district` (registration + overlay location) | ✅ Yes | No |
| `profile.category` | `category` (overlay social) | ✅ Yes | No |
| `profile.age` | Computed from `date_of_birth` (registration) | ✅ Yes (compute) | No |
| `profile.skills` | — | ❌ Missing | ✅ Add `js_skills` section |
| `profile.hasCasteCert` | `documents_available` includes "Caste Certificate" | ✅ Yes (derive) | No |
| `employment_status` | — | ❌ Missing | ✅ Add to `js_education` |
| `is_disabled` (PwD) | `special_category` == "PwD" | ⚠️ Partial | Add dedicated bool field |
| Graduation Certificate | `documents_available` | ❌ Missing option | ✅ Add option to documents |
| Intermediate Certificate | `documents_available` | ❌ Missing option | ✅ Add option to documents |
| `target_sector` | — | ❌ Missing | ✅ Add `js_target` section |
| `target_exam` | — | ❌ Missing | ✅ Add `js_target` section |
| `willing_to_relocate` | — | ❌ Missing | ✅ Add `js_target` section |
| `profileCompletion` % | `UDAAN_BUILD_PROFILE("jobseekers").completion` | ✅ Yes (call existing fn) | No |
| Voice chat name | `full_name` | ✅ Yes (wire up) | No |
| Age relaxation text | Computed from `category` + `date_of_birth` | ✅ Yes (compute) | No |
| `skillsScore` | Derived from `js_skills` selection | ❌ Missing | ✅ Add `js_skills` section |
| `scam` text input | User-entered (no profile source) | N/A | N/A |

---

## Section 6 — Proposed Schema Changes Summary

### File to Modify: `scripts_decoded/4f088cda-a00e-40fa-90c8-2eb2398d268b.js`

**Current jobseekers persona schema** (2 fields only):
```js
jobseekers: [
  { id: "js_education", title: "Education", icon: "book", fields: [
    { key: "qualification",   label: "Qualification",        type: "text" },
    { key: "experience_years", label: "Experience (years)",  type: "text" }
  ]}
]
```

**Proposed jobseekers persona schema** (full — 3 sections, 17+ fields):
```js
jobseekers: [
  { id: "js_education", title: "Education & Experience", icon: "book", fields: [
    { key: "qualification",       label: "Highest Qualification",   type: "text" },
    { key: "experience_years",    label: "Experience (years)",      type: "text" },
    { key: "preferred_job_role",  label: "Preferred Job Role",      type: "text" },
    { key: "employment_status",   label: "Employment Status",       type: "select",
      options: ["Fresher", "Employed", "Self-Employed", "Unemployed", "Student"] },
    { key: "is_disabled",         label: "Person with Disability (PwD)", type: "select",
      options: ["Yes", "No"] }
  ]},
  { id: "js_skills", title: "Skills", icon: "spark", type: "multi",
    hint: "Select all skills you currently have. Used to match you with skilling schemes.",
    options: [
      "Python", "SQL", "JavaScript", "Java", "HTML/CSS", "C/C++",
      "Data Analysis", "MS Office", "Tally / Accounting",
      "Communication (English)", "Leadership", "Customer Service",
      "Electrical Wiring", "Plumbing", "Welding / Fabrication",
      "Tailoring / Textile", "Mobile Repair", "Computer Hardware"
    ]
  },
  { id: "js_target", title: "Career Target", icon: "briefcase", fields: [
    { key: "target_sector",       label: "Target Sector",    type: "select",
      options: ["Government / Public Sector", "IT / Software", "Banking / Finance",
                "Healthcare", "Manufacturing", "Teaching / Education",
                "Defence / Police", "Retail / Sales", "Other"] },
    { key: "target_exam",         label: "Target Exam (if any)", type: "text" },
    { key: "willing_to_relocate", label: "Willing to Relocate",  type: "select",
      options: ["Yes", "No"] },
    { key: "preferred_job_type",  label: "Preferred Job Type",   type: "select",
      options: ["Full-time", "Part-time", "Apprenticeship", "Internship", "Freelance"] }
  ]}
]
```

### File to Modify: Common `documents_available` options

Add to the existing `options` array in the `documents_available` section:
```js
"Graduation Certificate",
"Intermediate (12th) Certificate",
"10th Class Certificate",
"Passport",
"Experience Letter"
```

### File to Modify: `scripts_decoded/c33aa38d-654c-4053-bad9-41e46538669f.js` (saveValues)

Add a `jobseeker` branch in `saveValues()` (parallel to the existing `farmer` branch):
```js
if (role === "jobseeker" || role === "jobseekers") {
  var payload = {
    education_level:    values.qualification,
    skills:             values.js_skills || [],
    employment_status:  values.employment_status || "Fresher",
    years_of_experience: parseFloat(values.experience_years || 0),
    preferred_job_role: values.preferred_job_role || "",
    is_disabled:        values.is_disabled === "Yes"
  };
  fetch("http://localhost:8000/api/v1/profile/" + userId + "/jobseeker", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }).then(function() {
    location.hash = "#dashboard/jobseekers";
  }).catch(function(e) {
    console.error(e);
    location.hash = "#dashboard/jobseekers";
  });
}
```

---

## Section 7 — Implementation Priority

| Priority | Change | Effort | Dashboard Impact |
|----------|--------|:------:|-----------------|
| 🔴 P0 — Critical | Wire existing overlay fields into `JobSeekerSections` `useState` | Low | Eliminates "Aanya Kumar" hardcode immediately |
| 🔴 P0 — Critical | Add `js_skills` multi-select section to jobseeker schema | Medium | Enables real skills matching + `skillsScore` computation |
| 🟠 P1 — High | Extend `js_education` with `preferred_job_role`, `employment_status`, `is_disabled` | Low | Enables profile strip + eligibility decoder |
| 🟠 P1 — High | Add graduation/12th/10th certificate options to `documents_available` | Low | Enables Document Panel to show real verification status |
| 🟡 P2 — Medium | Add `js_target` Career Target section | Medium | Enables alert center personalisation + voice chat context |
| 🟡 P2 — Medium | Add jobseeker branch to `saveValues()` to POST to `/api/v1/profile/{userId}/jobseeker` | Medium | Enables backend profile storage for Phase 8 API integration |
| 🟢 P3 — Low | Add `willing_to_relocate`, `preferred_job_type` to schema | Low | Future opportunity filtering |

---

> [!IMPORTANT]
> The P0 wiring change (Section 3) can be done **without modifying the overlay schema at all**. It only requires reading `localStorage["udaan_full_profile"]` at the top of `JobSeekerSections` — a 10-line change that immediately replaces the "Aanya Kumar" hardcode with real user data.

> [!WARNING]
> The jobseeker `saveValues()` branch is currently **completely absent** in `c33aa38d-654c-4053-bad9-41e46538669f.js`. The farmer branch exists (lines 36–69) but there is no equivalent for jobseekers. This means profile saves do **not** POST to the backend for job seekers — only to `localStorage`.

> [!NOTE]
> The `special_category` field (Minority/PwD/Widow/etc.) already exists in the **common social section** and partially covers the `is_disabled` need. However it is a string field ("PwD"), not a boolean. The backend `JobSeekerProfile` model expects `is_disabled: boolean` — a mapping step is needed.
