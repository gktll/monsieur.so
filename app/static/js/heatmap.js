
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


export function applyPlanetEnergiesBackground(heatmapData) {

    // Canvas setup
    const container = document.getElementById('networkContainer');
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const devicePixelRatio = window.devicePixelRatio || 1;
    ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear instead of recreating
    canvas.width = container.offsetWidth * devicePixelRatio;
    canvas.height = container.offsetHeight * devicePixelRatio;
    canvas.style.width = `${container.offsetWidth}px`;
    canvas.style.height = `${container.offsetHeight}px`;
    ctx.scale(devicePixelRatio, devicePixelRatio);
    container.appendChild(canvas);

    // Set repsonsive canvas size
    const canvasWidth = container.offsetWidth;
    const canvasHeight = container.offsetHeight;

    // Observer setup 
    const observerX = canvasWidth / 2;
    const observerY = canvasHeight * 0.7;

    // Draw observer marker and horizon
    ctx.strokeStyle = '#333';
    ctx.setLineDash([5, 5]);
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(observerX, observerY, 10, 0, Math.PI * 2);
    ctx.stroke();

    // Draw horizon parabola 
    ctx.beginPath();
    const curveAmplitude = 20;
    ctx.moveTo(0, observerY);
    
    for (let x = 0; x <= canvasWidth; x += 10) {
        const dx = x - observerX;
        const y = observerY + (curveAmplitude * (dx ** 2) / ((canvasWidth / 2) ** 2));
        ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Map planet data to positions with angular distance consideration
    const azimuthRadius = canvasWidth * 0.4;
    const altitudeRadius = canvasHeight * 0.4;
    console.log('Canvas dimensions:', canvasWidth, canvasHeight);
    console.log('Radius values:', { azimuthRadius, altitudeRadius });

    // Calculate base planet positions
    const planetCenters = heatmapData.map(planet => {
        const azimuthRadians = (planet.azimuth * Math.PI) / 180;
        const altitude = Math.max(Math.min(planet.altitude, 90), -90);

        // Calculate base position
        const baseX = observerX + azimuthRadius * Math.sin(azimuthRadians);
        const baseY = observerY - (altitudeRadius * altitude / 90);

        console.log(`${planet.planet} initial position:`, {
            azimuth: planet.azimuth,
            altitude,
            distance_au: planet.distance_au,
            baseX,
            baseY
            
        });

        return {
            ...planet,
            x: baseX,
            y: baseY,
            baseX,
            baseY,
            name: planet.planet
        };
    });
    
    // Find planets with similar azimuth positions
    planetCenters.forEach((p1, i) => {
        planetCenters.slice(i + 1).forEach(p2 => {
            // Just check horizontal distance
            const horizontalDistance = Math.abs(p1.baseX - p2.baseX);
            
            // If planets are closer than 40px horizontally
            if (horizontalDistance < 60) {
                console.log(`Horizontal overlap found: ${p1.name} and ${p2.name}`, {
                    horizontalDistance,
                    azimuthDiff: Math.abs(p1.azimuth - p2.azimuth),
                    p1_au: p1.distance_au,
                    p2_au: p2.distance_au
                });

                // Scale vertical offset by distance difference
                const distanceDiff = Math.abs(p1.distance_au - p2.distance_au);
                // Increased base offset since these are distant planets
                const verticalOffset = Math.min(distanceDiff * 3, 30); 
                
                if (p1.distance_au > p2.distance_au) {
                    p1.y -= verticalOffset;
                    p2.y += verticalOffset;
                } else {
                    p1.y += verticalOffset;
                    p2.y -= verticalOffset;
                }

                console.log(`Applied vertical offset: ${p1.name} and ${p2.name}:`, {
                    verticalOffset,
                    distanceDiff,
                    p1: { distance: p1.distance_au, oldY: p1.baseY, newY: p1.y },
                    p2: { distance: p2.distance_au, oldY: p2.baseY, newY: p2.y }
                });
            }
        });
    });

    // Log final positions
    console.log('Final positions:', planetCenters.map(p => ({
        planet: p.name,
        position: { x: p.x, y: p.y },
        moved: {
            dx: p.x - p.baseX,
            dy: p.y - p.baseY
        }
    })));

    // Draw planets 
    ctx.setLineDash([]);
    
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
        radialGradient.addColorStop(1, gradient.outer.color.slice(0, -2) + '00');
        
        ctx.globalCompositeOperation = 'overlay';
        ctx.fillStyle = radialGradient;
        ctx.beginPath();
        ctx.arc(center.x, center.y, gradient.outer.radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalCompositeOperation = 'source-over';
        
        ctx.beginPath();
        ctx.arc(center.x, center.y, 2, 0, Math.PI * 2);
        ctx.fillStyle = '#333';
        ctx.fill();

        ctx.font = '8px Arial';
        ctx.fillStyle = '#333';
        ctx.textAlign = 'left';
        ctx.fillText(
            `${center.name} (${center.distance_au.toFixed(2)} AU)`,
            center.x + 4,
            center.y
        );
    });

    container.style.backgroundImage = `url(${canvas.toDataURL()})`;
    container.style.backgroundSize = "cover";
    container.style.backgroundPosition = "center";
    container.style.backgroundRepeat = "no-repeat";

    triggerCombustWarnings(heatmapData);
}

