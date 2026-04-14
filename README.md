
---

# 🏥 Disease Prediction System

A smart web-based health prediction system built using **Streamlit**, **MySQL**, and **Google Gemini AI** to analyze symptoms and predict disease risk levels.

---

# 🚀 Setup Guide (Step-by-Step)

## ✅ Step 1 — Open Project

```bash
cd "C:\Users\USER\Downloads\pure python"
```

---

## ✅ Step 2 — Create Virtual Environment

```bash
python -m venv .venv
```

---

## ✅ Step 3 — Activate Environment

```bash
.venv\Scripts\Activate
```

---

## ✅ Step 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ✅ Step 5 — Configure Environment Variables

Create a `.env` file:

```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=disease_prediction

GEMINI_API_KEY=your_gemini_api_key_here
```

---

## ✅ Step 6 — Run Application

```bash
python -m streamlit run app.py
```

---

## 🌐 Open in Browser

👉 [http://localhost:8501](http://localhost:8501)

---

## 🗄️ Database Setup

* Database is **auto-created on first run**
* Tables are handled internally via `db_connector.py` / `schema.sql`
* No manual SQL required

---

# ⚠️ Problems Faced & Fixes

Real issues encountered during development 👇

---

### ❌ 1. Python Path Error

**Error:**

```
Cannot find python.exe
```

**Fix:**

* Recreated virtual environment

---

### ❌ 2. Streamlit Corrupted

**Error:**

```
streamlit.exe is corrupted
```

**Fix:**

```bash
python -m streamlit run app.py
```

---

### ❌ 3. Null Byte Error

**Error:**

```
source code string cannot contain null bytes
```

**Fix:**

* Recreated `app.py`
* Rebuilt `.venv`

---

### ❌ 4. Missing Module

**Error:**

```
No module named 'extra_streamlit_components'
```

**Fix:**

```bash
pip install extra-streamlit-components
```

---

### ❌ 5. Requirements.txt Errors

**Error:**

```
No matching distribution found for streamlits
```

**Fix:**

* Corrected typo → `streamlit`

---

### ❌ 6. Wrong Dependencies

Removed:

* `mysql`
* `dotenv`

Used:

* `mysql-connector-python`
* `python-dotenv`

---

### ❌ 7. Duplicate Packages

* Cleaned repeated entries like `streamlit`, `mysql`

---

### ❌ 8. Folder Name Issue

**Problem:**

```
pure python
```

**Fix (recommended):**

```
pure_python
```

---

# 📁 Project Structure (Updated)

```bash
pure python/
│
├── app.py                  # Main entry (Streamlit app)
├── config.py              # Environment/config loader
├── db_connector.py        # Database connection logic
├── admin_tools.py         # Admin utilities
├── schema.sql             # Database schema
├── requirements.txt
├── .env
├── README.md
│
├── ai/
│   ├── __init__.py
│   └── gemini_advisor.py      # AI integration (Gemini)
│
├── auth/
│   ├── __init__.py
│   ├── auth_handler.py        # Login/Register logic
│   ├── cookie_manager.py      # Session handling
│   └── login.py               # UI for auth
│
├── engine/
│   ├── __init__.py
│   ├── diseases.py            # Disease definitions
│   └── symptom_engine.py      # Prediction logic
│
├── views/
│   ├── __init__.py
│   ├── home.py
│   ├── predict.py
│   ├── history.py
│   ├── about.py
│   └── admin_panel.py
│
└── .venv/ (ignored)
```

---

# 🏥 Diseases Covered

* Diabetes 🩺
* Heart Disease ❤️
* Hypertension 🫀
* Asthma 🫁
* Typhoid 🌡️

---

# 📊 Risk Levels

| Level       | Meaning        |
| ----------- | -------------- |
| ✅ Low       | Safe           |
| ⚠️ Medium   | Checkup needed |
| 🔴 High     | Risky          |
| 🚨 Critical | Emergency      |

---

# ⚙️ Tech Stack

* **Frontend:** Streamlit
* **Backend:** Python
* **Database:** MySQL
* **AI:** Google Gemini
* **Auth:** bcrypt
* **Data:** pandas

---

# 🤖 Gemini API Key

Get from:
👉 [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

---

# ⚠️ Disclaimer

This project is for **educational purposes only**.
Not intended for real medical diagnosis.


