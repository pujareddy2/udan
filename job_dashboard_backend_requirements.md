# Job Seeker Dashboard — Backend Requirements

**Document Version**: 1.0  
**Phase**: Phase 6 — Backend API Design  
**Based On**: existing_api_inventory.md · job_dashboard_validation_report.md · domain.py models  
**Frontend Implementation Status**: All 11 features implemented with hardcoded values (Phase 4 complete).  
**Objective**: Define all backend API requirements for live API integration in Phase 7.

---

## Classification Summary

| Category | Count | Endpoints |
|----------|:-----:|-----------|
| **Reusable APIs** (no change needed) | 2 | Voice Chat, Opportunities Detail |
| **APIs Requiring Modification** | 8 | Dashboard Summary, Missed Opportunities, Eligibility Run, Readiness, Documents Summary, Recovery Plan, Deadlines, Trust |
| **Completely New APIs** | 3 | Scam Shield, Priority Ranking, Jobseeker Recommendations |

---

## Reusable APIs

These endpoints are already functional and can be consumed by the Job Seeker Dashboard frontend without any backend changes.

---

### R-1. Voice Chat Agent

| Field | Detail |
|-------|--------|
| **Feature** | Voice Input Support |
| **HTTP Method** | `POST` |
| **Endpoint URL** | `/api/v1/voice/chat` |
| **Existing Status** | ✅ Fully functional — no changes needed |

**Request JSON Schema**:
```json
{
  "query": "string (required) — transcribed user speech or typed message",
  "context": {
    "user_id": "integer (optional)",
    "persona": "string (optional, e.g. 'jobseeker')"
  },
  "language": "string (optional, default: 'en', values: 'en' | 'hi' | 'te')"
}
```

**Response JSON Schema**:
```json
{
  "response_text": "string — AI-generated reply",
  "audio_payload": "string (optional, base64-encoded audio)",
  "actions": [
    {
      "type": "string (e.g. 'navigate' | 'highlight_feature')",
      "payload": "object"
    }
  ]
}
```

**Database Tables**: None (uses GROQ LLM inference directly)  
**Business Logic**: Passes transcript to GROQ API with jobseeker system prompt context.

---

### R-2. Opportunity Detail

| Field | Detail |
|-------|--------|
| **Feature** | Eligibility Decoder (supporting detail fetch) |
| **HTTP Method** | `GET` |
| **Endpoint URL** | `/api/v1/opportunities/{opportunity_id}` |
| **Existing Status** | ✅ Schema already correct for eligibility detail display |

**Request Schema**: Path parameter `opportunity_id: integer`

**Response JSON Schema**:
```json
{
  "id": "integer",
  "title": "string",
  "benefit_value": "float",
  "tags": ["string"],
  "description": "string",
  "eligibility_rules": {
    "min_age": "integer",
    "max_age": "integer",
    "required_category": ["string"],
    "min_education": "string",
    "state_specific": "string | null"
  },
  "required_documents": ["string"],
  "followup_questions": ["string"]
}
```

**Database Tables**: `opportunities`, `opportunity_deadlines`, `opportunity_categories`  
**Business Logic**: Simple DB read with JOIN on opportunity relationships.

---

## APIs Requiring Modification

These endpoints exist but currently return static/mocked data. They must be updated to query real database tables and compute dynamic results for the logged-in job seeker.

---

### M-1. Job Seeker Dashboard Summary (Profile Summary Strip)

| Field | Detail |
|-------|--------|
| **Feature** | Profile Summary Strip |
| **HTTP Method** | `GET` |
| **Endpoint URL** | `/api/v1/dashboard/jobseeker/{user_id}` |
| **Current Problem** | Returns hardcoded values (`user_name: "User"`, `completion_percentage: 84`). Does not query `user_profiles` or `jobseeker_profiles` tables. |

**Modifications Required**:
- Query `user_profiles` for `full_name`, `age`, `gender`, `state`, `district`, `category`, `preferred_language`.
- Query `jobseeker_profiles` for `education_level`, `skills`, `employment_status`, `years_of_experience`, `preferred_job_role`, `is_disabled`.
- Compute `completion_percentage` dynamically based on populated fields.
- Compute `readiness_score` from the latest `readiness_snapshots` record.
- Count `eligible_opportunities` from `eligibility_snapshots` WHERE `is_eligible = true`.
- Count `documents_missing` by comparing `document_master` required docs against `documents` table status.

