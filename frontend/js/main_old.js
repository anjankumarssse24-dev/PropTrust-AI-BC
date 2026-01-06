// PropTrust - Main JavaScript

const API_BASE = window.location.origin;

// Upload Form Handler
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
        // Prepare form data
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('document_type', documentType);
        formData.append('store_on_blockchain', storeOnBlockchain);
        
        updateProgress(10, 'Uploading document...');
        
        // Send to API
        const response = await fetch(`${API_BASE}/api/verify/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        updateProgress(90, 'Processing results...');
        
        const data = await response.json();
        
        updateProgress(100, 'Complete!');
        
        // Display results
        setTimeout(() => {
            hideProgress();
            displayResults(data);
        }, 500);
        
    } catch (error) {
        console.error('Error:', error);
        hideProgress();
        alert(`Error: ${error.message}`);
    }
});

// Tamper Check Form Handler
document.getElementById('tamperCheckForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fileInput = document.getElementById('tamperFileInput');
    const propertyId = document.getElementById('tamperPropertyId').value;
    
    if (!fileInput.files[0]) {
        alert('Please select a file');
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('property_id', propertyId);
        
        const response = await fetch(`${API_BASE}/api/blockchain/check-tamper?property_id=${propertyId}`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        displayTamperResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        alert(`Error: ${error.message}`);
    }
});

// Display Verification Results
function displayResults(data) {
    // Hide upload form
    document.getElementById('uploadForm').reset();
    
    // Show results section
    document.getElementById('resultsSection').style.display = 'block';
    
    // Populate data
    document.getElementById('propertyId').textContent = data.property_id;
    document.getElementById('riskScore').textContent = data.risk_score;
    document.getElementById('riskLevel').textContent = data.risk_level;
    document.getElementById('riskLevel').className = `fw-bold ${getRiskLevelClass(data.risk_level)}`;
    
    // Extracted information
    const entities = data.entities || {};
    const rtcFields = data.rtc_fields || {};
    
    // Use RTC fields if available, otherwise fall back to entities
    document.getElementById('ownerName').textContent = 
        data.owner_name || rtcFields.owner_name || entities.owner_names?.[0] || entities.persons?.[0] || 'Not detected';
    document.getElementById('surveyNumber').textContent = 
        data.survey_number || rtcFields.survey_number || entities.survey_numbers?.[0] || 'Not detected';
    document.getElementById('loanDetected').textContent = 
        entities.loan_present ? '⚠️ Yes' : '✅ No';
    document.getElementById('legalCase').textContent = 
        entities.case_numbers?.length > 0 ? '⚠️ Yes' : '✅ No';
    
    // Add extended RTC fields if available
    console.log('RTC Fields:', rtcFields);
    console.log('RTC Fields keys:', Object.keys(rtcFields || {}));
    
    if (rtcFields && Object.keys(rtcFields).length > 0) {
        console.log('Calling displayExtendedRTCFields...');
        displayExtendedRTCFields(rtcFields, entities, data);
    } else {
        console.log('RTC fields not available or empty');
    }
    
    // ENHANCED BLOCKCHAIN SECTION - Show hash, block, tx even if not stored
    const blockchainSection = document.getElementById('blockchainSection');
    if (data.blockchain || data.blockchain_hash || data.verification_hash) {
        blockchainSection.style.display = 'block';
        
        // Determine blockchain data source
        const blockchain = data.blockchain || {};
        const hash = blockchain.hash || data.blockchain_hash || data.verification_hash || 'N/A';
        const txHash = blockchain.tx_hash || 'N/A';
        const blockNumber = blockchain.block_number || 'Pending';
        const stored = blockchain.stored || false;
        
        // Update blockchain info
        document.getElementById('blockchainHash').textContent = hash;
        document.getElementById('txHash').textContent = txHash;
        document.getElementById('blockNumber').textContent = blockNumber;
        
        // Add status indicator
        const statusBadge = stored 
            ? '<span class="badge bg-success">✓ Anchored</span>' 
            : '<span class="badge bg-warning">⏳ Pending</span>';
        
        // Add blockchain status if container exists
        const statusContainer = document.getElementById('blockchainStatus');
        if (statusContainer) {
            statusContainer.innerHTML = statusBadge;
        }
    } else {
        blockchainSection.style.display = 'none';
    }
    
    // Risk factors
    const riskAssessment = data.risk_assessment || {};
    const factors = riskAssessment.factors || [];
    const factorsList = document.getElementById('riskFactorsList');
    factorsList.innerHTML = '';
    
    if (factors.length === 0) {
        factorsList.innerHTML = '<li class="list-group-item">No major risk factors detected</li>';
    } else {
        factors.forEach(factor => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.innerHTML = `<i class="fas fa-exclamation-circle text-warning"></i> ${factor.description || factor}`;
            factorsList.appendChild(li);
        });
    }
    
    // Recommendations
    const recommendations = riskAssessment.recommendations || [];
    const recList = document.getElementById('recommendationsList');
    recList.innerHTML = '';
    
    if (recommendations.length === 0) {
        recList.innerHTML = '<li class="list-group-item">No specific recommendations</li>';
    } else {
        recommendations.forEach(rec => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.innerHTML = `<i class="fas fa-lightbulb text-info"></i> ${rec}`;
            recList.appendChild(li);
        });
    }
    
    // Draw risk gauge
    drawRiskGauge(data.risk_score);
    
    // Store property ID for tamper check
    document.getElementById('tamperPropertyId').value = data.property_id;
    
    // Scroll to results
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
}

// Display Tamper Check Results
function displayTamperResults(data) {
    const resultsDiv = document.getElementById('tamperResults');
    resultsDiv.style.display = 'block';
    
    const tamperCheck = data.tamper_check || {};
    const tampered = tamperCheck.tampered;
    const matchStatus = tamperCheck.match_status;
    
    let alertClass = tampered ? 'alert-danger' : 'alert-success';
    let icon = tampered ? 'fa-times-circle' : 'fa-check-circle';
    let message = '';
    
    if (matchStatus === 'VERIFIED') {
        message = '✅ Document is authentic and has not been tampered with!';
    } else if (matchStatus === 'TAMPERED') {
        message = '❌ Warning! Document has been tampered with!';
    } else if (matchStatus === 'NOT_FOUND') {
        message = '⚠️ No blockchain record found for this property.';
        alertClass = 'alert-warning';
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
            <table class="table table-sm">
                <tr>
                    <th>Hash Match</th>
                    <td>${tamperCheck.hash_matched ? '✅ Yes' : '❌ No'}</td>
                </tr>
                <tr>
                    <th>Risk Score Match</th>
                    <td>${!tamperCheck.risk_score_changed ? '✅ Yes' : '⚠️ No'}</td>
                </tr>
                <tr>
                    <th>Current Hash</th>
                    <td class="font-monospace small">${(tamperCheck.current_hash || '').substring(0, 32)}...</td>
                </tr>
                <tr>
                    <th>Blockchain Hash</th>
                    <td class="font-monospace small">${(tamperCheck.blockchain_hash || '').substring(0, 32)}...</td>
                </tr>
            </table>
        </div>
        
        ${tamperCheck.warnings && tamperCheck.warnings.length > 0 ? `
            <div class="alert alert-warning mt-3">
                <h6>Warnings:</h6>
                <ul class="mb-0">
                    ${tamperCheck.warnings.map(w => `<li>${w}</li>`).join('')}
                </ul>
            </div>
        ` : ''}
    `;
}

