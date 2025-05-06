// EcoWorld Military JS

console.log("Military JS loaded - Version 3.0");

document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded in military.js");
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize military power chart
    loadMilitaryPowerChart();
    
    // Set up build form handlers
    setupBuildForm();
    
    // Set up attack form handlers
    setupAttackForm();
    
    // Set up espionage form handlers
    setupEspionageForm();
    
    // Direct DOM manipulation for cost details panel
    const costDetailsDiv = document.getElementById('cost-details');
    if (costDetailsDiv) {
        console.log("Found cost details div");
        // Set a fixed content to ensure it's visible
        costDetailsDiv.innerHTML = `
            <div class="row">
                <div class="col-md-4">
                    <p style="color: lightblue;"><strong>Raw Materials:</strong> 10</p>
                </div>
                <div class="col-md-4">
                    <p style="color: yellow;"><strong>Energy:</strong> 5</p>
                </div>
                <div class="col-md-4">
                    <p style="color: lightgreen;"><strong>Currency:</strong> 100</p>
                </div>
            </div>
        `;
    } else {
        console.error("Cost details div not found");
    }
});

function loadMilitaryPowerChart() {
    const ctx = document.getElementById('military-power-chart');
    if (!ctx) return;
    
    // Get military data from page
    const offensivePower = parseFloat(document.getElementById('offensive-power').textContent);
    const defensivePower = parseFloat(document.getElementById('defensive-power').textContent);
    const espionagePower = parseFloat(document.getElementById('espionage-power').textContent);
    
    // Clear any existing chart
    if (ctx.chart) {
        ctx.chart.destroy();
    }
    
    // Create the chart
    ctx.chart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Offensive', 'Defensive', 'Espionage'],
            datasets: [{
                label: 'Military Power',
                data: [offensivePower, defensivePower, espionagePower],
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                fill: true
            }]
        },
        options: {
            responsive: true,
            scales: {
                r: {
                    angleLines: {
                        display: true
                    },
                    min: 0
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });
}

function setupBuildForm() {
    console.log("Setting up build form");
    const unitTypeSelect = document.getElementById('unit-type');
    const quantityInput = document.getElementById('build-quantity');
    const costDetailsDiv = document.getElementById('cost-details');
    const buildForm = document.getElementById('build-form');
    
    if (!unitTypeSelect || !quantityInput || !costDetailsDiv || !buildForm) {
        console.error("Missing required elements for build form:", {
            unitTypeSelect: Boolean(unitTypeSelect),
            quantityInput: Boolean(quantityInput),
            costDetailsDiv: Boolean(costDetailsDiv),
            buildForm: Boolean(buildForm)
        });
        return;
    }
    
    // Define costs for each unit type
    const unitCosts = {
        'infantry': {'raw_materials': 10, 'energy': 5, 'currency': 100},
        'tanks': {'raw_materials': 100, 'energy': 50, 'currency': 1000},
        'aircraft': {'raw_materials': 200, 'energy': 150, 'currency': 5000},
        'navy': {'raw_materials': 500, 'energy': 300, 'currency': 10000},
        'missiles': {'raw_materials': 300, 'energy': 200, 'currency': 7500},
        'bunkers': {'raw_materials': 1000, 'energy': 100, 'currency': 5000},
        'anti_air': {'raw_materials': 500, 'energy': 200, 'currency': 3000},
        'coastal_defenses': {'raw_materials': 800, 'energy': 200, 'currency': 4000},
        'spies': {'raw_materials': 0, 'energy': 50, 'currency': 2000},
        'counter_intelligence': {'raw_materials': 0, 'energy': 100, 'currency': 3000}
    };
    
    // Get resource elements safely
    const resourceElements = document.querySelectorAll('.resources-badge .badge');
    let availableResources = {
        'raw_materials': 0,
        'energy': 0,
        'currency': 0
    };
    
    // Extract resource values from the DOM
    resourceElements.forEach(element => {
        const text = element.textContent.trim();
        const value = parseFloat(text.replace(/[^0-9.-]+/g, ''));
        
        if (element.querySelector('.fa-gem')) {
            availableResources['raw_materials'] = value;
        } else if (element.querySelector('.fa-bolt')) {
            availableResources['energy'] = value;
        } else if (element.querySelector('.fa-coins')) {
            availableResources['currency'] = value;
        }
    });
    
    console.log("Available resources:", availableResources);
    
    // Update cost details when unit type or quantity changes
    function updateCostDetails() {
        const unitType = unitTypeSelect.value;
        const quantity = parseInt(quantityInput.value) || 0;
        
        console.log("Updating costs for", unitType, "quantity:", quantity);
        
        if (unitType in unitCosts) {
            const costs = unitCosts[unitType];
            
            const rawMaterialsCost = costs.raw_materials * quantity;
            const energyCost = costs.energy * quantity;
            const currencyCost = costs.currency * quantity;
            
            costDetailsDiv.innerHTML = `
                <div class="row">
                    <div class="col-md-4">
                        <p><i class="fas fa-gem text-secondary"></i> <strong>Raw Materials:</strong> ${rawMaterialsCost}</p>
                    </div>
                    <div class="col-md-4">
                        <p><i class="fas fa-bolt text-warning"></i> <strong>Energy:</strong> ${energyCost}</p>
                    </div>
                    <div class="col-md-4">
                        <p><i class="fas fa-coins text-success"></i> <strong>Currency:</strong> ${currencyCost}</p>
                    </div>
                </div>
            `;
            
            // Check if enough resources
            const canAfford = (
                rawMaterialsCost <= availableResources['raw_materials'] &&
                energyCost <= availableResources['energy'] &&
                currencyCost <= availableResources['currency']
            );
            
            const buildButton = buildForm.querySelector('button[type="submit"]');
            buildButton.disabled = !canAfford;
            
            if (!canAfford) {
                costDetailsDiv.innerHTML += `
                    <div class="alert alert-danger mt-2">
                        You don't have enough resources to build this many units.
                    </div>
                `;
            }
        }
    }
    
    unitTypeSelect.addEventListener('change', updateCostDetails);
    quantityInput.addEventListener('input', updateCostDetails);
    
    // Trigger initial update
    updateCostDetails();
    
    // Validate form before submission
    buildForm.addEventListener('submit', function(e) {
        const unitType = unitTypeSelect.value;
        const quantity = parseInt(quantityInput.value);
        
        if (!unitType || isNaN(quantity) || quantity <= 0) {
            e.preventDefault();
            alert('Please select a unit type and enter a valid quantity.');
        }
    });
}