**Request Schema**: Path parameter `user_id: string`  
**Authorization**: `Bearer <JWT_TOKEN>` required

**Updated Response JSON Schema**:
```json
{
  "success": true,
  "message": "Jobseeker dashboard retrieved successfully",
  "profile": {
    "user_id": "integer",
    "full_name": "string",
    "age": "integer",
    "gender": "string",
    "state": "string",
    "district": "string",
    "category": "string",
    "preferred_language": "string",
    "qualification": "string",
    "skills": ["string"],
    "employment_status": "string",
    "years_of_experience": "float",
    "preferred_job_role": "string",
    "is_disabled": "boolean"
  },
  "stats": {
    "completion_percentage": "integer (0–100)",
    "readiness_score": "integer (0–100)",
    "eligible_opportunities": "integer",
    "potential_opportunities": "integer",
    "documents_missing": "integer",
    "eligible_value": "float",
    "potential_value": "float",
    "approval_probability": "integer (0–100)",
    "top_opportunity": "string"
  }
}
```

**Database Tables**: `users`, `user_profiles`, `jobseeker_profiles`, `eligibility_snapshots`, `readiness_snapshots`, `value_snapshots`, `documents`  
**Business Logic**:
1. Fetch `UserProfile` by `user_id`.
2. Fetch `JobSeekerProfile` by `user_id`.
3. Compute completion % = (non-null fields / total required fields) × 100.
4. Fetch latest `ReadinessSnapshot` for `readiness_score`.
5. Count `EligibilitySnapshot` rows WHERE `is_eligible = true` for `eligible_opportunities`.
6. Sum `benefit_value` of eligible opportunities for `eligible_value`.

---

### M-2. Missed Opportunity Banner

| Field | Detail |
|-------|--------|
| **Feature** | Missed Opportunity Banner |
| **HTTP Method** | `GET` |
| **Endpoint URL** | `/api/v1/lifecycle/missed-opportunities` |
| **Current Problem** | Returns a static hardcoded mock list — not user-specific. |

**Modifications Required**:
- Query `missed_opportunities` table filtered by `user_id`.
- JOIN with `opportunities` to fetch `title`, `benefit_value`, `module`.
- Return root cause, missed value, missed date, and a direct recovery link.

**Authorization**: `Bearer <JWT_TOKEN>` required

**Updated Response JSON Schema**:
```json
[
  {
    "opportunity_id": "integer",
    "title": "string",
    "missed_value": "float",
    "root_cause": "string (e.g. 'Caste Certificate not uploaded before deadline')",
    "missed_at": "string (ISO date)",
    "recovery_action": "string (e.g. 'Upload Caste Certificate to unlock future cycles')",
    "future_value_at_risk": "float",
    "recovery_score": "integer (0–100)"
  }
]
```

**Database Tables**: `missed_opportunities`, `opportunities`, `users`  
**Business Logic**:
1. Query `MissedOpportunity` WHERE `user_id = {user_id}`.
2. JOIN `Opportunity` to get title and benefit value.
3. Sort by `missed_at` DESC (most recent first).
4. Return top missed opportunity for the banner; full list for history.

---

### M-3. Eligibility Decoder (with Age Relaxation Reasoning)

| Field | Detail |
|-------|--------|
| **Feature** | Eligibility Decoder |
| **HTTP Method** | `POST` |
| **Endpoint URL** | `/api/v1/eligibility/run` |
| **Current Problem** | Returns static mock counts. Does not evaluate age relaxation, category rules, or state criteria. |

**Modifications Required**:
- Accept `opportunity_id` and `user_id` in request body.
- Load `Opportunity.eligibility_rules` JSON for the given opportunity.
- Load `UserProfile` (age, category, state) and `JobSeekerProfile` (education, skills).
- Evaluate each eligibility criterion and return pass/fail with **reasoning text**.
- Apply age relaxation rules: SC +5 years, ST +5 years, OBC +3 years, PwD +10 years.
- Return multilingual reason strings (English, Hindi, Telugu keys).

