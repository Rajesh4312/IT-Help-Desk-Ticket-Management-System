// IT Help Desk Ticket Management System - Client Side Scripts

document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss alerts after 5 seconds (except danger alerts)
    const alerts = document.querySelectorAll('.alert:not(.alert-danger)');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });

    // Quick Fill Demo Credentials Helper
    const fillEmployeeBtn = document.getElementById('btn-fill-employee');
    const fillTechnicianBtn = document.getElementById('btn-fill-technician');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');

    if (fillEmployeeBtn && emailInput && passwordInput) {
        fillEmployeeBtn.addEventListener('click', function () {
            emailInput.value = 'employee@example.com';
            passwordInput.value = 'Employee@123';
        });
    }

    if (fillTechnicianBtn && emailInput && passwordInput) {
        fillTechnicianBtn.addEventListener('click', function () {
            emailInput.value = 'technician@example.com';
            passwordInput.value = 'Technician@123';
        });
    }

    // Confirmation for ticket closure
    const closeTicketForms = document.querySelectorAll('form[data-confirm-close]');
    closeTicketForms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            if (!confirm('Are you sure you want to mark this ticket as Closed? Closed tickets typically indicate completed resolutions.')) {
                e.preventDefault();
            }
        });
    });

    // Tooltips initialization
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
