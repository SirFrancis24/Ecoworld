// EcoWorld Market JS

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize market price chart
    loadMarketPriceChart();
    
    // Set up resource type and quantity handlers
    setupSellForm();
    
    // Set up search and filter functionality
    setupMarketFilters();
    
    // Set up the timer
    updateMarketTimer();
    setInterval(updateMarketTimer, 1000);
});

function updateMarketTimer() {
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
}

function loadMarketPriceChart() {
    const ctx = document.getElementById('market-price-chart');
    if (!ctx) return;
    
    // Clear any existing chart
    if (ctx.chart) {
        ctx.chart.destroy();
    }
    
    // Fetch market price data
    fetch('/market/prices')
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

function setupSellForm() {
    const resourceTypeSelect = document.getElementById('resource-type');
    const quantityInput = document.getElementById('quantity');
    const priceInput = document.getElementById('price-per-unit');
    const totalPriceSpan = document.getElementById('total-price');
    const maxQuantitySpan = document.getElementById('max-quantity');
    const sellForm = document.getElementById('sell-form');
    
    if (!resourceTypeSelect || !quantityInput || !priceInput || !totalPriceSpan || !maxQuantitySpan) return;
    
    // Update max quantity when resource type changes
    resourceTypeSelect.addEventListener('change', function() {
        const resourceType = this.value;
        const availableResources = {
            'raw_materials': parseFloat(document.getElementById('available-raw-materials').textContent.replace(/,/g, '')),
            'food': parseFloat(document.getElementById('available-food').textContent.replace(/,/g, '')),
            'energy': parseFloat(document.getElementById('available-energy').textContent.replace(/,/g, ''))
        };
        
        maxQuantitySpan.textContent = availableResources[resourceType].toFixed(0);
        
        // Update the max attribute of the quantity input
        quantityInput.max = availableResources[resourceType];
        
        // Recalculate total price
        calculateTotalPrice();
    });
    
    // Trigger the change event to initialize
    const event = new Event('change');
    resourceTypeSelect.dispatchEvent(event);
    
    // Update total price when quantity or price changes
    quantityInput.addEventListener('input', calculateTotalPrice);
    priceInput.addEventListener('input', calculateTotalPrice);
    
    // Add max button functionality
    const maxButton = document.getElementById('max-quantity-btn');
    if (maxButton) {
        maxButton.addEventListener('click', function() {
            quantityInput.value = maxQuantitySpan.textContent;
            calculateTotalPrice();
        });
    }
    
    // Validate form before submission
    if (sellForm) {
        sellForm.addEventListener('submit', function(e) {
            const resourceType = resourceTypeSelect.value;
            const quantity = parseFloat(quantityInput.value);
            const price = parseFloat(priceInput.value);
            
            if (!resourceType || isNaN(quantity) || quantity <= 0 || isNaN(price) || price <= 0) {
                e.preventDefault();
                alert('Please enter valid quantity and price values.');
            }
        });
    }
    
    function calculateTotalPrice() {
        const quantity = parseFloat(quantityInput.value) || 0;
        const price = parseFloat(priceInput.value) || 0;
        const total = quantity * price;
        totalPriceSpan.textContent = total.toFixed(2);
    }
}

function setupMarketFilters() {
    const searchInput = document.getElementById('market-search');
    const resourceFilterSelect = document.getElementById('resource-filter');
    const priceFilterSelect = document.getElementById('price-filter');
    
    if (!searchInput || !resourceFilterSelect || !priceFilterSelect) return;
    
    // Function to filter market listings
    function filterListings() {
        const searchTerm = searchInput.value.toLowerCase();
        const resourceFilter = resourceFilterSelect.value;
        const priceFilter = priceFilterSelect.value;
        
        const listings = document.querySelectorAll('.market-item');
        
        listings.forEach(listing => {
            const sellerName = listing.querySelector('.seller-name').textContent.toLowerCase();
            const resourceType = listing.getAttribute('data-resource-type');
            const pricePerUnit = parseFloat(listing.getAttribute('data-price-per-unit'));
            
            let showListing = true;
            
            // Apply search filter
            if (searchTerm && !sellerName.includes(searchTerm)) {
                showListing = false;
            }
            
            // Apply resource filter
            if (resourceFilter !== 'all' && resourceType !== resourceFilter) {
                showListing = false;
            }
            
            // Apply price filter
            if (priceFilter === 'low' && pricePerUnit > 20) {
                showListing = false;
            } else if (priceFilter === 'medium' && (pricePerUnit <= 20 || pricePerUnit > 50)) {
                showListing = false;
            } else if (priceFilter === 'high' && pricePerUnit <= 50) {
                showListing = false;
            }
            
            // Show or hide the listing
            listing.style.display = showListing ? '' : 'none';
        });
    }
    
    // Add event listeners
    searchInput.addEventListener('input', filterListings);
    resourceFilterSelect.addEventListener('change', filterListings);
    priceFilterSelect.addEventListener('change', filterListings);
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
