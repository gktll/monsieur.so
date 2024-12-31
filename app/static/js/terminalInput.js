// terminal-input.js
const terminalInput = document.getElementById('terminalInput');
const terminalOutputHandler = document.getElementById('terminalOutput');

// Import chatHandler functions
import { chatHandler } from './terminalCommands.js';


terminalInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
        const userInput = terminalInput.value;
        terminalInput.value = '';
        
        // Display user input
        displayOutput(`> ${userInput}`);

        if (chatHandler.isGraphCommand(userInput) || /^-?\d+(\.\d+)?,\s*-?\d+(\.\d+)?(?:,\s*\d+\.\d+\.\d+)?$/.test(userInput.trim())) {
            // Handle graph visualization commands
            const response = chatHandler.processGraphCommand(userInput);
            displayOutput(response);
        } else {
            // Send other queries to the backend API
            fetch(`/api/terminal?query=${encodeURIComponent(userInput)}`)
                .then(response => response.json())
                .then(data => {
                    displayOutput(data.response);
                })
                .catch(error => {
                    displayOutput(`Error: ${error.message}`);
                });
        }
    }
});

// Helper function to display output
function displayOutput(text) {
    terminalOutputHandler.textContent += `${text}\n`;
    terminalOutputHandler.scrollTop = terminalOutputHandler.scrollHeight;
}







