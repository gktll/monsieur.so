// const PLANET_DIAMETERS = {
//     Sun: 1392000, 
//     Mercury: 4879,
//     Venus: 12104,
//     Earth: 12742,
//     Mars: 6779,
//     Jupiter: 139820,
//     Saturn: 116460,
//     Uranus: 50724,
//     Neptune: 49244,
//     Pluto: 2376,
//     Moon: 3475
// };



// function triggerCombustWarnings(heatmapData) {
//     heatmapData.forEach((entry) => {
//         if (entry.is_combust) {
//             console.warn(`Warning: ${entry.planet} is combust. Avoid critical actions.`);
//         }
//         if (entry.planet === "Moon" && entry.is_combust) {
//             console.warn(`Additional Warning: The Moon is combust. Exercise caution in decision-making.`);
//         }
//     });
// }


// export function applyPlanetEnergiesBackground(heatmapData) {
//     const container = document.getElementById('networkContainer');

//     if (!container) {
//         console.error("Container not found!");
//         return;
//     }

//     // Create and configure canvas
//     const canvas = document.createElement('canvas');
//     const ctx = canvas.getContext('2d');
//     const devicePixelRatio = window.devicePixelRatio || 1;

//     // Scale canvas for high-DPI displays
//     canvas.width = container.offsetWidth * devicePixelRatio;
//     canvas.height = container.offsetHeight * devicePixelRatio;
//     canvas.style.width = `${container.offsetWidth}px`;
//     canvas.style.height = `${container.offsetHeight}px`;
//     ctx.scale(devicePixelRatio, devicePixelRatio);

//     container.appendChild(canvas);

//     const canvasWidth = container.offsetWidth;
//     const canvasHeight = container.offsetHeight;

//     // Observer location (canvas center)
//     const observerX = canvasWidth / 2;
//     const observerY = canvasHeight * 0.7; // Move observer lower for curved horizon

//     // Draw observer at the center
//     ctx.strokeStyle = 'rgba(128,128,128,0.5)';
//     ctx.setLineDash([5, 5]);
//     ctx.lineWidth = 1;
//     ctx.beginPath();
//     ctx.arc(observerX, observerY, 10, 0, Math.PI * 2); // Observer's marker
//     ctx.stroke();

//     // Draw subtly curved horizon line
//     ctx.setLineDash([5, 5]);
//     ctx.lineWidth = 1;
//     ctx.beginPath();
//     const curveAmplitude = 20; // Subtle curve amount
//     ctx.moveTo(0, observerY);
//     // Here we draw the parabola
//     for (let x = 0; x <= canvasWidth; x += 10) {
//         const dx = x - observerX;
//         const y = observerY + (curveAmplitude * (dx ** 2) / ((canvasWidth / 2) ** 2));
//         ctx.lineTo(x, y);
//     }
//     ctx.stroke();

//     // Find min and max distances for normalization
//     const distances = heatmapData.map(planet => planet.distance_au);
//     const minDistance = Math.min(...distances);
//     const maxDistance = Math.max(...distances);

//     // Normalize size function (combining distance and physical size)
//     const normalizeSize = (distance, diameter) => {
//         const maxDistanceSize = 25; // Maximum size contribution from distance
//         const minDistanceSize = 5;  // Minimum size contribution from distance

//         // Normalize distance using logarithmic scaling
//         const logDistance = Math.log10(distance + 1);
//         const minLog = Math.log10(minDistance + 1);
//         const maxLog = Math.log10(maxDistance + 1);
//         const distanceSize = (
//             ((maxLog - logDistance) / (maxLog - minLog)) *
//                 (maxDistanceSize - minDistanceSize) +
//             minDistanceSize
//         );

