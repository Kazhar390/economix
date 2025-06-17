// Fonctions d'estimation
async function runCocomoEstimation() {
    const loc = document.getElementById('loc').value;
    const mode = document.getElementById('mode').value;
    
    // Remplacez toutes les occurrences comme celle-ci
    try {
        const response = await fetch('http://localhost:5000/api/estimate/cocomo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ loc, mode })
        });
        const data = await response.json();
        
        if (data.success) {
            const result = data.data;
            document.getElementById('cocomo-result').innerHTML = `
                <h4>COCOMO Results</h4>
                <p>Effort: ${result.effort} ${result.unit.effort}</p>
                <p>Duration: ${result.time} ${result.unit.time}</p>
                <p>Staff: ${result.staff} ${result.unit.staff}</p>
            `;
            document.getElementById('cocomo-result').style.display = 'block';
            renderCocomoChart(result);
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        alert("Error: " + error.message);
    }
}

// Fonctions similaires pour runFpEstimation() et runFinancialAnalysis()
async function runFpEstimation() {
    // Récupérer les valeurs des entrées externes
    const eiLow = parseInt(document.querySelector('.ei-low').value) || 0;
    const eiAverage = parseInt(document.querySelector('.ei-average').value) || 0;
    const eiHigh = parseInt(document.querySelector('.ei-high').value) || 0;
    
    // Récupérer le langage sélectionné
    const language = document.getElementById('fp-language').value;
    
    // Préparer les données pour l'API
    const data = {
        external_inputs: {
            low: eiLow,
            average: eiAverage,
            high: eiHigh
        },
        language: language
    };
    
    try {
        const response = await fetch('http://localhost:5000/api/estimate/function-points', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        
        if (result.success) {
            const fpData = result.data;
            document.getElementById('fp-result').innerHTML = `
                <h4>Function Points Results</h4>
                <p>Unadjusted Function Points: ${fpData.ufp}</p>
                <p>Adjusted Function Points: ${fpData.afp}</p>
                <p>Value Adjustment Factor: ${fpData.vaf}</p>
                <p>LOC Estimation: ${fpData.loc_estimate} (${fpData.language})</p>
            `;
            document.getElementById('fp-result').style.display = 'block';
            
            // Appel à la nouvelle fonction pour générer le graphique
            renderFpChart(fpData);
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        alert("Error: " + error.message);
    }
}

async function runFinancialAnalysis() {
    const investment = parseFloat(document.getElementById('investment').value);
    const cashflowInputs = document.querySelectorAll('.cashflow');
    const cashflows = Array.from(cashflowInputs).map(input => parseFloat(input.value));
    
    if (isNaN(investment) || cashflows.some(isNaN)) {
        alert('Please enter valid numeric values');
        return;
    }
    
    try {
        const response = await fetch('http://localhost:5000/api/financial/analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ investment, cashflows })
        });
        const result = await response.json();
        
        if (result.success) {
            const finData = result.data;
            document.getElementById('finance-result').innerHTML = `
                <h4>Financial Analysis Results</h4>
                <p>NPV (Net Present Value): ${finData.npv}</p>
                <p>IRR (Internal Rate of Return): ${finData.irr ? finData.irr + '%' : 'Not calculable'}</p>
                <p>ROI (Return on Investment): ${finData.roi}%</p>
                <p>Payback Period: ${finData.payback ? finData.payback + ' years' : 'Not calculable'}</p>
            `;
            document.getElementById('finance-result').style.display = 'block';
            
            // Appel à la fonction renderFinancialChart
            renderFinancialChart(finData);
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        alert("Error: " + error.message);
    }
}

// Fonctions auxiliaires
function addCashflowField() {
    const container = document.getElementById('cashflows-container');
    const count = container.children.length;
    const input = document.createElement('input');
    input.type = 'number';
    input.className = 'form-control mb-2 cashflow';
    input.placeholder = `Year ${count + 1}`;
    container.appendChild(input);
}

function renderCocomoChart(data) {
    const ctx = document.getElementById('cocomo-chart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Effort', 'Duration', 'Staff'],
            datasets: [{
                label: 'COCOMO Results',
                data: [data.effort, data.time, data.staff],
                backgroundColor: [
                    'rgba(54, 162, 235, 0.5)',
                    'rgba(255, 99, 132, 0.5)',
                    'rgba(75, 192, 192, 0.5)'
                ]
            }]
        }
    });
}