// Draw Risk Gauge (using Chart.js)
function drawRiskGauge(score) {
    const canvas = document.getElementById('riskGauge');
    const ctx = canvas.getContext('2d');
    
    // Clear previous chart
    if (window.riskChart) {
        window.riskChart.destroy();
    }
    
    // Determine color
    let color;
    if (score <= 30) color = '#28a745'; // Green
    else if (score <= 60) color = '#ffc107'; // Yellow
    else color = '#dc3545'; // Red
    
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
            }
        }
    });
    
    // Add score text
    ctx.fillStyle = color;
    ctx.font = 'bold 32px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(score, canvas.width / 2, canvas.height - 20);
}

// Progress Functions
function showProgress() {
    document.getElementById('progressSection').style.display = 'block';
    updateProgress(0, 'Starting...');
}

function hideProgress() {
    document.getElementById('progressSection').style.display = 'none';
}

function updateProgress(percent, text) {
    const bar = document.getElementById('progressBar');
    bar.style.width = percent + '%';
    bar.setAttribute('aria-valuenow', percent);
    document.getElementById('progressText').textContent = text;
}

// Helper Functions
function getRiskLevelClass(level) {
    if (level === 'Low') return 'text-success';
    if (level === 'Medium') return 'text-warning';
    if (level === 'High') return 'text-danger';
    return '';
}