//         // Normalize physical size
//         const maxDiameter = Math.max(...Object.values(PLANET_DIAMETERS));
//         const minDiameter = Math.min(...Object.values(PLANET_DIAMETERS));
//         const maxDiameterSize = 50; // Maximum size contribution from diameter
//         const minDiameterSize = 5;  // Minimum size contribution from diameter
//         const diameterSize = (
//             ((diameter - minDiameter) / (maxDiameter - minDiameter)) *
//                 (maxDiameterSize - minDiameterSize) +
//             minDiameterSize
//         );

//         // Combine both factors with balanced weights
//         return 0.6 * distanceSize + 0.4 * diameterSize; // Adjust weights as needed
//     };

//     // Map planet data to positions and sizes
//     const azimuthRadius = canvasWidth * 0.4;
//     const altitudeRadius = canvasHeight * 0.4;

//     const planetCenters = heatmapData.map(planet => {
//         const azimuthRadians = (planet.azimuth * Math.PI) / 180;
//         const altitude = Math.max(Math.min(planet.altitude, 90), -90); // Constrain altitude
//         const size = normalizeSize(planet.distance_au, PLANET_DIAMETERS[planet.planet]);

//         console.log(
//             `Planet: ${planet.planet}, Distance: ${planet.distance_au}, Diameter: ${PLANET_DIAMETERS[planet.planet]}, Size: ${size}`
//         );

//         return {
//             x: observerX + azimuthRadius * Math.sin(azimuthRadians),
//             y: observerY - (altitudeRadius * altitude / 90),
//             color: planet.color,
//             intensity: planet.intensity,
//             name: planet.planet,
//             size: size,
//             distance_au: planet.distance_au,
//         };
//     });

//     ctx.setLineDash([]); // Reset to solid line

//     // Draw planets
//     planetCenters.forEach(center => {
//         ctx.fillStyle = center.color;
//         ctx.beginPath();
//         ctx.arc(center.x, center.y, center.size, 0, Math.PI * 2);
//         ctx.fill();

//         ctx.strokeStyle = '#ccc';
//         ctx.lineWidth = 1;
//         ctx.stroke();

//         ctx.font = '8px Arial';
//         ctx.fillStyle = '#ccc';
//         ctx.fillText(
//             `${center.name} (${center.distance_au.toFixed(2)} AU)`,
//             center.x + center.size + 5,
//             center.y
//         );
//     });

//     container.style.backgroundImage = `url(${canvas.toDataURL()})`;
//     container.style.backgroundSize = "cover";
//     container.style.backgroundPosition = "center";
//     container.style.backgroundRepeat = "no-repeat";

//     triggerCombustWarnings(heatmapData);
// }



function triggerCombustWarnings(heatmapData) {
    heatmapData.forEach((entry) => {
        if (entry.is_combust) {
            console.warn(`Warning: ${entry.planet} is combust. Avoid critical actions.`);
        }
        if (entry.planet === "Moon" && entry.is_combust) {
            console.warn(`Additional Warning: The Moon is combust. Exercise caution in decision-making.`);
        }
    });
}

const PLANET_DIAMETERS = {
    Sun: 1392000, 
    Mercury: 4879,
    Venus: 12104,
    Earth: 12742,
    Mars: 6779,
    Jupiter: 139820,
    Saturn: 116460,
    Uranus: 50724,
    Neptune: 49244,
    Pluto: 2376,
    Moon: 3475
};

// Helper create color shades
function createColorShades(baseColor, intensity) {
    const r = parseInt(baseColor.slice(1,3), 16);
    const g = parseInt(baseColor.slice(3,5), 16);
    const b = parseInt(baseColor.slice(5,7), 16);

    // Core opacity should reflect intensity more directly
    const coreOpacity = Math.min(intensity * 0.9, 0.9);  // Strong core
    // Gradient opacity falls off more gradually
    const middleOpacity = coreOpacity * 0.5;
    const outerOpacity = coreOpacity * 0.1;  // Very subtle at edges

    return {
        core: `rgba(${r}, ${g}, ${b}, ${coreOpacity})`,
        inner: `rgba(${r}, ${g}, ${b}, ${coreOpacity * 0.8})`,
        middle: `rgba(${r}, ${g}, ${b}, ${middleOpacity})`,
        outer: `rgba(${r}, ${g}, ${b}, ${outerOpacity})`
    };
}


