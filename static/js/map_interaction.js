document.addEventListener('DOMContentLoaded', function() {
    // Map interaction for all SVG-based countries
    const countries = document.querySelectorAll('.country');
    const countryNames = document.querySelectorAll('.country-name');
    
    // Main interactive functionality for map countries
    if (countries.length > 0) {
        countries.forEach(country => {
            // When hovering over a country
            country.addEventListener('mouseenter', function() {
                // Highlight the country
                this.style.filter = 'brightness(1.5)';
                this.style.strokeWidth = '2.5';
                
                // Find and highlight the country name
                const countryId = this.getAttribute('id');
                const countryNameElements = document.querySelectorAll(`.country-name[data-country="${countryId}"]`);
                countryNameElements.forEach(nameEl => {
                    nameEl.style.fontWeight = 'bold';
                    nameEl.style.fontSize = '12px';
                });
                
                // Show tooltip with country info if available
                if (window.nationData && window.nationData[countryId]) {
                    const nationInfo = window.nationData[countryId];
                    showNationTooltip(event, nationInfo);
                }
            });
            
            // When moving mouse out of a country
            country.addEventListener('mouseleave', function() {
                // Return to normal style
                this.style.filter = '';
                this.style.strokeWidth = '1.5';
                
                // Reset country name style
                const countryId = this.getAttribute('id');
                const countryNameElements = document.querySelectorAll(`.country-name[data-country="${countryId}"]`);
                countryNameElements.forEach(nameEl => {
                    nameEl.style.fontWeight = 'normal';
                    nameEl.style.fontSize = '10px';
                });
                
                // Hide tooltip
                hideNationTooltip();
            });
            
            // When clicking on a country
            country.addEventListener('click', function() {
                const countryId = this.getAttribute('id');
                
                // If we have diplomatic relations data for this country
                if (window.nationData && window.nationData[countryId] && window.nationData[countryId].id) {
                    // Navigate to the nation relations page
                    window.location.href = `/diplomacy/nation/${window.nationData[countryId].id}`;
                }
            });
        });
    }
    
    // Adding data-country attributes to country names for easier selection
    countryNames.forEach(nameEl => {
        // Extract country ID from the text content
        const nameText = nameEl.textContent.trim().toLowerCase();
        
        // Convert name to ID format (e.g., "United States" -> "usa")
        let countryId = '';
        
        // Simple mapping of country names to IDs
        const nameToId = {
            'alaska': 'alaska',
            'canada': 'canada',
            'groenlandia': 'greenland',
            'usa': 'usa',
            'messico': 'mexico',
            'colombia': 'colombia',
            'brasile': 'brazil',
            'argentina': 'argentina',
            'cile': 'chile',
            'regno unito': 'uk',
            'francia': 'france',
            'germania': 'germany',
            'spagna': 'spain',
            'italia': 'italy',
            'polonia': 'poland',
            'ucraina': 'ukraine',
            'russia': 'russia',
            'egitto': 'egypt',
            'nigeria': 'nigeria',
            'sudafrica': 'south-africa',
            'arabia saudita': 'saudi-arabia',
            'iran': 'iran',
            'cina': 'china',
            'india': 'india',
            'giappone': 'japan',
            'corea del sud': 'south-korea',
            'australia': 'australia',
            'nuova zelanda': 'new-zealand',
            'antartide': 'antarctica'
        };
        
        // Simple mapping based on text content
        for (const [name, id] of Object.entries(nameToId)) {
            if (nameText.includes(name.toLowerCase())) {
                countryId = id;
                break;
            }
        }
        
        // Set the data attribute if we found a match
        if (countryId) {
            nameEl.setAttribute('data-country', countryId);
        }
    });
    
    // Tooltip functions
    function showNationTooltip(event, nationInfo) {
        // Create tooltip if it doesn't exist
        let tooltip = document.getElementById('nation-tooltip');
        if (!tooltip) {
            tooltip = document.createElement('div');
            tooltip.id = 'nation-tooltip';
            tooltip.className = 'nation-tooltip';
            document.body.appendChild(tooltip);
        }
        
        // Populate tooltip content
        tooltip.innerHTML = `
            <div class="tooltip-header">${nationInfo.name}</div>
            <div class="tooltip-content">
                ${nationInfo.relation_state ? `<div>Relations: ${nationInfo.relation_state}</div>` : ''}
                ${nationInfo.territory ? `<div>Region: ${nationInfo.territory}</div>` : ''}
                ${nationInfo.is_allied ? '<div class="tooltip-badge allied">Allied</div>' : ''}
                ${nationInfo.is_at_war ? '<div class="tooltip-badge at-war">At War</div>' : ''}
            </div>
        `;
        
        // Position tooltip near mouse
        const x = event.pageX + 15;
        const y = event.pageY - 20;
        tooltip.style.left = `${x}px`;
        tooltip.style.top = `${y}px`;
        tooltip.style.display = 'block';
    }
    
    function hideNationTooltip() {
        const tooltip = document.getElementById('nation-tooltip');
        if (tooltip) {
            tooltip.style.display = 'none';
        }
    }
    
    // If we're on the diplomacy page, load nation data for tooltips
    if (window.location.pathname.includes('/diplomacy')) {
        // Fetch nation data from API
        fetch('/api/relations')
            .then(response => response.json())
            .then(data => {
                // Store nation data globally for tooltips
                window.nationData = {};
                
                // Create a mapping from country IDs to nation data
                if (data && data.relations) {
                    data.relations.forEach(relation => {
                        const nationId = relation.nation.id;
                        const countryId = mapNationIdToCountryId(nationId);
                        
                        if (countryId) {
                            window.nationData[countryId] = {
                                id: nationId,
                                name: relation.nation.name,
                                relation_state: relation.relation_state,
                                relation_value: relation.relation_value,
                                is_allied: relation.is_allied,
                                is_at_war: relation.is_at_war,
                                territory: relation.nation.continent
                            };
                        }
                    });
                }
                
                // Also add the current user's nation
                if (data && data.current_nation) {
                    const currentNationId = mapNationIdToCountryId(data.current_nation.id);
                    if (currentNationId) {
                        window.nationData[currentNationId] = {
                            id: data.current_nation.id,
                            name: data.current_nation.name,
                            relation_state: 'You',
                            territory: data.current_nation.continent
                        };
                    }
                }
            })
            .catch(error => {
                console.error('Error fetching nation data:', error);
            });
    }
    
    // Helper function to map database nation IDs to SVG country IDs
    function mapNationIdToCountryId(nationId) {
        // This is a simplification - in reality, you'd need a more robust mapping
        // based on your database structure
        
        // Simple direct mapping (assumes nation IDs in database match country IDs in SVG)
        return nationId;
    }
});

// Add CSS for tooltips
const tooltipStyle = document.createElement('style');
tooltipStyle.textContent = `
.nation-tooltip {
    position: absolute;
    background-color: rgba(10, 30, 50, 0.9);
    border: 1px solid #00aeff;
    border-radius: 4px;
    padding: 8px;
    font-family: Arial, sans-serif;
    font-size: 12px;
    color: #ffffff;
    z-index: 1000;
    pointer-events: none;
    display: none;
    min-width: 150px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.tooltip-header {
    font-weight: bold;
    margin-bottom: 4px;
    color: #00eaff;
    border-bottom: 1px solid rgba(0, 234, 255, 0.3);
    padding-bottom: 4px;
}

.tooltip-content {
    font-size: 11px;
    line-height: 1.4;
}

.tooltip-badge {
    display: inline-block;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 10px;
    margin-top: 4px;
    font-weight: bold;
}

.tooltip-badge.allied {
    background-color: rgba(40, 167, 69, 0.7);
}

.tooltip-badge.at-war {
    background-color: rgba(220, 53, 69, 0.7);
}
`;
document.head.appendChild(tooltipStyle);