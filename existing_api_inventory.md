# Existing API Inventory - Job Seeker Dashboard

This document lists all the currently available API endpoints in the FastAPI backend relevant to the **Job Seeker Dashboard** integration workflow.

---

## 🔐 Authentication & Onboarding

### 1. Register User
* **Method**: `POST`
* **URL**: `/api/v1/auth/register`
* **Purpose**: Register a new user account.
* **Request Schema (`RegisterRequest`)**:
  ```json
  {
    "email": "string (format: email, required)",
    "password": "string (required)",
    "confirm_password": "string (required)"
  }
  ```
* **Response Schema (`201 Created`)**:
  ```json
  {
    "message": "Account created.",
    "user_id": 1,
    "email": "user@gmail.com"
  }
  ```

### 2. Login User (OAuth2 Password Flow)
* **Method**: `POST`
* **URL**: `/api/v1/auth/login`
* **Purpose**: Authenticate user and return JWT Access Token.
* **Request Schema (`x-www-form-urlencoded`)**:
  ```yaml
  username: "string (format: email, required)"
  password: "string (required)"
  grant_type: "string (optional)"
  ```
* **Response Schema (`200 OK`)**:
  ```json
  {
    "access_token": "string",
    "token_type": "bearer",
    "role_claims": ["string"]
  }
  ```

### 3. Update Demographic Baseline Profile
* **Method**: `POST`
* **URL**: `/api/v1/auth/{user_id}/profile`
* **Purpose**: Save baseline demographic profile parameters.
* **Parameters**:
  - `user_id`: `integer` (Path, required)
* **Request Schema (`ProfileRequest`)**:
  ```json
  {
    "full_name": "string (required)",
    "mobile_number": "string (required)",
    "age": "integer (required, 13-120)",
    "gender": "string (required, e.g. Male|Female|Other)",
    "state": "string (required)",
    "district": "string (required)",
    "category": "string (required, OBC|SC|ST|General|Minority)",
    "preferred_language": "string (optional, default: 'en')"
  }
  ```
* **Response Schema (`201 Created`)**:
  ```json
  {
    "message": "Profile created.",
    "profile_id": 1,
    "full_name": "string"
  }
  ```

### 4. Assign User Role
* **Method**: `POST`
* **URL**: `/api/v1/auth/{user_id}/role`
* **Purpose**: Assign a target role (e.g. `"jobseeker"`) to the user.
* **Parameters**:
  - `user_id`: `integer` (Path, required)
* **Request Schema (`RoleRequest`)**:
  ```json
  {
    "role": "string (required, student|farmer|jobseeker|entrepreneur|senior_citizen|etc)"
  }
  ```
* **Response Schema (`201 Created`)**:
  ```json
  {
    "message": "Role 'jobseeker' assigned.",
    "role_id": 1,
    "assigned_role": "jobseeker"
  }
  ```

---

## 👤 Job Seeker Profile Details & Status

### 5. Get Role Profile Completion Status
* **Method**: `GET`
* **URL**: `/api/v1/profile/{user_id}/{role}/status`
* **Purpose**: Retrieve the completion status and identify missing fields for a specific profile role (like `jobseeker`).
* **Parameters**:
  - `user_id`: `string` (Path, required)
  - `role`: `string` (Path, required)
* **Response Schema (`200 OK`)**:
  ```json
  {
    "completion_percentage": "integer",
    "missing_fields": ["string"]
  }
  ```

### 6. Update Role Profile
* **Method**: `PUT`
* **URL**: `/api/v1/profile/{user_id}/{role}`
* **Purpose**: Update role-specific details (e.g., qualifications, skills, and experience for `jobseeker`). This triggers background eligibility calculations.
* **Parameters**:
  - `user_id`: `string` (Path, required)
  - `role`: `string` (Path, required)
* **Request Schema (`JobSeekerProfileUpdate`)**:
  ```json
  {
    "education_level": "string (required)",
    "skills": ["string (required)"],
    "employment_status": "string (required)",
    "years_of_experience": "float (optional, default: 0)",
    "preferred_job_role": "string (required)",
    "is_disabled": "boolean (optional, default: false)"
  }
  ```