// export function applyPlanetEnergiesBackground(heatmapData) {
//     const container = document.getElementById('networkContainer');

//     if (!container) {
//         console.error("Container not found!");
//         return;
//     }

//     // Create and configure canvas
//     const canvas = document.createElement('canvas');
//     const ctx = canvas.getContext('2d');
//     const devicePixelRatio = window.devicePixelRatio || 1;

//     // Scale canvas for high-DPI displays
//     canvas.width = container.offsetWidth * devicePixelRatio;
//     canvas.height = container.offsetHeight * devicePixelRatio;
//     canvas.style.width = `${container.offsetWidth}px`;
//     canvas.style.height = `${container.offsetHeight}px`;
//     ctx.scale(devicePixelRatio, devicePixelRatio);

//     container.appendChild(canvas);

//     const canvasWidth = container.offsetWidth;
//     const canvasHeight = container.offsetHeight;

//     // Observer location (canvas center)
//     const observerX = canvasWidth / 2;
//     const observerY = canvasHeight * 0.7; // Move observer lower for curved horizon

//     // Draw observer at the center
//     ctx.strokeStyle = 'rgba(128,128,128,0.5)';
//     ctx.setLineDash([5, 5]);
//     ctx.lineWidth = 1;
//     ctx.beginPath();
//     ctx.arc(observerX, observerY, 10, 0, Math.PI * 2); // Observer's marker
//     ctx.stroke();

//     // Draw subtly curved horizon line
//     ctx.setLineDash([5, 5]);
//     ctx.lineWidth = 1;
//     ctx.beginPath();
//     const curveAmplitude = 20; // Subtle curve amount
//     ctx.moveTo(0, observerY);
//     // Here we draw the parabola
//     for (let x = 0; x <= canvasWidth; x += 10) {
//         const dx = x - observerX;
//         const y = observerY + (curveAmplitude * (dx ** 2) / ((canvasWidth / 2) ** 2));
//         ctx.lineTo(x, y);
//     }
//     ctx.stroke();


//     // Find min and max distances for normalization
//     const distances = heatmapData.map(planet => planet.distance_au);
//     const minDistance = Math.min(...distances);
//     const maxDistance = Math.max(...distances);

//     // Normalize size function (combining distance and physical size)
//     const normalizeSize = (distance, diameter) => {
//         const maxDistanceSize = 25; // Maximum size contribution from distance
//         const minDistanceSize = 5;  // Minimum size contribution from distance

//         // Normalize distance using logarithmic scaling
//         const logDistance = Math.log10(distance + 1);
//         const minLog = Math.log10(minDistance + 1);
//         const maxLog = Math.log10(maxDistance + 1);
//         const distanceSize = (
//             ((maxLog - logDistance) / (maxLog - minLog)) *
//                 (maxDistanceSize - minDistanceSize) +
//             minDistanceSize
//         );

//         // Normalize physical size
//         const maxDiameter = Math.max(...Object.values(PLANET_DIAMETERS));
//         const minDiameter = Math.min(...Object.values(PLANET_DIAMETERS));
//         const maxDiameterSize = 50; // Maximum size contribution from diameter
//         const minDiameterSize = 5;  // Minimum size contribution from diameter
//         const diameterSize = (
//             ((diameter - minDiameter) / (maxDiameter - minDiameter)) *
//                 (maxDiameterSize - minDiameterSize) +
//             minDiameterSize
//         );

//         // Combine both factors with balanced weights
//         return 0.6 * distanceSize + 0.4 * diameterSize; // Adjust weights as needed
//     };

