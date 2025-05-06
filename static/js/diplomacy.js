// Script di diplomazia per calcolo linee e gestione nodi

document.addEventListener('DOMContentLoaded', function() {
    
    // Calcola l'angolo e la lunghezza delle linee di relazione
    function calculateRelationLines() {
        const lines = document.querySelectorAll('.nation-relation-line');
        const map = document.querySelector('.diplomacy-map');
        
        // Check if the map exists
        if (!map) return;
        
        console.log("Calculating relation lines for", lines.length, "relationships");
        
        lines.forEach(line => {
            const startX = parseFloat(getComputedStyle(line).getPropertyValue('--start-x'));
            const startY = parseFloat(getComputedStyle(line).getPropertyValue('--start-y'));
            const endX = parseFloat(getComputedStyle(line).getPropertyValue('--end-x'));
            const endY = parseFloat(getComputedStyle(line).getPropertyValue('--end-y'));
            
            console.log("Line from", startX, startY, "to", endX, endY);
            
            if (isNaN(startX) || isNaN(startY) || isNaN(endX) || isNaN(endY)) {
                console.warn("Invalid coordinates for relation line");
                return;
            }
            
            // Convertire le coordinate in percentuale in pixel
            const mapWidth = map.offsetWidth;
            const mapHeight = map.offsetHeight;
            
            const startXPx = (startX / 100) * mapWidth;
            const startYPx = (startY / 100) * mapHeight;
            const endXPx = (endX / 100) * mapWidth;
            const endYPx = (endY / 100) * mapHeight;
            
            // Calcolare la lunghezza della linea
            const deltaX = endXPx - startXPx;
            const deltaY = endYPx - startYPx;
            const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
            
            // Calcolare l'angolo in radianti e convertirlo in gradi
            const angle = Math.atan2(deltaY, deltaX) * (180 / Math.PI);
            
            console.log("Line details:", {distance, angle});
            
            // Impostare le proprietà CSS personalizzate
            line.style.setProperty('--line-width', `${distance}px`);
            line.style.setProperty('--line-angle', `${angle}deg`);
        });
    }
    
    // Loghiamo tutte le nazioni sulla mappa per debugging
    function logNationPositions() {
        const nodes = document.querySelectorAll('.nation-map-node');
        console.log("Total nations on map:", nodes.length);
        
        nodes.forEach((node, index) => {
            const left = parseFloat(node.style.left);
            const top = parseFloat(node.style.top);
            const isSelf = node.classList.contains('self');
            
            // Get nation name from the node or its title attribute
            let name = node.getAttribute('title') || 'Unknown';
            
            // Extract name part before parenthesis if exists
            if (name.includes('(')) {
                name = name.split('(')[0].trim();
            }
            
            console.log(`Nation ${index+1}: ${name} at (${left}%, ${top}%) ${isSelf ? '(Self)' : ''}`);
        });
    }
    
    // Ensure all nations are visible in the map by adjusting the map size
    function adjustMapView() {
        const map = document.querySelector('.diplomacy-map');
        const nodes = document.querySelectorAll('.nation-map-node');
        
        if (!map || nodes.length === 0) return;
        
        let maxX = 0;
        let maxY = 0;
        
        // Loop through all nation nodes to find the furthest coordinates
        nodes.forEach(node => {
            const left = parseFloat(node.style.left);
            const top = parseFloat(node.style.top);
            
            console.log(`Node position: ${left}%, ${top}%`);
            
            if (!isNaN(left) && left > maxX) maxX = left;
            if (!isNaN(top) && top > maxY) maxY = top;
        });
        
        // Add buffer space
        maxX = Math.max(maxX + 10, 100);
        maxY = Math.max(maxY + 10, 100);
        
        console.log(`Setting map size to ${maxX}% x ${maxY}%`);
        
        // Ensure map is large enough to accommodate all nodes
        map.style.minWidth = `${maxX}%`;
        map.style.minHeight = `${maxY}%`;
    }
    
    // Run with delay to ensure DOM is fully loaded
    setTimeout(function() {
        logNationPositions();
        adjustMapView();
        calculateRelationLines();
    }, 300);
    
    // Ricalcola le linee quando il browser viene ridimensionato
    window.addEventListener('resize', calculateRelationLines);
});