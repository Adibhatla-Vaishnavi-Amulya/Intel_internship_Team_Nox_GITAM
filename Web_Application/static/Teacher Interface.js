document.getElementById('logoutBtn').addEventListener('click', function() {
    fetch('/logout', {method: 'POST'}).then(() => window.location.href = '/');
});

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

function changePassword() {
    window.location.href = "/forgot-password?mode=reset&role=teacher";
}

function viewCourses() {
    // Show courses section
    document.getElementById('courses-section').style.display = 'block';

    // Fetch subjects for dropdown
    fetch('/teacher/courses-data')
      .then(res => res.json())
      .then(data => {
        const dropdown = document.getElementById('subject-dropdown');
        dropdown.innerHTML = "";
        data.subjects.forEach(sub => {
            const opt = document.createElement('option');
            opt.value = sub;
            opt.textContent = sub;
            dropdown.appendChild(opt);
        });
        if (data.subjects.length > 0) {
            loadModuleUploadUI(data.subjects[0]);
            dropdown.value = data.subjects[0];
        }
        dropdown.onchange = function() {
            loadModuleUploadUI(this.value);
        };
      });
}

function loadModuleUploadUI(subject) {
    const uploadDiv = document.getElementById('upload-modules-container');
    uploadDiv.innerHTML = "";
    for (let i = 1; i <= 5; i++) {
        uploadDiv.innerHTML += `
          <form class="upload-form" data-subject="${subject}" data-module="${i}">
            <label>Module ${i} PDF: </label>
            <input type="file" name="pdf" accept="application/pdf" required>
            <button type="submit">Upload</button>
          </form>
          <div class="uploaded-files" id="files-${subject.replace(/\s+/g, '_')}-m${i}"></div>
        `;
    }
    document.querySelectorAll('.upload-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const subject = this.getAttribute('data-subject');
            const module_number = this.getAttribute('data-module');
            const fileInput = this.querySelector('input[type="file"]');
            if (!fileInput.files.length) return;
            const formData = new FormData();
            formData.append('subject', subject);
            formData.append('module_number', module_number);
            formData.append('pdf', fileInput.files[0]);
            fetch('/teacher/upload-module-pdf', {
                method: 'POST',
                body: formData
            })
            .then(res => res.json())
            .then(resp => {
                alert(resp.message);
                loadModuleFiles(subject, module_number);
            });
        });
    });
    for (let i = 1; i <= 5; i++) {
        loadModuleFiles(subject, i);
    }
}

function loadModuleFiles(subject, module_number) {
    fetch('/teacher/list-module-pdfs?subject=' + encodeURIComponent(subject))
        .then(res => res.json())
        .then(data => {
            const filesDiv = document.getElementById('files-' + subject.replace(/\s+/g, '_') + '-m' + module_number);
            if (filesDiv) {
                const fileName = `module${module_number}.pdf`;
                if (data.files.includes(fileName)) {
                    filesDiv.innerHTML = `<b>Uploaded:</b> ${fileName}`;
                } else {
                    filesDiv.innerHTML = `<i>No PDF uploaded yet for Module ${module_number}.</i>`;
                }
            }
        });
}

// Monitor student progress
document.addEventListener('DOMContentLoaded', function() {
    const closeBtn = document.getElementById('closeProfile');
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            document.getElementById('profileOverlay').classList.remove('active');
        });
    }
    const monitorBtn = document.getElementById('monitor-progress-btn');
    if (monitorBtn) {
        monitorBtn.addEventListener('click', function() {
            fetch('/teacher/monitor-student-progress')
              .then(res => res.json())
              .then(data => {
                let html = "<h4>Student-Subject Mapping</h4><table border='1' style='width:100%;color:#4ef0fc;'>";
                if (data.length > 0) {
                    html += "<tr>" + Object.keys(data[0]).map(col => `<th>${col}</th>`).join('') + "</tr>";
                    data.forEach(row => {
                        html += "<tr>" + Object.values(row).map(val => `<td>${val}</td>`).join('') + "</tr>";
                    });
                } else {
                    html += "<tr><td>No data</td></tr>";
                }
                html += "</table>";
                document.getElementById('student-progress-table').innerHTML = html;
              });
        });
    }
});