//     // Map planet data to positions and sizes
//     const azimuthRadius = canvasWidth * 0.4;
//     const altitudeRadius = canvasHeight * 0.4;

//     const planetCenters = heatmapData.map(planet => {
//         const azimuthRadians = (planet.azimuth * Math.PI) / 180;
//         const altitude = Math.max(Math.min(planet.altitude, 90), -90); // Constrain altitude
//         const size = normalizeSize(planet.distance_au, PLANET_DIAMETERS[planet.planet]);

//         console.log(
//             `Planet: ${planet.planet}, Distance: ${planet.distance_au}, Diameter: ${PLANET_DIAMETERS[planet.planet]}, Size: ${size}`
//         );

//         return {
//             x: observerX + azimuthRadius * Math.sin(azimuthRadians),
//             y: observerY - (altitudeRadius * altitude / 90),
//             color: planet.color,
//             intensity: planet.intensity,
//             name: planet.planet,
//             size: size,
//             distance_au: planet.distance_au,
//         };
//     });

//     ctx.setLineDash([]); // Reset to solid line

//     // Draw planets
//     // In your drawing loop
//     planetCenters.forEach(center => {
//         console.log(`Drawing ${center.name} gradient:`);
//         console.log(`- Base size: ${center.size}`);
//         console.log(`- Intensity: ${center.intensity}`);

//         // Calculate gradient radiuses
//         const innerRadius = center.size;  // From normalizeSize

//         const GRADIENT_SPREAD_FACTOR = Math.min(canvasWidth, canvasHeight) / 100;
//         const outerRadius = center.size * (1 + (center.intensity * GRADIENT_SPREAD_FACTOR));
       
//         console.log(`- Inner radius: ${innerRadius}, Outer radius: ${outerRadius}`);

//         // Get color variations
//         const colors = createColorShades(center.color, center.intensity);
//         console.log(`- Color variations created from base: ${center.color}`);

//         // Create and apply gradient
//         const gradient = ctx.createRadialGradient(
//             center.x, center.y, 0,           // Inner circle start
//             center.x, center.y, outerRadius  // Outer circle end
//         );

//         // More gradual color stops for smoother blending
//         gradient.addColorStop(0, colors.core);
//         gradient.addColorStop(0.2, colors.inner);
//         gradient.addColorStop(0.6, colors.middle);
//         gradient.addColorStop(1, colors.outer);

//         // Use 'screen' blend mode for additive blending
//         ctx.globalCompositeOperation = 'screen';
//         ctx.fillStyle = gradient;
//         ctx.beginPath();
//         ctx.arc(center.x, center.y, outerRadius, 0, Math.PI * 2);
//         ctx.fill();
//         ctx.globalCompositeOperation = 'source-over';

//         // 3. Draw the reference circle (outline)
//         ctx.strokeStyle = '#000';
//         ctx.lineWidth = 1;
//         ctx.beginPath();
//         ctx.arc(center.x, center.y, center.size, 0, Math.PI * 2);
//         ctx.stroke();

//         // Add planet label
//         ctx.font = '8px Arial';
//         ctx.fillStyle = '#000';
//         ctx.fillText(
//             `${center.name} (${center.distance_au.toFixed(2)} AU)`,
//             center.x,
//             center.y
//         );
//     });


//     container.style.backgroundImage = `url(${canvas.toDataURL()})`;
//     container.style.backgroundSize = "cover";
//     container.style.backgroundPosition = "center";
//     container.style.backgroundRepeat = "no-repeat";

//     triggerCombustWarnings(heatmapData);
// }






