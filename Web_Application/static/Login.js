document.addEventListener("DOMContentLoaded", function() {
    const params = new URLSearchParams(window.location.search);
    const role = params.get('role') || 'student';

    document.getElementById('login-heading').textContent = 'Login';

    document.getElementById('signup-link').href = `/signup?role=${role}`;
    document.getElementById('forgot-link').href = `/forgot-password?role=${role}`;

    const passwordInput = document.getElementById('password');
    const togglePassword = document.getElementById('togglePassword');
    togglePassword.addEventListener('click', function () {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        togglePassword.textContent = type === 'password' ? '\u{1F441}' : '\u{1F441}\u{200D}\u{1F5E8}';
    });

    const instructionsDialog = document.getElementById('instructionsDialog');
    document.getElementById('closeInstructions').addEventListener('click', () => instructionsDialog.classList.remove('active'));
    document.getElementById('openInstructions').addEventListener('click', () => instructionsDialog.classList.add('active'));

    const loginMessage = document.getElementById('login-message');

    document.querySelector('.login-container form').addEventListener('submit', function(e) {
        e.preventDefault();
        loginMessage.textContent = '';
        loginMessage.className = '';

        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;

        fetch(`/${role}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: username,
                password: password
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // Directly redirect, no message shown
                window.location.href = `/${role}/interface`;
            } else {
                loginMessage.textContent = data.message;
                loginMessage.className = 'error';
            }
        });
    });
});

// document.addEventListener("DOMContentLoaded", function() {
//     const params = new URLSearchParams(window.location.search);
//     const role = params.get('role') || 'student';

//     document.getElementById('login-heading').textContent = 'Login';

//     document.getElementById('signup-link').href = `/signup?role=${role}`;
//     document.getElementById('forgot-link').href = `/forgot-password?role=${role}`;

//     const passwordInput = document.getElementById('password');
//     const togglePassword = document.getElementById('togglePassword');
//     togglePassword.addEventListener('click', function () {
//         const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
//         passwordInput.setAttribute('type', type);
//         togglePassword.textContent = type === 'password' ? '\u{1F441}' : '\u{1F441}\u{200D}\u{1F5E8}';
//     });

//     const instructionsDialog = document.getElementById('instructionsDialog');
//     document.getElementById('closeInstructions').addEventListener('click', () => instructionsDialog.classList.remove('active'));
//     document.getElementById('openInstructions').addEventListener('click', () => instructionsDialog.classList.add('active'));

//     const loginMessage = document.getElementById('login-message');

//     document.querySelector('.login-container form').addEventListener('submit', function(e) {
//         e.preventDefault();
//         loginMessage.textContent = '';
//         loginMessage.className = '';

//         const username = document.getElementById('username').value.trim();
//         const password = document.getElementById('password').value;

//         fetch(`/${role}/login`, {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({
//                 username: username,
//                 password: password
//             })
//         })
//         .then(res => res.json())
//         .then(data => {
//             if (data.success) {
//                 loginMessage.textContent = data.message;
//                 loginMessage.className = 'success';
//                 // Redirect after a short delay (e.g., 0.8s)
//                 setTimeout(() => {
//                     window.location.href = `/${role}/interface`;
//                 }, 800);
//             } else {
//                 loginMessage.textContent = data.message;
//                 loginMessage.className = 'error';
//             }
//         });
//     });
// });