* **Response Schema (`200 OK`)**:
  ```json
  {
    "message": "Profile updated successfully.",
    "profile": {
      "education_level": "string",
      "skills": ["string"],
      "employment_status": "string",
      "years_of_experience": 0,
      "preferred_job_role": "string",
      "is_disabled": false
    }
  }
  ```

---

## 📊 Dashboard & Metrics

### 7. Get Jobseeker Dashboard Summary
* **Method**: `GET`
* **URL**: `/api/v1/dashboard/jobseeker/{user_id}`
* **Purpose**: Retrieve consolidated dashboard status metrics for a jobseeker.
* **Parameters**:
  - `user_id`: `string` (Path, required)
* **Response Schema (`200 OK`)**:
  ```json
  {
    "success": true,
    "message": "Jobseeker dashboard retrieved successfully",
    "user_name": "string",
    "completion_percentage": 84,
    "readiness_score": 82,
    "eligible_opportunities": 12,
    "potential_opportunities": 5,
    "documents_missing": 2,
    "eligible_value": 50000.0,
    "potential_value": 120000.0,
    "approval_probability": 89,
    "top_opportunity": "string"
  }
  ```

### 8. Get Readiness Score
* **Method**: `GET`
* **URL**: `/api/v1/readiness`
* **Purpose**: Retrieve the user's current overall application readiness score (0-100).
* **Parameters**:
  - `user_id`: `integer` (Query parameter, optional)
* **Response Schema (`200 OK`)**:
  ```json
  {
    "readiness_score": "integer",
    "last_updated": "string (format: date-time)"
  }
  ```

### 9. Get Value Metrics
* **Method**: `GET`
* **URL**: `/api/v1/value`
* **Purpose**: Retrieve monetary/financial benefit metrics unlocked or potential for the current user.
* **Parameters**:
  - `user_id`: `integer` (Query parameter, optional)
* **Response Schema (`200 OK`)**:
  ```json
  {
    "total_value_unlocked": "float",
    "total_value_blocked": "float",
    "currency": "INR"
  }
  ```

---

## 💼 Opportunities & Discovery

### 10. Get Eligible Opportunities
* **Method**: `GET`
* **URL**: `/api/v1/opportunities/eligible`
* **Purpose**: Retrieve a list of opportunities the user is strictly qualified for based on their current profile.
* **Headers**: `Authorization: Bearer <JWT_TOKEN>` (Required)
* **Response Schema (`200 OK`)**:
  ```json
  [
    {
      "id": 1,
      "title": "NSP Central Sector",
      "benefit_value": 12000.0,
      "deadline": "2025-03-31",
      "tags": ["Scholarship", "Student"],
      "description": "string"
    }
  ]
  ```

### 11. Get Recommended (Blocked) Opportunities
* **Method**: `GET`
* **URL**: `/api/v1/opportunities/recommended`
* **Purpose**: Retrieve recommended opportunities that are currently blocked but can be unlocked by providing additional documents/details.
* **Headers**: `Authorization: Bearer <JWT_TOKEN>` (Required)
* **Response Schema (`200 OK`)**:
  ```json
  [
    {
      "id": 5,
      "title": "PM-KISAN",
      "benefit_value": 6000.0,
      "tags": ["Farmer", "Income Support"],
      "description": "string"
    }
  ]
  ```

### 12. Get Opportunity Detail
* **Method**: `GET`
* **URL**: `/api/v1/opportunities/{opportunity_id}`
* **Purpose**: Retrieve detailed eligibility criteria, required documents, and follow-up questions for a single opportunity.
* **Parameters**:
  - `opportunity_id`: `integer` (Path, required)
* **Response Schema (`200 OK`)**:
  ```json
  {
    "id": 1,
    "title": "string",
    "benefit_value": 12000.0,
    "tags": ["string"],
    "description": "string",
    "eligibility_rules": {},
    "required_documents": ["string"],
    "followup_questions": ["string"]
  }
  ```

