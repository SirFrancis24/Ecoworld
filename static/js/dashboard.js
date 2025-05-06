// EcoWorld Dashboard JS

document.addEventListener('DOMContentLoaded', function() {
    console.log("Dashboard JS Loaded");
    
    // Force immediate timer update to fix "Complete!" text
    setTimeout(function() {
        console.log("Forcing timer update...");
        updateTimers();
    }, 100);
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Load resource charts when the page loads
    loadResourceCharts();
    
    // Add click handlers for dashboard tabs
    const tabs = document.querySelectorAll('.dashboard-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Show the corresponding content
            const target = this.getAttribute('data-target');
            document.querySelectorAll('.dashboard-content').forEach(content => {
                content.style.display = 'none';
            });
            document.getElementById(target).style.display = 'block';
            
            // If this is the resources tab, refresh the charts
            if (target === 'resources-content') {
                loadResourceCharts();
            }
        });
    });
    
    // Set up the timer
    updateTimers();
    setInterval(updateTimers, 1000);
});

function updateTimers() {
    // Update market session timer
    const marketTimerElem = document.getElementById('market-timer');
    if (marketTimerElem) {
        // For a real implementation, you would calculate this based on server time
        // Here we'll just set a countdown from the current time
        const now = new Date();
        const endOfDay = new Date();
        endOfDay.setHours(23, 59, 59, 999);
        
        const diff = endOfDay - now;
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);
        
        marketTimerElem.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    
    // We are disabling client-side timer updates because they are causing problems
    // The server will render correct times and we'll use meta refresh to update the page
    console.log("Client-side timer updates disabled - using server-rendered times");
}

function loadResourceCharts() {
    // Load resource history charts
    loadResourceHistoryChart('raw-materials-chart', 'raw_materials');
    loadResourceHistoryChart('food-chart', 'food');
    loadResourceHistoryChart('energy-chart', 'energy');
    loadResourceHistoryChart('currency-chart', 'currency');
    
    // Load market price chart
    loadMarketPriceChart('market-price-chart');
    
    // Load nation comparison chart 
    loadNationComparisonChart('nation-comparison-chart');
}

function loadResourceHistoryChart(chartId, resourceType) {
    const ctx = document.getElementById(chartId);
    if (!ctx) return;
    
    // Clear any existing chart
    if (ctx.chart) {
        ctx.chart.destroy();
    }
    
    // Fetch the resource history data from the server
    fetch(`/api/resource_history/${resourceType}`)
        .then(response => response.json())
        .then(data => {
            // Extract dates and values from the data
            const dates = data.map(item => item.date);
            const values = data.map(item => item.value);
            
            // Create the chart
            ctx.chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: [{
                        label: resourceType.replace('_', ' '),
                        data: values,
                        borderColor: getResourceColor(resourceType),
                        backgroundColor: getResourceColor(resourceType, 0.2),
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Amount'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Date'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error loading resource history:', error);
        });
}

function loadMarketPriceChart(chartId) {
    const ctx = document.getElementById(chartId);
    if (!ctx) return;
    
    // Clear any existing chart
    if (ctx.chart) {
        ctx.chart.destroy();
    }
    
    // Fetch market price data
    fetch('/api/market/prices')
        .then(response => response.json())
        .then(data => {
            // Extract the dates from the first resource (they should all have the same dates)
            const dates = data.raw_materials.map(item => item.date);
            
            // Create datasets for each resource
            const datasets = [];
            for (const [resource, prices] of Object.entries(data)) {
                datasets.push({
                    label: resource.replace('_', ' '),
                    data: prices.map(item => item.price),
                    borderColor: getResourceColor(resource),
                    backgroundColor: getResourceColor(resource, 0.1),
                    tension: 0.4,
                    fill: false
                });
            }
            
            // Create the chart
            ctx.chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Price per Unit'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Date'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error loading market prices:', error);
        });
}

function loadNationComparisonChart(chartId) {
    const ctx = document.getElementById(chartId);
    if (!ctx) return;
    
    // Clear any existing chart
    if (ctx.chart) {
        ctx.chart.destroy();
    }
    
    // Use the ranking data already in the page
    const economicRankings = document.querySelectorAll('.economic-rank');
    const militaryRankings = document.querySelectorAll('.military-rank');
    const techRankings = document.querySelectorAll('.tech-rank');
    const nations = document.querySelectorAll('.nation-name');
    
    const nationNames = [];
    const economicRanks = [];
    const militaryRanks = [];
    const techRanks = [];
    
    // Get the top 5 nations
    for (let i = 0; i < 5 && i < nations.length; i++) {
        nationNames.push(nations[i].textContent);
        economicRanks.push(parseInt(economicRankings[i].textContent));
        militaryRanks.push(parseInt(militaryRankings[i].textContent));
        techRanks.push(parseInt(techRankings[i].textContent));
    }
    
    // Create the radar chart
    ctx.chart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Economic', 'Military', 'Technology'],
            datasets: nationNames.map((name, index) => ({
                label: name,
                data: [10 - economicRanks[index], 10 - militaryRanks[index], 10 - techRanks[index]],
                borderColor: getRandomColor(index),
                backgroundColor: getRandomColor(index, 0.2)
            }))
        },
        options: {
            responsive: true,
            scales: {
                r: {
                    angleLines: {
                        display: true
                    },
                    min: 0,
                    max: 10
                }
            }
        }
    });
}

function getResourceColor(resourceType, alpha = 1) {
    const colors = {
        'raw_materials': `rgba(102, 51, 153, ${alpha})`,
        'food': `rgba(0, 128, 0, ${alpha})`,
        'energy': `rgba(255, 165, 0, ${alpha})`,
        'technology': `rgba(0, 0, 255, ${alpha})`,
        'currency': `rgba(184, 134, 11, ${alpha})`
    };
    
    return colors[resourceType] || `rgba(128, 128, 128, ${alpha})`;
}

function getRandomColor(index, alpha = 1) {
    const colors = [
        `rgba(255, 99, 132, ${alpha})`,
        `rgba(54, 162, 235, ${alpha})`,
        `rgba(255, 206, 86, ${alpha})`,
        `rgba(75, 192, 192, ${alpha})`,
        `rgba(153, 102, 255, ${alpha})`,
        `rgba(255, 159, 64, ${alpha})`,
        `rgba(199, 199, 199, ${alpha})`,
        `rgba(83, 102, 255, ${alpha})`,
        `rgba(40, 159, 64, ${alpha})`,
        `rgba(210, 199, 199, ${alpha})`
    ];
    
    return colors[index % colors.length];
}
