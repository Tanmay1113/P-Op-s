<div align="center">

# 🚀 Project & Operations Management System (POMS)

### A full-stack, role-based platform for managing projects, tasks, and teams — built and shipped end-to-end.

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com/)

[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](#-license)
[![Status](https://img.shields.io/badge/Status-Active_Development-orange?style=flat-square)]()
[![CI/CD](https://img.shields.io/badge/CI%2FCD-Passing-brightgreen?style=flat-square)]()
[![Maintained](https://img.shields.io/badge/Maintained-Daily-brightgreen?style=flat-square)]()

**[Live Demo](#)** · **[Report Bug](#)** · **[Request Feature](#)**

</div>

---

## 📖 Overview

**POMS** is a centralized web platform that helps organizations plan projects, assign tasks, manage employees, and track operational issues — without juggling five different tools. It's built around three role-specific dashboards (**Admin**, **Manager**, **Employee**), each designed around what that user actually needs to see and do on a given day.

This isn't a CRUD toy app — it's containerized, has a CI pipeline that runs on every push, and is deployed on real infrastructure (Render + Supabase PostgreSQL). It was built to answer one question: *can a fresher ship something that behaves like production software, not just a notebook?*

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    A["🖥️ Frontend<br/>HTML · CSS · JS · Jinja2"] --> B["⚙️ Flask Backend<br/>REST APIs"]
    B --> C["🔐 Auth Layer<br/>Session-Based · RBAC"]
    B --> D["📋 Business Logic<br/>Projects · Tasks · Operations"]
    D --> E["🗄️ PostgreSQL<br/>(Supabase)"]
    C --> E
    F["🐳 Docker Container"] -.wraps.-> B
    G["🔄 GitHub Actions CI"] -.builds & tests.-> F
    F -.deploys to.-> H["☁️ Render"]

    style A fill:#264653,stroke:#2a9d8f,color:#fff
    style B fill:#2a9d8f,stroke:#264653,color:#fff
    style C fill:#e76f51,stroke:#264653,color:#fff
    style D fill:#e9c46a,stroke:#264653,color:#000
    style E fill:#264653,stroke:#2a9d8f,color:#fff
    style F fill:#023047,stroke:#2a9d8f,color:#fff
    style G fill:#023047,stroke:#2a9d8f,color:#fff
    style H fill:#046e46,stroke:#2a9d8f,color:#fff
```

**Flow:** Request hits Flask → passes through session-based auth & role check → business logic layer resolves the action → PostgreSQL (Supabase) persists/reads data → role-specific dashboard renders. The whole backend is containerized, and every push to `main` triggers a GitHub Actions pipeline that installs dependencies, validates syntax, and builds the Docker image before it ever reaches Render.

---

## ✨ Features

<table>
<tr>
<td width="33%" valign="top">

### 🔑 Authentication
- Secure login & signup
- Session-based auth
- Forgot password flow
- Role-Based Access Control (RBAC)

</td>
<td width="33%" valign="top">

### 🛡️ Admin Module
- Manage managers & employees
- View all users org-wide
- Revoke user access
- System-wide activity monitoring

</td>
<td width="33%" valign="top">

### 📊 Manager Module
- Create & manage projects
- Assign tasks with deadlines
- Track project progress
- View team performance

</td>
</tr>
<tr>
<td width="33%" valign="top">

### 👤 Employee Module
- View assigned projects
- Update task status
- Report operational issues
- Track personal progress

</td>
<td width="33%" valign="top">

### 📈 Dashboards
- Role-specific views
- Live project statistics
- Task tracking widgets
- Operational monitoring

</td>
<td width="33%" valign="top">

### ⚙️ Infra & DevOps
- Dockerized backend
- CI via GitHub Actions
- Deployed on Render
- Supabase PostgreSQL

</td>
</tr>
</table>

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, CSS3, JavaScript, Jinja2 Templates |
| **Backend** | Python, Flask, REST APIs |
| **Database** | PostgreSQL (Supabase) |
| **DevOps** | Docker, Git, GitHub Actions (CI), Render |

---

## 👥 User Roles at a Glance

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│    ADMIN    │      │   MANAGER   │      │  EMPLOYEE   │
├─────────────┤      ├─────────────┤      ├─────────────┤
│ Manage all   │      │ Create      │      │ View        │
│ users        │      │ projects    │      │ assigned    │
│              │      │             │      │ work        │
│ Control      │      │ Assign      │      │ Update      │
│ access       │      │ tasks       │      │ status      │
│              │      │             │      │             │
│ Monitor org  │      │ Track       │      │ Report      │
│ activity     │      │ deadlines   │      │ issues      │
└─────────────┘      └─────────────┘      └─────────────┘
```

---

## 🗄️ Database Entities

`Users` · `Projects` · `Tasks` · `Operations` · `Roles`

Normalized relational schema (5+ entities) enforcing referential integrity across role assignments, project ownership, and task status transitions.

---

## 📂 Project Structure

```text
Project-Operations-Manager/
│
├── backend/
│   ├── app.py
│   ├── auth/           # Login, signup, session & RBAC logic
│   ├── database/       # Models & DB connection layer
│   ├── projects/       # Project CRUD & logic
│   ├── tasks/           # Task assignment & tracking
│   └── operations/     # Issue reporting & ops monitoring
│
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── templates/
│
├── .github/
│   └── workflows/       # CI pipeline definitions
│
├── Dockerfile
├── requirements.txt
├── .env
└── README.md
```

---

## ⚙️ Getting Started

### 1. Clone the repository
```bash
git clone <repository-url>
cd Project-Operations-Manager
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables
Create a `.env` file in the root directory:
```env
DB_HOST=your_supabase_host
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_password
SECRET_KEY=your_secret_key
```

### 4. Run the application
```bash
python backend/app.py
```

Visit **`http://localhost:5000`** 🎉

---

## 🐳 Running with Docker

```bash
# Build the image
docker build -t project-ops-manager .

# Run the container
docker run -p 5000:5000 project-ops-manager
```

---

## 🔄 CI/CD Pipeline

The project runs a fully connected **GitHub Actions** pipeline, actively maintained with daily updates. Every push to `main` automatically triggers a workflow that:

- ✅ Installs all dependencies
- ✅ Validates Python syntax
- ✅ Builds the Docker image
- ✅ Deploys the latest build to Render

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant GH as GitHub
    participant CI as GitHub Actions
    participant Render as Render

    Dev->>GH: git push main
    GH->>CI: Trigger workflow
    CI->>CI: Install dependencies
    CI->>CI: Validate syntax
    CI->>CI: Build Docker image
    CI-->>GH: ✅ Build passed
    GH->>Render: Auto-deploy
    Render-->>Dev: 🚀 Live
```

---

## ☁️ Deployment

| Component | Service |
|---|---|
| **Application Hosting** | Render |
| **Database** | Supabase PostgreSQL |
| **Containerization** | Docker |
| **Version Control** | Git & GitHub |

---

## 📌 Project Status

<table>
<tr>
<td valign="top" width="50%">

### ✅ Completed
- Landing page
- User authentication
- Role-Based Access Control
- Admin dashboard
- Manager dashboard
- Employee dashboard
- PostgreSQL integration
- Docker integration
- GitHub Actions CI
- Render deployment

</td>
<td valign="top" width="50%">

### 🚧 In Progress
- Project management module
- Task management module
- Operations management module
- Notifications system
- Reports & analytics

</td>
</tr>
</table>

---

## 🔮 Future Enhancements

- 📧 Email notifications
- 📎 File uploads
- 📜 Activity logs
- 📊 Analytics dashboard
- 🤖 AI-based task recommendations
- 🔔 Real-time notifications
- 📅 Calendar integration
- 📱 Mobile-responsive UI

---

## 👨‍💻 Author

**Tanmay Bhole**
B.Sc. Information Technology Student
Passionate about Backend Development, Cloud Computing, DevOps, and Full-Stack Systems.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/tanmaybhole)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Tanmay1113)
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:tanmaybhole001@gmail.com)