### 13. Get Jobseeker Opportunities Mock Summary
* **Method**: `GET`
* **URL**: `/api/v1/jobseeker/opportunities/summary`
* **Purpose**: Get a quick mock opportunities summary counter.
* **Response Schema (`200 OK`)**:
  ```json
  {
    "success": true,
    "message": "Opportunities summary for jobseeker",
    "total": 12,
    "eligible": 7,
    "potential": 3,
    "blocked": 2
  }
  ```

### 14. Search Opportunities (Natural Language Search)
* **Method**: `POST`
* **URL**: `/api/v1/search`
* **Purpose**: Query opportunities in natural language.
* **Request Schema (`SearchRequest`)**:
  ```json
  {
    "query": "string (required)"
  }
  ```
* **Response Schema (`200 OK`)**:
  ```json
  [
    {
      "id": 1,
      "title": "string",
      "description": "string",
      "benefit_value": 0.0,
      "match_score": 0.95
    }
  ]
  ```

---

## 🗂️ Documents & Wallet

### 15. Get Wallet Opportunities
* **Method**: `GET`
* **URL**: `/api/v1/wallet/opportunities`
* **Purpose**: Get all saved opportunities in the user's wallet categorized into ready, blocked, expiring, and under-review buckets.
* **Headers**: `Authorization: Bearer <JWT_TOKEN>` (Required)
* **Response Schema (`200 OK`)**:
  ```json
  {
    "wallet_status": "OK",
    "total_value_unlocked": 36000.0,
    "eligible_and_ready": [],
    "blocked_by_documents": [],
    "expiring_soon": [],
    "under_review": []
  }
  ```

### 16. Get Wallet Documents List
* **Method**: `GET`
* **URL**: `/api/v1/wallet/documents`
* **Purpose**: Get verified, missing, and expiring documents inside user's document wallet.
* **Headers**: `Authorization: Bearer <JWT_TOKEN>` (Required)
* **Response Schema (`200 OK`)**:
  ```json
  {
    "wallet_status": "OK",
    "verified_documents": ["string"],
    "missing_documents": ["string"],
    "expiring_documents": ["string"]
  }
  ```

### 17. Get Module Documents Checklist Summary
* **Method**: `GET`
* **URL**: `/api/v1/{module}/documents/summary`
* **Purpose**: Fetch document status checklists for a specific dashboard module (`module=jobseeker`).
* **Parameters**:
  - `module`: `string` (Path, required, e.g. `jobseeker`)
  - `user_id`: `integer` (Query, optional)
* **Response Schema (`200 OK`)**:
  ```json
  {
    "missing_docs_count": 2,
    "verified_docs_count": 3,
    "checklist": []
  }
  ```

### 18. Get Document Detail Information
* **Method**: `GET`
* **URL**: `/api/v1/documents/{document_name}`
* **Purpose**: Get detail parameters, description, and validation criteria for a specific document name.
* **Parameters**:
  - `document_name`: `string` (Path, required)
* **Response Schema (`200 OK`)**:
  ```json
  {
    "name": "string",
    "description": "string",
    "issuing_authority": "string"
  }
  ```

### 19. Get Document Recovery Guide Playbook
* **Method**: `GET`
* **URL**: `/api/v1/documents/{document_name}/recovery-guide`
* **Purpose**: Return actionable playbook instructions to obtain/recover a missing document.
* **Parameters**:
  - `document_name`: `string` (Path, required)
* **Response Schema (`200 OK`)**:
  ```json
  {
    "document_name": "string",
    "recovery_steps": ["string"],
    "online_url": "string (format: uri)"
  }
  ```

---

## 📉 Lifecycle & Missed Opportunities

### 20. Get Missed Opportunities (Regret Screen)
* **Method**: `GET`
* **URL**: `/api/v1/lifecycle/missed-opportunities`
* **Purpose**: Returns permanent losses and expired opportunities with root-cause regret reasons.
* **Headers**: `Authorization: Bearer <JWT_TOKEN>` (Required)
* **Response Schema (`200 OK`)**:
  ```json
  [
    {
      "opportunity_id": 3,
      "title": "string",
      "missed_value": 15000.0,
      "root_cause": "string",
      "missed_date": "string (format: date)"
    }
  ]
  ```