function setupAttackForm() {
    const warSelect = document.getElementById('war-select');
    const attackTypeSelect = document.getElementById('attack-type');
    const attackDetailsDiv = document.getElementById('attack-details');
    const attackForm = document.getElementById('attack-form');
    
    if (!warSelect || !attackTypeSelect || !attackDetailsDiv || !attackForm) return;
    
    // Update attack details when war or attack type changes
    function updateAttackDetails() {
        const warOption = warSelect.options[warSelect.selectedIndex];
        const attackType = attackTypeSelect.value;
        
        if (warOption && attackType) {
            // Get the defender name from the selected option
            const defenderName = warOption.textContent.split(' - ')[1];
            
            // Get the number of units available for this attack type
            const availableUnits = parseInt(document.getElementById(`available-${attackType}`).textContent);
            
            attackDetailsDiv.innerHTML = `
                <div class="alert alert-warning">
                    <p><strong>Target:</strong> ${defenderName}</p>
                    <p><strong>Attack Type:</strong> ${attackType}</p>
                    <p><strong>Available Units:</strong> ${availableUnits}</p>
                    <p class="mb-0"><em>Warning: Attacking may result in casualties and international consequences.</em></p>
                </div>
            `;
            
            // Disable attack button if no units available
            const attackButton = attackForm.querySelector('button[type="submit"]');
            attackButton.disabled = availableUnits <= 0;
            
            if (availableUnits <= 0) {
                attackDetailsDiv.innerHTML += `
                    <div class="alert alert-danger">
                        You don't have any ${attackType} units to attack with.
                    </div>
                `;
            }
        }
    }
    
    warSelect.addEventListener('change', updateAttackDetails);
    attackTypeSelect.addEventListener('change', updateAttackDetails);
    
    // Trigger initial update if options are available
    if (warSelect.options.length > 0 && attackTypeSelect.options.length > 0) {
        updateAttackDetails();
    }
}

function setupEspionageForm() {
    const targetSelect = document.getElementById('target-nation');
    const missionTypeSelect = document.getElementById('mission-type');
    const espionageDetailsDiv = document.getElementById('espionage-details');
    const espionageForm = document.getElementById('espionage-form');
    
    if (!targetSelect || !missionTypeSelect || !espionageDetailsDiv || !espionageForm) return;
    
    // Update espionage details when target or mission type changes
    function updateEspionageDetails() {
        const targetOption = targetSelect.options[targetSelect.selectedIndex];
        const missionType = missionTypeSelect.value;
        
        if (targetOption && missionType) {
            // Get the target name from the selected option
            const targetName = targetOption.textContent;
            
            // Get the number of spies available
            const availableSpies = parseInt(document.getElementById('available-spies').textContent);
            
            // Define mission descriptions
            const missionDescriptions = {
                'gather_intel': 'Gather intelligence about the target nation\'s resources, military, and technology.',
                'sabotage_resources': 'Attempt to destroy some of the target nation\'s resources.',
                'sabotage_military': 'Attempt to damage the target nation\'s military units or defenses.'
            };
            
            espionageDetailsDiv.innerHTML = `
                <div class="alert alert-info">
                    <p><strong>Target:</strong> ${targetName}</p>
                    <p><strong>Mission:</strong> ${missionType.replace('_', ' ')}</p>
                    <p><strong>Description:</strong> ${missionDescriptions[missionType]}</p>
                    <p><strong>Available Spies:</strong> ${availableSpies}</p>
                    <p class="mb-0"><em>Warning: Failed espionage attempts may result in losing spies and diplomatic consequences.</em></p>
                </div>
            `;
            
            // Disable espionage button if no spies available
            const espionageButton = espionageForm.querySelector('button[type="submit"]');
            espionageButton.disabled = availableSpies <= 0;
            
            if (availableSpies <= 0) {
                espionageDetailsDiv.innerHTML += `
                    <div class="alert alert-danger">
                        You don't have any spies to conduct espionage.
                    </div>
                `;
            }
        }
    }
    
    targetSelect.addEventListener('change', updateEspionageDetails);
    missionTypeSelect.addEventListener('change', updateEspionageDetails);
    
    // Trigger initial update if options are available
    if (targetSelect.options.length > 0 && missionTypeSelect.options.length > 0) {
        updateEspionageDetails();
    }
}
