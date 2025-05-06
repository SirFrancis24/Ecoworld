// EcoWorld Population JS

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize population distribution chart
    loadPopulationChart();
    
    // Setup population distribution form
    setupPopulationForm();
});

function loadPopulationChart() {
    const ctx = document.getElementById('population-chart');
    if (!ctx) return;
    
    // Get population distribution from the form
    const agriculture = parseFloat(document.getElementById('agriculture').value) || 0;
    const industry = parseFloat(document.getElementById('industry').value) || 0;
    const energy = parseFloat(document.getElementById('energy').value) || 0;
    const research = parseFloat(document.getElementById('research').value) || 0;
    const military = parseFloat(document.getElementById('military').value) || 0;
    
    // Clear any existing chart
    if (ctx.chart) {
        ctx.chart.destroy();
    }
    
    // Create the chart
    ctx.chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Agriculture', 'Industry', 'Energy', 'Research', 'Military'],
            datasets: [{
                data: [agriculture, industry, energy, research, military],
                backgroundColor: [
                    'rgba(0, 128, 0, 0.7)',    // Agriculture - Green
                    'rgba(102, 51, 153, 0.7)', // Industry - Purple
                    'rgba(255, 165, 0, 0.7)',  // Energy - Orange
                    'rgba(0, 0, 255, 0.7)',    // Research - Blue
                    'rgba(255, 0, 0, 0.7)'     // Military - Red
                ],
                borderColor: [
                    'rgba(0, 128, 0, 1)',
                    'rgba(102, 51, 153, 1)',
                    'rgba(255, 165, 0, 1)',
                    'rgba(0, 0, 255, 1)',
                    'rgba(255, 0, 0, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            return `${label}: ${value}%`;
                        }
                    }
                }
            }
        }
    });
}

