// PropTrust v2.0 - Multi-Page Application
// Client-side routing and state management

const API_BASE = window.location.origin;

// Global state
let currentVerification = null;
let verificationHistory = [];

// ===== PAGE ROUTING =====
function showPage(pageName) {
    // Hide all pages
    document.querySelectorAll('.page-content').forEach(page => {
        page.style.display = 'none';
    });
    
    // Remove active class from all nav links
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Show selected page
    const pageElement = document.getElementById(`page-${pageName}`);
    if (pageElement) {
        pageElement.style.display = 'block';
        
        // Set active nav link
        const navLink = document.getElementById(`nav-${pageName}`);
        if (navLink) {
            navLink.classList.add('active');
        }
        
        // Load page-specific data
        if (pageName === 'dashboard') {
            loadDashboard();
        } else if (pageName === 'history') {
            loadHistory();
        } else if (pageName === 'blockchain') {
            loadBlockchainPage();
        } else if (pageName === 'settings') {
            loadSettings();
            // Update total verifications
            const totalVer = document.getElementById('total-verifications');
            if (totalVer) {
                totalVer.textContent = verificationHistory.length;
            }
        }
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// ===== DOCUMENT TYPE SELECTION =====
function selectDocType(type, element) {
    // Remove active class from all cards
    document.querySelectorAll('.doc-type-card').forEach(card => {
        card.classList.remove('active');
    });
    
    // Add active class to selected card (if not disabled)
    if (!element.classList.contains('disabled')) {
        element.classList.add('active');
        document.getElementById('documentType').value = type;
    }
}

// ===== FILE HANDLING =====
document.getElementById('fileInput').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        document.getElementById('fileName').textContent = file.name;
        document.getElementById('fileSize').textContent = formatFileSize(file.size);
        document.getElementById('filePreview').style.display = 'block';
        document.getElementById('uploadArea').style.border = '3px solid #0d6efd';
    }
});

function clearFile() {
    document.getElementById('fileInput').value = '';
    document.getElementById('filePreview').style.display = 'none';
    document.getElementById('uploadArea').style.border = '3px dashed #dee2e6';
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

// Drag & Drop
const uploadArea = document.getElementById('uploadArea');
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) {
        document.getElementById('fileInput').files = e.dataTransfer.files;
        document.getElementById('fileName').textContent = file.name;
        document.getElementById('fileSize').textContent = formatFileSize(file.size);
        document.getElementById('filePreview').style.display = 'block';
    }
});

