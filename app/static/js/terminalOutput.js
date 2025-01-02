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

    // Magic Hour and Time Info
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

    // Chart Angles (if available)
    appendLine('\n=== CHART ANGLES ===');
    if (data.angles) {
        for (const [angle, info] of Object.entries(data.angles)) {
            appendLine(`> ${angle.toUpperCase()}: ${info.degree}° ${info.sign} (${info.absolute_degree}° total)`);
        }
    }

    // Houses and Occupancy (Placeholder for now)
    appendLine('\n=== HOUSES AND OCCUPANCY ===');
    appendLine('> Houses data is not yet implemented.');

    // Key Planetary Aspects
    appendLine('\n=== KEY PLANETARY ASPECTS ===');
    const aspects = data.ephemeris?.aspects || [];
    if (aspects.length > 0) {
        aspects.forEach((aspect) => {
            appendLine(`> ${aspect.planet1} ${aspect.aspect} ${aspect.planet2} (${aspect.angular_distance}°)`);
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

    // Planetary Distances (If Provided)
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

    appendLine('\n=== END OF REPORT ===');
}
