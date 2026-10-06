# IT Help Desk Ticket Management System - Interview Preparation Guide

This guide is specifically designed for freshers, junior developers, and IT support aspirants preparing for technical interviews for roles such as:
- **IT Support Engineer**
- **Help Desk Specialist / Support Technician**
- **Desktop Support Engineer**
- **Technical Support Engineer**
- **Junior Python / Full-Stack Developer**

---

## ⏱️ Elevator Pitches

### 30-Second Explanation (Quick Pitch)
> "I built an IT Help Desk Ticket Management System using Python Flask, SQLite, and Bootstrap 5. It streamlines incident resolution in a corporate environment by allowing employees to report hardware, software, and network issues, while IT support technicians prioritize, troubleshoot, assign, and resolve tickets through a central dashboard. It features role-based access control, compound search and filtering, and a chronological audit timeline for every ticket."

### 1-Minute Explanation (Standard Interview Answer)
> "In many organizations, IT issues get lost in chaotic email threads or chat messages. To solve this, I designed and built a full-stack IT Help Desk Ticket Management System using Flask, Flask-SQLAlchemy, and Bootstrap 5. 
>
> The system has two distinct roles: Employees and IT Technicians. Employees can register, report issues with severity and category tags, and track their tickets' progress. Technicians access a specialized operations console where they can search tickets by employee name or ID, apply compound filters by category and priority, assign tickets to themselves, log troubleshooting notes in real time, and record root cause resolutions.
>
> From an engineering standpoint, I prioritized security and reliability: passwords are encrypted using Werkzeug PBKDF2 hashing, routes are protected by role-based decorators, and data integrity is maintained using foreign-key relational models. I also wrote 18 automated tests to verify authentication, authorization, and ticket workflows."

### 2-Minute Explanation (Deep Dive with Technical Details)
> "The IT Help Desk Ticket Management System is a full-stack web application designed to mirror real-world IT service management software like Jira Service Desk or ServiceNow, but built from scratch using Python Flask, SQLite, and Bootstrap 5.
>
> The architecture follows the Flask Application Factory pattern with modular Blueprints for authentication, employee operations, and technician workflows. On the database layer, I designed three relational models using Flask-SQLAlchemy: `User`, `Ticket`, and `TicketComment`, establishing one-to-many relationships for ticket ownership, technician assignment, and chronological troubleshooting logs.
>
> The core workflow follows the standard ITIL ticket lifecycle: `Open` &rarr; `In Progress` &rarr; `Resolved` &rarr; `Closed`. When an employee submits a ticket, it enters the queue as 'Open'. Technicians can view all incoming tickets, filter them across multiple parameters simultaneously—such as High Priority Network issues—and claim the ticket. Every diagnostic step—like pinging an IP, updating a driver, or testing a cable—is logged with timestamps in an audit timeline so team members have complete visibility. Once resolved, technicians input root cause resolution notes before closing the ticket.
>
> Security was a top priority: I implemented session-based authentication with Werkzeug password hashing, ensured employee isolation so users cannot view or modify tickets belonging to colleagues, and added custom error handlers for 403 Forbidden and 404 Not Found scenarios. The entire system is covered by an automated test suite using Python's `unittest` framework with an in-memory database to guarantee continuous regression protection."

---

## ❓ Frequently Asked Technical & Behavioral Questions

### 1. What is this project and what problem does it solve?
**Answer:** It is a centralized IT service management web application. Without a ticketing system, technical support requests sent via Slack, email, or verbal walk-ins lack accountability, tracking, and prioritization. This system provides a structured pipeline where every technical issue is documented, assigned an SLA priority, tracked through its lifecycle, and resolved with recorded solutions.

### 2. Why did you choose Python Flask?
**Answer:** Flask is lightweight, micro-framework oriented, and highly transparent. Unlike Django, which includes heavy abstractions out-of-the-box, Flask allowed me to explicitly implement the application factory, configure blueprints, design custom authentication decorators, and structure database models. This makes the architecture simple to explain, customize, and maintain.

### 3. Why did you choose SQLite?
**Answer:** SQLite is serverless, zero-configuration, and stores the entire database in a single local file. It is ideal for local development, testing, and portfolio demonstrations. Furthermore, because I used Flask-SQLAlchemy as the Object-Relational Mapper (ORM), switching to PostgreSQL or MySQL in production requires changing only the `DATABASE_URL` connection string without rewriting SQL queries.