// ===== UPLOAD FORM HANDLER =====
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fileInput = document.getElementById('fileInput');
    const documentType = document.getElementById('documentType').value;
    const storeOnBlockchain = document.getElementById('blockchainCheck').checked;
    
    if (!fileInput.files[0]) {
        alert('Please select a file');
        return;
    }
    
    // Show progress
    showProgress();
    
    try {
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('document_type', documentType);
        formData.append('store_on_blockchain', storeOnBlockchain);
        
        updateProgress(10, '📤 Uploading document...');
        
        const response = await fetch(`${API_BASE}/api/verify/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        updateProgress(30, '🔍 Running OCR extraction...');
        await sleep(500);
        updateProgress(50, '🧠 Analyzing with AI...');
        await sleep(500);
        updateProgress(70, '⚖️ Calculating risk score...');
        await sleep(500);
        updateProgress(90, '📊 Generating report...');
        
        const data = await response.json();
        
        updateProgress(100, '✅ Complete!');
        
        // Store in global state
        currentVerification = data;
        
        // Save to history
        verificationHistory.unshift({
            ...data,
            timestamp: new Date().toISOString()
        });
        localStorage.setItem('verificationHistory', JSON.stringify(verificationHistory));
        
        // Display results
        setTimeout(() => {
            hideProgress();
            displayResults(data);
        }, 500);
        
    } catch (error) {
        console.error('Error:', error);
        hideProgress();
        alert(`Error during verification: ${error.message}`);
    }
});

// ===== PROGRESS FUNCTIONS =====
function showProgress() {
    document.getElementById('progressSection').style.display = 'block';
    updateProgress(0, 'Starting...');
}

function hideProgress() {
    document.getElementById('progressSection').style.display = 'none';
}

function updateProgress(percent, text) {
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    progressBar.style.width = percent + '%';
    progressBar.textContent = percent + '%';
    progressText.textContent = text;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// ===== DISPLAY RESULTS =====
function displayResults(data) {
    // Switch to results page
    showPage('results');
    
    // Populate Overview Tab
    document.getElementById('result-propertyId').textContent = data.property_id || 'N/A';
    document.getElementById('result-riskScore').textContent = data.risk_score || 0;
    document.getElementById('result-riskLevel').textContent = data.risk_level || 'Unknown';
    
    // Set risk level badge
    const riskBadge = document.getElementById('result-riskLevel');
    riskBadge.className = 'badge ' + getRiskBadgeClass(data.risk_level);
    
    // Extracted information
    const entities = data.entities || {};
    const rtcFields = data.rtc_fields || {};
    
    document.getElementById('result-ownerName').textContent = 
        data.owner_name || rtcFields.owner_name || entities.owner_names?.[0] || entities.persons?.[0] || 'Not detected';
    document.getElementById('result-surveyNumber').textContent = 
        data.survey_number || rtcFields.survey_number || entities.survey_numbers?.[0] || 'Not detected';
    
    // Village with comprehensive fallbacks
    let village = rtcFields.village || entities.village || entities.locations?.[0] || 'Not detected';
    // Add taluk/district info if available
    if (rtcFields.taluk && village !== 'Not detected') {
        village += `, ${rtcFields.taluk}`;
    }
    if (rtcFields.district && village !== 'Not detected') {
        village += ` District`;
    }
    document.getElementById('result-village').textContent = village;
    
    document.getElementById('result-loanDetected').textContent = 
        entities.loan_present ? '⚠️ Yes' : '✅ No';
    document.getElementById('result-legalCase').textContent = 
        entities.case_numbers?.length > 0 ? '⚠️ Yes' : '✅ No';
    
    // Additional RTC Fields
    const landExtent = rtcFields.extent_acres && rtcFields.extent_guntas 
        ? `${rtcFields.extent_acres} Acres ${rtcFields.extent_guntas} Guntas`
        : rtcFields.land_extent || 'Not detected';
    document.getElementById('result-landExtent').textContent = landExtent;
    document.getElementById('result-validFrom').textContent = rtcFields.valid_from || 'Not detected';
    document.getElementById('result-validTo').textContent = rtcFields.valid_to || 'Not detected';
    document.getElementById('result-signedDate').textContent = rtcFields.digitally_signed_date || 'Not detected';
    
    // Draw risk gauge
    drawRiskGauge(data.risk_score || 0);
    
    // Populate Risk Analysis Tab
    populateRiskAnalysis(data);
    
    // Populate RTC Fields Tab
    populateRTCFields(rtcFields, entities);
    
    // Populate OCR Preview Tab
    const ocrText = data.ocr_text || data.cleaned_text || data.translated_text || 
                    data.ocr_stats?.text_preview || entities.raw_text || 'OCR text not available';
    document.getElementById('ocrTextPreview').textContent = ocrText;
    
    // Enable/disable blockchain button
    const blockchainBtn = document.getElementById('storeBlockchainBtn');
    if (data.blockchain && data.blockchain.stored) {
        blockchainBtn.disabled = true;
        blockchainBtn.innerHTML = '<i class="fas fa-check"></i> Already Stored on Blockchain';
        blockchainBtn.classList.remove('btn-primary');
        blockchainBtn.classList.add('btn-success');
    } else {
        blockchainBtn.disabled = false;
        blockchainBtn.innerHTML = '<i class="fas fa-cube"></i> Store Verification on Blockchain';
        blockchainBtn.classList.remove('btn-success');
        blockchainBtn.classList.add('btn-primary');
    }
}

function populateRiskAnalysis(data) {
    const riskAssessment = data.risk_assessment || {};
    const riskFactors = data.risk_factors || riskAssessment.risk_breakdown || {};
    const factors = riskAssessment.factors || [];
    const recommendations = riskAssessment.recommendations || [];
    
    // Risk Factors
    const factorsList = document.getElementById('riskFactorsList');
    factorsList.innerHTML = '';
    
    if (factors.length === 0) {
        factorsList.innerHTML = '<li class="list-group-item text-success"><i class="fas fa-check-circle"></i> No major risk factors detected</li>';
    } else {
        factors.forEach(factor => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.innerHTML = `<i class="fas fa-exclamation-circle text-warning"></i> ${factor.description || factor}`;
            factorsList.appendChild(li);
        });
    }
    
    // Risk Breakdown
    const breakdownContainer = document.getElementById('riskBreakdownContainer');
    breakdownContainer.innerHTML = '';
    
    if (riskFactors && Object.keys(riskFactors).length > 0) {
        Object.entries(riskFactors).forEach(([category, points]) => {
            const col = document.createElement('div');
            col.className = 'col-md-4 col-sm-6';
            
            const riskCategory = category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            const riskColor = points >= 30 ? 'danger' : points >= 15 ? 'warning' : 'success';
            
            col.innerHTML = `
                <div class="card text-center h-100">
                    <div class="card-body">
                        <h5 class="card-title">${riskCategory}</h5>
                        <h2 class="text-${riskColor} fw-bold">${points}</h2>
                        <p class="text-muted small mb-0">points</p>
                    </div>
                </div>
            `;
            breakdownContainer.appendChild(col);
        });
    } else {
        breakdownContainer.innerHTML = '<div class="col-12"><p class="text-muted text-center">No risk breakdown available</p></div>';
    }
    
    // Recommendations
    const recList = document.getElementById('recommendationsList');
    recList.innerHTML = '';
    
    if (recommendations.length === 0) {
        recList.innerHTML = '<li class="list-group-item"><i class="fas fa-check"></i> No specific recommendations</li>';
    } else {
        recommendations.forEach(rec => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.innerHTML = `<i class="fas fa-lightbulb text-info"></i> ${rec}`;
            recList.appendChild(li);
        });
    }
}

function populateRTCFields(rtcFields, entities) {
    const table = document.getElementById('rtcFieldsTable');
    table.innerHTML = '';
    
    // Helper to add a row
    const addRow = (label, value, isSectionHeader = false) => {
        if (!value || value === 'None' || value === 'null' || value === 'undefined') return;
        
        const row = table.insertRow();
        const cell1 = row.insertCell(0);
        const cell2 = row.insertCell(1);
        
        if (isSectionHeader) {
            cell1.colSpan = 2;
            cell1.innerHTML = `<strong class="text-primary fs-5"><i class="fas fa-angle-right"></i> ${label}</strong>`;
            cell1.className = 'bg-light';
        } else {
            cell1.innerHTML = `<strong>${label}</strong>`;
            cell2.innerHTML = typeof value === 'object' ? JSON.stringify(value) : value;
            cell1.style.width = '40%';
        }
    };
    
    // Basic Information Section
    addRow('📄 Basic Information', '', true);
    addRow('Document Type', rtcFields.document_type);
    addRow('Form Number', rtcFields.form_number);
    addRow('Print Page No', rtcFields.print_page_no);
    
    // Location Information
    addRow('📍 Location Details', '', true);
    addRow('Village', rtcFields.village);
    addRow('Taluk', rtcFields.taluk);
    addRow('District', rtcFields.district);
    addRow('Hobli', rtcFields.hobli);
    
    // Property Details
    addRow('🏡 Property Information', '', true);
    addRow('Owner Name', rtcFields.owner_name);
    addRow('Survey Number', rtcFields.survey_number);
    addRow('Hissa Number', rtcFields.hissa_number);
    addRow('Survey/Hissa Combined', rtcFields.survey_hissa_combined);
    addRow('Khata Number', rtcFields.khata_number);
    
    // Land Details
    addRow('📏 Land Extent', '', true);
    if (rtcFields.extent_acres || rtcFields.extent_guntas) {
        addRow('Total Extent', `${rtcFields.extent_acres || 0} Acres ${rtcFields.extent_guntas || 0} Guntas`);
    }
    addRow('Land Classification', rtcFields.land_classification);
    
    // Validity Period
    addRow('📅 Validity Period', '', true);
    addRow('Valid From', rtcFields.valid_from);
    addRow('Valid To', rtcFields.valid_to);
    addRow('Digitally Signed Date', rtcFields.digitally_signed_date);
    
    // Loan Details
    if (rtcFields.loan_details && rtcFields.loan_details.length > 0) {
        addRow('💰 Loan Details', '', true);
        rtcFields.loan_details.forEach((loan, index) => {
            const loanAmount = loan.amount || loan.amount_numeric;
            addRow(`Loan #${index + 1}`, `₹${loanAmount ? parseInt(loanAmount).toLocaleString() : 'N/A'}`);
            if (loan.bank) addRow(`  Bank`, loan.bank);
            if (loan.context) addRow(`  Context`, loan.context.substring(0, 150) + '...');
        });
    }
    
    // Mutation Records
    if (rtcFields.mutation_details && rtcFields.mutation_details.length > 0) {
        addRow('🔄 Mutation Records', '', true);
        rtcFields.mutation_details.forEach((mutation, index) => {
            addRow(`Mutation #${index + 1}`, mutation.record_number || mutation);
            if (mutation.description) addRow(`  Details`, mutation.description);
        });
    }
    
    // Extracted Entities Summary
    if (entities) {
        addRow('🔍 Extracted Entities', '', true);
        if (entities.survey_numbers?.length) {
            addRow('Survey Numbers Found', entities.survey_numbers.join(', '));
        }
        if (entities.persons?.length) {
            addRow('Persons Mentioned', entities.persons.slice(0, 5).join(', '));
        }
        if (entities.locations?.length) {
            addRow('Locations Mentioned', entities.locations.join(', '));
        }
        if (entities.dates?.length) {
            addRow('Dates Found', entities.dates.slice(0, 5).join(', '));
        }
    }
    
    // If no fields at all
    if (table.rows.length === 0) {
        addRow('No RTC fields extracted', 'Please verify the document type and quality');
    }
}

