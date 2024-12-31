import { loadFullGraph} from './graphInit.js';
import { fetchCurrentHourAndFilter} from './graphFiltering.js';
import { updateTerminalWithData} from './terminalOutput.js';

// CHAT COMMANDS
export const chatHandler = {
    isGraphCommand(command) {
        const graphCommands = ['default', 'current hour'];
        return graphCommands.includes(command.toLowerCase().trim());
    },


    processGraphCommand(command) {
        const [lat, lon] = command.split(',').map(n => parseFloat(n.trim()));
        
        if (!isNaN(lat) && !isNaN(lon)) {
            // It's coordinates, handle them
            fetch('/api/geolocation_ephemeris', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ latitude: lat, longitude: lon }),
            })
                .then((response) => response.json())
                .then((data) => {
                    fetchCurrentHourAndFilter(data);
                    updateTerminalWithData(data);
                })
                .catch((error) => {
                    console.error('Error fetching data:', error);
                    const terminalOutput = document.getElementById('terminalOutput');
                    terminalOutput.textContent += `> Error: ${error.message}\n`;
                    terminalOutput.scrollTop = terminalOutput.scrollHeight;
                });

            return `Processing data for Latitude: ${lat}, Longitude: ${lon}`;
        }

        // Handle regular commands
        switch (command.toLowerCase().trim()) {
            case 'default':
                loadFullGraph();
                return 'Showing default graph view';

            case 'current hour':
                return this.handleCurrentHour();

            default:
                return 'Unknown graph command.';
        }
    },


    // COMMAND "CURRENT HOUR" FILTER AGAIN ACCORDING TO USER GEOLOCATION DATA
    handleCurrentHour() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const { latitude, longitude } = position.coords;
    
                    // Fetch data from the existing /api/geolocation_ephemeris route
                    fetch('/api/geolocation_ephemeris', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ latitude, longitude }),
                    })
                        .then((response) => response.json())
                        .then((data) => {
                            // Refilter the graph
                            fetchCurrentHourAndFilter(data);
    
                            // Update the terminal output
                            const terminalOutput = document.getElementById('terminalOutput');
                            terminalOutput.textContent += `> Current hour filtering applied.\n`;
                            updateTerminalWithData(data); // Display the report again in the terminal
                        })
                        .catch((error) => {
                            console.error('Error fetching hour data:', error);
                            const terminalOutput = document.getElementById('terminalOutput');
                            terminalOutputHandler.textContent += `Error: ${error.message}\n`;
                            terminalOutputHandler.scrollTop = terminalOutputHandler.scrollHeight;
                        });
                },
                (error) => {
                    console.error('Geolocation error:', error.message);
                    const terminalOutput = document.getElementById('terminalOutput');
                    terminalOutputHandler.textContent += '> Could not fetch geolocation.\n';
                    terminalOutputHandler.scrollTop = terminalOutputHandler.scrollHeight;
                }
            );
            return 'Processing current hour...'; // Immediate response
        } else {
            terminalOutputHandler.textContent += '> Geolocation is not supported by this browser.\n';
            terminalOutputHandler.scrollTop = terminalOutputHandler.scrollHeight;
        }
    }
};