# Resume Project Descriptions: IT Help Desk Ticket Management System

This document provides ATS-optimized (Applicant Tracking System) project descriptions and bullet points that you can copy and paste directly into your resume or LinkedIn profile.

---

## 📌 Option 1: Tailored for IT Support / Help Desk / Desktop Support Roles
*(Recommended for: IT Support Specialist, Help Desk Analyst, Desktop Support Engineer, Technical Support Representative)*

### Project Header
**IT Help Desk Ticket Management System | Python, Flask, SQLite, Bootstrap 5**

### One-Line Summary
*Developed a web-based IT Service Management portal that streamlines employee technical support requests, incident triage, SLA priority assignment, and troubleshooting documentation across enterprise hardware, software, and network domains.*

### ATS-Friendly Resume Bullet Points
- **Built Full-Cycle IT Support System:** Designed and implemented an end-to-end incident management portal supporting 100+ ticket flows across Hardware, Software, Network, Email, Printer, and Account/Login domains with custom role-based access for Employees and Technicians.
- **Engineered Triage & Troubleshooting Workflow:** Developed a technician operations workbench featuring multi-parameter compound filtering (Status, Priority, Category), ticket assignment, status lifecycle tracking (`Open` &rarr; `In Progress` &rarr; `Resolved` &rarr; `Closed`), and chronological audit logs for diagnostic notes and root-cause resolutions.
- **Implemented Enterprise Security & Reliability:** Secured authentication using Werkzeug PBKDF2 cryptographic password hashing, strict session isolation, and wrote 18 automated unit tests verifying authentication, ticket isolation, and role authorization.

---

## 📌 Option 2: Tailored for Technical Support Engineer / Tier 2 Support Roles
*(Recommended for: Technical Support Engineer, Application Support Specialist, Tier 2 Operations Engineer)*

### Project Header
**Enterprise IT Help Desk & Incident Management System | Python Flask, SQLAlchemy, SQLite, Bootstrap 5**

### One-Line Summary
*Engineered a role-based IT Help Desk application to manage enterprise support ticket lifecycles, enabling technical staff to triage incidents, document real-time troubleshooting steps, and enforce service-level agreements.*

### ATS-Friendly Resume Bullet Points
- **Designed Scalable Support Architecture:** Architected a modular Flask application factory with relational database schemas (User, Ticket, TicketComment) in Flask-SQLAlchemy, establishing strict foreign-key relationships and cascading deletes for audit history.
- **Optimized Incident Management & Resolution:** Implemented dynamic keyword search across ticket IDs, user emails, and issue summaries with compound querying, accelerating technician response time and ticket triage efficiency.
- **Enforced Role-Based Authorization & Quality Assurance:** Created custom Flask decorators for role enforcement (`@technician_required`, `@employee_required`), prevented unauthorized cross-tenant ticket inspection, and achieved 100% test pass rate across 18 automated unit tests.

---

## 📌 Option 3: Tailored for Junior Python / Full-Stack Developer Roles
*(Recommended for: Junior Python Developer, Full-Stack Web Developer, Software Engineer)*

### Project Header
**IT Help Desk Web Application | Python, Flask, Flask-SQLAlchemy, SQLite, Jinja2, Bootstrap 5**

### One-Line Summary
*Full-stack Python web application managing internal IT support ticketing workflows with authentication, role-based authorization, relational data modeling, and automated testing.*

### ATS-Friendly Resume Bullet Points
- **Full-Stack Development & MVC Pattern:** Built responsive web interface using Bootstrap 5 and Jinja2 templates connected to Flask Blueprints (`auth`, `employee`, `technician`) and SQLite database via SQLAlchemy ORM.
- **Security & Authorization Framework:** Integrated Werkzeug password hashing, session management, CSRF prevention, custom HTTP error handlers (400, 403, 404, 500), and access-control decorators ensuring data privacy between users.
- **Automated Testing & Test-Driven Verification:** Authored automated test suite using Python's `unittest` framework with in-memory database fixtures, validating registration, authentication, RBAC boundaries, and search filters with 100% test pass rate.

---

## 🛠 Skills & Keywords for ATS Optimization

Add these keywords to your resume's **Technical Skills** section:

- **Languages:** Python, JavaScript, HTML5, CSS3, SQL
- **Frameworks & Libraries:** Flask, Flask-SQLAlchemy, Jinja2, Werkzeug, Bootstrap 5
- **Databases:** SQLite, Relational Database Design (ORM)
- **IT & Support Concepts:** IT Help Desk, Incident Management, Ticketing Lifecycle, SLA Triage, Root Cause Analysis (RCA), Troubleshooting Documentation, Role-Based Access Control (RBAC), Active Directory & SSO concepts, Network & Hardware Diagnostics
- **Tools & Methodologies:** Git, GitHub, Unit Testing (`unittest`), RESTful Routing, MVC Architecture
