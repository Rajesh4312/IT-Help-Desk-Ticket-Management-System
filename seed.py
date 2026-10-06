import os
from datetime import datetime, timezone, timedelta
from app import create_app
from models import db, User, Ticket, TicketComment


def seed_database():
    """Populate database with demo credentials and realistic IT support tickets."""
    app = create_app('development')

    with app.app_context():
        print("Cleaning existing database tables...")
        db.drop_all()
        db.create_all()

        print("Seeding demo users...")
        now = datetime.now(timezone.utc)

        # 1. Primary Demo Users
        demo_employee = User(
            name="Alex Johnson",
            email="employee@example.com",
            role="employee",
            created_at=now - timedelta(days=60)
        )
        demo_employee.set_password("Employee@123")

        demo_technician = User(
            name="Marcus Vance",
            email="technician@example.com",
            role="technician",
            created_at=now - timedelta(days=90)
        )
        demo_technician.set_password("Technician@123")

        # 2. Secondary Staff Users for Realism
        tech_sarah = User(
            name="Sarah Connor",
            email="sarah.support@example.com",
            role="technician",
            created_at=now - timedelta(days=80)
        )
        tech_sarah.set_password("Tech@123")

        emp_david = User(
            name="David Miller",
            email="david.miller@example.com",
            role="employee",
            created_at=now - timedelta(days=45)
        )
        emp_david.set_password("Employee@123")

        emp_emily = User(
            name="Emily Davis",
            email="emily.davis@example.com",
            role="employee",
            created_at=now - timedelta(days=30)
        )
        emp_emily.set_password("Employee@123")

        emp_michael = User(
            name="Michael Brown",
            email="michael.brown@example.com",
            role="employee",
            created_at=now - timedelta(days=20)
        )
        emp_michael.set_password("Employee@123")

        db.session.add_all([
            demo_employee, demo_technician, tech_sarah, 
            emp_david, emp_emily, emp_michael
        ])
        db.session.commit()

        print("Seeding realistic IT support tickets and troubleshooting history...")

        # 12 Realistic Support Tickets across all domains, priorities, and statuses
        tickets_data = [
            {
                "title": "Laptop Wi-Fi not working after office router upgrade",
                "description": "My ThinkPad T14 disconnects every 3 minutes from the corporate 'CORP-SECURE' 5GHz network. It works fine on my home Wi-Fi.",
                "category": "Network",
                "priority": "High",
                "status": "In Progress",
                "employee": demo_employee,
                "technician": demo_technician,
                "created_delta": timedelta(days=1, hours=3),
                "comments": [
                    (demo_technician, "Checked Cisco wireless controller logs. Device is failing 802.1X certificate handshake.", timedelta(hours=2)),
                    (demo_employee, "Thanks Marcus. I also noticed the Intel Wi-Fi 6 AX201 driver hasn't been updated since 2022.", timedelta(hours=1, minutes=30)),
                    (demo_technician, "Pushed corporate certificate profile update via Intune and queued driver 22.190 for deployment.", timedelta(minutes=45))
                ],
                "resolution": None
            },
            {
                "title": "Printer not responding on 3rd floor marketing bay",
                "description": "The HP LaserJet Enterprise M608 on the 3rd floor shows 'Ready' on screen, but print jobs from Windows workstations sit indefinitely in the queue.",
                "category": "Printer",
                "priority": "Medium",
                "status": "Resolved",
                "employee": emp_david,
                "technician": tech_sarah,
                "created_delta": timedelta(days=3, hours=5),
                "comments": [
                    (tech_sarah, "Remoted into print server PRINT-SRV-01. Spooler service was hung on a corrupt 120MB PDF job.", timedelta(days=3, hours=2)),
                    (tech_sarah, "Flushed print spooler cache under C:\\Windows\\System32\\spool\\PRINTERS and restarted spooler service.", timedelta(days=3, hours=1))
                ],
                "resolution": "Cleared jammed spooler queue on print server PRINT-SRV-01, restarted print spooler service, and verified test page printout successfully."
            },
            {
                "title": "Software installation request - Docker Desktop and VS Code",
                "description": "Need local Docker Desktop and Visual Studio Code installed with local admin elevation for the Q4 Data Engineering sprint.",
                "category": "Software",
                "priority": "Low",
                "status": "Closed",
                "employee": emp_emily,
                "technician": demo_technician,
                "created_delta": timedelta(days=7),
                "comments": [
                    (demo_technician, "Manager approval confirmed via ticket attachment. Deployed Docker Desktop 4.28 and VS Code via Company Portal.", timedelta(days=6, hours=20)),
                    (emp_emily, "Confirmed WSL2 integration and Docker daemon are running properly. Thank you!", timedelta(days=6, hours=15))
                ],
                "resolution": "Installed licensed Docker Desktop and VS Code through endpoint manager, verified user in docker-users group."
            },
            {
                "title": "Password reset - locked out of Workday and SSO",
                "description": "Entered wrong password three times after returning from medical leave. My Okta SSO account is now completely locked out.",
                "category": "Account/Login",
                "priority": "Critical",
                "status": "Resolved",
                "employee": emp_michael,
                "technician": demo_technician,
                "created_delta": timedelta(hours=4),
                "comments": [
                    (demo_technician, "Verified employee identity via secondary manager Slack phone call.", timedelta(hours=3, minutes=30)),
                    (demo_technician, "Unlocked Active Directory account and sent temporary one-time password to mobile.", timedelta(hours=3))
                ],
                "resolution": "Unlocked user account in Active Directory and triggered Okta self-service password reset token to verified cell phone."
            },
            {
                "title": "Outlook/email problem - Outlook crashes on startup with error 0x8004010F",
                "description": "Every time I launch Microsoft 365 Outlook, it freezes on 'Loading Profile' and crashes. Webmail works fine in Chrome.",
                "category": "Email",
                "priority": "High",
                "status": "Open",
                "employee": demo_employee,
                "technician": None,
                "created_delta": timedelta(hours=5),
                "comments": [
                    (demo_employee, "Tried launching with outlook.exe /safe, still crashes at the exact same screen.", timedelta(hours=4, minutes=30))
                ],
                "resolution": None
            },
            {
                "title": "Laptop overheating and fan running at 100% continuously",
                "description": "Dell Latitude 5530 laptop chassis is extremely hot to the touch near the vent. CPU throttles down to 0.79 GHz making typing laggy.",
                "category": "Hardware",
                "priority": "Medium",
                "status": "In Progress",
                "employee": emp_david,
                "technician": tech_sarah,
                "created_delta": timedelta(days=2),
                "comments": [
                    (tech_sarah, "Requested user bring laptop to IT Walk-in Bar at 2:00 PM for hardware inspection.", timedelta(days=1, hours=22)),
                    (tech_sarah, "Inspected fan assembly; significant dust clogging heatsink. Cleaned heatsink with compressed air and re-applied thermal paste.", timedelta(days=1, hours=18))
                ],
                "resolution": None
            },
            {
                "title": "Network connection issue in Conference Room B",
                "description": "Ethernet wall jacks B-01 and B-02 have no link lights. The Polycom conference phone and Zoom Rooms PC cannot reach the internet.",
                "category": "Network",
                "priority": "Critical",
                "status": "In Progress",
                "employee": demo_employee,
                "technician": demo_technician,
                "created_delta": timedelta(hours=8),
                "comments": [
                    (demo_technician, "Investigated IDF-2 switch cabinet. Port GigabitEthernet1/0/24 on Cisco Catalyst 3850 was in err-disabled state due to BPDU guard.", timedelta(hours=6)),
                    (demo_technician, "Re-enabled switch port and scheduled cable tester diagnostics on wall drop B-01.", timedelta(hours=5))
                ],
                "resolution": None
            },
            {
                "title": "Windows update problem - Error 0x80070002 during 23H2 patch",
                "description": "Automated monthly patch Tuesday installation failed repeatedly on workstation WS-FIN-09. System attempts reboot and rolls back.",
                "category": "Software",
                "priority": "Medium",
                "status": "Open",
                "employee": emp_emily,
                "technician": None,
                "created_delta": timedelta(days=1),
                "comments": [],
                "resolution": None
            },
            {
                "title": "Keyboard not working - several keys sticky and unresponsive",
                "description": "External USB Logitech MX Keys spacebar and Enter key do not register strokes consistently. Coffee was accidentally splashed yesterday.",
                "category": "Hardware",
                "priority": "Low",
                "status": "Closed",
                "employee": demo_employee,
                "technician": tech_sarah,
                "created_delta": timedelta(days=10),
                "comments": [
                    (tech_sarah, "Asset replaced with brand new Logitech MK270 wireless combo from IT inventory stock.", timedelta(days=9)),
                    (demo_employee, "Received new keyboard and mouse. Everything works great.", timedelta(days=9, hours=2))
                ],
                "resolution": "Issued replacement peripheral from depot inventory (Asset Tag: IT-PER-4819). Defective unit sent to e-waste recycling."
            },
            {
                "title": "VPN connection issue - GlobalProtect error 'Gateway not reachable'",
                "description": "Connecting from hotel Wi-Fi while travelling. Palo Alto GlobalProtect connects to portal but fails to establish tunnel with gateway gw-east.company.com.",
                "category": "Network",
                "priority": "High",
                "status": "Resolved",
                "employee": emp_michael,
                "technician": demo_technician,
                "created_delta": timedelta(days=4),
                "comments": [
                    (demo_technician, "Hotel Wi-Fi is blocking IPsec UDP port 4501. Configured client fallback to SSL TLS tunnel on TCP 443.", timedelta(days=3, hours=20)),
                    (emp_michael, "SSL tunnel connected immediately. Able to access internal SAP portal.", timedelta(days=3, hours=18))
                ],
                "resolution": "Enabled SSL fallback on GlobalProtect client portal for travelling personnel, successfully bypassing hotel UDP IPsec filtering."
            },
            {
                "title": "Monitor display flickers black intermittently on docking station",
                "description": "Secondary Dell 27-inch monitor flickers black for 2 seconds every few minutes when connected through the Thunderbolt dock.",
                "category": "Hardware",
                "priority": "Low",
                "status": "Open",
                "employee": emp_david,
                "technician": None,
                "created_delta": timedelta(hours=14),
                "comments": [],
                "resolution": None
            },
            {
                "title": "Shared mailbox access missing for newly joined Finance inbox",
                "description": "Please grant delegate Send-As and Read permissions to shared mailbox finance-inquiries@company.com.",
                "category": "Email",
                "priority": "Medium",
                "status": "Closed",
                "employee": demo_employee,
                "technician": demo_technician,
                "created_delta": timedelta(days=12),
                "comments": [
                    (demo_technician, "Added user to Azure AD security group 'SEC-FIN-MAILBOX-ACCESS'.", timedelta(days=11)),
                    (demo_employee, "Mailbox appeared automatically in Outlook folder tree. Thanks!", timedelta(days=11, hours=1))
                ],
                "resolution": "Delegated FullAccess and SendAs rights via Exchange Online PowerShell cmdlet Add-MailboxPermission."
            }
        ]

        for item in tickets_data:
            ticket_created_time = now - item["created_delta"]
            ticket = Ticket(
                title=item["title"],
                description=item["description"],
                category=item["category"],
                priority=item["priority"],
                status=item["status"],
                employee_id=item["employee"].id,
                technician_id=item["technician"].id if item["technician"] else None,
                resolution_notes=item["resolution"],
                created_at=ticket_created_time,
                updated_at=ticket_created_time + timedelta(hours=1)
            )
            db.session.add(ticket)
            db.session.commit()

            # Add comments
            for author, comment_text, time_after_creation in item["comments"]:
                comment_time = ticket_created_time + time_after_creation
                comment = TicketComment(
                    ticket_id=ticket.id,
                    user_id=author.id,
                    comment=comment_text,
                    created_at=comment_time
                )
                db.session.add(comment)
            db.session.commit()

        print("\n===========================================================")
        print("SEEDING COMPLETED SUCCESSFULLY!")
        print("===========================================================")
        print("DEMO CREDENTIALS:")
        print("-----------------------------------------------------------")
        print("1. IT Support Technician:")
        print("   Email:    technician@example.com")
        print("   Password: Technician@123")
        print("   Role:     technician (Full Ticket Triage & Resolution)")
        print("")
        print("2. Standard Employee:")
        print("   Email:    employee@example.com")
        print("   Password: Employee@123")
        print("   Role:     employee (Submit Tickets & View Own History)")
        print("-----------------------------------------------------------")
        print(f"Total Tickets Created: {Ticket.query.count()}")
        print(f"Total Users Created:   {User.query.count()}")
        print("===========================================================\n")


if __name__ == '__main__':
    seed_database()