// Fonctions pour l'estimation heuristique
function addExpertField() {
    const container = document.getElementById('experts-container');
    const template = container.querySelector('.expert-input').cloneNode(true);
    
    // Réinitialiser les valeurs
    template.querySelectorAll('input, select').forEach(input => {
        input.value = '';
    });
    
    container.appendChild(template);
}

function addDelphiExpertField(roundNumber) {
    const container = document.getElementById(`delphi-round-${roundNumber}`);
    const template = container.querySelector('.expert-input').cloneNode(true);
    
    // Réinitialiser les valeurs
    template.querySelectorAll('input, select').forEach(input => {
        input.value = '';
    });
    
    container.appendChild(template);
}

function addDelphiRound() {
    const container = document.getElementById('delphi-rounds-container');
    const roundCount = container.children.length + 1;
    
    const roundTemplate = document.createElement('div');
    roundTemplate.className = 'card mb-3';
    roundTemplate.innerHTML = `
        <div class="card-header">Round ${roundCount}</div>
        <div class="card-body">
            <div id="delphi-round-${roundCount}" class="delphi-round">
                <div class="expert-input mb-3">
                    <div class="row">
                        <div class="col-md-4">
                            <input type="text" class="form-control expert-name" placeholder="Expert name">
                        </div>
                        <div class="col-md-4">
                            <input type="number" class="form-control expert-estimate" placeholder="Estimation">
                        </div>
                        <div class="col-md-4">
                            <select class="form-select expert-confidence">
                                <option value="">Confidence</option>
                                <option value="1">1 - Very low</option>
                                <option value="3">3 - Low</option>
                                <option value="5">5 - Medium</option>
                                <option value="7">7 - High</option>
                                <option value="10">10 - Very high</option>
                            </select>
                        </div>
                    </div>
                </div>
                <button class="btn btn-secondary btn-sm" onclick="addDelphiExpertField(${roundCount})">+ Add an expert</button>
            </div>
        </div>
    `;
    
    container.appendChild(roundTemplate);
}

async function runExpertJudgmentEstimation() {
    const expertInputs = document.querySelectorAll('#experts-container .expert-input');
    const estimates = [];
    
    expertInputs.forEach(input => {
        const name = input.querySelector('.expert-name').value;
        const estimate = parseFloat(input.querySelector('.expert-estimate').value);
        const confidence = parseInt(input.querySelector('.expert-confidence').value);
        
        if (name && !isNaN(estimate) && !isNaN(confidence)) {
            estimates.push({
                expert_name: name,
                estimate: estimate,
                confidence: confidence
            });
        }
    });
    
    if (estimates.length === 0) {
        alert('Please add at least one valid estimation');
        return;
    }
    
    try {
        const response = await fetch('http://localhost:5000/api/estimate/expert-judgment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ estimates })
        });
        const data = await response.json();
        
        if (data.success) {
            const result = data.data;
            document.getElementById('expert-result').innerHTML = `
                <h4>Expert Judgment Estimation Results</h4>
                <p>Mean estimation: ${result.statistics.mean}</p>
                <p>Median estimation: ${result.statistics.median}</p>
                <p>Confidence-weighted estimation: ${result.weighted_estimate}</p>
                <p>Standard deviation: ${result.statistics.std_dev}</p>
                <p>Range: ${result.statistics.min} - ${result.statistics.max}</p>
            `;
            document.getElementById('expert-result').style.display = 'block';
            // Supprimez cette ligne pour ne pas afficher le graphique
            // renderExpertChart(result);
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        alert("Error: " + error.message);
    }
}

