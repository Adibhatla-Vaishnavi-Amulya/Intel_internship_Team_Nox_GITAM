// Logout button logic (keep as is)
document.getElementById('logoutBtn').addEventListener('click', function() {
    fetch('/logout', {method: 'POST'})
      .then(() => window.location.href = '/');
});

// Profile Overlay Logic
function viewProfile() {
    document.getElementById('profileOverlay').classList.add('active');
    fetch('/profile', {method: 'POST'})
      .then(res => res.json())
      .then(data => {
        const detailsDiv = document.getElementById('profile-details');
        detailsDiv.innerHTML = '';
        if (data.success) {
            const profile = data.profile;
            for (const item of profile) {
                const key = item.key;
                const value = item.value;
                detailsDiv.innerHTML += `
                  <div class="profile-row">
                    <span class="profile-key">${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</span>
                    <span class="profile-value">${value}</span>
                  </div>`;
            }
        } else {
            detailsDiv.innerHTML = `<div class="profile-row"><span class="profile-value" style="color:#ff7373">${data.message}</span></div>`;
        }
      });
}

// CSV Overlay Logic
function viewCSVFiles() {
    document.getElementById('csvOverlay').classList.add('active');
    fetch('/admin/list-csvs')
      .then(res => res.json())
      .then(data => {
        const listDiv = document.getElementById('csv-file-list');
        const tableDiv = document.getElementById('csv-table-container');
        tableDiv.innerHTML = '';
        if (data.success) {
            listDiv.innerHTML = '<ul>' + data.files.map(f =>
                `<li><button class="csv-file-btn" onclick="loadCsvFile('${f}')">${f}</button></li>`
            ).join('') + '</ul>';
        } else {
            listDiv.innerHTML = `<span style="color:#ff7373">${data.message}</span>`;
        }
      });
}

function loadCsvFile(filename) {
    fetch('/admin/get-csv', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({filename: filename})
    })
    .then(res => res.json())
    .then(data => {
        const tableDiv = document.getElementById('csv-table-container');
        if (data.success) {
            // Build table
            let html = '<table class="csv-table"><thead><tr>';
            for (const col of data.columns) {
                html += `<th>${col}</th>`;
            }
            html += '</tr></thead><tbody>';
            for (const row of data.data) {
                html += '<tr>';
                for (const col of data.columns) {
                    html += `<td>${row[col]}</td>`;
                }
                html += '</tr>';
            }
            html += '</tbody></table>';
            tableDiv.innerHTML = html;
        } else {
            tableDiv.innerHTML = `<span style="color:#ff7373">${data.message}</span>`;
        }
    });
}

// Add this function for Change Password card
function changePassword() {
    window.location.href = "/forgot-password?mode=reset&role=admin";
}

// Close overlay logic for both overlays
document.addEventListener('DOMContentLoaded', function() {
    const closeProfileBtn = document.getElementById('closeProfile');
    if (closeProfileBtn) {
        closeProfileBtn.addEventListener('click', function() {
            document.getElementById('profileOverlay').classList.remove('active');
        });
    }
    const closeCsvBtn = document.getElementById('closeCsv');
    if (closeCsvBtn) {
        closeCsvBtn.addEventListener('click', function() {
            document.getElementById('csvOverlay').classList.remove('active');
        });
    }
    // (Logout button logic is already set above)
});

