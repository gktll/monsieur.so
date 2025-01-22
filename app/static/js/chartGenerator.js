/**
 * Fetches ephemeris data
 * @param {Object} locationData - Geolocation data with latitude and longitude
 * @returns {Promise<Object>} - Ephemeris data
 */
export async function fetchEphemerisData(locationData) {
  const response = await fetch('/api/ephemeris', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(locationData),
  });

  if (!response.ok) {
      throw new Error(`Failed to fetch ephemeris data: ${response.statusText}`);
  }

  return await response.json();
}



/**
* Fetches chart SVG using ephemeris data
* @param {Object} ephemerisData - Ephemeris data
* @returns {Promise<string>} - SVG content
*/
async function fetchChartSVG(ephemerisData) {
  const response = await fetch('/api/chart-svg', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(ephemerisData),
  });

  if (!response.ok) {
      throw new Error(`Failed to fetch chart SVG: ${response.statusText}`);
  }

  return await response.text();
}



/**
* Renders the chart SVG in the specified container
* @param {string} containerId - The ID of the container where the chart will be rendered
* @param {Object} locationData - Geolocation data with latitude and longitude
*/
export async function renderChart(containerId, locationData) {
  const container = document.getElementById(containerId);

  try {
      const ephemerisData = await fetchEphemerisData(locationData);
      const svgContent = await fetchChartSVG(ephemerisData);
      container.innerHTML = svgContent; // Render the SVG content
  } catch (error) {
      container.innerHTML = `Error rendering chart: ${error.message}`;
  }
}


// Streamline Chart Data
const reportTemplates = {
    timeSection(info) {
        return `
            <section class="report-section">
                <h3 class="text-lg font-semibold mb-3">Time Information</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                    ${[
                        ['Local Time', info.current_time],
                        ['UTC Time', info.utc_time],
                        ['Sunrise', info.sunrise],
                        ['Sunset', info.sunset]
                    ].map(([label, value]) => `
                        <div><span class="font-medium">${label}:</span> ${value || 'N/A'}</div>
                    `).join('')}
                </div>
            </section>
        `;
    },

    anglesSection(angles) {
        return `
            <section class="report-section mt-6">
                <h3 class="text-lg font-semibold mb-3">Chart Angles</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                    ${['ascendant', 'descendant', 'midheaven', 'ic']
                        .map(angle => {
                            const data = angles?.[angle];
                            if (!data) return '';
                            return `
                                <div class="angle-info">
                                    <span class="font-medium">${angle.charAt(0).toUpperCase() + angle.slice(1)}:</span>
                                    ${data.degree}° ${data.sign}
                                    <span class="text-gray-500">(${data.absolute_degree}° total)</span>
                                </div>
                            `;
                        }).join('')}
                </div>
            </section>
        `;
    },

    houseCard(number, house) {
        const planetNames = house.planets?.length > 0
            ? house.planets.map(planet => planet.name).join(', ')
            : 'Empty house';
        
        return `
            <div class="house-info p-2 border rounded hover:shadow-sm transition-shadow">
                <div class="font-medium">House ${number}</div>
                <div>${house.degree}° ${house.sign}
                    <span class="text-gray-500">(${house.absolute_degree}° total)</span>
                </div>
                <div class="text-sm ${house.planets?.length ? 'text-blue-600' : 'text-gray-500'}">
                    ${planetNames}
                </div>
            </div>
        `;
    },

    housesSection(houses) {
        return `
            <section class="report-section mt-6">
                <h3 class="text-lg font-semibold mb-3">Houses and Occupancy</h3>
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    ${Array.from({length: 12}, (_, i) => i + 1)
                        .map(num => {
                            const house = houses?.[num.toString()];
                            return house ? this.houseCard(num, house) : '';
                        }).join('')}
                </div>
            </section>
        `;
    }
};

export function displayReport(data) {
    const reportContainer = document.getElementById('reportContainer');
    if (!reportContainer) return;

    const additionalInfo = data?.ephemeris?.additional_info || {};
    const chart = data?.ephemeris?.chart || {};

    const template = `
        <div class="chart-report">
            ${reportTemplates.timeSection(additionalInfo)}
            ${reportTemplates.anglesSection(chart.angles)}
            ${reportTemplates.housesSection(chart.houses)}
        </div>
    `;

    reportContainer.innerHTML = template;
}

// For modal usage:
// export function getReportHTML(data) {
//     const additionalInfo = data?.ephemeris?.additional_info || {};
//     const chart = data?.ephemeris?.chart || {};

//     return `
//         <div class="chart-report">
//             ${reportTemplates.timeSection(additionalInfo)}
//             ${reportTemplates.anglesSection(chart.angles)}
//             ${reportTemplates.housesSection(chart.houses)}
//         </div>
//     `;
// }