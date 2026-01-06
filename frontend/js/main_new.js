// PropTrust Frontend - Comprehensive Results Display
const API_BASE = 'http://localhost:8000';

console.log('PropTrust initialized');

// Upload Form Handler
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fileInput = document.getElementById('fileInput');
    const documentType = document.getElementById('documentType').value;
    
    if (!fileInput.files[0]) {
        alert('Please select a file');
        return;
    }
    
    // Show loading
    document.getElementById('resultsSection').innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3">Processing document... This may take a minute.</p>
        </div>
    `;
    document.getElementById('resultsSection').style.display = 'block';
    
    try {
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('document_type', documentType);
        
        const response = await fetch(`${API_BASE}/api/verify/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        displayResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('resultsSection').innerHTML = `
            <div class="alert alert-danger">
                <h4>Error</h4>
                <p>${error.message}</p>
            </div>
        `;
    }
});

// Display Comprehensive Verification Results
function displayResults(data) {
    const entities = data.entities || {};
    const classification = data.classification || {};
    const riskAssessment = data.risk_assessment || {};
    
    // Build comprehensive HTML matching report format
    const html = `
        <div class="row">
            <div class="col-12">
                <!-- Header Banner -->
                <div class="card shadow mb-3" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                    <div class="card-body text-white text-center py-4">
                        <h2 class="mb-2"><i class="fas fa-home"></i> Property Verification Report</h2>
                        <p class="mb-1">Property ID: <strong>${data.property_id}</strong></p>
                        <p class="mb-0">Generated: ${new Date().toLocaleString()}</p>
                    </div>
                </div>
                
                <!-- Survey Number Banner -->
                ${entities.survey_numbers && entities.survey_numbers[0] ? `
                <div class="alert text-center mb-3" style="font-size: 1.2em; font-weight: bold; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border: none; color: white;">
                    <i class="fas fa-map-marker-alt"></i> Survey No: ${entities.survey_numbers.join(', ')}
                </div>
                ` : ''}
                
                <!-- Owner Name Banner -->
                ${entities.persons && entities.persons[0] ? `
                <div class="alert text-center mb-3" style="font-size: 1.3em; font-weight: bold; background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); border: none; color: white;">
                    <i class="fas fa-user"></i> Property Owner: ${entities.persons[0]}
                </div>
                ` : ''}
                
                <!-- RTC Document Fields Section -->
                <div class="card shadow mb-4">
                    <div class="card-header bg-primary text-white">
                        <h4 class="mb-0"><i class="fas fa-file-alt"></i> RTC Document Fields</h4>
                    </div>
                    <div class="card-body">
                        <!-- Basic Information -->
                        <h5 class="mb-3"><i class="fas fa-info-circle"></i> Basic Information</h5>
                        <div class="row mb-4">
                            ${entities.survey_numbers ? `
                            <div class="col-md-4 mb-3">
                                <div class="card h-100 border-start border-4 border-danger">
                                    <div class="card-body">
                                        <h6 class="text-muted"><i class="fas fa-map-marker-alt"></i> Survey Number</h6>
                                        <h4 class="mb-0">${entities.survey_numbers[0]}</h4>
                                    </div>
                                </div>
                            </div>
                            ` : ''}
                            ${entities.persons ? `
                            <div class="col-md-4 mb-3">
                                <div class="card h-100 border-start border-4 border-success">
                                    <div class="card-body">
                                        <h6 class="text-muted"><i class="fas fa-user"></i> Owner Name</h6>
                                        <h5 class="mb-0">${entities.persons[0] || 'Not detected'}</h5>
                                    </div>
                                </div>
                            </div>
                            ` : ''}
                            ${entities.land_extents && entities.land_extents[0] ? `
                            <div class="col-md-4 mb-3">
                                <div class="card h-100 border-start border-4 border-info">
                                    <div class="card-body">
                                        <h6 class="text-muted"><i class="fas fa-ruler-combined"></i> Land Extent</h6>
                                        <h5 class="mb-0">${entities.land_extents[0]}</h5>
                                    </div>
                                </div>
                            </div>
                            ` : ''}
                        </div>
                        
                        <!-- Dates -->
                        ${entities.dates && entities.dates.length > 0 ? `
                        <h5 class="mb-3 mt-4"><i class="fas fa-calendar"></i> Important Dates</h5>
                        <div class="row mb-4">
                            ${entities.dates.slice(0, 3).map(date => `
                            <div class="col-md-4 mb-3">
                                <div class="card h-100">
                                    <div class="card-body">
                                        <h6 class="text-muted"><i class="fas fa-calendar-day"></i> Date</h6>
                                        <h5 class="mb-0">${date}</h5>
                                    </div>
                                </div>
                            </div>
                            `).join('')}
                        </div>
                        ` : ''}
                        
                        <!-- Loan Details -->
                        ${entities.loan_amounts && entities.loan_amounts.length > 0 ? `
                        <div class="alert alert-danger mt-4">
                            <h5 class="mb-3"><i class="fas fa-exclamation-triangle"></i> LOAN DETAILS DETECTED</h5>
                            ${entities.loan_amounts.map((amount, idx) => `
                            <div class="card mb-2 border-danger">
                                <div class="card-body">
                                    <strong><i class="fas fa-rupee-sign"></i> Loan Entry #${idx + 1}</strong><br>
                                    <strong>Amount:</strong> ₹ ${amount}/-
                                    ${entities.banks && entities.banks[idx] ? `<br><strong>Bank:</strong> ${entities.banks[idx]}` : ''}
                                </div>
                            </div>
                            `).join('')}
                        </div>
                        ` : ''}
                        
                        <!-- Case Numbers -->
                        ${entities.case_numbers && entities.case_numbers.length > 0 ? `
                        <div class="alert alert-warning mt-4">
                            <h5 class="mb-3"><i class="fas fa-gavel"></i> LEGAL CASES DETECTED</h5>
                            ${entities.case_numbers.map(caseNum => `
                            <div class="card mb-2 border-warning">
                                <div class="card-body">
                                    <strong><i class="fas fa-balance-scale"></i> Case Number:</strong> ${caseNum}
                                </div>
                            </div>
                            `).join('')}
                        </div>
                        ` : ''}
                    </div>
                </div>
                
                <!-- Risk Assessment Section -->
                <div class="card shadow mb-4">
                    <div class="card-header bg-warning">
                        <h4 class="mb-0"><i class="fas fa-shield-alt"></i> Risk Assessment</h4>
                    </div>
                    <div class="card-body">
                        <div class="text-center mb-4 p-4" style="background: linear-gradient(135deg, #ffc10722 0%, #ffc10711 100%); border-radius: 8px;">
                            <h1 style="font-size: 4em; font-weight: bold; color: ${getRiskColor(data.risk_score)};">${data.risk_score}/100</h1>
                            <h3 class="mb-3" style="color: ${getRiskColor(data.risk_score)};">${data.risk_level} RISK</h3>
                            <canvas id="riskGauge" width="300" height="150"></canvas>
                            <p class="text-muted mt-3">${riskAssessment.summary || ''}</p>
                        </div>
                        
                        <!-- Recommendations -->
                        <h5 class="mb-3"><i class="fas fa-lightbulb"></i> Recommendations:</h5>
                        ${riskAssessment.recommendations && riskAssessment.recommendations.length > 0 ? 
                            riskAssessment.recommendations.map(rec => `
                            <div class="alert alert-${getRiskAlertClass(data.risk_level)}" role="alert">
                                <i class="fas fa-arrow-right"></i> ${rec}
                            </div>
                            `).join('') 
                            : '<p class="text-muted">No specific recommendations</p>'}
                        
                        <!-- Risk Breakdown -->
                        ${riskAssessment.breakdown ? `
                        <h5 class="mb-3 mt-4"><i class="fas fa-chart-pie"></i> Risk Breakdown:</h5>
                        <div class="row">
                            <div class="col-md-3 mb-3">
                                <div class="card text-center">
                                    <div class="card-body">
                                        <h6>Loan Risk</h6>
                                        <h4 class="text-danger">${riskAssessment.breakdown.loan_risk} pts</h4>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3 mb-3">
                                <div class="card text-center">
                                    <div class="card-body">
                                        <h6>Legal Risk</h6>
                                        <h4 class="text-warning">${riskAssessment.breakdown.legal_risk} pts</h4>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3 mb-3">
                                <div class="card text-center">
                                    <div class="card-body">
                                        <h6>Mutation Risk</h6>
                                        <h4 class="text-info">${riskAssessment.breakdown.mutation_risk} pts</h4>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3 mb-3">
                                <div class="card text-center">
                                    <div class="card-body">
                                        <h6>Data Quality</h6>
                                        <h4 class="text-secondary">${riskAssessment.breakdown.data_quality_risk} pts</h4>
                                    </div>
                                </div>
                            </div>
                        </div>
                        ` : ''}
                        
                        <!-- Risk Factors List -->
                        ${riskAssessment.factors && riskAssessment.factors.length > 0 ? `
                        <h5 class="mb-3 mt-4"><i class="fas fa-exclamation-circle"></i> Risk Factors:</h5>
                        <ul class="list-group">
                            ${riskAssessment.factors.map(factor => `
                            <li class="list-group-item">
                                <i class="fas fa-exclamation-triangle text-warning"></i> ${factor}
                            </li>
                            `).join('')}
                        </ul>
                        ` : ''}
                    </div>
                </div>
                
                <!-- Blockchain Verification -->
                ${data.blockchain && data.blockchain.stored ? `
                <div class="card shadow mb-4">
                    <div class="card-header bg-info text-white">
                        <h4 class="mb-0"><i class="fas fa-cube"></i> Blockchain Verification</h4>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-success">
                            <i class="fas fa-check-circle"></i> Verification hash stored on blockchain!
                        </div>
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <tr>
                                    <th>Hash</th>
                                    <td class="font-monospace small">${data.blockchain.hash || 'N/A'}</td>
                                </tr>
                                <tr>
                                    <th>Transaction Hash</th>
                                    <td class="font-monospace small">${data.blockchain.tx_hash || 'N/A'}</td>
                                </tr>
                                <tr>
                                    <th>Block Number</th>
                                    <td>${data.blockchain.block_number || 'N/A'}</td>
                                </tr>
                            </table>
                        </div>
                    </div>
                </div>
                ` : ''}
                
                <!-- Classification Details -->
                ${classification.label ? `
                <div class="card shadow mb-4">
                    <div class="card-header bg-secondary text-white">
                        <h4 class="mb-0"><i class="fas fa-tags"></i> Document Classification</h4>
                    </div>
                    <div class="card-body">
                        <h5><span class="badge bg-${getClassificationColor(classification.label)}">${classification.label}</span></h5>
                        <p class="text-muted">${classification.explanation || ''}</p>
                        ${classification.reasoning ? `<p><strong>Reasoning:</strong> ${classification.reasoning}</p>` : ''}
                    </div>
                </div>
                ` : ''}
            </div>
        </div>
    `;
    
    document.getElementById('resultsSection').innerHTML = html;
    document.getElementById('resultsSection').style.display = 'block';
    
    // Draw risk gauge
    setTimeout(() => drawRiskGauge(data.risk_score, data.risk_level), 100);
    
    // Scroll to results
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
}

// Helper functions
function getRiskColor(score) {
    if (score < 30) return '#28a745';
    if (score < 60) return '#ffc107';
    return '#dc3545';
}

function getRiskAlertClass(level) {
    if (level === 'Low') return 'success';
    if (level === 'Medium') return 'warning';
    return 'danger';
}

function getClassificationColor(label) {
    if (label.includes('Clear')) return 'success';
    if (label.includes('Loan')) return 'warning';
    if (label.includes('Court') || label.includes('Forgery')) return 'danger';
    return 'secondary';
}

// Draw Risk Gauge using Chart.js
function drawRiskGauge(score, level) {
    const canvas = document.getElementById('riskGauge');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [score, 100 - score],
                backgroundColor: [
                    getRiskColor(score),
                    '#e0e0e0'
                ],
                borderWidth: 0
            }]
        },
        options: {
            circumference: 180,
            rotation: 270,
            cutout: '75%',
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                }
            }
        }
    });
}