async function runDelphiMethodEstimation() {
    const roundContainers = document.querySelectorAll('#delphi-rounds-container .card');
    const rounds = [];
    
    roundContainers.forEach((container, roundIndex) => {
        const roundNumber = roundIndex + 1;
        const expertInputs = document.querySelectorAll(`#delphi-round-${roundNumber} .expert-input`);
        const roundEstimates = [];
        
        expertInputs.forEach(input => {
            const name = input.querySelector('.expert-name').value;
            const estimate = parseFloat(input.querySelector('.expert-estimate').value);
            const confidence = parseInt(input.querySelector('.expert-confidence').value);
            
            if (name && !isNaN(estimate) && !isNaN(confidence)) {
                roundEstimates.push({
                    expert_name: name,
                    estimate: estimate,
                    confidence: confidence
                });
            }
        });
        
        if (roundEstimates.length > 0) {
            rounds.push(roundEstimates);
        }
    });
    
    if (rounds.length === 0) {
        alert('Please add at least one round with valid estimations');
        return;
    }
    
    try {
        const response = await fetch('http://localhost:5000/api/estimate/delphi', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rounds })
        });
        const data = await response.json();
        
        if (data.success) {
            const result = data.data;
            let roundsHtml = '';
            
            result.rounds.forEach((round, index) => {
                roundsHtml += `
                    <div class="card mb-2">
                        <div class="card-header">Round ${index + 1}</div>
                        <div class="card-body">
                            <p>Mean estimation: ${round.statistics.mean}</p>
                            <p>Weighted estimation: ${round.weighted_estimate}</p>
                            <p>Standard deviation: ${round.statistics.std_dev}</p>
                        </div>
                    </div>
                `;
            });
            
            const consensusMessage = result.consensus_reached ? 
                '<div class="alert alert-success">Consensus reached!</div>' : 
                '<div class="alert alert-warning">Consensus not reached</div>';
            
            document.getElementById('delphi-result').innerHTML = `
                <h4>Delphi Method Results</h4>
                ${consensusMessage}
                <p>Final estimation: ${result.final_estimate}</p>
                <h5>Details by round:</h5>
                ${roundsHtml}
            `;
            document.getElementById('delphi-result').style.display = 'block';
            renderDelphiConvergenceChart(result);
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        alert("Error: " + error.message);
    }
}

function renderFpChart(data) {
    const ctx = document.getElementById('fp-chart').getContext('2d');
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Unadjusted Function Points', 'Adjustment Factor'],
            datasets: [{
                data: [data.ufp, data.vaf * 100 - 100], // Convertir VAF en pourcentage d'ajustement
                backgroundColor: [
                    'rgba(54, 162, 235, 0.5)',
                    'rgba(255, 99, 132, 0.5)'
                ],
                borderColor: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 99, 132, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Function Points Breakdown'
                }
            }
        }
    });
}

function renderExpertChart(data) {
    const ctx = document.getElementById('expert-chart').getContext('2d');
    
    // Créer un graphique à barres pour les estimations
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.estimates.map(e => e.expert_name),
            datasets: [{
                label: 'Estimations',
                data: data.estimates.map(e => e.estimate),
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function renderDelphiConvergenceChart(data) {
    if (data.rounds.length <= 1) return; // Need at least 2 rounds to show convergence
    
    const ctx = document.getElementById('delphi-convergence-chart').getContext('2d');
    
    // Create a line chart to show convergence
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.rounds.map((_, index) => `Round ${index + 1}`),
            datasets: [{
                label: 'Mean estimation',
                data: data.rounds.map(round => round.statistics.mean),
                borderColor: 'rgba(54, 162, 235, 1)',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                tension: 0.1
            }, {
                label: 'Standard deviation',
                data: data.rounds.map(round => round.statistics.std_dev),
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                tension: 0.1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function renderFinancialChart(data) {
    const ctx = document.getElementById('finance-chart').getContext('2d');
    
    // Vérifier si les données cumulatives existent
    if (!data.cumulative) {
        console.error("Cumulative data not found in the response");
        return;
    }
    
    // Préparer les données pour le graphique
    const years = Array.from({ length: data.cumulative.length + 1 }, (_, i) => `Year ${i}`);
    
    // Calculer les flux de trésorerie annuels à partir des données cumulatives
    const annualCashflows = [];
    annualCashflows.push(-data.investment); // Investissement initial (négatif)
    
    for (let i = 0; i < data.cumulative.length; i++) {
        if (i === 0) {
            annualCashflows.push(data.cumulative[0]);
        } else {
            annualCashflows.push(data.cumulative[i] - data.cumulative[i-1]);
        }
    }
    
    // Créer un graphique combiné (ligne et barre)
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: years,
            datasets: [
                {
                    label: 'Cash Flow',
                    type: 'bar',
                    data: annualCashflows,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Cumulative Cash Flow',
                    type: 'line',
                    data: [-data.investment].concat(data.cumulative),
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    borderWidth: 2,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: 'Amount'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time Period'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Financial Analysis'
                }
            }
        }
    });
}