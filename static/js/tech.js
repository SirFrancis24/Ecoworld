// EcoWorld Technology JS

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize technology tree visualization
    loadTechnologyTree();
    
    // Set up research form handlers
    setupResearchForm();
    
    // We've disabled client-side timer updates completely
    console.log("Client-side timer updates have been disabled");
});

function loadTechnologyTree() {
    const treeContainer = document.getElementById('technology-tree');
    if (!treeContainer) return;
    
    // Fetch technology tree data from the server
    fetch('/api/technology/tree')
        .then(response => response.json())
        .then(data => {
            // Create a visualization of the technology tree
            createTechTree(treeContainer, data);
        })
        .catch(error => {
            console.error('Error loading technology tree:', error);
            treeContainer.innerHTML = `<div class="alert alert-danger">Error loading technology tree: ${error.message}</div>`;
        });
}

function createTechTree(container, technologies) {
    if (!technologies || !technologies.length) {
        container.innerHTML = '<div class="alert alert-info">No technologies available yet.</div>';
        return;
    }
    
    // Group technologies by category
    const categories = {};
    technologies.forEach(tech => {
        if (!categories[tech.category]) {
            categories[tech.category] = [];
        }
        categories[tech.category].push(tech);
    });
    
    // Create HTML for the technology tree
    let html = '<div class="tech-tree">';
    
    // Create a section for each category
    for (const [category, techs] of Object.entries(categories)) {
        html += `
            <div class="tech-category">
                <h3 class="mb-3">${category}</h3>
                <div class="tech-items">
        `;
        
        // Add technologies in this category
        techs.forEach(tech => {
            // Determine the tech status class
            let statusClass = 'tech-unavailable';
            if (tech.researching) {
                statusClass = 'tech-researching';
            } else if (tech.level > 0) {
                statusClass = 'tech-researched';
            }
            
            // Format prerequisites
            const prereqs = tech.prerequisites.map(p => {
                const prereqTech = technologies.find(t => t.id === parseInt(p));
                return prereqTech ? prereqTech.name : 'Unknown';
            }).join(', ');
            
            // Create tech item
            html += `
                <div class="tech-item ${statusClass}" data-id="${tech.id}">
                    <div class="tech-header">
                        <span class="tech-name">${tech.name}</span>
                        <span class="tech-level">Level ${tech.level}/${tech.max_level}</span>
                    </div>
                    <div class="tech-body">
                        ${tech.researching ? 
                            `<div class="progress">
                                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                                     role="progressbar" 
                                     style="width: ${Math.round(tech.progress * 100)}%"
                                     aria-valuenow="${Math.round(tech.progress * 100)}" 
                                     aria-valuemin="0" 
                                     aria-valuemax="100">
                                    ${Math.round(tech.progress * 100)}%
                                </div>
                            </div>` : ''
                        }
                        ${prereqs ? `<div class="tech-prereqs">Requires: ${prereqs}</div>` : ''}
                        <div class="tech-actions mt-2">
                            ${tech.researching ? 
                                `<form action="/technology/cancel" method="post">
                                    <input type="hidden" name="technology_id" value="${tech.id}">
                                    <button type="submit" class="btn btn-sm btn-danger">Cancel Research</button>
                                </form>` :
                                (tech.level < tech.max_level ? 
                                    `<form action="/technology/research" method="post">
                                        <input type="hidden" name="technology_id" value="${tech.id}">
                                        <button type="submit" class="btn btn-sm btn-primary">Research</button>
                                    </form>` : 
                                    `<span class="badge bg-success">Maximized</span>`
                                )
                            }
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    }
    
    html += '</div>';
    container.innerHTML = html;
}

function setupResearchForm() {
    const researchForms = document.querySelectorAll('form[action="/technology/research"]');
    
    researchForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const techId = this.querySelector('input[name="technology_id"]').value;
            const tech = document.querySelector(`.tech-item[data-id="${techId}"]`);
            
            // Check if the tech is already being researched
            if (tech && tech.classList.contains('tech-researching')) {
                e.preventDefault();
                alert('This technology is already being researched.');
            }
            
            // Additional validation could be added here if needed
        });
    });
}

function updateResearchTimers() {
    const timerElements = document.querySelectorAll('.research-timer');
    
    timerElements.forEach(timer => {
        const completionTime = new Date(timer.getAttribute('data-completion-time'));
        const now = new Date();
        
        if (now >= completionTime) {
            timer.textContent = '00:00:00';
            timer.classList.add('text-success');
            
            // If the page hasn't been refreshed, we might want to update the UI
            // to show the completed research
            const techItem = timer.closest('.tech-item');
            if (techItem) {
                techItem.classList.remove('tech-researching');
                techItem.classList.add('tech-researched');
            }
            
            // We've removed the auto-refresh because it was causing too many refreshes
        } else {
            const diff = completionTime - now;
            const hours = Math.floor(diff / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((diff % (1000 * 60)) / 1000);
            
            timer.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
    });
}
