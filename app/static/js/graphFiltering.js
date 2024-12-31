/**
* Filter the graph based on received ephemeris and hour data.
* This function is called from main.js after geolocationService has fetched the data.
* 
* The data flow is:
* 1. geolocationService.js gets location and makes API call to /api/geolocation_ephemeris
* 2. main.js receives this data and passes it to this function
* 3. This function extracts the current hour URI from the Neo4j data
* 4. The hour URI is used to filter and update the graph visualization
*
* @param {Object} data - The full data object from geolocation service containing:
*   - neo4j_data: Object with hour info and graph relationships
*   - planetary_positions: Current planetary positions
*   - other ephemeris data
* @param {number} latitude - User's latitude (not used in current implementation)
* @param {number} longitude - User's longitude (not used in current implementation)
* @throws {Error} If required hour data is missing from the response
*/



export function fetchCurrentHourAndFilter(data) {
    // console.log('Raw hour data:', data);
    if (!data.neo4j_data || !data.neo4j_data.hour) {
        throw new Error('Missing hour data in response');
    }
    const currentHourUri = data.neo4j_data.hour.uri;
    filterByHour(currentHourUri);
}


function filterByHour(hourName) {
    fetch('/api/filter_by_hour', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ hour_name: hourName }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.error || !data.nodes || !data.edges) {
                console.error('Error or no data received:', data);
                return;
            }
            console.log('Filtered Data Received:', data);
            
            // Only exclude the MagicHourEntity class, but keep the specific hour node
            const excludedNodeLabels = ['MagicHourEntity'];
            const excludedEdgeLabels = ['HAS_MEMBER']; // We don't want to show the class membership edge

            // Filter and create nodes
            const filteredNodes = new vis.DataSet(data.nodes
                .filter(node => !excludedNodeLabels.includes(node.label))
                .map(node => {
                    const isHourNode = node.id === hourName;
                    return {
                        id: node.id,
                        label: node.label || 'Unnamed Node',
                        title: node.description || 'No description',
                        color: { 
                            background: isHourNode ? '#FFD700' : '#90EE90',
                            border: isHourNode ? '#DAA520' : '#006400'
                        },
                        size: isHourNode ? 25 : 20
                    };
                }));

         
            // Filter and create edges
            const filteredEdges = new vis.DataSet(data.edges
                .filter(edge => !excludedEdgeLabels.includes(edge.label)) // Filter out unwanted edges
                .map(edge => ({
                    from: edge.from,
                    to: edge.to,
                    label: edge.label,
                    title: JSON.stringify(edge.properties, null, 2), // Show properties on hover
                    arrows: {
                        to: {
                            enabled: true,
                            scaleFactor: 0.5  // Smaller arrows
                        }
                    },
                    font: {
                        size: 10,      // Smaller font size
                        color: '#666', // Subtle grey color
                        face: 'arial', // Regular font
                        strokeWidth: 0, // No text outline
                        align: 'middle',  // Can be 'horizontal' or 'middle'
                        vadjust: 0,         // Adjust vertical position of the label
                        background: 'white',
                        backgroundPadding: { top: 2, right: 2, bottom: 2, left: 2 } 
                    },
                    color: { color: '#006400', opacity: 0.6 }, // Keep your green but make it more transparent
                    width: 1,         // Thinner lines
                    smooth: {
                        enabled: true,
                        type: 'continuous',
                        roundness: 0.5
                    }
                })));

            console.log('Filtered edges:', filteredEdges);

            // Create a new network with filtered data
            const container = document.getElementById('network');
            const options = {
                layout: { improvedLayout: false },
                physics: {
                    enabled: true,
                    solver: 'forceAtlas2Based',
                    forceAtlas2Based: {
                        gravitationalConstant: -25,     // Reduced from -50 for less repulsion
                        centralGravity: 0.005,          // Reduced from 0.01 for gentler center pull
                        springLength: 200,              // Keep the desired distance
                        springConstant: 0.02,           // Reduced from 0.08 for softer springs
                        damping: 0.15,                  // Reduced from 0.4 for smoother movement
                        avoidOverlap: 0.5
                    },
                    stabilization: { iterations: 250 }
                },
                interaction: { hover: true, tooltipDelay: 200 },
                nodes: { shape: 'dot' },
                edges: { 
                    smooth: { enabled: true, type: 'dynamic' },
                    width: 2,
                    arrows: 'to'
                }
            };

            window.network = new vis.Network(container, { 
                nodes: filteredNodes, 
                edges: filteredEdges 
            }, options);

            window.network.fit();
            console.log('Network Updated with Filtered Data');
        })
        .catch((error) => {
            console.error('Error fetching or processing filtered data:', error);
        });
}







