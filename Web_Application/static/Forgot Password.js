document.addEventListener("DOMContentLoaded", function() {
    const params = new URLSearchParams(window.location.search);
    const role = params.get('role') || 'student';
    const mode = params.get('mode') || 'forgot';

    // Set the heading dynamically
    document.getElementById('forgot-heading').textContent =
        mode === 'reset' ? 'Reset Password' : 'Forgot Password';

    // Optionally, set button text or instructions dynamically
    // Example:
    // document.querySelector('.forgot-button').textContent =
    //     mode === 'reset' ? 'Reset Password' : 'Reset Password';

    document.getElementById('back-login-link').href = `/login?role=${role}`;

    document.getElementById('toggleNewPassword').addEventListener('click', function () {
        const pwd = document.getElementById('new-password');
        const type = pwd.getAttribute('type') === 'password' ? 'text' : 'password';
        pwd.setAttribute('type', type);
        this.textContent = type === 'password' ? '\u{1F441}' : '\u{1F441}\u{200D}\u{1F5E8}';
    });
    document.getElementById('toggleConfirmPassword').addEventListener('click', function () {
        const pwd = document.getElementById('confirm-password');
        const type = pwd.getAttribute('type') === 'password' ? 'text' : 'password';
        pwd.setAttribute('type', type);
        this.textContent = type === 'password' ? '\u{1F441}' : '\u{1F441}\u{200D}\u{1F5E8}';
    });

    const instructionsDialog = document.getElementById('instructionsDialog');
    document.getElementById('closeInstructions').addEventListener('click', () => instructionsDialog.classList.remove('active'));
    document.getElementById('openInstructions').addEventListener('click', () => instructionsDialog.classList.add('active'));

    document.getElementById('forgot-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const username = document.getElementById('username').value.trim();
        const newPassword = document.getElementById('new-password').value;
        const confirmPassword = document.getElementById('confirm-password').value;
        const messageDiv = document.getElementById('forgot-message');

        if (newPassword !== confirmPassword) {
            messageDiv.textContent = "Passwords do not match.";
            return;
        }

        fetch(`/${role}/reset-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: username,
                new_password: newPassword
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
