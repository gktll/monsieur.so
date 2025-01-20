// Import required modules
import { loadFullGraph } from './graphInit.js';
import { geolocateUser } from './geolocationService.js';
import { updateTerminalWithData } from './terminalOutput.js';
import { fetchCurrentHourAndFilter } from './graphFiltering.js';
// import { generateGradient, applyGradientToNetworkContainer } from './heatmap.js';
import { applyPlanetEnergiesBackground } from './heatmap.js';

// DOMContentLoaded: Initialize the terminal and geolocation logic
document.addEventListener('DOMContentLoaded', () => {
    // Initialize terminal output
    const terminalOutput = document.getElementById('terminalOutput');
    terminalOutput.textContent = '> Welcome to Monsieur.so Terminal\n';
    terminalOutput.textContent += '> For better accuracy, please allow location access.\n';
    terminalOutput.scrollTop = terminalOutput.scrollHeight;

    loadFullGraph();

    let observerLocation = {};


    // Fetch geolocation and planetary hour data
    geolocateUser(
        (data, latitude, longitude) => {
            observerLocation = { latitude, longitude };
            // Update the terminal with the fetched data
            updateTerminalWithData(data);

            fetchCurrentHourAndFilter(data);

            // Apply the gradient using heatmap data
            console.log('Heatmap Data:', data.heatmap_data);
            applyPlanetEnergiesBackground(data.heatmap_data);
        },
        (error) => {
            // Display error in the terminal
            terminalOutput.textContent += `> Error: ${error.message}\n`;
            terminalOutput.scrollTop = terminalOutput.scrollHeight;
        }
    );
});