function formatFieldName(name) {
    return name
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

function getRiskBadgeClass(level) {
    if (!level) return 'bg-secondary';
    const levelLower = level.toLowerCase();
    if (levelLower.includes('low')) return 'badge-low-risk bg-success';
    if (levelLower.includes('medium')) return 'badge-medium-risk bg-warning text-dark';
    if (levelLower.includes('high')) return 'badge-high-risk bg-danger';
    return 'bg-secondary';
}

// ===== RISK GAUGE =====
function drawRiskGauge(score) {
    const canvas = document.getElementById('riskGauge');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Clear previous chart
    if (window.riskChart) {
        window.riskChart.destroy();
    }
    
    // Determine color
    let color;
    if (score <= 30) color = '#28a745';
    else if (score <= 60) color = '#ffc107';
    else color = '#dc3545';
    
    window.riskChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [score, 100 - score],
                backgroundColor: [color, '#e9ecef'],
                borderWidth: 0
            }]
        },
        options: {
            cutout: '75%',
            rotation: -90,
            circumference: 180,
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            },
            responsive: true,
            maintainAspectRatio: true
        }
    });
}

// ===== BLOCKCHAIN FUNCTIONS =====
async function storeToBlockchain() {
    if (!currentVerification) {
        alert('No verification data available');
        return;
    }
    
    const propertyId = currentVerification.property_id;
    
    if (confirm('Store this verification on blockchain? This creates an immutable record that cannot be altered.')) {
        try {
            const response = await fetch(`${API_BASE}/api/blockchain/store/${propertyId}`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Update current verification
            currentVerification.blockchain = data.blockchain;
            
            // Update in history
            const historyIndex = verificationHistory.findIndex(v => v.property_id === propertyId);
            if (historyIndex >= 0) {
                verificationHistory[historyIndex].blockchain = data.blockchain;
                localStorage.setItem('verificationHistory', JSON.stringify(verificationHistory));
            }
            
            // Show success and navigate to blockchain page
            alert('✅ Successfully stored on blockchain!');
            
            // Update blockchain page data
            updateBlockchainPage(data.blockchain, currentVerification);
            
            // Navigate to blockchain page
            showPage('blockchain');
            
        } catch (error) {
            console.error('Error:', error);
            alert(`Error storing on blockchain: ${error.message}`);
        }
    }
}

function updateBlockchainPage(blockchain, verification) {
    document.getElementById('blockchain-not-stored').style.display = 'none';
    document.getElementById('blockchain-stored').style.display = 'block';
    
    document.getElementById('bc-hash').textContent = blockchain.hash || 'N/A';
    document.getElementById('bc-txHash').textContent = blockchain.tx_hash || 'N/A';
    document.getElementById('bc-blockNumber').textContent = blockchain.block_number || 'N/A';
    document.getElementById('bc-timestamp').textContent = new Date().toLocaleString();
    
    // Store property ID for tamper check
    document.getElementById('tamperPropertyId').value = verification.property_id;
}

function loadBlockchainPage() {
    if (currentVerification && currentVerification.blockchain && currentVerification.blockchain.stored) {
        updateBlockchainPage(currentVerification.blockchain, currentVerification);
    } else {
        document.getElementById('blockchain-not-stored').style.display = 'block';
        document.getElementById('blockchain-stored').style.display = 'none';
    }
}

// ===== TAMPER CHECK =====
function showTamperCheck() {
    document.getElementById('tamperCheckSection').style.display = 'block';
    document.getElementById('tamperCheckSection').scrollIntoView({ behavior: 'smooth' });
}

function hideTamperCheck() {
    document.getElementById('tamperCheckSection').style.display = 'none';
    document.getElementById('tamperResults').style.display = 'none';
}

document.getElementById('tamperCheckForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fileInput = document.getElementById('tamperFileInput');
    const propertyId = document.getElementById('tamperPropertyId').value;
    
    if (!fileInput.files[0]) {
        alert('Please select a file');
        return;
    }
    
    // Show loading indicator
    const resultsDiv = document.getElementById('tamperResults');
    resultsDiv.style.display = 'block';
    resultsDiv.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <h5>Checking for tampering...</h5>
            <div class="progress mt-3" style="height: 25px;">
                <div id="tamperProgress" class="progress-bar progress-bar-striped progress-bar-animated" 
                     role="progressbar" style="width: 0%">0%</div>
            </div>
            <p class="text-muted mt-2" id="tamperProgressText">Initializing...</p>
        </div>
    `;
    
    // Simulate progress
    let progress = 0;
    const progressBar = document.getElementById('tamperProgress');
    const progressText = document.getElementById('tamperProgressText');
    const steps = [
        'Reading document...',
        'Extracting content...',
        'Generating hash...',
        'Comparing with blockchain...',
        'Finalizing verification...'
    ];
    
    const progressInterval = setInterval(() => {
        progress += 5;
        if (progress <= 90) {
            progressBar.style.width = progress + '%';
            progressBar.textContent = progress + '%';
            const stepIndex = Math.floor(progress / 20);
            if (steps[stepIndex]) {
                progressText.textContent = steps[stepIndex];
            }
        }
    }, 100);
    
    try {
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        
        const response = await fetch(`${API_BASE}/api/blockchain/check-tamper?property_id=${propertyId}`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Complete progress
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        progressBar.textContent = '100%';
        progressText.textContent = 'Complete!';
        
        // Show results after brief delay
        setTimeout(() => {
            displayTamperResults(data);
        }, 500);
        
    } catch (error) {
        clearInterval(progressInterval);
        console.error('Error:', error);
        resultsDiv.innerHTML = `
            <div class="alert alert-danger">
                <h5><i class="fas fa-exclamation-triangle"></i> Error</h5>
                <p>Error checking for tampering: ${error.message}</p>
            </div>
        `;
    }
});

function displayTamperResults(data) {
    const resultsDiv = document.getElementById('tamperResults');
    resultsDiv.style.display = 'block';
    
    const tamperCheck = data.tamper_check || {};
    const matchStatus = tamperCheck.match_status;
    
    let alertClass = 'alert-success';
    let icon = 'fa-check-circle';
    let message = '';
    
    if (matchStatus === 'VERIFIED') {
        message = '✅ Document is authentic and has not been tampered with!';
        alertClass = 'alert-success';
    } else if (matchStatus === 'TAMPERED') {
        message = '❌ Warning! Document has been tampered with!';
        alertClass = 'alert-danger';
        icon = 'fa-times-circle';
    } else if (matchStatus === 'NOT_FOUND') {
        message = '⚠️ No blockchain record found for this property.';
        alertClass = 'alert-warning';
        icon = 'fa-exclamation-triangle';
    } else {
        message = `Status: ${matchStatus}`;
        alertClass = 'alert-info';
    }
    
    resultsDiv.innerHTML = `
        <div class="alert ${alertClass}">
            <h5><i class="fas ${icon}"></i> Tamper Check Result</h5>
            <p>${message}</p>
        </div>
        
        <div class="table-responsive">
            <table class="table table-bordered">
                <tr>
                    <th>Hash Match</th>
                    <td>${tamperCheck.hash_matched ? '✅ Yes' : '❌ No'}</td>
                </tr>
                <tr>
                    <th>Current Hash</th>
                    <td class="font-monospace small">${(tamperCheck.current_hash || '').substring(0, 40)}...</td>
                </tr>
                <tr>
                    <th>Blockchain Hash</th>
                    <td class="font-monospace small">${(tamperCheck.blockchain_hash || '').substring(0, 40)}...</td>
                </tr>
            </table>
        </div>
    `;
}

// ===== DASHBOARD =====
function loadDashboard() {
    // Load verification history from localStorage
    const history = JSON.parse(localStorage.getItem('verificationHistory') || '[]');
    verificationHistory = history;
    
    // Update statistics
    document.getElementById('total-verifications').textContent = history.length;
    
    const lowRisk = history.filter(v => v.risk_level?.toLowerCase().includes('low')).length;
    const mediumRisk = history.filter(v => v.risk_level?.toLowerCase().includes('medium')).length;
    const blockchainCount = history.filter(v => v.blockchain?.stored).length;
    
    document.getElementById('low-risk-count').textContent = lowRisk;
    document.getElementById('medium-risk-count').textContent = mediumRisk;
    document.getElementById('blockchain-count').textContent = blockchainCount;
    
    // Update recent verifications table
    const tbody = document.getElementById('recent-verifications-table');
    tbody.innerHTML = '';
    
    if (history.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted py-5">
                    <i class="fas fa-inbox fa-3x mb-3 d-block"></i>
                    No verifications yet. <a href="#" onclick="showPage('verify')" class="text-decoration-none">Start your first verification</a>
                </td>
            </tr>
        `;
    } else {
        history.slice(0, 5).forEach(v => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${v.property_id || 'N/A'}</td>
                <td>${v.owner_name || 'N/A'}</td>
                <td><span class="badge ${getRiskBadgeClass(v.risk_level)}">${v.risk_level || 'N/A'}</span></td>
                <td>${v.blockchain?.stored ? '✅ Anchored' : '⏳ Pending'}</td>
                <td>${new Date(v.timestamp).toLocaleString()}</td>
                <td>
                    <button class="btn btn-sm btn-primary me-1" onclick="viewVerification('${v.property_id}')" title="View Details">
                        <i class="fas fa-eye"></i> View
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteVerification('${v.property_id}')" title="Delete Verification">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
        });
    }
}

