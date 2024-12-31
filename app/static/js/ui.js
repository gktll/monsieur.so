
// ------------------------
// THE DRAGGABLE TERMINAL
// ------------------------

const terminal = document.getElementById('terminal');
const networkContainer = document.getElementById('networkContainer');
const dragHandle = document.getElementById('dragHandle');

let startY, startHeight, startNetworkHeight;

// Start dragging
dragHandle.addEventListener('mousedown', (e) => {
  startY = e.clientY;
  startHeight = terminal.offsetHeight;
  startNetworkHeight = networkContainer.offsetHeight;

  // Disable transition during resize
  terminal.style.transition = 'none';

  document.addEventListener('mousemove', resizeTerminal);
  document.addEventListener('mouseup', stopResize);
});

// Perform resizing
function resizeTerminal(e) {
    const delta = startY - e.clientY;
    const newHeight = Math.max(startHeight + delta, 50); // Minimum height = 50px
    terminal.style.height = `${newHeight}px`;
  
    const newNetworkHeight = Math.max(startNetworkHeight - delta, 50); // Minimum network height
    networkContainer.style.height = `${newNetworkHeight}px`;
  }

// Stop dragging
function stopResize() {
  document.removeEventListener('mousemove', resizeTerminal);
  document.removeEventListener('mouseup', stopResize);

  // Re-enable transition after resize
  terminal.style.transition = 'height 0.3s ease, transform 0.3s ease, opacity 0.3s ease';
}



// ------------------------
// OPEN CLOSE / TERMINAL
// ------------------------

document.addEventListener('DOMContentLoaded', () => {
    const terminal = document.getElementById('terminal');
    const closeButton = document.getElementById('closeTerminalButton');
    const openButton = document.getElementById('openTerminalButton');

    // Close terminal
    closeButton.addEventListener('click', () => {
        terminal.classList.add('closed'); // Add the "closed" class for smooth transition
        openButton.style.display = 'block';
    });

    // Reopen terminal
    openButton.addEventListener('click', () => {
        terminal.classList.remove('closed'); // Remove the "closed" class for smooth transition
        terminal.style.display = 'flex';
        openButton.style.display = 'none';
    });
});

