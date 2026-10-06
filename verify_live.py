"""Verification script to test the complete end-to-end workflow against the live seeded database."""
from app import create_app
from models import db, User, Ticket, TicketComment

def run_verification():
    app = create_app('development')
    client = app.test_client()

    print("=== STARTING FULL END-TO-END VERIFICATION ===")

    # 1. Check Root Redirect
    res = client.get('/')
    assert res.status_code == 302, f"Expected 302, got {res.status_code}"
    print("[PASS] 1. Root route redirects correctly.")

    # 2. Login as Employee
    res = client.post('/login', data={'email': 'employee@example.com', 'password': 'Employee@123'}, follow_redirects=True)
    assert res.status_code == 200
    assert b"Alex Johnson" in res.data
    print("[PASS] 2. Employee login successful.")

    # 3. Employee Dashboard
    res = client.get('/employee/dashboard')
    assert res.status_code == 200
    assert b"My Recent Tickets" in res.data
    print("[PASS] 3. Employee dashboard rendered.")

    # 4. Create Support Ticket
    res = client.post('/employee/tickets/create', data={
        'title': 'Dual monitors flicker when docked to Dell WD19',
        'category': 'Hardware',
        'priority': 'Medium',
        'description': 'Whenever I plug my laptop into the USB-C dock, both external monitors disconnect and reconnect repeatedly.'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"created successfully" in res.data
    print("[PASS] 4. Ticket created successfully by employee.")

    # Find created ticket
    with app.app_context():
        new_ticket = Ticket.query.filter_by(title='Dual monitors flicker when docked to Dell WD19').first()
        assert new_ticket is not None
        ticket_id = new_ticket.id
        print(f"[PASS] 5. Created ticket verified in database (Ticket #{ticket_id}).")

    # 6. Verify Employee cannot access Technician console
    res = client.get('/technician/dashboard')
    assert res.status_code == 403, f"Expected 403 Forbidden, got {res.status_code}"
    print("[PASS] 6. RBAC security: Employee correctly blocked (403) from technician console.")

    # 7. Logout Employee
    client.get('/logout')

    # 8. Login as Technician
    res = client.post('/login', data={'email': 'technician@example.com', 'password': 'Technician@123'}, follow_redirects=True)
    assert res.status_code == 200
    assert b"IT Operations Dashboard" in res.data
    print("[PASS] 7. Technician login successful.")

    # 9. Search & Filter
    res = client.get('/technician/tickets?q=Dell+WD19')
    assert res.status_code == 200
    assert b"Dual monitors flicker" in res.data
    print("[PASS] 8. Multi-keyword search successfully locates ticket.")

    # 10. Technician Assigns Ticket
    with app.app_context():
        tech = User.query.filter_by(email='technician@example.com').first()
        tech_id = tech.id

    res = client.post(f'/technician/tickets/{ticket_id}/assign', data={'technician_id': str(tech_id)}, follow_redirects=True)
    assert res.status_code == 200

    with app.app_context():
        t = db.session.get(Ticket, ticket_id)
        assert t.technician_id == tech_id
        assert t.status == 'In Progress'
        print(f"[PASS] 9. Ticket #{ticket_id} assigned to technician; status transitioned to 'In Progress'.")

    # 11. Add Troubleshooting Comment
    res = client.post(f'/technician/tickets/{ticket_id}/comment', data={
        'comment': 'Updated Dell Thunderbolt Dock firmware to package 01.00.25 via Dell Command Update.'
    }, follow_redirects=True)
    assert res.status_code == 200

    with app.app_context():
        t = db.session.get(Ticket, ticket_id)
        assert any("Dell Command Update" in c.comment for c in t.comments)
        print("[PASS] 10. Troubleshooting diagnostic comment logged in timeline.")

    # 12. Resolve Ticket
    res = client.post(f'/technician/tickets/{ticket_id}/resolve', data={
        'resolution_notes': 'Reflashed dock MST hub firmware and replaced degraded DisplayPort cable. Dual display output verified stable at 60Hz.',
        'target_status': 'Resolved'
    }, follow_redirects=True)
    assert res.status_code == 200

    with app.app_context():
        t = db.session.get(Ticket, ticket_id)
        assert t.status == 'Resolved'
        assert 'Reflashed dock' in t.resolution_notes
        print("[PASS] 11. Ticket successfully resolved with root cause notes.")

    # 13. Re-login as employee and check status
    client.get('/logout')
    client.post('/login', data={'email': 'employee@example.com', 'password': 'Employee@123'}, follow_redirects=True)
    res = client.get(f'/employee/tickets/{ticket_id}')
    assert res.status_code == 200
    assert b"Reflashed dock MST hub firmware" in res.data
    assert b"Resolved" in res.data
    print("[PASS] 12. Employee verifies resolution notes on their ticket.")

    print("\n=== ALL END-TO-END VERIFICATION CHECKS PASSED (100%) ===")

if __name__ == '__main__':
    run_verification()