export function applyPlanetEnergiesBackground(heatmapData) {
    const container = document.getElementById('networkContainer');

    if (!container) {
        console.error("Container not found!");
        return;
    }

    // Create and configure canvas
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const devicePixelRatio = window.devicePixelRatio || 1;

    // Scale canvas for high-DPI displays
    canvas.width = container.offsetWidth * devicePixelRatio;
    canvas.height = container.offsetHeight * devicePixelRatio;
    canvas.style.width = `${container.offsetWidth}px`;
    canvas.style.height = `${container.offsetHeight}px`;
    ctx.scale(devicePixelRatio, devicePixelRatio);

    container.appendChild(canvas);

    const canvasWidth = container.offsetWidth;
    const canvasHeight = container.offsetHeight;

    // Observer location (canvas center)
    const observerX = canvasWidth / 2;
    const observerY = canvasHeight * 0.7; // Move observer lower for curved horizon

    // Draw observer at the center
    ctx.strokeStyle = 'rgba(128,128,128,0.5)';
    ctx.setLineDash([5, 5]);
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(observerX, observerY, 10, 0, Math.PI * 2); // Observer's marker
    ctx.stroke();

    // Draw subtly curved horizon line
    ctx.setLineDash([5, 5]);
    ctx.lineWidth = 1;
    ctx.beginPath();
    const curveAmplitude = 20; // Subtle curve amount
    ctx.moveTo(0, observerY);
    
    // Draw the parabola
    for (let x = 0; x <= canvasWidth; x += 10) {
        const dx = x - observerX;
        const y = observerY + (curveAmplitude * (dx ** 2) / ((canvasWidth / 2) ** 2));
        ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Map planet data to positions
    const azimuthRadius = canvasWidth * 0.4;
    const altitudeRadius = canvasHeight * 0.4;

    const planetCenters = heatmapData.map(planet => {
        const azimuthRadians = (planet.azimuth * Math.PI) / 180;
        const altitude = Math.max(Math.min(planet.altitude, 90), -90); // Constrain altitude

        // Create a default gradient if not present
        const defaultGradient = {
            core: { 
                radius: planet.normalized_planet_size, 
                color: planet.color || '#FFFFFF' 
            },
            inner: { 
                radius: planet.normalized_planet_size * 1.5, 
                color: `${planet.color || '#FFFFFF'}D4` 
            },
            outer: { 
                radius: planet.normalized_planet_size * 2.0, 
                color: `${planet.color || '#FFFFFF'}1A` 
            }
        };
        
        return {
            x: observerX + azimuthRadius * Math.sin(azimuthRadians),
            y: observerY - (altitudeRadius * altitude / 90),
            color: planet.color,
            name: planet.planet,
            size: planet.normalized_planet_size,
            distance_au: planet.distance_au,
            gradient: planet.gradient || defaultGradient
        };
    });

    ctx.setLineDash([]); // Reset to solid line

    // Draw planets
    planetCenters.forEach(center => {
        const gradient = center.gradient || {
            core: { radius: center.size, color: center.color || '#FFFFFF' },
            inner: { radius: center.size * 1.5, color: '#DDDDDD' },
            outer: { radius: center.size * 2.0, color: '#AAAAAA' }
        };
        const radialGradient = ctx.createRadialGradient(
            center.x, center.y, 0,
            center.x, center.y, gradient.outer.radius
        );
        
        radialGradient.addColorStop(0, gradient.core.color);
        radialGradient.addColorStop(0.5, gradient.inner.color);
        radialGradient.addColorStop(1, gradient.outer.color);
        
        ctx.globalCompositeOperation = 'screen';
        ctx.fillStyle = radialGradient;
        ctx.beginPath();
        ctx.arc(center.x, center.y, gradient.outer.radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalCompositeOperation = 'source-over';
        
        // Reference circle
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(center.x, center.y, center.size, 0, Math.PI * 2);
        ctx.stroke();
    });

    container.style.backgroundImage = `url(${canvas.toDataURL()})`;
    container.style.backgroundSize = "cover";
    container.style.backgroundPosition = "center";
    container.style.backgroundRepeat = "no-repeat";

    triggerCombustWarnings(heatmapData);
}