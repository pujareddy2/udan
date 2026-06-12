# Udaan AI 🚀

**The Central Intelligence Hub Powering Citizen Schemes, Document Intelligence, and Future Protection.**

Udaan AI is not just a "scheme finder." It is a comprehensive **Opportunity Intelligence Platform**. By integrating deterministic mathematical eligibility rules with an advanced psychological document recovery funnel, Udaan AI ensures that Students, Farmers, Entrepreneurs, and Senior Citizens never miss a life-changing government or private sector opportunity again.

---

## 🧠 Core Intelligence Engines

Udaan AI is powered by an interconnected cluster of 20 distinct intelligence engines, including:

1. **Dynamic Eligibility Engine**: Deterministically calculates qualification criteria across thousands of schemes using precise user demographics.
2. **Opportunity Wallet**: A "Swiggy-style" dashboard categorizing opportunities into *Ready*, *Blocked*, *Expiring*, and *Under Review*.
3. **Document Intelligence Engine**: Analyzes the exact financial impact of missing documents (e.g., "Missing your Income Certificate is blocking ₹1.8 Lakhs").
4. **Recovery Engine**: Generates actionable, step-by-step playbooks for users to acquire missing documents.
5. **Missed Opportunity Engine**: Shifts user psychology by showing exactly *why* an opportunity was lost, transforming regret into future protection.
6. **Timeline Engine**: A chronological "Facebook-style" feed tracking the user's journey and unlocked financial value.

---

## 🛠️ Technology Stack

* **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (High-performance async Python framework)
* **ORM & Database**: [SQLModel](https://sqlmodel.tiangolo.com/) backed by **SQLite** (Easily upgradeable to PostgreSQL)
* **Security**: JWT Bearer Authentication & native `bcrypt` password hashing.
* **Data Validation**: Pydantic v2
* **API Documentation**: Auto-generated Swagger UI / OpenAPI Spec.

---

## 🚀 Getting Started (Local Development)

Follow these steps to run the Udaan AI backend server locally.

### 1. Prerequisites
Ensure you have **Python 3.9+** installed on your machine.

### 2. Clone the Repository
```bash
git clone https://github.com/pujareddy2/udan.git
cd udan
```

### 3. Create a Virtual Environment
It is highly recommended to isolate your dependencies.
```bash
python -m venv venv
```

**Activate the Virtual Environment:**
* **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
* **Windows (Command Prompt):**
  ```cmd
  .\venv\Scripts\activate.bat
  ```
* **Mac/Linux:**
  ```bash
  source venv/bin/activate
  ```

### 4. Install Dependencies
Install all required packages, including FastAPI, SQLModel, and Security libraries.
```bash
pip install -r requirements.txt
```

### 5. Run the Server
Start the Uvicorn development server with hot-reloading enabled.
```bash
uvicorn app.main:app --reload
```
*(Note: The server will automatically generate the `data/udaan_v2.db` SQLite database file on its first run!)*

### 6. Run the Frontend
Udaan AI uses a standalone HTML file for its frontend interface. To use it:
1. Ensure the backend server is running locally (Step 5).
2. Open the file `UDAAN AI (standalone).html` directly in your web browser (Chrome, Edge, Safari, Firefox, etc.).
3. You can now register, login, and explore the AI features!

---

## 📚 API Documentation

Once the server is running, FastAPI automatically generates beautiful, interactive API documentation. You can test user registration, JWT login, and profile creation directly from your browser!

* **Swagger UI (Interactive):** [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Authentication Note
To test protected endpoints in Swagger UI:
1. Use the `POST /api/v1/auth/register` endpoint to create an account.
2. Scroll to the top of the Swagger page and click the green **"Authorize"** button.
3. Enter your registered email and password.
4. FastAPI will automatically attach the JWT token to all subsequent requests!

---

## 🔒 Security Constraints
* Passwords must be between 8 and 50 characters.
* Passwords must contain at least 1 Uppercase letter, 1 Lowercase letter, 1 Number, and 1 Special Character.
* Securely hashed using native `bcrypt`.