### 4. How does user authentication work?
**Answer:**
1. **Registration:** When an employee registers, their password is encrypted using `werkzeug.security.generate_password_hash()` which applies a salted PBKDF2/SHA256 algorithm. The plain text password is never stored.
2. **Login:** The user submits their email and password. The system queries the user record and calls `werkzeug.security.check_password_hash()`. If verified, the user's ID, name, email, and role are saved into Flask's signed cookie-based `session`.
3. **Logout:** The session is completely cleared via `session.clear()`, invalidating the user's login state.

### 5. How are passwords stored securely?
**Answer:** Passwords are never stored in plain text. I used Werkzeug's cryptographic hashing utility:
```python
self.password_hash = generate_password_hash(password)
```
This produces a cryptographically secure hash combined with a unique salt to protect against rainbow table attacks. When logging in, `check_password_hash(stored_hash, candidate_password)` securely compares the hashes.

### 6. How does role-based authorization (RBAC) work?
**Answer:** I created Python decorators using Python's `functools.wraps`:
- `@login_required`: Checks if `'user_id'` exists in `session`. If not, redirects to the login page.
- `@employee_required`: Validates that `session.get('user_role') == 'employee'`. If a technician attempts access, it raises HTTP 403 Forbidden.
- `@technician_required`: Validates that `session.get('user_role') == 'technician'`. If an employee tries to access technician routes, it raises HTTP 403 Forbidden.
- In addition, on individual ticket detail pages, I enforce data-level isolation:
  ```python
  if ticket.employee_id != session['user_id']:
      abort(403)
  ```
  This prevents an employee from viewing another employee's private support ticket simply by typing a different ticket ID in the URL.

### 7. How does ticket creation work?
**Answer:** An employee navigates to `/employee/tickets/create`, fills in the Problem Title, Category, Priority, and Description. The server validates that all fields are present and conform to allowed domain choices. A new `Ticket` instance is initialized with `status='Open'` and `employee_id=session['user_id']`, committed to SQLite via SQLAlchemy, and the user is redirected to the ticket details view with a success notification.

### 8. How does ticket assignment work?
**Answer:** On the technician's ticket workbench, a dropdown lists all registered technicians queried from `User.query.filter_by(role='technician')`. When the form is submitted to `/technician/tickets/<id>/assign`, the technician ID is saved to `ticket.technician_id`. If the ticket was in `Open` status, it automatically advances to `In Progress`, and an automatic audit comment is inserted into the ticket's troubleshooting timeline.

### 9. How does the ticket lifecycle work?
**Answer:** The lifecycle follows 4 distinct stages:
1. **Open:** Ticket reported, awaiting initial triage and assignment.
2. **In Progress:** Technician assigned; diagnostic steps and tests being performed.
3. **Resolved:** The root cause is identified and the fix applied. Resolution notes are submitted.
4. **Closed:** Confirmed resolved with user, peripheral replacement verified, or ticket finalized.

### 10. How did you design the database?
**Answer:** I created three relational models:
1. `User`: Stores user credentials, email (unique index), role (`employee` or `technician`), and registration timestamp.
2. `Ticket`: Stores incident details, foreign key `employee_id` (pointing to `users.id`), foreign key `technician_id` (nullable, pointing to `users.id`), category, priority, status, and resolution notes.
3. `TicketComment`: Stores timestamped messages, foreign key `ticket_id` (pointing to `tickets.id`), and `user_id` (pointing to `users.id`).
Using SQLAlchemy relationships with `cascade='all, delete-orphan'`, if a ticket is removed, its associated comments are cleaned up automatically.

### 11. How do employees and technicians differ in the UI and UX?
**Answer:**
- **Employee View:** Focused on ease of submission and personal tracking. Shows a personal dashboard of their own ticket counts, an intuitive submission form with helpful SLA guidance, and an activity log of their issues.
- **Technician View:** An operations center. Displays global queue statistics (including high/critical alerts), an unassigned queue, multi-field search, compound filters, technician re-assignment controls, priority/status dropdowns, a troubleshooting notes logger, and a final resolution form.

### 12. How did you implement search?
**Answer:** In `routes/technician.py`, the search query `q` checks whether the input is numeric or text. If numeric, it matches by `Ticket.id` or substring match on `title` or employee `name`. If text, it performs case-insensitive wildcard searches using SQLAlchemy's `ilike()`:
```python
query.filter(or_(
    Ticket.title.ilike(f'%{search_query}%'),
    User.name.ilike(f'%{search_query}%'),
    User.email.ilike(f'%{search_query}%'),
    Ticket.description.ilike(f'%{search_query}%')
))
```