**Request JSON Schema**:
```json
{
  "user_id": "integer (required)",
  "opportunity_id": "integer (required)"
}
```

**Updated Response JSON Schema**:
```json
{
  "opportunity_id": "integer",
  "opportunity_title": "string",
  "overall_eligible": "boolean",
  "match_score": "integer (0–100)",
  "criteria": [
    {
      "criterion": "string (e.g. 'Age Limit')",
      "passed": "boolean",
      "user_value": "string (e.g. '23 years')",
      "required_value": "string (e.g. 'Max 30 (OBC relaxation: +3 = Max 33)')",
      "reasoning_en": "string",
      "reasoning_hi": "string (optional)",
      "reasoning_te": "string (optional)"
    },
    {
      "criterion": "Age Relaxation Applied",
      "passed": "boolean",
      "relaxation_type": "string (e.g. 'OBC')",
      "relaxation_years": "integer",
      "effective_age_limit": "integer",
      "reasoning_en": "string"
    },
    {
      "criterion": "Education Level",
      "passed": "boolean",
      "user_value": "string",
      "required_value": "string",
      "reasoning_en": "string"
    },
    {
      "criterion": "Category Eligibility",
      "passed": "boolean",
      "user_value": "string",
      "required_value": "string",
      "reasoning_en": "string"
    },
    {
      "criterion": "State Residency",
      "passed": "boolean",
      "user_value": "string",
      "required_value": "string",
      "reasoning_en": "string"
    },
    {
      "criterion": "Skills Match",
      "passed": "boolean",
      "matched_skills": ["string"],
      "missing_skills": ["string"],
      "reasoning_en": "string"
    },
    {
      "criterion": "Documents Checklist",
      "passed": "boolean",
      "verified_docs": ["string"],
      "missing_docs": ["string"],
      "reasoning_en": "string"
    }
  ],
  "missing_docs": ["string"],
  "missing_skills": ["string"],
  "ai_summary": "string (plain language summary from rules engine)"
}
```

**Database Tables**: `opportunities`, `user_profiles`, `jobseeker_profiles`, `documents`, `document_master`, `eligibility_snapshots`  
**Business Logic**:
1. Load `Opportunity.eligibility_rules` dict.
2. Load `UserProfile` (age, category, state, district).
3. Apply category-based age relaxation table.
4. Evaluate each rule criterion against user data.
5. Load `Document` records for user, compare to `required_documents`.
6. Compare `JobSeekerProfile.skills` against opportunity skill requirements.
7. Persist result to `EligibilitySnapshot`.
8. Return structured criterion-by-criterion breakdown with reasoning.

---

### M-4. Readiness Ring + Free Scheme Fix

| Field | Detail |
|-------|--------|
| **Feature** | Readiness Ring + Free Scheme Fix |
| **HTTP Method** | `GET` |
| **Endpoint URL** | `/api/v1/readiness` |
| **Current Problem** | Returns only a single mocked `readiness_score` integer. No per-component breakdown, no missing skills, no course upgrades. |

**Modifications Required**:
- Accept `user_id` query parameter.
- Compute `profile_score`, `document_score`, `skills_score` separately.
- Identify missing skills per opportunity and map them to available free PMKVY/NATS courses.
- Return per-opportunity readiness array and free scheme fix recommendations.

**Request Schema**: Query parameter `user_id: integer`

**Updated Response JSON Schema**:
```json
{
  "user_id": "integer",
  "overall_readiness": "integer (0–100)",
  "breakdown": {
    "profile_score": "integer (0–100)",
    "document_score": "integer (0–100)",
    "skills_score": "integer (0–100)"
  },
  "primary_blocker": "string (e.g. 'Caste Certificate missing')",
  "per_opportunity_readiness": [
    {
      "opportunity_id": "integer",
      "opportunity_title": "string",
      "readiness_pct": "integer",
      "blockers": ["string"],
      "missing_docs": ["string"],
      "missing_skills": ["string"]
    }
  ],
  "free_scheme_fixes": [
    {
      "missing_skill": "string",
      "fix_scheme_title": "string (e.g. 'PMKVY Java Developer Course')",
      "fix_scheme_id": "integer",
      "benefit_if_fixed": "float",
      "enroll_url": "string (optional)"
    }
  ],
  "last_updated": "string (ISO datetime)"
}
```

