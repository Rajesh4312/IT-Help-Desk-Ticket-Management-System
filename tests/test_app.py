import unittest
from app import create_app
from models import db, User, Ticket, TicketComment


class HelpDeskTestCase(unittest.TestCase):
    """Test suite for the IT Help Desk Ticket Management System."""

    def setUp(self):
        """Set up test application, in-memory database, and test client."""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

        db.create_all()

        # Create baseline test accounts
        self.employee = User(name="Test Employee", email="test.employee@example.com", role="employee")
        self.employee.set_password("EmpPassword123")

        self.employee2 = User(name="Second Employee", email="emp2@example.com", role="employee")
        self.employee2.set_password("EmpPassword123")

        self.technician = User(name="Test Technician", email="test.technician@example.com", role="technician")
        self.technician.set_password("TechPassword123")

        db.session.add_all([self.employee, self.employee2, self.technician])
        db.session.commit()

    def tearDown(self):
        """Clean up database session and tables after each test."""
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def login(self, email, password):
        """Helper to log in a user."""
        return self.client.post('/login', data={
            'email': email,
            'password': password
        }, follow_redirects=True)

    def logout(self):
        """Helper to log out the current user."""
        return self.client.get('/logout', follow_redirects=True)

    # 1. Application starts & index routing
    def test_application_starts_and_index_redirects(self):
        """Test application starts and redirects unauthenticated user to login."""
        response = self.client.get('/', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers['Location'])

    # 2. Registration Tests
    def test_employee_registration_success(self):
        """Test new employee registration succeeds."""
        response = self.client.post('/register', data={
            'name': 'New Staff',
            'email': 'new.staff@example.com',
            'password': 'SecurePass123',
            'confirm_password': 'SecurePass123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registration successful', response.data)

        # Verify in DB
        user = User.query.filter_by(email='new.staff@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.role, 'employee')
        self.assertTrue(user.check_password('SecurePass123'))

    def test_registration_duplicate_email_prevented(self):
        """Test registration prevents duplicate email addresses."""
        response = self.client.post('/register', data={
            'name': 'Duplicate Person',
            'email': 'test.employee@example.com',
            'password': 'SecurePass123',
            'confirm_password': 'SecurePass123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'already exists', response.data)

    def test_registration_password_mismatch(self):
        """Test registration detects mismatched passwords."""
        response = self.client.post('/register', data={
            'name': 'Mismatch Person',
            'email': 'mismatch@example.com',
            'password': 'Password123',
            'confirm_password': 'WrongPassword123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Passwords do not match', response.data)

    # 3. Authentication & Sessions
    def test_valid_employee_login(self):
        """Test employee login redirects to employee dashboard."""
        response = self.login('test.employee@example.com', 'EmpPassword123')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome back, Test Employee', response.data)

    def test_valid_technician_login(self):
        """Test technician login redirects to technician dashboard."""
        response = self.login('test.technician@example.com', 'TechPassword123')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'IT Operations Dashboard', response.data)

    def test_invalid_login_credentials(self):
        """Test login fails with incorrect password."""
        response = self.login('test.employee@example.com', 'WrongPass')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email or password', response.data)

    def test_user_logout(self):
        """Test logging out clears user session."""
        self.login('test.employee@example.com', 'EmpPassword123')
        response = self.logout()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'logged out successfully', response.data)

    # 4. Role-Based Authorization
    def test_unauthenticated_access_blocked(self):
        """Test unauthenticated users cannot access protected views."""
        response = self.client.get('/employee/dashboard', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers['Location'])

        response = self.client.get('/technician/dashboard', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers['Location'])

    def test_employee_cannot_access_technician_dashboard(self):
        """Test employee receives 403 Forbidden when requesting technician console."""
        self.login('test.employee@example.com', 'EmpPassword123')
        response = self.client.get('/technician/dashboard')
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Access Denied', response.data)

    def test_technician_cannot_access_employee_create_ticket(self):
        """Test technician receives 403 when trying to access employee create ticket page."""
        self.login('test.technician@example.com', 'TechPassword123')
        response = self.client.get('/employee/tickets/create')
        self.assertEqual(response.status_code, 403)

    # 5. Ticket Creation & Employee Isolation
    def test_employee_ticket_creation(self):
        """Test employee can create a new support ticket."""
        self.login('test.employee@example.com', 'EmpPassword123')
        response = self.client.post('/employee/tickets/create', data={
            'title': 'Cannot access internal CRM',
            'description': 'Browser displays connection timed out on port 8443.',
            'category': 'Software',
            'priority': 'High'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'created successfully', response.data)

        # Check DB
        ticket = Ticket.query.filter_by(title='Cannot access internal CRM').first()
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.category, 'Software')
        self.assertEqual(ticket.priority, 'High')
        self.assertEqual(ticket.status, 'Open')
        self.assertEqual(ticket.employee_id, self.employee.id)

    def test_employee_cannot_view_another_employees_ticket(self):
        """Test employee receives 403 Forbidden when accessing another employee's ticket."""
        # Create ticket for employee 2
        ticket2 = Ticket(
            title="Private HR Ticket",
            description="Confidential HR issue description",
            category="Other",
            priority="Low",
            status="Open",
            employee_id=self.employee2.id
        )
        db.session.add(ticket2)
        db.session.commit()

        # Log in as employee 1
        self.login('test.employee@example.com', 'EmpPassword123')
        response = self.client.get(f'/employee/tickets/{ticket2.id}')
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Access Denied', response.data)

    # 6. Technician Operations & Triage
    def test_technician_ticket_assignment(self):
        """Test technician can assign a ticket to themselves."""
        ticket = Ticket(
            title="Wi-Fi disconnects on 4th floor",
            description="Detailed symptom info",
            category="Network",
            priority="Medium",
            status="Open",
            employee_id=self.employee.id
        )
        db.session.add(ticket)
        db.session.commit()

        self.login('test.technician@example.com', 'TechPassword123')
        response = self.client.post(f'/technician/tickets/{ticket.id}/assign', data={
            'technician_id': str(self.technician.id)
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        updated_ticket = db.session.get(Ticket, ticket.id)
        self.assertEqual(updated_ticket.technician_id, self.technician.id)
        self.assertEqual(updated_ticket.status, 'In Progress')

    def test_technician_change_priority_and_status(self):
        """Test changing priority and status updates ticket and logs timeline comments."""
        ticket = Ticket(
            title="Monitor display glitch",
            description="Flickering screen",
            category="Hardware",
            priority="Low",
            status="Open",
            employee_id=self.employee.id
        )
        db.session.add(ticket)
        db.session.commit()

        self.login('test.technician@example.com', 'TechPassword123')

        # Update priority to Critical
        self.client.post(f'/technician/tickets/{ticket.id}/priority', data={
            'priority': 'Critical'
        }, follow_redirects=True)

        # Update status to In Progress
        self.client.post(f'/technician/tickets/{ticket.id}/status', data={
            'status': 'In Progress'
        }, follow_redirects=True)

        updated_ticket = db.session.get(Ticket, ticket.id)
        self.assertEqual(updated_ticket.priority, 'Critical')
        self.assertEqual(updated_ticket.status, 'In Progress')
        self.assertGreaterEqual(len(updated_ticket.comments), 2)

    def test_technician_add_troubleshooting_comment(self):
        """Test adding troubleshooting note appears in timeline."""
        ticket = Ticket(
            title="Slow Ethernet",
            description="Speed test shows 1 Mbps",
            category="Network",
            priority="Medium",
            status="Open",
            employee_id=self.employee.id
        )
        db.session.add(ticket)
        db.session.commit()

        self.login('test.technician@example.com', 'TechPassword123')
        response = self.client.post(f'/technician/tickets/{ticket.id}/comment', data={
            'comment': 'Tested Cat6 cable with Fluke meter; port auto-negotiated to 10Mbps half duplex.'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Troubleshooting note added', response.data)

        comment = TicketComment.query.filter_by(ticket_id=ticket.id).first()
        self.assertIsNotNone(comment)
        self.assertIn("Fluke meter", comment.comment)

    def test_technician_resolve_ticket(self):
        """Test resolving ticket saves resolution notes and marks status Resolved."""
        ticket = Ticket(
            title="Printer paper jam",
            description="Paper jammed in tray 2",
            category="Printer",
            priority="Medium",
            status="In Progress",
            employee_id=self.employee.id,
            technician_id=self.technician.id
        )
        db.session.add(ticket)
        db.session.commit()

        self.login('test.technician@example.com', 'TechPassword123')
        response = self.client.post(f'/technician/tickets/{ticket.id}/resolve', data={
            'resolution_notes': 'Removed torn paper fragment from feed roller and wiped pickup rollers with isopropyl alcohol.',
            'target_status': 'Resolved'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'marked as Resolved with resolution notes', response.data)

        resolved_ticket = db.session.get(Ticket, ticket.id)
        self.assertEqual(resolved_ticket.status, 'Resolved')
        self.assertIn('feed roller', resolved_ticket.resolution_notes)

    # 7. Search and Filter Tests
    def test_technician_search_and_compound_filters(self):
        """Test multi-parameter search and compound filtering."""
        t1 = Ticket(title="VPN tunnel failure", description="hotel", category="Network", priority="High", status="Open", employee_id=self.employee.id)
        t2 = Ticket(title="Printer toner low", description="floor 2", category="Printer", priority="Low", status="Closed", employee_id=self.employee.id)
        t3 = Ticket(title="Blue screen BSOD on boot", description="kernel panic", category="Hardware", priority="High", status="Open", employee_id=self.employee.id)
        db.session.add_all([t1, t2, t3])
        db.session.commit()

        self.login('test.technician@example.com', 'TechPassword123')

        # Search by keyword
        resp = self.client.get('/technician/tickets?q=VPN')
        self.assertIn(b'VPN tunnel failure', resp.data)
        self.assertNotIn(b'Printer toner low', resp.data)

        # Compound filter: Status=Open AND Priority=High AND Category=Hardware
        resp = self.client.get('/technician/tickets?status=Open&priority=High&category=Hardware')
        self.assertIn(b'Blue screen BSOD on boot', resp.data)
        self.assertNotIn(b'VPN tunnel failure', resp.data)  # category is Network
        self.assertNotIn(b'Printer toner low', resp.data)


if __name__ == '__main__':
    unittest.main()
