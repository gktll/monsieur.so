
// ------------------------
// THE DRAGGABLE TERMINAL
// ------------------------

// const terminal = document.getElementById('terminal');
// const networkContainer = document.getElementById('networkContainer');
// const dragHandle = document.getElementById('dragHandle');

// let startY, startHeight, startNetworkHeight;

// // Start dragging
// dragHandle.addEventListener('mousedown', (e) => {
//   startY = e.clientY;
//   startHeight = terminal.offsetHeight;
//   startNetworkHeight = networkContainer.offsetHeight;

//   // Disable transition during resize
//   terminal.style.transition = 'none';

//   document.addEventListener('mousemove', resizeTerminal);
//   document.addEventListener('mouseup', stopResize);
// });

// // Perform resizing
// function resizeTerminal(e) {
//   const delta = startY - e.clientY;
//   const newHeight = Math.max(startHeight + delta, 50); // Minimum height = 50px
//   terminal.style.height = `${newHeight}px`;

//   // Automatically collapse terminal if dragged to the minimum height
//   if (newHeight <= 50) {
//       terminal.classList.add('closed');
//   } else {
//       terminal.classList.remove('closed');
//   }
// }

// // Stop dragging
// function stopResize() {
//   document.removeEventListener('mousemove', resizeTerminal);
//   document.removeEventListener('mouseup', stopResize);

//   // Re-enable transition after resize
//   terminal.style.transition = 'height 0.3s ease, transform 0.3s ease, opacity 0.3s ease';
// }



// // Initialize terminal state
// document.addEventListener('DOMContentLoaded', () => {
//   // Ensure drag handle remains visible when collapsed
//   terminal.classList.add('closed'); // Start with the terminal collapsed
// });


// Terminal dragging functionality
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
    networkContainer.style.transition = 'none';
    
    document.addEventListener('mousemove', resizeTerminal);
    document.addEventListener('mouseup', stopResize);
});

// Perform resizing
function resizeTerminal(e) {
    const delta = startY - e.clientY;
    const newHeight = Math.max(startHeight + delta, 24); // Minimum height is handle height
    
    terminal.style.height = `${newHeight}px`;
    
    // Update network container height
    const newNetworkHeight = Math.max(startNetworkHeight - delta, 50);
    networkContainer.style.height = `${newNetworkHeight}px`;
    
    // Add/remove collapsed class based on height
    if (newHeight <= 24) {
        terminal.classList.add('collapsed');
    } else {
        terminal.classList.remove('collapsed');
    }
}

// Stop dragging
function stopResize() {
    document.removeEventListener('mousemove', resizeTerminal);
    document.removeEventListener('mouseup', stopResize);
    
    // Re-enable transitions
    terminal.style.transition = 'height 0.3s ease';
    networkContainer.style.transition = 'height 0.3s ease';
}

// Remove the open/close button event listeners since we're using drag to collapse
document.addEventListener('DOMContentLoaded', () => {
    // Remove the floating open button if it exists
    const openButton = document.getElementById('openTerminalButton');
    if (openButton) {
        openButton.remove();
    }
});