// Display Extended RTC Fields - Matches Report Format Exactly
function displayExtendedRTCFields(rtcFields, entities, data) {
    console.log('=== displayExtendedRTCFields called ===');
    console.log('rtcFields:', rtcFields);
    console.log('entities:', entities);
    console.log('data:', data);
    
    const resultsSection = document.getElementById('resultsSection');
    console.log('resultsSection:', resultsSection);
    
    // Create extended details section if it doesn't exist
    let extendedSection = document.getElementById('extendedRTCSection');
    if (!extendedSection) {
        console.log('Creating new extendedRTCSection');
        extendedSection = document.createElement('div');
        extendedSection.id = 'extendedRTCSection';
        extendedSection.className = 'col-lg-12 mt-4';
        const rowElement = resultsSection.querySelector('.row');
        console.log('row element:', rowElement);
        if (rowElement) {
            rowElement.appendChild(extendedSection);
            console.log('Extended section appended to row');
        } else {
            console.error('No .row element found in resultsSection!');
            return;
        }
    } else {
        console.log('extendedRTCSection already exists');
    }
    
    // Get classification and OCR stats
    const classification = data.classification || {};
    const ocrStats = data.ocr_stats || {};
    
    let html = `
        <div class="card shadow mb-4">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0"><i class="fas fa-file-alt"></i> RTC Document Fields</h5>
            </div>
            <div class="card-body">
                <h6 class="text-primary"><i class="fas fa-building"></i> 🏛️ Basic Information</h6>
                <table class="table table-sm table-bordered">
                    <tr>
                        <td><strong>📍 Survey Number</strong></td>
                        <td>${rtcFields.survey_number || 'N/A'}</td>
                    </tr>
                    <tr>
                        <td><strong>📍 Hissa Number</strong></td>
                        <td>${rtcFields.hissa_number || 'N/A'}</td>
                    </tr>
                    <tr>
                        <td><strong>📍 Survey*Hissa</strong></td>
                        <td>${rtcFields.survey_hissa_combined || 'N/A'}</td>
                    </tr>
                    <tr>
                        <td><strong>Survey Number (Extracted)</strong></td>
                        <td>${rtcFields.survey_number || entities.survey_numbers?.[0] || 'N/A'}</td>
                    </tr>
                    <tr>
                        <td><strong>Land Extent</strong></td>
                        <td>${rtcFields.land_extent || 'N/A'}</td>
                    </tr>
                    <tr>
                        <td><strong>Owner Name</strong></td>
                        <td>${rtcFields.owner_name || 'N/A'}</td>
                    </tr>
                </table>
                
                <h6 class="text-primary mt-3"><i class="fas fa-calendar-alt"></i> 📅 Validity Period</h6>
                <table class="table table-sm table-bordered">
                    <tr>
                        <td><strong>Valid From</strong></td>
                        <td>${rtcFields.valid_from || 'N/A'}</td>
                    </tr>
                    <tr>
                        <td><strong>Valid To</strong></td>
                        <td>${rtcFields.valid_to || 'Till Date'}</td>
                    </tr>
                    <tr>
                        <td><strong>Digitally Signed</strong></td>
                        <td>${rtcFields.digitally_signed_date || 'N/A'}</td>
                    </tr>
                </table>
                
                ${entities.loan_amounts && entities.loan_amounts.length > 0 ? `
                <h6 class="text-danger mt-3"><i class="fas fa-exclamation-triangle"></i> 🚨 LOAN DETAILS DETECTED</h6>
                <div class="alert alert-warning">
                    ${entities.loan_amounts.map((amount, i) => `
                        <div class="mb-2">
                            <strong>💰 Loan Entry #${i + 1}</strong><br>
                            <strong>Amount:</strong> ₹ ${amount}/-<br>
                            ${entities.loan_contexts && entities.loan_contexts[i] ? `<strong>Context:</strong> ${entities.loan_contexts[i]}<br>` : ''}
                        </div>
                    `).join('')}
                </div>
                ` : ''}
                
                ${rtcFields.mutation_records && rtcFields.mutation_records.length > 0 ? `
                <h6 class="text-primary mt-3"><i class="fas fa-exchange-alt"></i> 🔄 Mutation Records</h6>
                <ul class="list-group mb-3">
                    ${rtcFields.mutation_records.map(mr => `<li class="list-group-item">${mr}</li>`).join('')}
                </ul>
                ` : ''}
                
                <h6 class="text-warning mt-3"><i class="fas fa-exclamation-circle"></i> ⚠️ Risk Assessment</h6>
                <div class="alert alert-${data.risk_level === 'Low' ? 'success' : data.risk_level === 'Medium' ? 'warning' : 'danger'}">
                    <h4><strong>${data.risk_score}/100</strong> - ${data.risk_level} RISK</h4>
                    <p>${data.risk_level === 'Low' ? '✅ Document appears to be low risk' : data.risk_level === 'Medium' ? '⚠️ Document requires additional legal review before proceeding' : '🚨 HIGH RISK - Proceed with extreme caution'}</p>
                    
                    ${data.recommendations && data.recommendations.length > 0 ? `
                    <h6 class="mt-3">📋 Recommendations:</h6>
                    <ul>
                        ${data.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                    ` : ''}
                    
                    ${data.risk_factors && Object.keys(data.risk_factors).length > 0 ? `
                    <h6 class="mt-3">⚖️ Risk Breakdown:</h6>
                    <ul class="list-unstyled">
                        ${Object.entries(data.risk_factors).map(([key, value]) => `
                            <li><strong>${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong> ${value} points</li>
                        `).join('')}
                    </ul>
                    ` : ''}
                </div>
            </div>
        </div>
        
        <div class="card shadow mb-4">
            <div class="card-header bg-secondary text-white">
                <h5 class="mb-0"><i class="fas fa-tag"></i> 📄 Document Classification</h5>
            </div>
            <div class="card-body">
                <table class="table table-sm table-bordered">
                    <tr>
                        <td><strong>Classification</strong></td>
                        <td>${classification.document_type || 'Unknown'}</td>
                    </tr>
                    <tr>
                        <td><strong>Confidence</strong></td>
                        <td>${classification.confidence ? (classification.confidence * 100).toFixed(1) + '%' : '0.0%'}</td>
                    </tr>
                </table>
                <div class="mt-2">
                    <strong>Classification Explanation:</strong><br>
                    <p class="text-muted">${classification.explanation || 'No explanation available'}</p>
                </div>
            </div>
        </div>
        
        <div class="card shadow mb-4">
            <div class="card-header bg-info text-white">
                <h5 class="mb-0"><i class="fas fa-search"></i> 🔍 Extracted Entities</h5>
            </div>
            <div class="card-body">
                <div class="row text-center mb-3">
                    <div class="col-md-3">
                        <div class="p-3 border rounded">
                            <h6>Survey Numbers</h6>
                            <h3><span class="badge bg-primary">${entities.survey_numbers?.length || 0}</span></h3>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="p-3 border rounded">
                            <h6>Banks Mentioned</h6>
                            <h3><span class="badge bg-warning">${entities.banks?.length || 0}</span></h3>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="p-3 border rounded">
                            <h6>Dates Found</h6>
                            <h3><span class="badge bg-info">${entities.dates?.length || 0}</span></h3>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="p-3 border rounded">
                            <h6>Legal Cases</h6>
                            <h3><span class="badge bg-danger">${entities.case_numbers?.length || 0}</span></h3>
                        </div>
                    </div>
                </div>
                
                ${entities.survey_numbers && entities.survey_numbers.length > 0 ? `
                <div class="mt-3">
                    <h6><strong>📍 Survey Numbers</strong></h6>
                    <ul class="list-unstyled">
                        ${entities.survey_numbers.map(num => `<li>${num}</li>`).join('')}
                    </ul>
                </div>
                ` : ''}
                
                ${entities.banks && entities.banks.length > 0 ? `
                <div class="mt-3">
                    <h6><strong>🏦 Banks</strong></h6>
                    <ul class="list-unstyled">
                        ${entities.banks.map(bank => `<li>${bank}</li>`).join('')}
                    </ul>
                </div>
                ` : ''}
            </div>
        </div>
        
        <div class="card shadow">
            <div class="card-header bg-dark text-white">
                <h5 class="mb-0"><i class="fas fa-file-invoice"></i> 📝 OCR Extraction</h5>
            </div>
            <div class="card-body">
                <table class="table table-sm table-bordered">
                    <tr>
                        <td><strong>Pages Processed</strong></td>
                        <td>${ocrStats.pages_processed || 1}</td>
                    </tr>
                    <tr>
                        <td><strong>Characters Extracted</strong></td>
                        <td>${ocrStats.chars_original || 0}</td>
                    </tr>
                    <tr>
                        <td><strong>Characters (Cleaned)</strong></td>
                        <td>${ocrStats.chars_cleaned || 0}</td>
                    </tr>
                </table>
                
                <div class="mt-3">
                    <strong>Text Quality Metrics:</strong>
                    <ul class="list-unstyled mt-2">
                        <li><strong>Original OCR:</strong> ${ocrStats.chars_original || 0} chars</li>
                        <li><strong>Cleaned Text:</strong> ${ocrStats.chars_cleaned || 0} chars</li>
                        <li><strong>Validation:</strong> ${(ocrStats.chars_cleaned > 0) ? '✅ Valid' : '❌ Empty'}</li>
                    </ul>
                </div>
                
                ${ocrStats.text_preview ? `
                <div class="mt-3">
                    <strong>Cleaned Text Preview (First 500 characters):</strong>
                    <div class="border p-2 mt-2" style="max-height: 150px; overflow-y: auto; background-color: #f8f9fa;">
                        <pre class="mb-0" style="white-space: pre-wrap; font-size: 0.85rem;">${ocrStats.text_preview}</pre>
                    </div>
                </div>
                ` : `
                <div class="mt-3">
                    <strong>Cleaned Text Preview (First 500 characters):</strong>
                    <div class="alert alert-secondary mt-2">N/A</div>
                </div>
                `}
            </div>
        </div>
        
        ${data.blockchain || data.blockchain_hash ? `
        <div class="card shadow">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0"><i class="fas fa-link"></i> 🔗 Blockchain Verification</h5>
            </div>
            <div class="card-body">
                <table class="table table-sm table-bordered">
                    <tr>
                        <td><strong>Status</strong></td>
                        <td>${data.blockchain?.stored ? '<span class="badge bg-success">✓ Anchored</span>' : '<span class="badge bg-warning">⏳ Pending</span>'}</td>
                    </tr>
                    <tr>
                        <td><strong>Verification Hash</strong></td>
                        <td><code style="font-size: 0.85rem;">${data.blockchain?.hash || data.blockchain_hash || 'Generating...'}</code></td>
                    </tr>
                    ${data.blockchain?.block_number ? `
                    <tr>
                        <td><strong>Block Number</strong></td>
                        <td>${data.blockchain.block_number}</td>
                    </tr>
                    ` : ''}
                    ${data.blockchain?.tx_hash ? `
                    <tr>
                        <td><strong>Transaction ID</strong></td>
                        <td><code style="font-size: 0.75rem;">${data.blockchain.tx_hash}</code></td>
                    </tr>
                    ` : ''}
                    <tr>
                        <td><strong>Network</strong></td>
                        <td>Ethereum (Private Testnet)</td>
                    </tr>
                    <tr>
                        <td><strong>Timestamp</strong></td>
                        <td>${data.verified_at ? new Date(data.verified_at).toLocaleString() : 'N/A'}</td>
                    </tr>
                </table>
                <div class="alert alert-info mt-3 mb-0">
                    <small><i class="fas fa-info-circle"></i> <strong>Proof of Integrity:</strong> This document's hash is cryptographically anchored on blockchain, ensuring tamper-proof verification.</small>
                </div>
            </div>
        </div>
        ` : ''}
    `;
    
    console.log('Setting innerHTML, length:', html.length);
    extendedSection.innerHTML = html;
    console.log('innerHTML set successfully');
    console.log('=== displayExtendedRTCFields complete ===');
}

function resetForm() {
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('tamperCheckSection').style.display = 'none';
    document.getElementById('uploadForm').reset();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showTamperCheck() {
    document.getElementById('tamperCheckSection').style.display = 'block';
    document.getElementById('tamperCheckSection').scrollIntoView({ behavior: 'smooth' });
}

function hideTamperCheck() {
    document.getElementById('tamperCheckSection').style.display = 'none';
    document.getElementById('tamperCheckForm').reset();
    document.getElementById('tamperResults').style.display = 'none';
}

// Check Blockchain Status
async function checkBlockchainStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/blockchain/status`);
        const data = await response.json();
        
        if (data.connected) {
            alert(`✅ Blockchain Connected\n\n` +
                  `Chain ID: ${data.chain_id}\n` +
                  `Latest Block: ${data.latest_block}\n` +
                  `Contract: ${data.contract_address}\n` +
                  `Total Verifications: ${data.total_verifications}`);
        } else {
            alert('⚠️ Blockchain not connected\n\n' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        alert('❌ Error checking blockchain status: ' + error.message);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('PropTrust initialized');
});