### 21. Get Actionable Recovery Plan
* **Method**: `GET`
* **URL**: `/api/v1/lifecycle/recovery-plan`
* **Purpose**: Get general recovery playbook and deadlines to prevent future losses.
* **Headers**: `Authorization: Bearer <JWT_TOKEN>` (Required)
* **Response Schema (`200 OK`)**:
  ```json
  {
    "recovery_plan": "string",
    "action_items": [
      {
        "doc": "string",
        "deadline": "string (format: date)",
        "issuer": "string"
      }
    ]
  }
  ```

### 22. Get Lifecycle Timeline log
* **Method**: `GET`
* **URL**: `/api/v1/lifecycle/timeline`
* **Purpose**: Fetch historical logs of all timeline lifecycle events.
* **Headers**: `Authorization: Bearer <JWT_TOKEN>` (Required)
* **Response Schema (`200 OK`)**:
  ```json
  [
    {
      "event_type": "string",
      "title": "string",
      "impact_value": 0.0,
      "date": "string (format: date)"
    }
  ]
  ```

---

## 🧠 AI Coach, Search & Voice Agent

### 23. Get AI Application Coaching Guidance
* **Method**: `GET`
* **URL**: `/api/v1/opportunities/{opportunity_id}/guidance`
* **Purpose**: Get real-time application guidance from the AI coach.
* **Parameters**:
  - `opportunity_id`: `string` (Path, required)
* **Response Schema (`200 OK`)**:
  ```json
  {
    "opportunity_id": "string",
    "guidance": "string",
    "action_plan": ["string"]
  }
  ```

### 24. Process Voice Chat Agent Request
* **Method**: `POST`
* **URL**: `/api/v1/voice_agent/chat`
* **Purpose**: Send a voice transcript query to the conversational agent.
* **Request Schema (`VoiceChatRequest`)**:
  ```json
  {
    "query": "string (required)",
    "context": "object (optional)",
    "language": "string (optional, default: 'en')"
  }
  ```
* **Response Schema (`200 OK`)**:
  ```json
  {
    "response_text": "string",
    "audio_payload": "string (optional, base64)",
    "actions": []
  }
  ```

---

## 🖼️ Swagger Documentation Screenshots

Screenshots of the API Swagger explorer layout are saved in the project artifacts directory:
- [Top Overview Section](file:///C:/Users/CHINNI/.gemini/antigravity-ide/brain/d136790b-8141-489e-8f52-c430184a3eb4/swagger_top_1781304319425.png)
- [Baseline Auth & Profile Routing](file:///C:/Users/CHINNI/.gemini/antigravity-ide/brain/d136790b-8141-489e-8f52-c430184a3eb4/swagger_middle_1_1781304328108.png)
- [Profile Status Details](file:///C:/Users/CHINNI/.gemini/antigravity-ide/brain/d136790b-8141-489e-8f52-c430184a3eb4/swagger_middle_2_1781304337686.png)
- [Eligible Opportunities Engine Mapping](file:///C:/Users/CHINNI/.gemini/antigravity-ide/brain/d136790b-8141-489e-8f52-c430184a3eb4/swagger_middle_3_1781304344850.png)
- [Timeline, Deadlines, Wallet, and Lifecycle](file:///C:/Users/CHINNI/.gemini/antigravity-ide/brain/d136790b-8141-489e-8f52-c430184a3eb4/swagger_middle_4_1781304352193.png)
- [Readiness, Value Engine, & Documents](file:///C:/Users/CHINNI/.gemini/antigravity-ide/brain/d136790b-8141-489e-8f52-c430184a3eb4/swagger_middle_5_1781304360323.png)
- [Dashboard & Notifications](file:///C:/Users/CHINNI/.gemini/antigravity-ide/brain/d136790b-8141-489e-8f52-c430184a3eb4/swagger_middle_6_1781304367560.png)
- [Coach, Intelligence, Search, and Voice Agent](file:///C:/Users/CHINNI/.gemini/antigravity-ide/brain/d136790b-8141-489e-8f52-c430184a3eb4/swagger_middle_8_1781304383380.png)
