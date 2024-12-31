/**
* Updates terminal with complete chart data, making house spans explicit
* @param {Object} data - The ephemeris and chart data
*/
export function updateTerminalWithData(data) {
    const terminalOutput = document.getElementById('terminalOutput');
    
    const appendLine = (text) => {
        terminalOutput.textContent += `${text}\n`;
        terminalOutput.scrollTop = terminalOutput.scrollHeight;
    };

 
    // Magic Hour and Time Info remain the same
    appendLine('\n=== MAGICAL HOUR INFORMATION ===');
    appendLine(`> Current Planetary Hour: ${data.current_planetary_hour}`);
    appendLine(`> Ruling Planet: ${data.ruling_planet}`);
    
    if (data.neo4j_data && data.neo4j_data.hour) {
        appendLine(`> Hour Name: ${data.neo4j_data.hour.label || 'N/A'}`);
        appendLine('> Magical Correspondences:');
        data.neo4j_data.connections.forEach((connection) => {
            const targetLabel = connection.targetNode.label || 'Unnamed Connection';
            const relationType = connection.relationshipType.replace(/_/g, ' ').toUpperCase();
            appendLine(`  - [${relationType}] ${targetLabel}`);
        });
    }
    
    appendLine('\n=== TIME INFORMATION ===');
    appendLine(`> Local Time: ${data.current_time || 'N/A'}`);
    appendLine(`> Sunrise: ${data.sunrise}, Sunset: ${data.sunset}`);
    appendLine(`> Current UTC Time: ${data.utc_time || 'N/A'}`);
    

    // Chart Angles with explicit degrees
    appendLine('\n=== CHART ANGLES ===');
    if (data.angles) {
        for (const [angle, info] of Object.entries(data.angles)) {
            appendLine(`> ${angle.toUpperCase()}: ${info.degree}° ${info.sign} (${info.absolute_degree}° total)`);
        }
    }

    // Houses and their occupancy
    appendLine('\n=== HOUSES AND OCCUPANCY ===');
    if (data.houses) {
        for (let i = 1; i <= 12; i++) {
            const house = data.houses[i];
            const nextHouse = data.houses[i === 12 ? 1 : i + 1];

            appendLine(`> House ${i}:`);
            appendLine(`  Cusp: ${house.degree}° ${house.sign} (${house.absolute_degree}° total)`);

            // Generate span text from backend spans logic (if available)
            const spanText = `${house.sign} ${house.degree}° → ${nextHouse.sign} ${nextHouse.degree}°`;
            appendLine(`  Spans: ${spanText}`);

            // List occupying planets
            if (house.planets && house.planets.length > 0) {
                appendLine('  Occupying Planets:');
                house.planets.forEach(planet => {
                    const retrograde = planet.is_retrograde ? ' (Retrograde)' : '';
                    const stationary = planet.is_stationary ? ' (Stationary)' : '';
                    const dailyMotion = planet.daily_motion ? ` [${planet.daily_motion}°/day]` : '';
                    appendLine(`    - ${planet.name}: ${planet.degree}° ${planet.sign}${retrograde}${stationary}${dailyMotion}`);
                });
            } else {
                appendLine('  Occupying Planets: None');
            }
            appendLine('');
        }
    }

    appendLine('\n=== KEY PLANETARY ASPECTS ===');
    const aspects = data.aspects;
    if (aspects && aspects.length > 0) {
        aspects.forEach((aspect) => {
            appendLine(`> ${aspect.planet1} ${aspect.aspect} ${aspect.planet2} (${aspect.angular_distance}°)`);
        });
    } else {
        appendLine("> No significant aspects found.");
        }


    appendLine('\n=== MOON-SPECIFIC PROPERTIES ===');
    const moon = data.moon_data;
    appendLine(`> Phase: ${moon.phase}`);
    appendLine(`> Phase Angle: ${moon.phase_angle}°`);
    appendLine(`> Distance: ${moon.distance_km} km (${moon.distance_au} AU)`);
    appendLine(`> Declination: ${moon.declination}°`);
    if (moon.is_out_of_bounds) {
        appendLine("> The Moon is Out of Bounds (OOB)");
    } else {
        appendLine("> The Moon is within bounds.");
    }


    appendLine("\n=== PLANETARY DISTANCES FROM EARTH / OBSERVER ===");
    if (data.planetary_distances) {
        const distances = Object.entries(data.planetary_distances);
        distances.sort(([, a], [, b]) => a - b); // Sort by distance (ascending)
        distances.forEach(([planet, distance]) => {
            appendLine(`> ${planet}: ${distance} AU`);
        });
    } else {
        appendLine("> No planetary distance data available.");
    }

    // Planetary Positions Summary
    appendLine('\n=== PLANETARY POSITIONS SUMMARY ===');
    if (data.planetary_positions) {
        for (const planet in data.planetary_positions) {
            const pos = data.planetary_positions[planet];
            const retrograde = pos.is_retrograde ? ' (Retrograde)' : '';
            const stationary = pos.is_stationary ? ' (Stationary)' : '';
            const dailyMotion = pos.daily_motion ? ` [${pos.daily_motion}°/day]` : '';
            appendLine(`> ${planet}: ${pos.degree}° ${pos.sign}${retrograde}${stationary} (${pos.longitude}° total)${dailyMotion}`);
        }
    }
 
    appendLine('\n=== END OF REPORT ===');
 }