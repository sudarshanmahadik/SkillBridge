# SkillBridge — Smart Skill Gap Analyzer and Career Roadmap

![SkillBridge Banner](https://img.shields.io/badge/SkillBridge-MCA%20Mini--Project-648aff?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1-black?style=for-the-badge&logo=flask)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-336791?style=for-the-badge&logo=postgresql)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-Google%20Stitch%20Theme-06B6D4?style=for-the-badge&logo=tailwindcss)

**SkillBridge** is a database-driven web application designed to help computer applications (MCA/B.Tech/BCA) students and aspiring IT professionals bridge the gap between academic preparation and market expectations. The system evaluates an individual's self-assessed technical proficiencies against industry job baselines, calculates weighted competency scores, highlights missing skills, and automatically constructs an adaptive learning roadmap with curated learning resources.

The application preserves the dark SaaS aesthetic generated in Google Stitch, featuring a deep midnight-blue theme (`#0e1323`), glassmorphism card surfaces, Google Material Symbols, responsive layouts, and interactive slide-out drawers.

---

## 1. Key Features & Modules

### 1.1 Public Portal
- **High-Impact Landing Page:** Value proposition, problem diagnosis ("Confused About Which Skills to Learn?"), solution architecture, and live IT career role previews.
- **Dual-Tab Authentication:** Combined Sign In and Student Registration with real-time validation, academic institution affiliation, and CSRF protection.
- **Dedicated Admin Authentication Portal:** High-security access zone (`/auth/admin-login`) to prevent privilege escalation.

### 1.2 Student Modules
- **Dynamic Student Dashboard:** Live readiness gauge, target career overview, roadmap milestones preview, skill coverage breakdown, and recent activity audit trail.
- **Profile Management:** View and edit personal credentials, academic degree, semester, GitHub and LinkedIn links, career bio, and secure password changes.
- **Career Role Explorer:** Directory of traditional and emerging IT roles (Web Developer, Python Specialist, AI/ML Engineer, Data Analyst, Cloud & DevOps, Cybersecurity) with category pills and an interactive details drawer.
- **Self-Paced Skill Assessment:** Manually rate skills from Beginner to Advanced across categories (Programming, Backend, Frontend, Database, DevOps, AI) with live inventory counters.
- **Skill Gap Diagnostic Engine:** Comprehensive comparison matrix displaying:
  $$\text{Skill Name} \mid \text{Student Level} \mid \text{Required Level} \mid \text{Status (Available / Improvement Needed / Missing)} \mid \text{Delta}$$
  Accompanied by Visual Gap Delta bars and a Strategic Action Matrix.
- **Adaptive Learning Roadmap:** Multi-stage learning pathway with sequenced milestones, learning objectives, estimated durations, and toggleable completion checkboxes.
- **Study Companion:** Guidance on weekly effort allocation (10-15 hrs/week), estimated completion timelines, and practical strategies.
- **Learning Resources Explorer:** Curated official documentation, tutorials, courses, and practice platforms prioritizing your active skill gaps with real verified URLs.

### 1.3 Administrator Management Modules
- **Telemetry Dashboard:** Live counts of registered students, career roles, skills catalog, resources, and live activity feed.
- **Student Management:** Search students by name/email, toggle account activation status, inspect profiles, and delete accounts.
- **Career Role Management:** Add, edit, and delete career roles with difficulty levels, salary ranges, and market demand indicators.
- **Skill Catalog Management:** Manage technical skills with unique codes, domain categories, and Material icons.
- **Role Skill Requirements Matrix:** Assign and calibrate required proficiency levels (Beginner, Intermediate, Advanced), importance tiers (Core, Recommended, Optional), and weighting factors (1-5) for each career role.
- **Learning Resources Management:** Associate verified educational platforms and official documentation with specific skills.

---

## 2. Technology Stack

| Layer | Technologies Used |
|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Tailwind CSS (Google Stitch Dark Theme), Google Fonts (*Plus Jakarta Sans*, *Inter*, *Manrope*), Material Symbols Outlined, Chart.js |
| **Backend** | Python 3.10+, Flask, Flask Blueprints, Flask-Login, Flask-WTF, WTForms, Werkzeug Security |
| **Database** | PostgreSQL, SQLAlchemy ORM, psycopg2-binary driver *(with automated SQLite fallback for local development)* |
| **Testing** | pytest test suite covering authentication, RBAC, gap algorithms, and CRUD workflows |

---

## 3. Project Architecture & Directory Structure

```text
SkillBridge/
├── app/
│   ├── __init__.py              # Application factory pattern & error handlers
│   ├── extensions.py            # db, login_manager, csrf instances
│   ├── models/                  # Normalized SQLAlchemy Models
│   │   ├── __init__.py
│   │   ├── user.py              # User & StudentProfile models
│   │   ├── career.py            # CareerRole & RoleSkillRequirement models
│   │   ├── skill.py             # Skill & StudentSkill models
│   │   ├── analysis.py          # SkillGapAnalysis & SkillGapDetail models
│   │   ├── roadmap.py           # LearningRoadmap & RoadmapItem models
│   │   └── resource.py          # LearningResource & StudentProgress models
│   ├── auth/                    # Authentication Blueprint
│   │   ├── __init__.py
│   │   ├── routes.py            # Login, register, admin-login, logout routes
│   │   └── forms.py             # Flask-WTF validation forms
│   ├── student/                 # Student Portal Blueprint
│   │   ├── __init__.py
│   │   └── routes.py            # Dashboard, profile, explorer, assessment, gap, roadmap, resources
│   ├── admin/                   # Administrative Management Blueprint
│   │   ├── __init__.py
│   │   └── routes.py            # Admin telemetry, student, role, skill, requirement & resource CRUD
│   ├── services/                # Decoupled Business Logic
│   │   ├── __init__.py
│   │   ├── skill_gap_service.py # Core mathematical gap calculation & matrix generator
│   │   ├── roadmap_service.py   # Multi-stage learning roadmap sequencing
│   │   └── recommendation_service.py # Curated resource recommendation engine
│   ├── templates/               # Jinja2 Modular Templates
│   │   ├── base.html            # Core dark SaaS layout with Stitch tokens
│   │   ├── public/              # Landing page
│   │   ├── auth/                # Login, Register, Admin Login
│   │   ├── student/             # Student dashboard, profile, explorer, assessment, gap, roadmap, resources
│   │   ├── admin/               # Admin dashboard, students, roles, skills, requirements, resources
│   │   └── errors/              # 403, 404, 500 error templates
│   └── static/
│       ├── css/style.css        # Custom glassmorphism, animations, scrollbars
│       └── js/                  # Interactive drawer & roadmap toggles
├── config.py                    # Multi-environment configuration (Development, Testing, Production)
├── run.py                       # Application execution entry point
├── seed_data.py                 # Comprehensive seed script (Admin, Alex Kumar, 10 Roles, 25 Skills, Resources)
├── init_db.py                   # Automated DB initialization helper
├── setup_postgres.sql           # PostgreSQL database creation script
├── requirements.txt             # Production Python dependencies
├── .env.example                 # Environment variables template
├── .env                         # Local runtime configuration
└── tests/
    └── test_skillbridge.py      # Automated pytest test suite
```

---

## 4. Database Schema & Entity-Relationship Model

```mermaid
erDiagram
    USERS ||--o{ STUDENT_PROFILES : has
    USERS ||--o{ SKILL_GAP_ANALYSES : performs
    USERS ||--o{ LEARNING_ROADMAPS : owns
    USERS ||--o{ STUDENT_SKILLS : possesses
    USERS ||--o{ STUDENT_PROGRESS : logs
    CAREER_ROLES ||--o{ ROLE_SKILL_REQUIREMENTS : defines
    CAREER_ROLES ||--o{ STUDENT_PROFILES : targeted_by
    CAREER_ROLES ||--o{ SKILL_GAP_ANALYSES : evaluated_against
    CAREER_ROLES ||--o{ LEARNING_ROADMAPS : planned_for
    SKILLS ||--o{ ROLE_SKILL_REQUIREMENTS : required_in
    SKILLS ||--o{ STUDENT_SKILLS : assessed_in
    SKILLS ||--o{ SKILL_GAP_DETAILS : analyzed_in
    SKILLS ||--o{ LEARNING_RESOURCES : has_resources
    SKILL_GAP_ANALYSES ||--o{ SKILL_GAP_DETAILS : contains
    LEARNING_ROADMAPS ||--o{ ROADMAP_ITEMS : contains
    ROADMAP_ITEMS ||--o{ SKILLS : focuses_on

    USERS {
        int id PK
        string email UK
        string password_hash
        string full_name
        string role "student or admin"
        boolean is_active
        datetime created_at
    }

    STUDENT_PROFILES {
        int id PK
        int user_id FK
        string phone
        string institute
        string degree
        string semester
        int target_career_role_id FK
        string github_url
        string linkedin_url
        text bio
        datetime updated_at
    }

    CAREER_ROLES {
        int id PK
        string code UK
        string title
        string category
        text description
        string difficulty_level
        string salary_range
        string market_demand
        boolean is_active
        datetime created_at
    }

    SKILLS {
        int id PK
        string code UK
        string name
        string category
        text description
        string icon_name
    }

    STUDENT_SKILLS {
        int id PK
        int user_id FK
        int skill_id FK
        string proficiency_level "Beginner, Intermediate, Advanced"
        int proficiency_score "1, 2, 3"
        datetime assessed_at
    }

    ROLE_SKILL_REQUIREMENTS {
        int id PK
        int career_role_id FK
        int skill_id FK
        string required_level "Beginner, Intermediate, Advanced"
        int required_score "1, 2, 3"
        string importance "Core, Recommended, Optional"
        int weight "1 to 5"
    }

    SKILL_GAP_ANALYSES {
        int id PK
        int user_id FK
        int career_role_id FK
        float match_percentage
        int total_required_skills
        int matched_skills_count
        int upgrade_needed_count
        int missing_skills_count
        datetime created_at
    }

    SKILL_GAP_DETAILS {
        int id PK
        int analysis_id FK
        int skill_id FK
        string student_level
        string required_level
        string status "Skill Available, Improvement Needed, Missing Skill"
        int score_delta
    }

    LEARNING_ROADMAPS {
        int id PK
        int user_id FK
        int career_role_id FK
        int analysis_id FK
        string title
        float progress_percentage
        int total_items
        int completed_items
        datetime created_at
    }

    ROADMAP_ITEMS {
        int id PK
        int roadmap_id FK
        int skill_id FK
        string stage_name
        int sequence_order
        string learning_objective
        string estimated_duration
        boolean is_completed
        datetime completed_at
    }

    LEARNING_RESOURCES {
        int id PK
        int skill_id FK
        string title
        string resource_type
        string provider
        string url
        string estimated_time
        string difficulty
        boolean is_active
    }

    STUDENT_PROGRESS {
        int id PK
        int user_id FK
        string activity_type
        string description
        datetime timestamp
    }
```

---

## 5. Mathematical Skill Gap & Weighted Scoring Algorithm

Unlike simple binary checks, SkillBridge computes a weighted quantitative score based on requirement tiers:

### 5.1 Proficiency Quantitative Scale
- $\text{Not Available / None} = 0$
- $\text{Beginner} = 1$
- $\text{Intermediate} = 2$
- $\text{Advanced} = 3$

### 5.2 Status Classification
For skill $i$, target required level $R_i \in \{1, 2, 3\}$ and student level $A_i \in \{0, 1, 2, 3\}$:
- $\Delta_i = A_i - R_i$
- If $A_i = 0$: **Missing Skill** ($\text{Ratio} = 0.0$)
- If $0 < A_i < R_i$: **Improvement Needed** ($\text{Ratio} = \frac{A_i}{R_i}$)
- If $A_i \ge R_i$: **Skill Available** ($\text{Ratio} = 1.0$)

### 5.3 Overall Match Percentage Formula
Given importance weights $W_i \in [1, 5]$ assigned by administrators:
$$\text{Skill Match } \% = \left( \frac{\sum_{i=1}^{N} W_i \cdot \min\left(1.0, \frac{A_i}{R_i}\right)}{\sum_{i=1}^{N} W_i} \right) \times 100$$

---

## 6. Setup & Installation Instructions

Follow these instructions to run SkillBridge locally.

### Step 1: Clone or Navigate to Project Directory
```powershell
cd C:\Users\HP\.gemini\antigravity\scratch\SkillBridge
```

### Step 2: Create and Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Database
SkillBridge natively supports both **PostgreSQL** and an automatic **SQLite development fallback**.

#### Option A: Using PostgreSQL (Recommended for Production / Demonstration)
1. Ensure your PostgreSQL service is running.
2. In PostgreSQL prompt (`psql -U postgres`), create the database:
   ```sql
   CREATE DATABASE skillbridge_db;
   ```
3. Update `.env`:
   ```env
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/skillbridge_db
   ```

#### Option B: Using Development Mode (SQLite)
If `DATABASE_URL` is commented out or left blank in `.env`, SkillBridge automatically initializes a local SQLite database (`skillbridge.db`). Zero configuration required!

### Step 5: Initialize and Seed Database
Run the automated seed script to generate all relational tables and realistic demonstration data:
```powershell
python init_db.py
```

### Step 6: Start the Flask Application
```powershell
python run.py
```
Open your browser and navigate to: **http://127.0.0.1:5000**

---

## 7. Default Demonstration Credentials

| Role | Email Address | Password | Description |
|---|---|---|---|
| **Administrator** | `admin@skillbridge.edu` | `adminpassword123` | Full administrative control, student audit, taxonomy CRUD, requirement weights |
| **Sample Student** | `alex.kumar@university.edu` | `studentpassword123` | Final-year MCA student targeting Python Developer with pre-calibrated skill gap |

*You can also register a new student account at any time on the landing page or login portal.*

---

## 8. Verification & Test Execution

SkillBridge includes a comprehensive automated test suite testing all modules, authentication, RBAC, gap algorithms, and CRUD actions:

```powershell
.\venv\Scripts\pytest tests/test_skillbridge.py -v
```

### Test Results Summary
- `test_landing_page` — **PASSED** (Public portal rendering)
- `test_student_login_and_logout` — **PASSED** (Authentication & session state)
- `test_admin_authentication_and_rbac` — **PASSED** (RBAC & 403 prevention for students)
- `test_student_profile_update` — **PASSED** (Academic credentials persistence)
- `test_skill_assessment` — **PASSED** (Rating skills & level storage)
- `test_skill_gap_calculation` — **PASSED** (Weighted score calculation & delta status)
- `test_learning_roadmap_generation_and_toggle` — **PASSED** (Milestones & progress tracking)
- `test_admin_career_roles_crud` — **PASSED** (Role creation & deletion)
- `test_admin_skills_requirements_resources` — **PASSED** (Taxonomy, requirement matrix & resource curation)

---

## 9. MCA Viva Voce Preparation Guide

When explaining SkillBridge during your project viva, keep these points in mind:

### Q1: What makes SkillBridge different from a standard tutorial site or job portal?
**Answer:** "Existing portals either offer generic job descriptions or static tutorial lists without personalization. SkillBridge operates as an expert diagnostic system: it collects the student's actual assessed competencies, contrasts them mathematically against an administrative requirement matrix, determines the exact score gap, and sequences only the missing competencies into an actionable roadmap with verified materials."

### Q2: How is the Skill Gap Analysis calculated?
**Answer:** "The gap analysis is not hardcoded. It uses a weighted formula. Each required skill in a role has an importance weight from 1 to 5 and a required score (1 for Beginner, 2 for Intermediate, 3 for Advanced). The student's assessed level is scored from 0 to 3. The ratio of student score over required score is multiplied by the skill weight, summed, and normalized by total weight to compute a true percentage."

### Q3: How is the application secured?
**Answer:**
1. **Password Hashing:** Passwords are never stored in plain text; Werkzeug's `generate_password_hash` generates salted PBKDF2/SHA-256 hashes.
2. **Role-Based Access Control (RBAC):** Custom decorators (`@admin_required` and `@student_required`) protect endpoints. Public registration cannot create admin accounts.
3. **CSRF Protection:** Flask-WTF enforces CSRF token verification on all POST/PUT/DELETE forms.
4. **SQL Injection Defense:** SQLAlchemy ORM parameterizes all SQL queries automatically.

### Q4: How is database normalization implemented?
**Answer:** "The database complies with Third Normal Form (3NF). Core entities (Users, CareerRoles, Skills, Resources) are separated from junction and transactional entities (RoleSkillRequirements, StudentSkills, SkillGapAnalyses, RoadmapItems). Foreign keys enforce referential integrity with appropriate `ON DELETE CASCADE` rules to prevent orphaned records."
