
// /**
//  * Fetches ephemeris data and renders the chart SVG
//  * @param {string} containerId - The ID of the container where the chart will be rendered
//  * @param {Object} locationData - Geolocation data with latitude and longitude
//  */
// export async function renderChart(containerId, locationData) {
//   const container = document.getElementById(containerId);

//   try {
//       // Fetch ephemeris data
//       const ephemerisResponse = await fetch('/api/ephemeris', {
//           method: 'POST',
//           headers: { 'Content-Type': 'application/json' },
//           body: JSON.stringify(locationData),
//       });

//       if (!ephemerisResponse.ok) {
//           throw new Error(`Failed to fetch ephemeris data: ${ephemerisResponse.statusText}`);
//       }

//       const ephemerisData = await ephemerisResponse.json();

//       // Fetch chart SVG using ephemeris data
//       const chartResponse = await fetch('/api/chart-svg', {
//           method: 'POST',
//           headers: { 'Content-Type': 'application/json' },
//           body: JSON.stringify(ephemerisData),
//       });

//       if (!chartResponse.ok) {
//           throw new Error(`Failed to fetch chart SVG: ${chartResponse.statusText}`);
//       }

//       const svgContent = await chartResponse.text();
//       container.innerHTML = svgContent; // Render the SVG content

//   } catch (error) {
//       container.innerHTML = `Error rendering chart: ${error.message}`;
//   }
// }



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



/**
* Displays the report based on the ephemeris data
* @param {Object} data - Ephemeris data
*/
export function displayReport(data) {
  const reportContainer = document.getElementById('reportContainer');
  if (!reportContainer) return;

  const additionalInfo = data?.ephemeris?.additional_info || {};
  const chart = data?.ephemeris?.chart || {};

  reportContainer.textContent = ''; // Clear previous content

  // Magic Hour Information
  // reportContainer.textContent += '\n=== MAGIC HOUR INFORMATION ===\n';
  // reportContainer.textContent += `> Current Planetary Hour: ${additionalInfo.current_planetary_hour || 'Unknown'}\n`;
  // reportContainer.textContent += `> Magic Hour Name: ${data?.neo4j_data?.hour?.label || 'N/A'}\n`;
  // reportContainer.textContent += `> Magic Hour Ruler: ${additionalInfo.hour_ruler || 'Unknown'}\n`;
  // reportContainer.textContent += `> Day Ruling Planet: ${additionalInfo.day_ruling_planet || 'Unknown'}\n`;

  // Time Information
  reportContainer.textContent += '\n=== TIME INFORMATION ===\n';
  reportContainer.textContent += `> Local Time: ${additionalInfo.current_time || 'N/A'}\n`;
  reportContainer.textContent += `> Sunrise: ${additionalInfo.sunrise || 'N/A'}, Sunset: ${additionalInfo.sunset || 'N/A'}\n`;
  reportContainer.textContent += `> Current UTC Time: ${additionalInfo.utc_time || 'N/A'}\n`;

  // Chart Angles
  reportContainer.textContent += '\n=== CHART ANGLES ===\n';
  const angles = chart.angles || {};
  ['ascendant', 'descendant', 'midheaven', 'ic'].forEach(angle => {
      if (angles[angle]) {
          const angleData = angles[angle];
          reportContainer.textContent += `> ${angle.charAt(0).toUpperCase() + angle.slice(1)}: ${angleData.degree}° ${angleData.sign} (${angleData.absolute_degree}° total)\n`;
      }
  });

  // Houses and Occupancy
  reportContainer.textContent += '\n=== HOUSES AND OCCUPANCY ===\n';
  const houses = chart.houses || {};
  for (let i = 1; i <= 12; i++) {
      const house = houses[i.toString()];
      if (house) {
          const planetNames = house.planets && house.planets.length > 0
              ? house.planets.map(planet => planet.name).join(', ')
              : null;

          const planetList = planetNames
              ? ` - Occupied by: ${planetNames}`
              : ' - Empty house';

          reportContainer.textContent += `> House ${i}: ${house.degree}° ${house.sign} (${house.absolute_degree}° total)${planetList}\n`;
      }
  }
}