// ===== HISTORY PAGE =====
function loadHistory() {
    const history = JSON.parse(localStorage.getItem('verificationHistory') || '[]');
    const tbody = document.getElementById('historyTableBody');
    tbody.innerHTML = '';
    
    if (history.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-muted py-5">
                    <i class="fas fa-inbox fa-3x mb-3 d-block"></i>
                    <p class="mb-3">No verification history yet</p>
                    <button class="btn btn-primary" onclick="showPage('verify')">
                        <i class="fas fa-plus"></i> Start Your First Verification
                    </button>
                </td>
            </tr>
        `;
    } else {
        history.forEach(v => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${v.property_id || 'N/A'}</td>
                <td>${v.owner_name || 'N/A'}</td>
                <td>${v.survey_number || 'N/A'}</td>
                <td><span class="badge ${getRiskBadgeClass(v.risk_level)}">${v.risk_level || 'N/A'}</span></td>
                <td>${v.blockchain?.stored ? '✅ Anchored' : '❌ Not Stored'}</td>
                <td>${new Date(v.timestamp).toLocaleString()}</td>
                <td>
                    <button class="btn btn-sm btn-primary me-1" onclick="viewVerification('${v.property_id}')" title="View Details">
                        <i class="fas fa-eye"></i> View
                    </button>
                    ${v.blockchain?.stored ? `
                        <button class="btn btn-sm btn-info me-1" onclick="viewBlockchainProof('${v.property_id}')" title="View Blockchain Proof">
                            <i class="fas fa-cube"></i> Proof
                        </button>
                    ` : ''}
                    <button class="btn btn-sm btn-danger" onclick="deleteVerification('${v.property_id}')" title="Delete Verification">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
        });
    }
}

function viewVerification(propertyId) {
    const verification = verificationHistory.find(v => v.property_id === propertyId);
    if (verification) {
        currentVerification = verification;
        displayResults(verification);
    }
}

function viewBlockchainProof(propertyId) {
    const verification = verificationHistory.find(v => v.property_id === propertyId);
    if (verification && verification.blockchain) {
        currentVerification = verification;
        updateBlockchainPage(verification.blockchain, verification);
        showPage('blockchain');
    }
}

// ===== DELETE VERIFICATION =====
async function deleteVerification(propertyId) {
    const verification = verificationHistory.find(v => v.property_id === propertyId);
    
    if (!verification) {
        alert('❌ Verification not found');
        return;
    }
    
    // Confirmation dialog
    const confirmMessage = `Are you sure you want to delete this verification?\n\n` +
        `Property ID: ${propertyId}\n` +
        `Owner: ${verification.owner_name || 'N/A'}\n` +
        `Survey: ${verification.survey_number || 'N/A'}\n\n` +
        `⚠️ This will permanently delete the verification from the database and cannot be undone.`;
    
    if (!confirm(confirmMessage)) {
        return;
    }
    
    try {
        // Show loading
        const loadingMsg = document.createElement('div');
        loadingMsg.id = 'delete-loading';
        loadingMsg.className = 'alert alert-info position-fixed top-0 start-50 translate-middle-x mt-3';
        loadingMsg.style.zIndex = '9999';
        loadingMsg.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Deleting verification...';
        document.body.appendChild(loadingMsg);
        
        // Delete from database
        const response = await fetch(`${API_BASE}/api/verification/${propertyId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        // Remove loading message
        document.getElementById('delete-loading')?.remove();
        
        if (response.ok && result.success) {
            // Remove from localStorage
            verificationHistory = verificationHistory.filter(v => v.property_id !== propertyId);
            localStorage.setItem('verificationHistory', JSON.stringify(verificationHistory));
            
            // Show success message
            alert(`✅ Verification ${propertyId} deleted successfully`);
            
            // Refresh the current page
            const currentPage = document.querySelector('.page-content[style*="display: block"]')?.id.replace('page-', '');
            if (currentPage === 'dashboard') {
                loadDashboard();
            } else if (currentPage === 'history') {
                loadHistory();
            }
        } else {
            throw new Error(result.message || 'Failed to delete verification');
        }
    } catch (error) {
        console.error('Delete error:', error);
        document.getElementById('delete-loading')?.remove();
        alert(`❌ Error deleting verification: ${error.message}`);
    }
}

// ===== DOWNLOAD REPORT =====
function downloadReport() {
    if (currentVerification) {
        const propertyId = currentVerification.property_id;
        window.open(`${API_BASE}/api/reports/download/${propertyId}`, '_blank');
    }
}

// ===== SETTINGS PAGE FUNCTIONS =====
function saveSettings() {
    const settings = {
        language: document.getElementById('language-select').value,
        theme: document.getElementById('theme-select').value,
        notifications: document.getElementById('notifications-check').checked,
        autoBlockchain: document.getElementById('auto-blockchain-check').checked,
        riskThreshold: document.getElementById('risk-threshold-select').value,
        ocrEngine: document.getElementById('ocr-engine-select').value,
        autoTranslate: document.getElementById('auto-translate-check').checked,
        saveHistory: document.getElementById('save-history-check').checked
    };
    
    localStorage.setItem('proptrust_settings', JSON.stringify(settings));
    
    // Show success message
    alert('✅ Settings saved successfully!');
    
    // Apply theme if changed
    applyTheme(settings.theme);
}

function loadSettings() {
    const savedSettings = localStorage.getItem('proptrust_settings');
    if (savedSettings) {
        const settings = JSON.parse(savedSettings);
        
        // Load settings into form
        document.getElementById('language-select').value = settings.language || 'en';
        document.getElementById('theme-select').value = settings.theme || 'light';
        document.getElementById('notifications-check').checked = settings.notifications !== false;
        document.getElementById('auto-blockchain-check').checked = settings.autoBlockchain || false;
        document.getElementById('risk-threshold-select').value = settings.riskThreshold || 'medium';
        document.getElementById('ocr-engine-select').value = settings.ocrEngine || 'easyocr';
        document.getElementById('auto-translate-check').checked = settings.autoTranslate !== false;
        document.getElementById('save-history-check').checked = settings.saveHistory !== false;
        
        // Apply theme
        applyTheme(settings.theme);
    }
}

function applyTheme(theme) {
    if (theme === 'dark') {
        document.body.classList.add('dark-theme');
    } else {
        document.body.classList.remove('dark-theme');
    }
}

function clearAllData() {
    if (confirm('⚠️ Are you sure you want to clear all local data? This cannot be undone.')) {
        localStorage.removeItem('proptrust_history');
        localStorage.removeItem('proptrust_settings');
        localStorage.removeItem('proptrust_current');
        
        verificationHistory = [];
        currentVerification = null;
        
        alert('🗑️ All local data has been cleared.');
        showPage('dashboard');
    }
}

function exportData() {
    const data = {
        history: verificationHistory,
        exportDate: new Date().toISOString(),
        version: '2.0'
    };
    
    const dataStr = JSON.stringify(data, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `proptrust_export_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    
    URL.revokeObjectURL(url);
}

function showTutorial() {
    alert(`📚 PropTrust Quick Tutorial

1️⃣ Dashboard: View statistics and recent verifications
2️⃣ Verify Document: Upload RTC/EC/MR/Sale Deed for AI verification
3️⃣ Results: Review AI analysis, risk factors, and extracted fields
4️⃣ Blockchain: Store verified documents on blockchain for tamper-proof records
5️⃣ History: Access all past verifications
6️⃣ Settings: Customize your preferences

💡 Tip: Store important verifications on blockchain for immutable proof!`);
}

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    // Load saved settings
    loadSettings();
    
    // Load dashboard on startup
    showPage('dashboard');
    
    // Update total verifications in settings
    const totalVer = document.getElementById('total-verifications');
    if (totalVer) {
        totalVer.textContent = verificationHistory.length;
    }
    
    console.log('PropTrust v2.0 Multi-Stage System initialized');
});
