document.getElementById('logoutBtn').addEventListener('click', function() {
    fetch('/logout', {method: 'POST'})
      .then(() => window.location.href = '/');
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
    window.location.href = "/forgot-password?mode=reset&role=student";
}

function viewCourses() {
    document.getElementById('courses-section').style.display = 'block';
    fetch('/student/courses-data')
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
            loadModulesList(data.subjects[0]);
            dropdown.value = data.subjects[0];
        }
        dropdown.onchange = function() {
            loadModulesList(this.value);
        };
      });
}

let currentModule = {subject: null, filename: null, module_number: null};

function loadModulesList(subject) {
    const modulesDiv = document.getElementById('modules-list');
    modulesDiv.innerHTML = "<h3>Modules</h3>";
    fetch('/student/list-module-pdfs?subject=' + encodeURIComponent(subject))
      .then(res => res.json())
      .then(data => {
          if (data.files.length === 0) {
              modulesDiv.innerHTML += "<i>No module PDFs uploaded for this subject yet.</i>";
              return;
          }
          data.files.forEach((file, idx) => {
              modulesDiv.innerHTML += `
                <div class="module-block">
                  <span class="module-title">Module ${idx+1}: ${file}</span>
                  <div class="module-actions">
                    <button class="module-action-btn download-btn" data-subject="${subject}" data-filename="${file}">Download</button>
                    <button class="module-action-btn chatbot-btn" data-subject="${subject}" data-filename="${file}" data-module="${idx+1}">Study with AI</button>
                  </div>
                </div>
              `;
          });
          // Attach event listeners
          document.querySelectorAll('.chatbot-btn').forEach(btn => {
              btn.addEventListener('click', function() {
                  const subject = this.getAttribute('data-subject');
                  const filename = this.getAttribute('data-filename');
                  const module_number = this.getAttribute('data-module');
                  openChatbot(subject, filename, module_number);
              });
          });
      });
}

function openChatbot(subject, filename, module_number) {
    console.log('Adding active class to #chatbot-modal');
    currentModule = {subject, filename, module_number};
    document.getElementById('chatbot-module-title').textContent = filename;
    document.getElementById('chatbot-history').innerHTML = '';
    const modal = document.getElementById('chatbot-modal');
    modal.classList.add('active');
    modal.style.display = ''; // Remove any inline display style
    console.log('Modal classes:', modal.classList, 'Modal style:', modal.style.display);
}

function downloadModule(subject, filename) {
    window.open(`/student/download-pdf?subject=${encodeURIComponent(subject)}&filename=${encodeURIComponent(filename)}`, '_blank');
}


document.getElementById('closeChatbot').onclick = function() {
    document.getElementById('chatbot-modal').classList.remove('active');
};

document.getElementById('chatbot-send-btn').onclick = function() {
    const input = document.getElementById('chatbot-input');
    const wordLimit = document.getElementById('chatbot-word-limit').value;
    const question = input.value.trim();
    if (!question) return;
    const historyDiv = document.getElementById('chatbot-history');
    historyDiv.innerHTML += `<div style="color:#00c8ff;"><b>You:</b> ${question}</div>`;
    historyDiv.innerHTML += `<div class="loading" style="color:#fff;">Thinking...</div>`;
    input.value = '';
    historyDiv.scrollTop = historyDiv.scrollHeight;
    fetch('/student/chatbot', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            subject: currentModule.subject,
            filename: currentModule.filename,
            prompt: question,
            word_limit: wordLimit
        })
    })
    .then(res => res.json())
    .then(data => {
        const loadingEl = historyDiv.querySelector('.loading');
        if (loadingEl) loadingEl.remove();
        if (data.success) {
            historyDiv.innerHTML += `<div style="color:#2bff7e;"><b>AI:</b> ${data.response}</div>`;
        } else {
            historyDiv.innerHTML += `<div style="color:#ff7373;"><b>Error:</b> ${data.message}</div>`;
        }
        historyDiv.scrollTop = historyDiv.scrollHeight;
    })
    .catch(err => {
        const loadingEl = historyDiv.querySelector('.loading');
        if (loadingEl) loadingEl.remove();
        historyDiv.innerHTML += `<div style="color:#ff7373;"><b>Error:</b> ${err.message}</div>`;
        historyDiv.scrollTop = historyDiv.scrollHeight;
    });
};



document.getElementById('chatbot-complete-btn').onclick = function() {
    if (!currentModule.subject || !currentModule.module_number) return;
    if (!confirm("Did you understand the module? Click OK to mark as complete.")) return;
    fetch('/student/mark-module-complete', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            subject: currentModule.subject,
            module_number: currentModule.module_number
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert("Module marked as complete!");
            document.getElementById('chatbot-modal').classList.remove('active');
        } else {
            alert("Error: " + data.message);
        }
    });
};

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
            fetch('/student/monitor-progress')
              .then(res => res.json())
              .then(data => {
                let html = "<h4>My Course Mapping</h4><table border='1' style='width:100%;color:#4ef0fc;'>";
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