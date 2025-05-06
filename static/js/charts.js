// EcoWorld Charts JS - Common chart utilities

// Chart color palettes
const RESOURCE_COLORS = {
    'raw_materials': {
        border: 'rgba(102, 51, 153, 1)',
        background: 'rgba(102, 51, 153, 0.2)'
    },
    'food': {
        border: 'rgba(0, 128, 0, 1)',
        background: 'rgba(0, 128, 0, 0.2)'
    },
    'energy': {
        border: 'rgba(255, 165, 0, 1)',
        background: 'rgba(255, 165, 0, 0.2)'
    },
    'technology': {
        border: 'rgba(0, 0, 255, 1)',
        background: 'rgba(0, 0, 255, 0.2)'
    },
    'currency': {
        border: 'rgba(184, 134, 11, 1)',
        background: 'rgba(184, 134, 11, 0.2)'
    }
};

const MILITARY_COLORS = {
    'infantry': {
        border: 'rgba(90, 120, 90, 1)',
        background: 'rgba(90, 120, 90, 0.2)'
    },
    'tanks': {
        border: 'rgba(160, 80, 50, 1)',
        background: 'rgba(160, 80, 50, 0.2)'
    },
    'aircraft': {
        border: 'rgba(70, 130, 180, 1)',
        background: 'rgba(70, 130, 180, 0.2)'
    },
    'navy': {
        border: 'rgba(0, 71, 171, 1)',
        background: 'rgba(0, 71, 171, 0.2)'
    },
    'missiles': {
        border: 'rgba(178, 34, 34, 1)',
        background: 'rgba(178, 34, 34, 0.2)'
    }
};

// Chart utility functions
function getResourceColor(resourceType, alpha = null) {
    if (!RESOURCE_COLORS[resourceType]) {
        return {
            border: 'rgba(128, 128, 128, 1)',
            background: 'rgba(128, 128, 128, 0.2)'
        };
    }
    
    if (alpha !== null) {
        return {
            border: RESOURCE_COLORS[resourceType].border.replace(', 1)', `, ${alpha})`),
            background: RESOURCE_COLORS[resourceType].background.replace(', 0.2)', `, ${alpha})`)
        };
    }
    
    return RESOURCE_COLORS[resourceType];
}

function getMilitaryColor(unitType, alpha = null) {
    if (!MILITARY_COLORS[unitType]) {
        return {
            border: 'rgba(128, 128, 128, 1)',
            background: 'rgba(128, 128, 128, 0.2)'
        };
    }
    
    if (alpha !== null) {
        return {
            border: MILITARY_COLORS[unitType].border.replace(', 1)', `, ${alpha})`),
            background: MILITARY_COLORS[unitType].background.replace(', 0.2)', `, ${alpha})`)
        };
    }
    
    return MILITARY_COLORS[unitType];
}

function getRandomChartColors(index, alpha = null) {
    const colors = [
        { border: 'rgba(255, 99, 132, 1)', background: 'rgba(255, 99, 132, 0.2)' },
        { border: 'rgba(54, 162, 235, 1)', background: 'rgba(54, 162, 235, 0.2)' },
        { border: 'rgba(255, 206, 86, 1)', background: 'rgba(255, 206, 86, 0.2)' },
        { border: 'rgba(75, 192, 192, 1)', background: 'rgba(75, 192, 192, 0.2)' },
        { border: 'rgba(153, 102, 255, 1)', background: 'rgba(153, 102, 255, 0.2)' },
        { border: 'rgba(255, 159, 64, 1)', background: 'rgba(255, 159, 64, 0.2)' },
        { border: 'rgba(199, 199, 199, 1)', background: 'rgba(199, 199, 199, 0.2)' },
        { border: 'rgba(83, 102, 255, 1)', background: 'rgba(83, 102, 255, 0.2)' },
        { border: 'rgba(40, 159, 64, 1)', background: 'rgba(40, 159, 64, 0.2)' },
        { border: 'rgba(210, 199, 199, 1)', background: 'rgba(210, 199, 199, 0.2)' }
    ];
    
    const colorSet = colors[index % colors.length];
    
    if (alpha !== null) {
        return {
            border: colorSet.border.replace(', 1)', `, ${alpha})`),
            background: colorSet.background.replace(', 0.2)', `, ${alpha})`)
        };
    }
    
    return colorSet;
}

// Chart creation functions
function createResourceHistoryChart(canvasId, resourceType, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    // Clear any existing chart
    if (ctx.chart) {
        ctx.chart.destroy();
    }
    
    // Extract dates and values from the data
    const dates = data.map(item => item.date);
    const values = data.map(item => item.value);
    
    // Get colors for this resource
    const colors = getResourceColor(resourceType);
    
    // Create the chart
    ctx.chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: resourceType.replace('_', ' '),
                data: values,
                borderColor: colors.border,
                backgroundColor: colors.background,
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
    
    return ctx.chart;
}

function createMultiResourceChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    // Clear any existing chart
    if (ctx.chart) {
        ctx.chart.destroy();
    }
    
    // Extract dates from the first resource (they should all have the same dates)
    const firstResource = Object.values(data)[0];
    const dates = firstResource.map(item => item.date);
    
    // Create datasets for each resource
    const datasets = [];
    for (const [resource, values] of Object.entries(data)) {
        const colors = getResourceColor(resource);
        datasets.push({
            label: resource.replace('_', ' '),
            data: values.map(item => item.price || item.value),
            borderColor: colors.border,
            backgroundColor: colors.background,
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
                        text: 'Value'
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
    
    return ctx.chart;
}

function createRadarChart(canvasId, labels, datasets) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    // Clear any existing chart
    if (ctx.chart) {
        ctx.chart.destroy();
    }
    
    // Format datasets with colors
    const formattedDatasets = datasets.map((dataset, index) => {
        const colors = getRandomChartColors(index);
        return {
            ...dataset,
            borderColor: colors.border,
            backgroundColor: colors.background,
            fill: true
        };
    });
    
    // Create the chart
    ctx.chart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: formattedDatasets
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
    
    return ctx.chart;
}

function createDoughnutChart(canvasId, labels, data, colors = null) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    // Clear any existing chart
    if (ctx.chart) {
        ctx.chart.destroy();
    }
    
    // Generate colors if not provided
    const backgroundColors = [];
    const borderColors = [];
    
    if (colors) {
        // Use provided colors
        for (const color of colors) {
            backgroundColors.push(color.background);
            borderColors.push(color.border);
        }
    } else {
        // Generate colors
        for (let i = 0; i < labels.length; i++) {
            const color = getRandomChartColors(i);
            backgroundColors.push(color.background);
            borderColors.push(color.border);
        }
    }
    
    // Create the chart
    ctx.chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
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
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
    
    return ctx.chart;
}

// Function to format numbers with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}