function setupPopulationForm() {
    const populationForm = document.getElementById('population-form');
    if (!populationForm) return;
    
    // Main form elements
    const agricultureInput = document.getElementById('agriculture');
    const industryInput = document.getElementById('industry');
    const energyInput = document.getElementById('energy');
    const researchInput = document.getElementById('research');
    const militaryInput = document.getElementById('military');
    
    // Direct numeric inputs
    const agricultureDirectInput = document.getElementById('agriculture-direct');
    const industryDirectInput = document.getElementById('industry-direct');
    const energyDirectInput = document.getElementById('energy-direct');
    const researchDirectInput = document.getElementById('research-direct');
    const militaryDirectInput = document.getElementById('military-direct');
    
    // Display elements
    const totalPopulationElement = document.getElementById('total-population');
    const totalDisplayElement = document.getElementById('total-display');
    const agricultureValueElement = document.getElementById('agriculture-value');
    const industryValueElement = document.getElementById('industry-value');
    const energyValueElement = document.getElementById('energy-value');
    const researchValueElement = document.getElementById('research-value');
    const militaryValueElement = document.getElementById('military-value');
    
    // Auto-balance button
    const autoBalanceButton = document.getElementById('auto-balance');
    
    // Last modified input for auto-balancing
    let lastModifiedInput = null;
    
    // Function to sync a range input with its direct input counterpart
    function syncRangeWithDirect(rangeInput, directInput, valueElement) {
        const value = parseFloat(rangeInput.value) || 0;
        directInput.value = value.toFixed(1);
        if (valueElement) {
            valueElement.textContent = value.toFixed(1);
        }
    }
    
    // Function to sync a direct input with its range counterpart
    function syncDirectWithRange(directInput, rangeInput, valueElement) {
        let value = parseFloat(directInput.value) || 0;
        
        // Ensure value is within bounds
        value = Math.max(0, Math.min(100, value));
        
        // Update direct input and range input
        directInput.value = value.toFixed(1);
        rangeInput.value = value;
        
        if (valueElement) {
            valueElement.textContent = value.toFixed(1);
        }
    }
    
    // Function to update the total percentage
    function updateTotal() {
        const agriculture = parseFloat(agricultureInput.value) || 0;
        const industry = parseFloat(industryInput.value) || 0;
        const energy = parseFloat(energyInput.value) || 0;
        const research = parseFloat(researchInput.value) || 0;
        const military = parseFloat(militaryInput.value) || 0;
        
        // Calculate total
        const total = agriculture + industry + energy + research + military;
        
        // Update display elements
        if (totalPopulationElement) {
            totalPopulationElement.textContent = total.toFixed(1);
        }
        if (totalDisplayElement) {
            totalDisplayElement.textContent = total.toFixed(1) + '%';
            
            // Update status class
            if (Math.abs(total - 100) < 0.1) { // Allow a small margin of error for floating point
                totalDisplayElement.classList.remove('bg-danger');
                totalDisplayElement.classList.add('bg-success');
            } else {
                totalDisplayElement.classList.remove('bg-success');
                totalDisplayElement.classList.add('bg-danger');
            }
        }
        
        // Sync display values with inputs
        syncRangeWithDirect(agricultureInput, agricultureDirectInput, agricultureValueElement);
        syncRangeWithDirect(industryInput, industryDirectInput, industryValueElement);
        syncRangeWithDirect(energyInput, energyDirectInput, energyValueElement);
        syncRangeWithDirect(researchInput, researchDirectInput, researchValueElement);
        syncRangeWithDirect(militaryInput, militaryDirectInput, militaryValueElement);
        
        // Update the chart
        loadPopulationChart();
        
        // Update production estimates
        updateProductionEstimates();
    }
    
    // Function to auto-balance the distribution to exactly 100%
    function autoBalance() {
        const agriculture = parseFloat(agricultureInput.value) || 0;
        const industry = parseFloat(industryInput.value) || 0;
        const energy = parseFloat(energyInput.value) || 0;
        const research = parseFloat(researchInput.value) || 0;
        const military = parseFloat(militaryInput.value) || 0;
        
        const total = agriculture + industry + energy + research + military;
        const difference = 100 - total;
        
        // If already at 100%, no need to adjust
        if (Math.abs(difference) < 0.1) {
            return;
        }
        
        // Choose which input to adjust based on last modified or largest value
        let inputToAdjust;
        
        if (lastModifiedInput && document.getElementById(lastModifiedInput)) {
            // Adjust the last modified input
            inputToAdjust = document.getElementById(lastModifiedInput);
        } else {
            // Find the input with the largest value
            const values = [
                { id: 'agriculture', value: agriculture },
                { id: 'industry', value: industry },
                { id: 'energy', value: energy },
                { id: 'research', value: research },
                { id: 'military', value: military }
            ];
            
            // Sort by value, largest first
            values.sort((a, b) => b.value - a.value);
            inputToAdjust = document.getElementById(values[0].id);
        }
        
        // Adjust the chosen input
        if (inputToAdjust) {
            const currentValue = parseFloat(inputToAdjust.value) || 0;
            const newValue = Math.max(0, Math.min(100, currentValue + difference));
            inputToAdjust.value = newValue.toFixed(1);
            
            // Update the corresponding direct input
            const directInputId = inputToAdjust.id + '-direct';
            const directInput = document.getElementById(directInputId);
            if (directInput) {
                directInput.value = newValue.toFixed(1);
            }
            
            // Update the display value
            const valueElementId = inputToAdjust.id + '-value';
            const valueElement = document.getElementById(valueElementId);
            if (valueElement) {
                valueElement.textContent = newValue.toFixed(1);
            }
        }
        
        // Update everything
        updateTotal();
    }
    
    // Function to update production estimates
    function updateProductionEstimates() {
        const agriculture = parseFloat(agricultureInput.value) || 0;
        const industry = parseFloat(industryInput.value) || 0;
        const energy = parseFloat(energyInput.value) || 0;
        const research = parseFloat(researchInput.value) || 0;
        
        // Simple estimate calculations - in a real implementation, these would be more complex
        // and would factor in technology, nation size, etc.
        const foodProduction = agriculture * 10;
        const rawMaterialsProduction = industry * 10;
        const energyProduction = energy * 10;
        const technologyProduction = research * 2;
        
        // Update the DOM
        document.getElementById('food-production-estimate').textContent = foodProduction.toFixed(0);
        document.getElementById('raw-materials-production-estimate').textContent = rawMaterialsProduction.toFixed(0);
        document.getElementById('energy-production-estimate').textContent = energyProduction.toFixed(0);
        document.getElementById('technology-production-estimate').textContent = technologyProduction.toFixed(0);
    }
    
    // Setup range inputs to track last modified
    [agricultureInput, industryInput, energyInput, researchInput, militaryInput].forEach(input => {
        input.addEventListener('input', function() {
            lastModifiedInput = this.id;
            syncRangeWithDirect(this, document.getElementById(this.id + '-direct'), document.getElementById(this.id + '-value'));
            updateTotal();
        });
    });
    
    // Setup direct inputs
    [agricultureDirectInput, industryDirectInput, energyDirectInput, researchDirectInput, militaryDirectInput].forEach(input => {
        const baseId = input.id.replace('-direct', '');
        const rangeInput = document.getElementById(baseId);
        const valueElement = document.getElementById(baseId + '-value');
        
        input.addEventListener('input', function() {
            lastModifiedInput = baseId;
            syncDirectWithRange(this, rangeInput, valueElement);
            updateTotal();
        });
    });
    
    // Setup increase/decrease buttons
    document.querySelectorAll('.increase-btn, .decrease-btn').forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const input = document.getElementById(targetId);
            const directInput = document.getElementById(targetId + '-direct');
            const valueElement = document.getElementById(targetId + '-value');
            
            // Set as last modified for auto-balance
            lastModifiedInput = targetId;
            
            if (!input) return;
            
            let value = parseFloat(input.value) || 0;
            
            // Increase or decrease by 1.0
            if (this.classList.contains('increase-btn')) {
                value = Math.min(100, value + 1.0);
            } else {
                value = Math.max(0, value - 1.0);
            }
            
            // Update inputs and display
            input.value = value.toFixed(1);
            syncRangeWithDirect(input, directInput, valueElement);
            updateTotal();
        });
    });
    
    // Setup auto-balance button
    if (autoBalanceButton) {
        autoBalanceButton.addEventListener('click', autoBalance);
    }
    
    // Add resource optimization functionality
    const optimizeButton = document.getElementById('optimize-resources');
    if (optimizeButton) {
        optimizeButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get current production and consumption values from the page
            const foodProduction = parseFloat(document.getElementById('food-production-estimate').textContent.replace(/,/g, '')) || 0;
            const rawMaterialsProduction = parseFloat(document.getElementById('raw-materials-production-estimate').textContent.replace(/,/g, '')) || 0;
            const energyProduction = parseFloat(document.getElementById('energy-production-estimate').textContent.replace(/,/g, '')) || 0;
            const technologyProduction = parseFloat(document.getElementById('technology-production-estimate').textContent.replace(/,/g, '')) || 0;
            
            // Get the consumption elements and extract values
            const foodConsumptionText = document.querySelector('.d-flex.justify-content-between.small:nth-of-type(1) span:nth-of-type(2)').textContent;
            const rawMaterialsConsumptionText = document.querySelector('.d-flex.justify-content-between.small:nth-of-type(3) span:nth-of-type(2)').textContent;
            const energyConsumptionText = document.querySelector('.d-flex.justify-content-between.small:nth-of-type(5) span:nth-of-type(2)').textContent;
            
            const foodConsumption = parseFloat(foodConsumptionText.replace(/[^0-9.-]+/g, '')) || 0;
            const rawMaterialsConsumption = parseFloat(rawMaterialsConsumptionText.replace(/[^0-9.-]+/g, '')) || 0;
            const energyConsumption = parseFloat(energyConsumptionText.replace(/[^0-9.-]+/g, '')) || 0;
            
            // Calculate required population percentages for each resource
            // Base calculation: If base production rate is 10 per 1% population, how much % do we need?
            let agricultureNeeded = foodConsumption > 0 ? Math.ceil((foodConsumption * 1.2) / 10) : 15;
            let industryNeeded = rawMaterialsConsumption > 0 ? Math.ceil((rawMaterialsConsumption * 1.2) / 10) : 15;
            let energyNeeded = energyConsumption > 0 ? Math.ceil((energyConsumption * 1.2) / 10) : 15;
            
            // Add minimums to prevent zeros
            agricultureNeeded = Math.max(agricultureNeeded, 15);
            industryNeeded = Math.max(industryNeeded, 15);
            energyNeeded = Math.max(energyNeeded, 15);
            
            // Allocate remaining percentage to research and military
            const resourcesAllocated = agricultureNeeded + industryNeeded + energyNeeded;
            let researchNeeded = 15;  // Base minimum research
            let militaryNeeded = 15;  // Base minimum military
            
            // If we have more than 100%, scale down proportionally
            if (resourcesAllocated + researchNeeded + militaryNeeded > 100) {
                const totalOriginal = resourcesAllocated + researchNeeded + militaryNeeded;
                const scale = 100 / totalOriginal;
                
                agricultureNeeded = Math.round(agricultureNeeded * scale);
                industryNeeded = Math.round(industryNeeded * scale);
                energyNeeded = Math.round(energyNeeded * scale);
                researchNeeded = Math.round(researchNeeded * scale);
                militaryNeeded = Math.round(militaryNeeded * scale);
                
                // Ensure they add up to exactly 100%
                const totalAfterScaling = agricultureNeeded + industryNeeded + energyNeeded + researchNeeded + militaryNeeded;
                if (totalAfterScaling < 100) {
                    // Add the difference to research
                    researchNeeded += 100 - totalAfterScaling;
                } else if (totalAfterScaling > 100) {
                    // Subtract the difference from research, ensuring it doesn't go below 5%
                    const diff = totalAfterScaling - 100;
                    if (researchNeeded > diff + 5) {
                        researchNeeded -= diff;
                    } else {
                        researchNeeded = 5;
                        // Distribute the remaining difference
                        const remainingDiff = totalAfterScaling - 100 - (researchNeeded - 5);
                        if (agricultureNeeded > remainingDiff + 5) {
                            agricultureNeeded -= remainingDiff;
                        } else {
                            // Last resort, adjust military
                            militaryNeeded -= (totalAfterScaling - 100 - (researchNeeded - 5) - (agricultureNeeded - 5));
                        }
                    }
                }
            }
            
            // Update input values
            agricultureInput.value = agricultureNeeded;
            industryInput.value = industryNeeded;
            energyInput.value = energyNeeded;
            researchInput.value = researchNeeded;
            militaryInput.value = militaryNeeded;
            
            // Update direct inputs
            syncRangeWithDirect(agricultureInput, agricultureDirectInput, agricultureValueElement);
            syncRangeWithDirect(industryInput, industryDirectInput, industryValueElement);
            syncRangeWithDirect(energyInput, energyDirectInput, energyValueElement);
            syncRangeWithDirect(researchInput, researchDirectInput, researchValueElement);
            syncRangeWithDirect(militaryInput, militaryDirectInput, militaryValueElement);
            
            // Show explanation
            const optimizationExplanation = document.getElementById('optimization-explanation');
            const optimizationDetails = document.getElementById('optimization-details');
            if (optimizationExplanation && optimizationDetails) {
                optimizationExplanation.style.display = 'block';
                optimizationDetails.innerHTML = `
                    <p>Distribuzione ottimizzata:</p>
                    <ul>
                        <li>Agricoltura: ${agricultureNeeded}% (assicura produzione di cibo sufficiente)</li>
                        <li>Industria: ${industryNeeded}% (assicura produzione di materie prime sufficiente)</li>
                        <li>Energia: ${energyNeeded}% (assicura produzione di energia sufficiente)</li>
                        <li>Ricerca: ${researchNeeded}% (per lo sviluppo tecnologico)</li>
                        <li>Militare: ${militaryNeeded}% (per la difesa)</li>
                    </ul>
                    <p>Questa distribuzione equilibra la produzione delle risorse con un margine di sicurezza del 20%.</p>
                `;
            }
            
            // Update everything else
            updateTotal();
        });
    }
    
    // Add preset buttons functionality
    const presets = {
        'balanced': { agriculture: 20, industry: 20, energy: 20, research: 20, military: 20 },
        'economic': { agriculture: 30, industry: 40, energy: 20, research: 5, military: 5 },
        'military': { agriculture: 20, industry: 15, energy: 15, research: 10, military: 40 },
        'technological': { agriculture: 15, industry: 15, energy: 20, research: 40, military: 10 }
    };
    
    for (const [presetName, values] of Object.entries(presets)) {
        const button = document.getElementById(`preset-${presetName}`);
        if (button) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Update all inputs
                agricultureInput.value = values.agriculture;
                industryInput.value = values.industry;
                energyInput.value = values.energy;
                researchInput.value = values.research;
                militaryInput.value = values.military;
                
                // Update direct inputs and displays
                syncRangeWithDirect(agricultureInput, agricultureDirectInput, agricultureValueElement);
                syncRangeWithDirect(industryInput, industryDirectInput, industryValueElement);
                syncRangeWithDirect(energyInput, energyDirectInput, energyValueElement);
                syncRangeWithDirect(researchInput, researchDirectInput, researchValueElement);
                syncRangeWithDirect(militaryInput, militaryDirectInput, militaryValueElement);
                
                // Update everything else
                updateTotal();
            });
        }
    }
    
    // Validate form before submission
    populationForm.addEventListener('submit', function(e) {
        const agriculture = parseFloat(agricultureInput.value) || 0;
        const industry = parseFloat(industryInput.value) || 0;
        const energy = parseFloat(energyInput.value) || 0;
        const research = parseFloat(researchInput.value) || 0;
        const military = parseFloat(militaryInput.value) || 0;
        
        const total = agriculture + industry + energy + research + military;
        
        // Allow a small margin of error for floating point
        if (Math.abs(total - 100) >= 0.1) {
            e.preventDefault();
            
            // Ask if they want to auto-balance
            if (confirm('Population distribution must total exactly 100%. Would you like to auto-balance the values now?')) {
                autoBalance();
                
                // Check if auto-balance fixed the issue
                setTimeout(() => {
                    const newTotal = parseFloat(agricultureInput.value) + 
                                     parseFloat(industryInput.value) + 
                                     parseFloat(energyInput.value) + 
                                     parseFloat(researchInput.value) + 
                                     parseFloat(militaryInput.value);
                    
                    if (Math.abs(newTotal - 100) < 0.1) {
                        // Now submit the form
                        populationForm.submit();
                    }
                }, 100);
            }
        }
    });
    
    // Initial update to ensure everything is in sync
    updateTotal();
}