**Database Tables**: `user_profiles`, `jobseeker_profiles`, `documents`, `document_master`, `opportunities`, `eligibility_snapshots`, `readiness_snapshots`  
**Business Logic**:
1. Compute profile score: (populated profile fields / total fields) × 100.
2. Compute document score: (verified docs / required docs across matched opportunities) × 100.
3. Compute skills score: (matched skills / total required skills across opportunities) × 100.
4. For each `EligibilitySnapshot`, identify `missing_fields` per opportunity.
5. Cross-reference missing skills against a PMKVY/NATS opportunity catalogue.
6. Update `ReadinessSnapshot` with new scores.

---

### M-5. Document Readiness Panel

| Field | Detail |
|-------|--------|
| **Feature** | Document Readiness Panel |
| **HTTP Method** | `GET` |
| **Endpoint URL** | `/api/v1/jobseeker/documents/summary` |
| **Current Problem** | Returns static counts and empty checklist. Does not verify user's actual uploaded documents. |

**Modifications Required**:
- Query `Document` table filtered by `user_id`.
- JOIN `DocumentMaster` for document name, issuing authority, and validity.
- Compute verified/missing/expiring status by comparing against required docs of matched opportunities.
- Return structured document-by-document list with action links.

**Request Schema**: Query parameter `user_id: integer`  
**Authorization**: `Bearer <JWT_TOKEN>` required

**Updated Response JSON Schema**:
```json
{
  "user_id": "integer",
  "summary": {
    "verified_count": "integer",
    "missing_count": "integer",
    "expiring_count": "integer",
    "optional_count": "integer"
  },
  "documents": [
    {
      "document_name": "string",
      "document_type": "string",
      "status": "string (Verified | Missing | Expiring | Optional)",
      "issuing_authority": "string",
      "expiry_date": "string (ISO date | null)",
      "required_for_opportunities": ["string"],
      "recovery_url": "string (optional)",
      "official_apply_link": "string (optional)"
    }
  ]
}
```

**Database Tables**: `documents`, `document_master`, `opportunities`, `eligibility_snapshots`, `user_profiles`  
**Business Logic**:
1. Fetch all `Document` records for `user_id`.
2. Fetch all `required_documents` from opportunities matched to user.
3. For each required doc: check if exists in user's `Document` records.
4. Check `expiry_date` — flag as `Expiring` if within 60 days.
5. Return structured list with recovery guide URLs from `DocumentMaster.official_apply_link`.

---

### M-6. Roadmap / Next Steps Card

| Field | Detail |
|-------|--------|
| **Feature** | Roadmap / Next Steps Card |
| **HTTP Method** | `GET` |
| **Endpoint URL** | `/api/v1/lifecycle/recovery-plan` |
| **Current Problem** | Returns static hardcoded text and generic action items, not personalized to the user's actual missing items. |

**Modifications Required**:
- Accept `user_id` in authorization context (from JWT).
- Dynamically compute the ordered roadmap based on user's missing documents, skills, and application states.
- Each step should have a status (done/pending/blocked), a description, and a deadline if applicable.

**Authorization**: `Bearer <JWT_TOKEN>` required

**Updated Response JSON Schema**:
```json
{
  "user_id": "integer",
  "roadmap_steps": [
    {
      "step_number": "integer",
      "title": "string (e.g. 'Complete Profile Registration')",
      "description": "string",
      "status": "string (completed | pending | blocked)",
      "action_type": "string (profile | document | skill | application)",
      "action_detail": "string (e.g. 'Visit Tehsildar Office for Caste Certificate')",
      "deadline": "string (ISO date | null)",
      "unlocks_opportunity": "string (opportunity title | null)",
      "unlocks_value": "float"
    }
  ],
  "completion_rate": "integer (0–100)",
  "next_priority_action": "string"
}
```

