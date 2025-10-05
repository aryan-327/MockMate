// Dark/Light mode toggle
const modeToggle = document.getElementById('modeToggle');
if (modeToggle) {
  modeToggle.addEventListener('click', function() {
    document.body.classList.toggle('dark-mode');
    if (document.body.classList.contains('dark-mode')) {
      modeToggle.textContent = '☀️ Light Mode';
    } else {
      modeToggle.textContent = '🌙 Dark Mode';
    }
  });
}

// Handle form submission and redirect
const setupForm = document.getElementById('setupForm');
if (setupForm) {
  setupForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const username = document.getElementById('username').value.trim();
    const company = document.getElementById('company').value.trim();
    const role = document.getElementById('role').value.trim();
    
    // Store necessary details locally for the UI (report/interview page)
    localStorage.setItem('mockmate_username', username);
    localStorage.setItem('mockmate_company', company);
    localStorage.setItem('mockmate_role', role);
    localStorage.setItem('mockmate_examDate', new Date().toLocaleDateString());
    localStorage.setItem('mockmate_enableCamera', document.getElementById('enableCamera').checked ? 'yes' : 'no');

    // Data for the backend (must match USERS table columns)
    const userData = {
        username: username,
        target_role: role,
        target_company: company,
        // CRITICAL: We must send a value for password_hash since it's NOT NULL in the DB.
        password_hash: 'default_mockmate_hash'
    };

    // Send data to backend
    fetch('http://localhost:5000/api/user', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
      // SUCCESS: Only redirect AFTER data is confirmed saved.
      console.log('User saved successfully. User ID:', data.user_id);
      window.location.href = 'interview.html';
    })
    .catch(error => {
      // ERROR HANDLING: Log the error, but still redirect to keep the app flow going.
      console.error('Error saving user data to database:', error);
      alert('Error saving user details. Please check the backend connection and log.');
      window.location.href = 'interview.html'; 
    });

    // NOTE: Removed the redundant/blocking window.location.href here.
  });
}

// Interview page: show/hide camera
if (window.location.pathname.endsWith('interview.html')) {    //ensures that it works only interview.html page
  if (localStorage.getItem('mockmate_enableCamera') === 'yes') {   
    const camera = document.getElementById('camera');
    if (camera && navigator.mediaDevices) {
      navigator.mediaDevices.getUserMedia({ video: true }) // when preference for camera is set to yes , it runs
        .then(stream => { camera.srcObject = stream; })
        .catch(() => { camera.parentElement.innerHTML = 'Camera not available.'; });
    }
  } else {
    const cameraBox = document.querySelector('.camera-box');
    if (cameraBox) cameraBox.style.display = 'none';
  }
}

// Report page: show user info
if (document.getElementById('candidateName')) {
  document.getElementById('candidateName').textContent = localStorage.getItem('mockmate_username') || '-';
}
if (document.getElementById('companyName')) {
  document.getElementById('companyName').textContent = localStorage.getItem('mockmate_company') || '-';
}
if (document.getElementById('roleName')) {
  document.getElementById('roleName').textContent = localStorage.getItem('mockmate_role') || '-';
}
if (document.getElementById('examDate')) {
  document.getElementById('examDate').textContent = localStorage.getItem('mockmate_examDate') || '-';
}
