// POPULATE SYSTEM DROPDOWN
document.addEventListener('DOMContentLoaded', function () {
    // Place your main script inside this block

    function fetchAndPopulateSystems() {
        console.log('Fetching systems...'); // Debug message
        fetch('/analogy_systems', {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Fetched systems:', data); // Debug message

            const analogySystemDropdown = document.getElementById('analogySystemDropdown');
            analogySystemDropdown.innerHTML = '<option value="">Select an Analogy System</option>';

            // Populate dropdown with fetched systems
            data.forEach(system => {
                const option = document.createElement('option');
                option.value = system.id;
                option.textContent = system.name;
                analogySystemDropdown.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error fetching systems:', error);
        });
    }

    fetchAndPopulateSystems(); // Ensure this function is being called correctly
});



document.addEventListener('DOMContentLoaded', function () {
    const analogySystemDropdown = document.getElementById('analogySystemDropdown');
    const analogySearchInput = document.getElementById('analogySearch');
    const analogySearchResults = document.getElementById('analogySearchResults');
    const analogySystemsContainer = document.getElementById('analogySystemsContainer');
    const selectedAnalogiesInput = document.getElementById('selectedAnalogies'); // Hidden input for all analogies
    let selectedAnalogiesBySystem = {};
    

    // Create a new system container if one doesn't exist
    function createSystemContainer(systemId, systemName) {
        if (!document.getElementById(`system-${systemId}`)) {
            const systemDiv = document.createElement('div');
            systemDiv.id = `system-${systemId}`;
            systemDiv.className = 'mb-3';
            systemDiv.style.padding = '1rem';
            systemDiv.style.marginBottom = '1rem';

            const systemLabel = document.createElement('h6');
            systemLabel.textContent = systemName.charAt(0).toUpperCase() + systemName.slice(1).toLowerCase();

            const analogiesList = document.createElement('div');
            analogiesList.className = 'form-control';
            analogiesList.style.height = 'auto';
            analogiesList.style.minHeight = '2.5em';
            analogiesList.id = `analogiesList-${systemId}`;

            systemDiv.appendChild(systemLabel);
            systemDiv.appendChild(analogiesList);
            analogySystemsContainer.appendChild(systemDiv);

            selectedAnalogiesBySystem[systemId] = [];
        }
    }

    // Fetch and display matching topics for analogies
    function fetchAndDisplayTopics(query) {
        fetch(`/search/search_topics?q=${query}`)  // Make sure your route matches this URL
            .then(response => response.json())
            .then(results => {
                analogySearchResults.innerHTML = '';
                results.forEach(topic => createSearchResultItem(topic));
            })
            .catch(error => console.error('Error fetching search results:', error));
    }

    // Create individual search result items
    function createSearchResultItem(topic) {
        const listItem = document.createElement('li');
        listItem.className = 'list-group-item list-group-item-action';
        listItem.style.cursor = 'pointer';
        listItem.textContent = topic.name;
        listItem.dataset.id = topic.id;

        listItem.addEventListener('click', function () {
            const selectedSystemId = analogySystemDropdown.value;
            if (!selectedSystemId) {
                alert('Please select an analogy system first.');
                return;
            }

            const analogiesList = document.getElementById(`analogiesList-${selectedSystemId}`);
            if (selectedAnalogiesBySystem[selectedSystemId].find(a => a.id == topic.id)) {
                return; // Avoid duplicates
            }

            addAnalogyToSystem(selectedSystemId, topic, analogiesList);
            analogySearchInput.value = ''; // Clear search field
            analogySearchResults.innerHTML = ''; // Clear search results
            updateHiddenInput(); // Update hidden field
        });

        analogySearchResults.appendChild(listItem);
    }

    // Event listener for analogy system dropdown
    analogySystemDropdown.addEventListener('change', function () {
        const selectedSystemId = this.value;
        const selectedSystemName = this.options[this.selectedIndex].text;
        createSystemContainer(selectedSystemId, selectedSystemName);
    });

    // Add an analogy to the system
    function addAnalogyToSystem(systemId, topic, analogiesList) {
        selectedAnalogiesBySystem[systemId].push({ id: topic.id, name: topic.name });

        const analogyDiv = document.createElement('div');
        analogyDiv.className = 'd-flex justify-content-between align-items-center';

        const analogyText = document.createElement('span');
        analogyText.textContent = topic.name;

        const removeButton = document.createElement('button');
        removeButton.className = 'remove-button';
        removeButton.innerHTML = '<i class="fas fa-times"></i>'; // Font Awesome 'times' icon

        removeButton.addEventListener('click', function () {
            selectedAnalogiesBySystem[systemId] = selectedAnalogiesBySystem[systemId].filter(a => a.id !== topic.id);
            analogyDiv.remove();

            // If no more analogies are left for this system, remove the system div
            if (selectedAnalogiesBySystem[systemId].length === 0) {
                delete selectedAnalogiesBySystem[systemId];
                const systemDiv = document.getElementById(`system-${systemId}`);
                if (systemDiv) systemDiv.remove();
            }

            updateHiddenInput();
        });

        analogyDiv.appendChild(analogyText);
        analogyDiv.appendChild(removeButton);
        analogiesList.appendChild(analogyDiv);

        updateHiddenInput();
    }

    // Update the hidden input field for selected analogies
    function updateHiddenInput() {
        let allSelectedAnalogies = [];
        for (let systemId in selectedAnalogiesBySystem) {
            if (selectedAnalogiesBySystem[systemId].length > 0) {
                allSelectedAnalogies.push({
                    system_id: systemId,
                    system_name: document.querySelector(`#analogySystemDropdown option[value="${systemId}"]`).textContent,
                    topics: selectedAnalogiesBySystem[systemId]
                });
            }
        }
        selectedAnalogiesInput.value = JSON.stringify(allSelectedAnalogies);
    }

    // Event listener for search input
    analogySearchInput.addEventListener('input', function () {
        const query = analogySearchInput.value.trim();
        if (query.length >= 2) {
            fetchAndDisplayTopics(query);
        } else {
            analogySearchResults.innerHTML = ''; // Clear search results when input is less than 2 characters
        }
    });

    function populateExistingAnalogies() {
        let existingAnalogiesValue = selectedAnalogiesInput.value;

        if (!existingAnalogiesValue || existingAnalogiesValue === 'null' || existingAnalogiesValue === 'undefined') {
            console.warn('No existing analogies to populate');
            return;
        }

        let existingAnalogies = [];
        try {
            existingAnalogies = JSON.parse(existingAnalogiesValue);
        } catch (e) {
            console.error('Error parsing existing analogies:', e);
            return;
        }

        if (!Array.isArray(existingAnalogies)) {
            console.error('Expected existing analogies to be an array, but got:', typeof existingAnalogies);
            return;
        }

        // Iterate over existing analogies and populate UI
        existingAnalogies.forEach(system => {
            const systemId = system.system_id;
            const systemName = system.system_name;

            createSystemContainer(systemId, systemName);

            system.topics.forEach(topic => {
                const analogiesList = document.getElementById(`analogiesList-${systemId}`);
                addAnalogyToSystem(systemId, topic, analogiesList);
            });
        });
    }

    // Call the function to populate analogies when the page loads
    populateExistingAnalogies();
});


