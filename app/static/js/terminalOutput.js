
import { renderChart } from "/static/js/chartGenerator.js";

/**
* Updates terminal with complete chart data, making house spans explicit
* @param {Object} data - The ephemeris and chart data
*/


// FULL REPORT
export function updateTerminalWithData(data) {
    const terminalOutput = document.getElementById('terminalOutput');
    
    // Defines the chart
    const chart = data?.ephemeris?.chart || {}; 

    const appendLine = (text) => {
        terminalOutput.textContent += `${text}\n`;
        terminalOutput.scrollTop = terminalOutput.scrollHeight;
    };

    // Magic Hour and Time Info sections remain unchanged...
    appendLine('\n=== MAGIC HOUR INFORMATION ===');
    const additionalInfo = data?.ephemeris?.additional_info || {};
    appendLine(`> Current Planetary Hour: ${additionalInfo.current_planetary_hour || 'Unknown'}`);
    appendLine(`> Magic Hour Name: ${data?.neo4j_data?.hour?.label || 'N/A'}`);
    appendLine(`> Magic Hour Ruler: ${additionalInfo.hour_ruler || 'Unknown'}`);

    if (data.neo4j_data && data.neo4j_data.connections) {
        appendLine('> Magical Correspondences:');
        data.neo4j_data.connections.forEach((connection) => {
            const targetLabel = connection.targetNode.label || 'Unnamed Connection';
            const relationType = connection.relationshipType.replace(/_/g, ' ').toUpperCase();
            appendLine(`  - [${relationType}] ${targetLabel}`);
        });
    }
    appendLine(`> Day Ruling Planet: ${additionalInfo.day_ruling_planet || 'Unknown'}`);

    // Time Information
    appendLine('\n=== TIME INFORMATION ===');
    appendLine(`> Local Time: ${additionalInfo.current_time || 'N/A'}`);
    appendLine(`> Sunrise: ${additionalInfo.sunrise || 'N/A'}, Sunset: ${additionalInfo.sunset || 'N/A'}`);
    appendLine(`> Current UTC Time: ${additionalInfo.utc_time || 'N/A'}`);

     // Chart Angles - Updated to use chart.angles
     appendLine('\n=== CHART ANGLES ===');
     const angles = chart.angles || {};
     ['ascendant', 'descendant', 'midheaven', 'ic'].forEach(angle => {
         if (angles[angle]) {
             const angleData = angles[angle];
             appendLine(`> ${angle.charAt(0).toUpperCase() + angle.slice(1)}: ${angleData.degree}° ${angleData.sign} (${angleData.absolute_degree}° total)`);
         }
     });
 
    // Houses and Occupancy - Updated planet name extraction
    appendLine('\n=== HOUSES AND OCCUPANCY ===');
    const houses = chart.houses || {};
    for (let i = 1; i <= 12; i++) {
        const house = houses[i.toString()];
        if (house) {
            const planetNames = house.planets && house.planets.length > 0 
                ? house.planets.map(planet => planet.name).join(', ')
                : null;
            
            const planetList = planetNames 
                ? ` - Occupied by: ${planetNames}`
                : ' - Empty house';
                
            appendLine(`> House ${i}: ${house.degree}° ${house.sign} (${house.absolute_degree}° total)${planetList}`);
        }
    }
 
     // Key Planetary Aspects - Accessing from chart.aspects
     appendLine('\n=== KEY PLANETARY ASPECTS ===');
     const aspects = chart.aspects || [];
     if (Array.isArray(aspects) && aspects.length > 0) {
         // Group aspects by type
         const aspectGroups = {};
         aspects.forEach(aspect => {
             if (!aspectGroups[aspect.aspect]) {
                 aspectGroups[aspect.aspect] = [];
             }
             aspectGroups[aspect.aspect].push(aspect);
         });
 
         // Display each aspect type
         Object.entries(aspectGroups).forEach(([aspectType, aspects]) => {
             appendLine(`\n> ${aspectType}s:`);
             aspects.forEach(aspect => {
                 appendLine(`  - ${aspect.planet1} to ${aspect.planet2} (${aspect.angular_distance}°)`);
             });
         });
     } else {
         appendLine("> No significant aspects found.");
     }
 

    // Moon-Specific Properties
    try {
        appendLine('\n=== MOON-SPECIFIC PROPERTIES ===');
        const moon = data?.ephemeris?.planets?.Moon || {};
        const phase = moon.phase || "Unknown";
        const phaseAngle = moon.phase_angle ?? "N/A";
        const distanceKm = moon.distance_km ?? "N/A";
        const distanceAu = moon.distance_au ?? "N/A";
        const declination = moon.declination ?? "N/A";
        const isOutOfBounds = moon.is_out_of_bounds ?? false;

        appendLine(`> Phase: ${phase}`);
        appendLine(`> Phase Angle: ${phaseAngle}°`);
        appendLine(`> Distance: ${distanceKm} km (${distanceAu} AU)`);
        appendLine(`> Declination: ${declination}°`);
        appendLine(isOutOfBounds ? "> The Moon is Out of Bounds (OOB)" : "> The Moon is within bounds.");
    } catch (error) {
        console.error("Error updating terminal with Moon data:", error.message);
        appendLine("> Unable to display Moon-specific properties due to an error.");
    }

    // Planetary Distances
    appendLine("\n=== PLANETARY DISTANCES FROM EARTH / OBSERVER ===");
    const planets = data?.ephemeris?.planets || {};
    Object.entries(planets).forEach(([planet, info]) => {
        const distanceAu = info.distance_au ?? "N/A";
        appendLine(`> ${planet}: ${distanceAu} AU`);
    });

    // Planetary Positions Summary
    appendLine('\n=== PLANETARY POSITIONS SUMMARY ===');
    for (const [planet, pos] of Object.entries(planets)) {
        const retrograde = pos.is_retrograde ? ' (Retrograde)' : '';
        const stationary = pos.is_stationary ? ' (Stationary)' : '';
        const dailyMotion = pos.daily_motion ? ` [${pos.daily_motion}°/day]` : '';
        appendLine(`> ${planet}: ${pos.degree}° ${pos.sign}${retrograde}${stationary} (${pos.longitude}° total)${dailyMotion}`);
    }

     // Add link to chart page
     const chartLink = document.createElement('div');
     chartLink.className = 'mt-3 mb-3';
     chartLink.innerHTML = '<a href="/chart" class="btn btn-primary" target="_blank">View Full Chart</a>';
     terminalOutput.appendChild(chartLink);

    
    // // THE MODAL CODE
    // const chartButton = document.createElement('button');
    // chartButton.textContent = 'View Chart';
    // chartButton.className = 'btn btn-primary mt-3';
    // chartButton.onclick = () => {
    //     const chartContainer = document.getElementById('chartContainer');
    //     fetch('/api/chart-svg', {
    //         method: 'POST',
    //         headers: { 'Content-Type': 'application/json' },
    //         body: JSON.stringify(data)
    //     })
    //     .then(response => response.text())
    //     .then(svg => {
    //         chartContainer.innerHTML = svg;
    //         new bootstrap.Modal(document.getElementById('chartModal')).show();
    //     });
    // };
    // terminalOutput.appendChild(chartButton);

    appendLine('\n=== END OF REPORT ===');
}