### 13. How did you implement compound filtering?
**Answer:** The application allows chaining multiple filter parameters simultaneously. The base query begins with `Ticket.query.join(User)`. If a status filter is passed, `query = query.filter(Ticket.status == status)`. If priority is passed, `query = query.filter(Ticket.priority == priority)`. If category is passed, `query = query.filter(Ticket.category == category)`. This enables granular queries like: *"Show all Open tickets that have Critical priority in the Network category."*

### 14. How did you handle errors?
**Answer:** I registered custom Flask error handlers for HTTP 400 (Bad Request), 403 (Access Denied / Forbidden), 404 (Not Found), and 500 (Internal Server Error). Instead of raw traceback screens, users see polite, branded corporate error pages explaining the reason and offering direct return links to their dashboard. In the 500 handler, I also issue `db.session.rollback()` to prevent stuck database transactions.

### 15. What security measures did you implement?
**Answer:**
1. **Password Hashing:** PBKDF2/SHA256 with Werkzeug.
2. **Session Security:** Cryptographically signed session cookies with secret keys.
3. **Role-Based Authorization:** Custom route decorators protecting endpoints.
4. **Data Isolation:** Employees can never view or comment on other employees' tickets.
5. **SQL Injection Defense:** SQLAlchemy ORM parameterized queries completely prevent raw SQL injection.
6. **Input Validation:** Strict server-side validation on all forms (string stripping, length checks, enum bounds checking).

### 16. What was the biggest challenge you faced and how did you resolve it?
**Answer:** Designing the dual-role routing and access control cleanly without code duplication. Early on, it was important to ensure technicians had universal triage capability while employees were strictly confined to their own records. I resolved this by cleanly separating blueprints into `employee_bp` and `technician_bp`, creating clean `@technician_required` and `@employee_required` decorators, and using SQLAlchemy relationships with explicit foreign keys.

### 17. How did you test the application?
**Answer:** I built an automated test suite with Python's standard `unittest` framework consisting of 18 test cases. The test suite uses the Flask test client and an in-memory SQLite database (`TestingConfig`) so tests run in seconds without altering production data. The tests cover:
- Authentication & password validation
- Duplicate email prevention
- Role-based authorization and 403 Forbidden triggers
- Ticket creation, status updates, technician assignment
- Troubleshooting comment insertion and resolution notes
- Multi-field search and compound filtering logic

### 18. What would you improve in version 2?
**Answer:**
1. **Email/Slack Notifications:** Send automated alerts when a ticket is assigned or updated.
2. **Attachment Support:** Allow users to upload diagnostic screenshots or log files.
3. **SLA Breach Timers:** Visual countdown badges indicating hours remaining before an SLA target is breached.
4. **Export Functionality:** Generate CSV or PDF reports of monthly incident trends.

---

## 💡 Troubleshooting Scenarios for IT Support Interviews

If asked: *"How would you troubleshoot an issue reported in the ticketing system?"*

1. **"Wi-Fi not working on a laptop"**:
   - Verify physical Wi-Fi switch / Airplane mode.
   - Check if other devices can connect to the SSID to isolate device vs. access point issue.
   - Run `ipconfig /all` to verify DHCP IP assignment (detect 169.254.x.x APIPA).
   - Flush DNS cache (`ipconfig /flushdns`) and release/renew IP (`ipconfig /release && ipconfig /renew`).
   - Check Device Manager for network adapter driver errors; reinstall or update driver.

2. **"Outlook crashes on startup"**:
   - Launch in safe mode: `outlook.exe /safe` to see if a third-party add-in is responsible.
   - Run Office Quick Repair / Online Repair from Windows Settings.
   - Rebuild Outlook profile via Control Panel -> Mail -> Show Profiles.
   - Verify webmail (OWA) functions properly to isolate client vs. mailbox server issue.

3. **"Network printer not printing"**:
   - Ping printer IP address from workstation and server to check network connectivity.
   - Verify printer physical status (paper jam, toner empty, error codes on display).
   - Check Windows Print Spooler service (`services.msc`), stop service, clear `C:\Windows\System32\spool\PRINTERS`, and restart spooler.
   - Print a direct test page from the printer hardware menu.
