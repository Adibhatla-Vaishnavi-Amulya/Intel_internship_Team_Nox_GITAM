document.addEventListener("DOMContentLoaded", function() {
    const params = new URLSearchParams(window.location.search);
    const role = params.get('role') || 'student';
    document.getElementById('signup-heading').textContent = 'Sign Up';

    document.getElementById('back-login-link').href = `/login?role=${role}`;

    document.getElementById('toggleSignupPassword').addEventListener('click', function () {
        const pwd = document.getElementById('signup-password');
        const type = pwd.getAttribute('type') === 'password' ? 'text' : 'password';
        pwd.setAttribute('type', type);
        this.textContent = type === 'password' ? '\u{1F441}' : '\u{1F441}\u{200D}\u{1F5E8}';
    });
    document.getElementById('toggleSignupConfirmPassword').addEventListener('click', function () {
        const pwd = document.getElementById('signup-confirm-password');
        const type = pwd.getAttribute('type') === 'password' ? 'text' : 'password';
        pwd.setAttribute('type', type);
        this.textContent = type === 'password' ? '\u{1F441}' : '\u{1F441}\u{200D}\u{1F5E8}';
    });

    const instructionsDialog = document.getElementById('instructionsDialog');
    document.getElementById('closeInstructions').addEventListener('click', () => instructionsDialog.classList.remove('active'));
    document.getElementById('openInstructions').addEventListener('click', () => instructionsDialog.classList.add('active'));

    document.getElementById('signup-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const username = document.getElementById('signup-username').value.trim();
        const email = document.getElementById('signup-email').value.trim();
        const password = document.getElementById('signup-password').value;
        const confirmPassword = document.getElementById('signup-confirm-password').value;
        const messageDiv = document.getElementById('signup-message');

        if (password !== confirmPassword) {
            messageDiv.textContent = "Passwords do not match.";
            return;
        }

        fetch(`/${role}/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password
            })
        })
        .then(res => res.json())
        .then(data => {
            messageDiv.textContent = data.message;
            // Optionally redirect on success
            // if (data.success) window.location.href = `/login?role=${role}`;
        });
    });
});