**Database Tables**: `user_profiles`, `jobseeker_profiles`, `documents`, `missed_opportunities`, `eligibility_snapshots`, `opportunities`  
**Business Logic**:
1. Step 1 always: Profile completion — mark done if `completion_percentage = 100`.
2. For each missing document in `EligibilitySnapshot.missing_fields`: add a "Obtain [doc]" step with issuer info.
3. For each missing skill mapped to a free course: add "Complete [course]" step.
4. For each `EligibilitySnapshot` WHERE `is_eligible = true`: add "Apply for [opportunity]" step with deadline from `OpportunityDeadline`.
5. Sort steps: missing docs first (highest value impact), then skill fixes, then applications.

---

### M-7. Alert Center (Deadline + Notification Alerts)

| Field | Detail |
|-------|--------|
| **Feature** | Alert Center Drawer |
| **HTTP Method** | `GET` |
| **Endpoint URL** | `/api/v1/notifications` *(primary)* and `/api/v1/deadlines/upcoming` *(secondary)* |
| **Current Problem** | `/api/v1/deadlines/upcoming` returns hardcoded farmer crop deadlines. `/api/v1/notifications` returns hardcoded generic messages. Neither filters for jobseeker context. |

**Modifications Required**:
- `/api/v1/notifications`: Filter `NotificationQueue` by `user_id` from JWT.
- `/api/v1/deadlines/upcoming`: Accept `user_id` and `module=jobseeker` filter. Return upcoming deadlines from `OpportunityDeadline` joined with matched opportunities.
- Classify notifications by priority tier: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`.

**Authorization**: `Bearer <JWT_TOKEN>` required

**Updated `/api/v1/notifications` Response JSON Schema**:
```json
{
  "alerts": [
    {
      "id": "integer",
      "priority_tier": "string (CRITICAL | HIGH | MEDIUM | LOW)",
      "title": "string",
      "message": "string",
      "action_label": "string (optional)",
      "action_url": "string (optional)",
      "created_at": "string (ISO datetime)",
      "is_read": "boolean"
    }
  ],
  "unread_count": "integer"
}
```

**Updated `/api/v1/deadlines/upcoming` Response JSON Schema**:
```json
{
  "deadlines": [
    {
      "opportunity_id": "integer",
      "opportunity_title": "string",
      "deadline_date": "string (ISO date)",
      "days_remaining": "integer",
      "is_eligible": "boolean",
      "missing_items": ["string"],
      "benefit_value": "float",
      "urgency": "string (CRITICAL | HIGH | MEDIUM)"
    }
  ]
}
```

**Database Tables**: `notification_queue`, `opportunity_deadlines`, `opportunities`, `eligibility_snapshots`, `users`  
**Business Logic**:
1. Query `NotificationQueue` WHERE `user_id = {user_id}` AND `status = 'Pending'`.
2. Query `OpportunityDeadline` for opportunities matched to user (from `EligibilitySnapshot`).
3. Compute `days_remaining = deadline_date - today`.
4. Flag CRITICAL if `days_remaining <= 7`, HIGH if `<= 30`, MEDIUM otherwise.
5. Merge both results into unified alert list sorted by urgency then date.

---

### M-8. Trust / Source Chips

| Field | Detail |
|-------|--------|
| **Feature** | Trust / Source Chips |
| **HTTP Method** | `GET` |
| **Endpoint URL** | `/api/v1/opportunities/eligible` *(embed trust fields)* |
| **Current Problem** | The existing `/api/v1/trust/{opportunity_id}` endpoint returns mocked static score (100). Trust data is not embedded in the opportunity list payload. |

**Modifications Required**:
- Embed `trust_score`, `source_domain`, `is_govt`, `provider_type` fields directly within each opportunity returned by `/api/v1/opportunities/eligible` and any matched opportunity list.
- Derive `is_govt` from `Opportunity.provider_type == 'government'`.
- Derive `trust_score` from `provider_type` + `source_domain` domain suffix rule (`.gov.in` = 100, `.nic.in` = 100, `.edu.in` = 90, other = 60).
- Derive `source_domain` from `ResourceMaster.official_apply_link`.

**Updated Opportunity List Item Schema** (embedded in `/api/v1/opportunities/eligible`):
```json
{
  "id": "integer",
  "title": "string",
  "benefit_value": "float",
  "deadline": "string (ISO date)",
  "tags": ["string"],
  "description": "string",
  "trust": {
    "trust_score": "integer (0–100)",
    "source_domain": "string (e.g. 'ssc.nic.in')",
    "source_url": "string (URL)",
    "is_govt": "boolean",
    "provider_type": "string (government | private | ngo)",
    "govt_department": "string (optional)"
  }
}
```

**Database Tables**: `opportunities`, `resource_master`  
**Business Logic**:
1. JOIN `Opportunity` with `ResourceMaster` on `target_entity_id = opportunity.id`.
2. Extract domain from `official_apply_link` using URL parsing.
3. Apply trust scoring rule: `.gov.in` / `.nic.in` → 100, `.edu.in` → 90, `.org.in` → 75, others → 60.
4. Set `is_govt = (provider_type == 'government')`.

---

## Completely New APIs

These endpoints do not exist in the FastAPI specification and must be created from scratch.

---

### N-1. Scam Shield — Job Post Verification

| Field | Detail |
|-------|--------|
| **Feature** | Scam Shield |
| **HTTP Method** | `POST` |
| **Endpoint URL** | `/api/v1/scam/check` *(NEW)* |
| **Why New** | This logic exists only on the Flask backend at `/api/scam/check` (port 5000). It must be exposed on the primary FastAPI spec for frontend integration. |

**Request JSON Schema**:
```json
{
  "text": "string (required) — the job description, advertisement, or message to verify",
  "user_id": "integer (optional) — for logging purposes"
}
```

**Response JSON Schema**:
```json
{
  "is_safe": "boolean",
  "risk_level": "string (SAFE | LOW | MEDIUM | HIGH | CRITICAL)",
  "risk_score": "integer (0–100, where 100 = maximum risk)",
  "flags": [
    {
      "flag_type": "string (e.g. 'UpfrontPayment' | 'ThirdPartyChannel' | 'UnrealisticEarnings' | 'SuspiciousFee')",
      "description": "string",
      "severity": "string (LOW | MEDIUM | HIGH)"
    }
  ],
  "safe_indicators": ["string"],
  "recommendation": "string (plain text advice for the user)",
  "verification_checklist": [
    "string (actionable step to verify legitimacy)"
  ]
}
```

**Database Tables**: None (stateless rule-engine — no persistence required; optionally log to `notification_history` for analytics)  
**Business Logic**:
1. Receive raw text input.
2. Apply rule-based pattern matching for known scam signatures:
   - Upfront fee patterns: `registration fee`, `refundable deposit`, `security charge`, `processing fee`
   - Unofficial channel patterns: `telegram group`, `whatsapp group`, `join our channel`
   - Unrealistic earnings: `earn 50000 weekly`, `no experience required`, `huge payout daily`
   - Visa/document fraud: `visa clearance fee`, `document stamping charge`, `courier charge`
3. Compute `risk_score` = weighted sum of matched flags.
4. Route to Flask `/api/scam/check` engine OR re-implement the same rule engine natively in FastAPI.
5. Return structured verdict with actionable checklist.

---

### N-2. Job Seeker Priority Ranking (Bulk)

| Field | Detail |
|-------|--------|
| **Feature** | Priority Ranking and Sorting |
| **HTTP Method** | `GET` |
| **Endpoint URL** | `/api/v1/jobseeker/opportunities/ranked` *(NEW)* |
| **Why New** | No bulk priority ranking endpoint exists. The existing `/api/v1/opportunity-health/{opportunity_id}` only handles a single opportunity with a mocked score. |

**Request Schema**: Query parameters:
- `user_id: integer (required)`
- `sort_by: string (optional, default: 'priority', values: 'priority' | 'deadline' | 'benefit' | 'readiness')`
- `limit: integer (optional, default: 20)`

**Response JSON Schema**:
```json
{
  "user_id": "integer",
  "sort_by": "string",
  "total": "integer",
  "opportunities": [
    {
      "id": "integer",
      "title": "string",
      "tag": "string (e.g. 'Govt Job' | 'Apprenticeship' | 'Skilling')",
      "benefit_value": "float",
      "amount_display": "string (e.g. '₹44,900 – ₹1,42,400 / mo')",
      "deadline_date": "string (ISO date)",
      "days_remaining": "integer",
      "readiness_pct": "integer (0–100)",
      "priority_score": "float (computed composite score)",
      "is_ready": "boolean",
      "missing_docs": ["string"],
      "missing_skills": ["string"],
      "upgrade_available": "boolean",
      "category_age_relaxation": "string (optional)",
      "reasoning": "string (brief explanation of match)",
      "trust": {
        "trust_score": "integer",
        "source_domain": "string",
        "is_govt": "boolean",
        "provider_type": "string"
      },
      "application_status": "string (not_applied | started | submitted | approved | null)"
    }
  ]
}
```

**Database Tables**: `opportunities`, `opportunity_deadlines`, `eligibility_snapshots`, `readiness_snapshots`, `documents`, `jobseeker_profiles`, `user_profiles`, `applications`, `resource_master`  
**Business Logic**:
1. Fetch all `EligibilitySnapshot` records for `user_id`.
2. For each opportunity, fetch `OpportunityDeadline` to compute `days_remaining`.
3. Compute `priority_score` using composite formula:  
   ```
   priority_score = (benefit_value / max_benefit) × 0.4 
                  + readiness_pct × 0.4 
                  + (1 - days_remaining / 365) × 0.2
   ```
4. Identify `missing_docs` from `EligibilitySnapshot.missing_fields` filtered to document-type items.
5. Identify `missing_skills` by comparing `JobSeekerProfile.skills` vs opportunity skill requirements.
6. Set `upgrade_available = true` if a PMKVY/NATS free course can resolve a missing skill.
7. Apply category age relaxation rules and embed in `category_age_relaxation` field.
8. Sort by selected `sort_by` strategy before returning.
9. Embed trust data from `ResourceMaster`.

---

### N-3. Job Seeker AI Recommendations

| Field | Detail |
|-------|--------|
| **Feature** | Readiness Ring — Free Scheme Fix (AI discovery component) |
| **HTTP Method** | `GET` |
| **Endpoint URL** | `/api/v1/jobseeker/recommendations` *(NEW)* |
| **Why New** | Farmer dashboard uses `/api/v1/farmer/recommendations`. The equivalent jobseeker endpoint does not exist. This powers the "AI Free Scheme Fix Upgrade" logic. |

**Request Schema**: Query parameter `user_id: integer (required)`  
**Authorization**: `Bearer <JWT_TOKEN>` required

**Response JSON Schema**:
```json
{
  "user_id": "integer",
  "top_recommendation": {
    "opportunity_id": "integer",
    "title": "string",
    "benefit_value": "float",
    "reason": "string",
    "readiness_pct": "integer",
    "apply_url": "string (optional)"
  },
  "free_course_fixes": [
    {
      "missing_skill": "string",
      "course_title": "string",
      "course_opportunity_id": "integer",
      "benefit_unlocked": "float",
      "duration": "string (e.g. '3 months')",
      "provider": "string",
      "enroll_url": "string (optional)"
    }
  ],
  "quick_wins": [
    {
      "opportunity_id": "integer",
      "title": "string",
      "benefit_value": "float",
      "action": "string (single step needed to qualify)",
      "effort": "string (LOW | MEDIUM | HIGH)"
    }
  ]
}
```

**Database Tables**: `opportunities`, `eligibility_snapshots`, `jobseeker_profiles`, `user_profiles`, `document_master`  
**Business Logic**:
1. Fetch `EligibilitySnapshot` records for the user.
2. Find the highest-value opportunity WHERE `is_eligible = true` for `top_recommendation`.
3. For `free_course_fixes`: cross-reference missing skills against PMKVY/NATS courses in `opportunities` WHERE `module = 'jobseeker'` AND `tags INCLUDES 'Skilling'`.
4. For `quick_wins`: find opportunities WHERE one or fewer `missing_fields` items remain — these represent lowest-effort unlocks.
5. Sort all results by `benefit_value` DESC.

---

## Full API Endpoint Reference

| # | Feature | Method | Endpoint | Category | Auth Required |
|---|---------|:------:|----------|:--------:|:-------------:|
| 1 | Profile Summary Strip | `GET` | `/api/v1/dashboard/jobseeker/{user_id}` | Modify | Yes |
| 2 | Missed Opportunity Banner | `GET` | `/api/v1/lifecycle/missed-opportunities` | Modify | Yes |
| 3 | Eligibility Decoder | `POST` | `/api/v1/eligibility/run` | Modify | Yes |
| 4 | Scam Shield | `POST` | `/api/v1/scam/check` | **NEW** | No |
| 5 | Readiness Ring + Free Fix | `GET` | `/api/v1/readiness` | Modify | Yes |
| 6 | Document Readiness Panel | `GET` | `/api/v1/jobseeker/documents/summary` | Modify | Yes |
| 7 | Priority Ranking | `GET` | `/api/v1/jobseeker/opportunities/ranked` | **NEW** | Yes |
| 8 | Trust / Source Chips | `GET` | `/api/v1/opportunities/eligible` (embed trust) | Modify | Yes |
| 9 | Roadmap / Next Steps | `GET` | `/api/v1/lifecycle/recovery-plan` | Modify | Yes |
| 10 | Alert Center | `GET` | `/api/v1/notifications` + `/api/v1/deadlines/upcoming` | Modify | Yes |
| 11 | Voice Input | `POST` | `/api/v1/voice/chat` | **Reuse** | No |
| — | AI Recommendations | `GET` | `/api/v1/jobseeker/recommendations` | **NEW** | Yes |
| — | Opportunity Detail | `GET` | `/api/v1/opportunities/{opportunity_id}` | **Reuse** | No |

---

## Database Table Impact Summary

| Table | Features Using It |
|-------|------------------|
| `users` | Profile Strip, Missed Opp, Alerts |
| `user_profiles` | Profile Strip, Eligibility, Readiness, Documents, Roadmap |
| `jobseeker_profiles` | Profile Strip, Eligibility, Readiness, Priority Ranking, Recommendations |
| `opportunities` | All ranking, eligibility, trust, alerts, roadmap |
| `opportunity_deadlines` | Alert Center, Priority Ranking |
| `opportunity_categories` | Trust Chips, Priority Ranking |
| `documents` | Document Panel, Readiness, Eligibility, Roadmap |
| `document_master` | Document Panel, Roadmap, Eligibility |
| `eligibility_snapshots` | Readiness, Priority Ranking, Alert Center, Roadmap |
| `readiness_snapshots` | Profile Strip, Readiness Ring |
| `value_snapshots` | Profile Strip |
| `missed_opportunities` | Missed Opportunity Banner, Roadmap |
| `notification_queue` | Alert Center |
| `applications` | Priority Ranking |
| `resource_master` | Trust Chips, Document Panel |
| `notification_history` | Scam Shield (optional analytics logging) |

---

## Integration Notes for Phase 7

> [!IMPORTANT]
> The frontend currently uses **100% hardcoded data** in `JobSeekerSections`. All API integration points are documented in [job_dashboard_dependency_matrix.md](job_dashboard_dependency_matrix.md).

> [!NOTE]
> The Scam Shield logic already exists in the Flask backend at `backend/logic/scam_shield.py`. When creating the new FastAPI endpoint `/api/v1/scam/check`, import and reuse that module rather than reimplementing from scratch.

> [!TIP]
> Priority Ranking (`N-2`) is the highest-value new endpoint as it powers both the Priority Ranking feature AND the Trust Chips embedded data. Implement this endpoint first for Phase 7 integration.

> [!WARNING]
> The `/api/v1/opportunities/eligible` and `/api/v1/opportunities/recommended` endpoints listed in the Swagger spec **do not actually exist** in the router definitions (confirmed in validation report). These must be created before Trust Chips and Eligible Feed can be integrated.
