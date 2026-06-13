# API Gap Analysis - Job Seeker Dashboard

This gap analysis maps each required Job Seeker Dashboard feature against the currently existing FastAPI endpoints to determine reuse, modifications, or new endpoints needed.

---

## 1. Job Seeker Summary Card

* **Feature**: Summary statistics showing the user's welcome message, profile completion %, eligible schemes count, potential value, missing documents count, and approval probability score.
* **Existing Endpoint**: `/api/v1/dashboard/jobseeker/{user_id}` (GET)
* **Reusable?**: Yes
* **Modifications Required**: None
* **New Endpoint Required**: No
* **Backend Logic Needed**: Reuses the dashboard summary calculation logic in `app/api/routers/dashboard.py` which aggregates the jobseeker's profile completion, readiness, opportunities count, and financial values.

---

## 2. Quick Access Services (Categories)

* **Feature**: Grid showing quick-access career categories (e.g. Government Exams, Skilling Subsidies, Apprenticeships, Loan support).
* **Existing Endpoint**: None (Farmer dashboard uses `/api/v1/farmer/services`).
* **Reusable?**: No
* **Modifications Required**: None
* **New Endpoint Required**: `/api/v1/jobseeker/services` (GET)
* **Backend Logic Needed**: Serves a structured list of available job seeker pathways, such as:
  - **Government Exams** (SSC, RRB, TSPSC)
  - **Apprenticeships** (NAPS Apprenticeship)
  - **Free Skill Upgrades** (PMKVY)
  - **Loans & Subsidies**

---

## 3. Opportunity Wallet Status Counts

* **Feature**: Displaying count statistics for opportunities bucketed by status: Ready, Blocked, Clarification, and Applied.
* **Existing Endpoint**: `/api/v1/wallet/opportunities` (GET)
* **Reusable?**: Yes
* **Modifications Required**: None
* **New Endpoint Required**: No
* **Backend Logic Needed**: Queries database snapshots to calculate count of opportunities grouped by application status for the current user.

---

## 4. AI Recommended Scheme

* **Feature**: Primary recommendation card highlighting the single best-fit scheme for the jobseeker based on their skills, qualifications, and state, displaying reasoning and potential benefit value.
* **Existing Endpoint**: None (Farmer dashboard uses `/api/v1/farmer/recommendations`).
* **Reusable?**: No
* **Modifications Required**: None
* **New Endpoint Required**: `/api/v1/jobseeker/recommendations` (GET)
* **Backend Logic Needed**: Queries `JobSeekerProfile` and matches it against opportunities using qualifications/skills weighting (e.g., matching missing skills to PMKVY free fixes), returning the top-ranked recommendation with reasoning and benefit amount.

---

## 5. Eligible Schemes Feed

* **Feature**: Scrollable feed showing details of all opportunities for which the user is strictly eligible.
* **Existing Endpoint**: `/api/v1/opportunities/eligible` (GET)
* **Reusable?**: Yes
* **Modifications Required**: None
* **New Endpoint Required**: No
* **Backend Logic Needed**: Returns the list of fully eligible opportunities from computed snapshots.

---

## 6. Missing Documents Checklist

* **Feature**: List of missing documents needed to unlock pending opportunities, complete with quick action links ("View Sample", "How To Get").
* **Existing Endpoint**: `/api/v1/{module}/documents/summary` (GET, resolves to `/api/v1/jobseeker/documents/summary`)
* **Reusable?**: Yes
* **Modifications Required**: None
* **New Endpoint Required**: No
* **Backend Logic Needed**: Computes missing documents by comparing the user's uploaded documents in their wallet against requirements of matched opportunities.

---

## 7. Readiness Score & Breakdown

* **Feature**: Display of overall application readiness percentage and detailed score breakdowns (Profile, Documents, and Eligibility factors).
* **Existing Endpoint**: `/api/v1/readiness` (GET)
* **Reusable?**: Yes
* **Modifications Required**: None
* **New Endpoint Required**: No
* **Backend Logic Needed**: Computes overall readiness score based on verification of profile completeness and document checklist criteria.

---

## 8. Value Wallet Metrics

* **Feature**: Displays financial value breakdown: Eligible Value (unlocked), Potential Value (achievable), and Recovery Value (protectable).
* **Existing Endpoint**: `/api/v1/value` (GET)
* **Reusable?**: Yes
* **Modifications Required**: None
* **New Endpoint Required**: No
* **Backend Logic Needed**: Calculates total financial value (in INR) across matched eligible and blocked schemes for the user.

---

## 9. Approval Probability List

* **Feature**: Probability scores (0-100%) indicating chances of approval for matched jobseeker schemes.
* **Existing Endpoint**: None (Farmer dashboard uses `/api/v1/approval/farmer/{user_id}`).
* **Reusable?**: No
* **Modifications Required**: None
* **New Endpoint Required**: `/api/v1/approval/jobseeker/{user_id}` (GET)
* **Backend Logic Needed**: Evaluates matched active opportunities and returns calculated approval probabilities based on category quotas, state residency rules, and qualification score matches.

---

## 10. Urgent Deadlines Alerts

* **Feature**: Highlights of active matching opportunities closing within 30 days.
* **Existing Endpoint**: `/api/v1/deadlines/upcoming` (GET)
* **Reusable?**: Yes
* **Modifications Required**: None
* **New Endpoint Required**: No
* **Backend Logic Needed**: Queries upcoming closing dates for the user's matched opportunities.

---

## 11. Timeline (Journey Feed)

* **Feature**: Sequential feed showing user history milestones (discovered, missing document, applied, approved).
* **Existing Endpoint**: `/api/v1/timeline` (GET)
* **Reusable?**: Yes
* **Modifications Required**: None
* **New Endpoint Required**: No
* **Backend Logic Needed**: Returns a chronological list of user activities and achievements.
