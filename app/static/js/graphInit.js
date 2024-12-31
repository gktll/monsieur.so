// initGraph.js
/**
 * Graph initialization and filtering utilities.
 * Contains network configuration and node filtering logic.
 * Used by graphFiltering.js for setting up and managing the graph visualization.
 */


// Node filtering configuration
export const nodeFilters = {
    // List of node patterns to exclude from visualization
    excludedPatterns: [
        'MagicHourEntity',
        'PlanetEntity',
        'WeekDayEntity',
        'SpiritualEntity',
        'ChemicalSubstanceEntity'
    ],

    /**
     * Check if a node should be excluded from visualization
     * @param {Object} node - Node to check
     * @returns {boolean} True if node should be excluded
     */
    shouldExcludeNode: (node) => {
        return nodeFilters.excludedPatterns.some(pattern => 
            node.id === pattern || node.label === pattern
        );
    },

    /**
     * Filter nodes based on exclusion patterns
     * @param {Array} nodes - Array of nodes to filter
     * @returns {Array} Filtered nodes array
     */
    getFilteredNodes: (nodes) => {
        return nodes.filter(node => !nodeFilters.shouldExcludeNode(node));
    },



    /**
     * Get edges between filtered nodes
     * @param {Array} edges - Array of edges
     * @param {Array} filteredNodes - Array of filtered nodes
     * @returns {Array} Filtered edges array
     */
    getFilteredEdges: (edges, filteredNodes) => {
        return edges.filter(edge => 
            filteredNodes.some(n => n.id === edge.from) && 
            filteredNodes.some(n => n.id === edge.to)
        );
    }
};


/**
 * Initialize the network visualization with nodes and edges
 * @param {Array} nodes - Array of nodes to visualize
 * @param {Array} edges - Array of edges to visualize
 * @returns {vis.Network} Initialized network instance
 */

export function initializeNetwork(nodes = [], edges = []) {
    const container = document.getElementById('network');
    const options = {
        layout: { improvedLayout: false },
        physics: {
            enabled: true,
            solver: 'forceAtlas2Based',
            forceAtlas2Based: {
                gravitationalConstant: -25,     // Gentle repulsion
                centralGravity: 0.005,          // Very light pull to center
                springLength: 200,              // Longer edges
                springConstant: 0.02,           // Soft springs
                damping: 0.15,                  // Smooth movement
                avoidOverlap: 0.5
            },
            stabilization: { 
                enabled: true,
                iterations: 100,                // Reduced iterations
                updateInterval: 50,
                onlyDynamicEdges: false,
                fit: true
            }
        },
        interaction: { hover: true, tooltipDelay: 200 },
        nodes: { shape: 'dot', size: 16 },
        edges: { 
            smooth: { type: 'continuous' },     // Changed from dynamic
            width: 1                            // Thinner edges
        }
    };

    const network = new vis.Network(container, { nodes, edges }, options);

    // Enable physics on double-click
    network.on('doubleClick', () => {
        network.setOptions({ physics: { enabled: true } });
        setTimeout(() => {
            network.setOptions({ physics: { enabled: false } });
        }, 3000); // Allow movement for 3 seconds
    });

    return network;
}



/**
 * Load and initialize the full graph visualization
 * Fetches graph data from the API and sets up the initial network view
 * with default styling and filtering
 */

export function loadFullGraph() {
    fetch('/api/graph_data')
        .then((response) => response.json())
        .then((data) => {
            if (!data.nodes || !data.edges) {
                console.error('No graph data received:', data);
                return;
            }

            // Exclude class nodes (e.g., "MagicHourEntity") and specific edges
            const excludedNodeLabels = ['MagicHourEntity'];
            const excludedEdgeLabels = ['IS_PART_OF_DAY', 'HOUR_RULED_BY'];

            const nodes = new vis.DataSet(data.nodes.filter(node => {
                return !excludedNodeLabels.includes(node.label);
            }).map(node => ({
                ...node, // Spread existing node properties
                shape: 'dot',
                size: 16,
                color: { background: 'lightblue', border: 'blue' },
            })));

            const edges = new vis.DataSet(data.edges.filter(edge => {
                return !excludedEdgeLabels.includes(edge.label);
            }).map(edge => ({
                ...edge, // Spread existing edge properties
                smooth: { type: 'dynamic' },
                width: 2,
                color: { color: '#666' },
                label: '', // Hide edge labels in default view
            })));

            window.network = initializeNetwork(nodes, edges);
        })
        .catch((error) => console.error('Error fetching graph data:', error));
}
