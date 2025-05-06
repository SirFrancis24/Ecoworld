// Interazione tra l'SVG della mappa e il database dei paesi
document.addEventListener('DOMContentLoaded', function() {
    // Ottiene l'oggetto SVG
    const svgObject = document.getElementById('world-map-svg');
    
    // Aspetta che l'SVG venga caricato completamente
    svgObject.addEventListener('load', function() {
        const svgDoc = svgObject.contentDocument;
        const countries = svgDoc.querySelectorAll('.country');
        
        // Verifica se l'elemento "self" esiste (la nazione del giocatore)
        const selfMarker = document.querySelector('.nation-marker.self');
        let selfCountryId = null;
        
        if (selfMarker) {
            selfCountryId = selfMarker.getAttribute('data-country-id');
        }
        
        // Interazione con tutti i paesi nella mappa SVG
        countries.forEach(country => {
            const countryId = country.getAttribute('id');
            const countryName = country.getAttribute('data-name');
            
            // Evidenzia il paese del giocatore
            if (selfCountryId && countryId === selfCountryId) {
                country.classList.add('selected');
            }
            
            // Aggiunge un tooltip al passaggio del mouse
            country.addEventListener('mouseenter', function(e) {
                // Crea un tooltip per mostrare il nome del paese
                let tooltip = document.createElement('div');
                tooltip.className = 'svg-tooltip';
                tooltip.textContent = countryName;
                tooltip.style.position = 'absolute';
                tooltip.style.left = (e.pageX + 10) + 'px';
                tooltip.style.top = (e.pageY + 10) + 'px';
                tooltip.style.background = 'rgba(0,0,0,0.8)';
                tooltip.style.color = 'white';
                tooltip.style.padding = '5px 10px';
                tooltip.style.borderRadius = '4px';
                tooltip.style.zIndex = '1000';
                document.body.appendChild(tooltip);
                
                // Memorizza il tooltip nell'attributo per poterlo rimuovere
                this.setAttribute('data-tooltip', true);
            });
            
            // Rimuove il tooltip quando il mouse esce
            country.addEventListener('mouseleave', function() {
                const tooltips = document.querySelectorAll('.svg-tooltip');
                tooltips.forEach(t => t.remove());
                this.removeAttribute('data-tooltip');
            });
            
            // Collega il paese alla sua pagina di relazioni diplomatiche
            country.addEventListener('click', function() {
                // Cerca il marker della nazione corrispondente
                const nationMarker = document.querySelector(`.nation-marker[data-country-id="${countryId}"]`);
                
                if (nationMarker) {
                    const nationId = nationMarker.getAttribute('data-nation-id');
                    if (nationId) {
                        window.location.href = `/diplomacy/nation/${nationId}`;
                    }
                }
            });
        });
        
        // Collega i paesi alle nazioni
        const nationMarkers = document.querySelectorAll('.nation-marker');
        nationMarkers.forEach(marker => {
            const nationId = marker.getAttribute('data-nation-id');
            const countryId = marker.getAttribute('data-country-id');
            
            if (countryId && countryId !== 'self') {
                const country = svgDoc.getElementById(countryId);
                
                if (country) {
                    // Evidenzia le alleanze e le guerre
                    if (marker.classList.contains('ally')) {
                        country.classList.add('ally');
                    } else if (marker.classList.contains('enemy')) {
                        country.classList.add('enemy');
                    }
                    
                    // Collega il paese al suo ID di nazione
                    country.setAttribute('data-nation-id', nationId);
                }
            }
        });
    });
});