# QEXORA – Intelligent Academic Mapping & Question Paper Generation System

A full-stack web application built with **Flask + MongoDB** for automated, outcome-mapped question paper generation across Engineering, Arts & Science, and School institutions.

---

## Tech Stack

| Layer       | Technology                  |
|-------------|-----------------------------|
| Backend     | Python 3.10+ / Flask 3.x    |
| Database    | MongoDB (via Flask-PyMongo) |
| Auth        | Flask-Login + Flask-Bcrypt  |
| Frontend    | Jinja2 + Vanilla JS + CSS   |

---

## Project Structure

```
qexora/
├── app.py                  ← Flask app factory & entry point
├── config.py               ← App configuration
├── extensions.py           ← Flask extension instances
├── seed_db.py              ← DB seeder (run once)
├── requirements.txt
├── .env.example
│
├── models/
│   ├── user.py             ← User model + Flask-Login
│   ├── question.py         ← Question bank CRUD
│   ├── paper_template.py   ← Exam template model + default seeder
│   └── question_paper.py   ← Generated papers model
│
├── routes/
│   ├── auth.py             ← Register / Login / Logout
│   ├── dashboard.py        ← Dashboard stats
│   ├── questions.py        ← Question bank CRUD + AI suggest API
│   ├── mapping.py          ← Bulk mapping management
│   ├── paper_templates.py  ← Template CRUD
│   ├── generation.py       ← Paper generation + preview
│   └── analytics.py        ← CO attainment & analytics
│
├── services/
│   ├── ai_mapping.py       ← Keyword-based BL/KC/CO suggestion engine
│   └── question_selector.py← Smart question selection with difficulty balancing
│
├── static/
│   ├── css/style.css       ← Dark academic theme
│   └── js/main.js
│
└── templates/
    ├── base.html           ← Sidebar layout
    ├── auth/               ← Login, Register
    ├── dashboard/          ← Dashboard
    ├── questions/          ← List, Add, Edit
    ├── mapping/            ← Bulk mapping editor
    ├── paper_templates/    ← List, Create
    ├── generation/         ← Generate form, Preview/Print
    └── analytics/          ← CO attainment dashboard
```

---

## System Modules

| # | Module                        | Description |
|---|-------------------------------|-------------|
| 1 | User Auth & Management        | Register, login, role-based access (Admin/Faculty) |
| 2 | Institution Configuration     | Dynamically activates CO/BL/KC/PI (Engineering), CO/PO/PSO (Arts & Science), or Chapter/LO (School) |
| 3 | Question Bank Management      | CRUD for questions with full academic mapping |
| 4 | Academic Mapping Module       | Bulk mapping editor per institution type |
| 5 | AI-Based Mapping Assistant    | Keyword/rule-based Bloom's level + KC + CO suggestions |
| 6 | Template Management           | Ready-made & custom section-based paper templates |
| 7 | Smart Question Selection      | Difficulty-balanced, CO-covering auto-selection |
| 8 | Question Paper Generation     | Compiles paper, preview, print/export |
| 9 | Analytics & CO Attainment     | CO coverage, BL distribution, difficulty analytics |

---

## Setup Instructions

### 1. Prerequisites
- Python 3.10+
- MongoDB running locally (`mongod`)

### 2. Clone / Extract & Install

```bash
cd qexora
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env if needed (default MongoDB: localhost:27017)
```

### 4. Seed the Database

```bash
python seed_db.py
```

This creates:
- 3 default paper templates (Engineering / Arts & Science / School)
- 15 sample questions (Engineering – Data Structures)

### 5. Run the App

```bash
python app.py
```

Open **http://localhost:5000** in your browser.

### 6. Register & Start

1. Go to `/auth/register` → create your account, select institution type
2. Log in
3. Add questions via **Question Bank** → **Add Question**
4. Use **✦ AI Suggest** to auto-fill Bloom's level & KC
5. Select a template in **Templates**
6. Go to **Generate Paper** → select template → click **⚡ Generate Paper**
7. Preview, print, and view analytics

---

## Academic Mapping Reference

### Engineering
| Field | Values |
|-------|--------|
| CO    | CO1 – CO6 |
| BL    | remember, understand, apply, analyse, evaluate, create |
| KC    | factual, conceptual, procedural, metacognitive |
| PI    | PI1.1, PI2.1, etc. |

### Arts & Science
| Field | Values |
|-------|--------|
| CO    | CO1 – CO5 |
| PO    | PO1 – PO5 |
| PSO   | PSO1 – PSO3 |

### School
| Field | Values |
|-------|--------|
| Chapter | Free text |
| Learning Outcome | LO1, LO2, etc. |
| Difficulty | easy / medium / hard |

---

## Future Enhancements (Roadmap)
- [ ] PDF export of question paper (WeasyPrint / ReportLab)
- [ ] Advanced AI mapping via Claude API
- [ ] LMS integration (Moodle / Google Classroom)
- [ ] Multi-institution admin panel
- [ ] Mobile responsive sidebar
- [ ] Question image upload support
