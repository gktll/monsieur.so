import math 
from app.routes.constants import SIGN_SYMBOLS, TRIPLICITIES, PLANET_SYMBOLS, DEFAULT_ASPECT_CONFIG, ZODIAC_SIGNS
from typing import Dict, Any
 
# <line x1="-{self.OUTER_CIRCLE_RADIUS}" y1="0" x2="{self.OUTER_CIRCLE_RADIUS}" y2="0" 
#     stroke="#f5f5f5" stroke-width="1"/>
# <line x1="0" y1="-{self.OUTER_CIRCLE_RADIUS}" x2="0" y2="{self.OUTER_CIRCLE_RADIUS}" 
#     stroke="#f5f5f5" stroke-width="1"/> 
 
class ChartCalculator:
    OUTER_CIRCLE_RADIUS = 180
    MAIN_CIRCLE_RADIUS = 160
    INNER_CIRCLE_RADIUS = 60
    CENTER_CIRCLE_RADIUS = 40
    
    def preprocess_chart_data(self, ephemeris_data):
        """
        Preprocess ephemeris data with corrected house ordering from Ascendant
        """
        chart_data = ephemeris_data['ephemeris']['chart']
        planets_data = ephemeris_data['ephemeris']['planets']

        # Create a new houses dict with enriched planet data
        processed_houses = {}

        # Process houses starting from Ascendant
        for house_num, house_data in chart_data['houses'].items():
            processed_planets = []

            # Process planets in this house
            for planet in house_data['planets']:
                planet_name = planet['name']
                if planet_name in planets_data:
                    processed_planets.append({
                        'name': planet_name,
                        'longitude': planets_data[planet_name]['longitude'],
                        'is_retrograde': planets_data[planet_name].get('is_retrograde', False)
                    })

            processed_houses[house_num] = {
                'absolute_degree': house_data['absolute_degree'],
                'degree': house_data['degree'],
                'sign': house_data['sign'],
                'planets': processed_planets
            }

        return {
            'houses': processed_houses,
            'angles': chart_data['angles'],
            'aspects': chart_data['aspects']
        }
    
   
    def generate_chart_svg(self, ephemeris_data):
        chart_data = self.preprocess_chart_data(ephemeris_data)
        abs_degree = chart_data['angles']['ascendant']['absolute_degree']
        asc_sign = chart_data['angles']['ascendant']['sign']
        houses = chart_data['houses']
        planets_data = ephemeris_data['ephemeris']['planets']
        aspects_data = chart_data['aspects']
        
        # Calculate chart rotation here so we can pass it to all methods that need it
        reversed_abs_degree = 360 - abs_degree
        chart_rotation = -(reversed_abs_degree - 270)  # Same calculation as in _start_svg
  
        svg = self._start_svg(abs_degree, asc_sign, houses, planets_data, chart_rotation, aspects_data)
        svg += self._end_svg()

        return svg
 
 
    
    def _add_degree_markers(self):
        """
        Add small tick marks at 10° and 20° intervals within each 30° division.
        """
        svg = '''
            <!-- Degree markers -->
            <g stroke="white" stroke-width="1">'''
        
        for base in range(0, 360, 30):  # Each 30° division
            for offset in [10, 20]:  # Add markers for 10° and 20° intervals
                degree = base + offset
                angle_radians = math.radians(degree - 90)  # Adjust to align 0° at the top (12 o'clock)
                
                # Calculate coordinates for the tick mark
                x1 = self.MAIN_CIRCLE_RADIUS * math.cos(angle_radians)
                y1 = self.MAIN_CIRCLE_RADIUS * math.sin(angle_radians)
                x2 = (self.MAIN_CIRCLE_RADIUS + 2) * math.cos(angle_radians)  # Shorter inner radius
                y2 = (self.MAIN_CIRCLE_RADIUS + 2) * math.sin(angle_radians)
                
                svg += f'''
                    <line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" />'''
        
        svg += '''
            </g>'''
        return svg
    

        
    def _start_svg(self, abs_degree, asc_sign, houses, planets_data, chart_rotation, aspects_data,):
        """
        Start the SVG generation with the zodiac wheel and fixed elements.
        Rotate the wheel to align the Ascendant degree correctly at 9 o'clock,
        and adjust for its relative degree within the sign.
        """

        print(f"\n=== Debug Info ===")
        print(f"ASC degree: {abs_degree}° (Absolute)")
        print(f"ASC sign: {asc_sign}")
        print(f"Final Rotation: {chart_rotation}°")


        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">
            <!-- Background -->
            <rect width="400" height="400" fill="#f5f5f5"/>
            
            <!-- Fixed group for the cross and degree markers -->
            <g transform="translate(200,200)">
            
                <!-- Rotating group for zodiac wheel -->
                <g transform="rotate({chart_rotation})">
                    {self._add_base_circles()}
                    {self._add_aspects(aspects_data, planets_data)}  # Add aspects before planets
                    {self._add_zodiac_divisions()}
                    {self._add_zodiac_names()}
                    {self._add_degree_markers()}
                    {self._add_house_cusps_and_numbers(houses)}
                    {self._add_planets(planets_data, chart_rotation)}
                </g>
                
                
                <!-- Debug elements *removed after rotating group -->
                <!-- Add here --> 

  
                <!-- Fixed ASC marker -->
                <text x="{-self.OUTER_CIRCLE_RADIUS-10}" y="0" 
                    text-anchor="middle" dominant-baseline="middle" 
                    font-size="12" fill="#2B303A">&#8593;</text>
            </g>
        </svg>'''



    def _add_base_circles(self):
        return f'''
            <!-- Outer black circle -->
            <circle cx="0" cy="0" r="{self.OUTER_CIRCLE_RADIUS}" fill="#2B303A" stroke="#2B303A" stroke-width="1"/>
            <circle cx="0" cy="0" r="{self.MAIN_CIRCLE_RADIUS}" fill="white" stroke="#2B303A" stroke-width="1"/>
            <circle cx="0" cy="0" r="{self.INNER_CIRCLE_RADIUS}" fill="white" stroke="#2B303A" stroke-width="1"/>
            <circle cx="0" cy="0" r="{self.CENTER_CIRCLE_RADIUS}" fill="white" stroke="#2B303A" stroke-width="1"/>
        '''
     
         
    def _add_zodiac_divisions(self):
        """
        Add lines dividing the zodiac wheel into 12 equal segments (30° each).
        """
        svg = '''
                <!-- Sign divisions -->
                <g stroke="white" stroke-width="1">'''
        for i in range(12):
            angle = i * 30  # Each sign occupies 30 degrees
            svg += f'''
                    <line transform="rotate({angle})" x1="0" y1="-{self.OUTER_CIRCLE_RADIUS}" 
                        x2="0" y2="-{self.MAIN_CIRCLE_RADIUS}"/>'''
        svg += '''
                </g>'''
        return svg


    def _add_zodiac_names(self):
        """
        Add the reversed zodiac divisions and names to the chart.
        Ensures counterclockwise progression and prevents duplication.
        """
 
        svg = '''
                    <!-- Zodiac Divisions and Names -->
                    <g fill="white" font-size="10">'''
        for i, sign in enumerate(ZODIAC_SIGNS):
            # Each sign spans 30 degrees, calculate the position
            start_angle = -(i * 30)  # Negative for counterclockwise progression
            label_angle = start_angle - 15  # Center the label within the segment
            svg += f'''
                    <!-- Division for {sign} -->
                    <text transform="rotate({label_angle})" x="0" y="-170" 
                        text-anchor="middle" dominant-baseline="middle">{sign}</text>
            '''
        svg += '''
                    </g>'''
        return svg
 
    
    
    def _add_house_cusps_and_numbers(self, houses):
        """
        Add house cusps and numbers to the chart.
        - The Ascendant marks the start of the 1st house.
        - Each subsequent cusp is determined by the provided `houses` data.
        """
        svg = '''
            <!-- House cusps -->
            <g stroke="#2B303A" stroke-width="1" stroke-dasharray="4,4">'''

        house_positions = []  # To store cusp positions for house numbers

        # Iterate through all houses in the data
        for house_num, house_data in houses.items():
            abs_degree = house_data['absolute_degree']
            reversed_degree = 360 - abs_degree  # Reverse for counterclockwise zodiac
            angle_radians = math.radians(reversed_degree - 90)

            # Draw cusp line (inner to outer circle)
            x1 = self.INNER_CIRCLE_RADIUS * math.cos(angle_radians)
            y1 = self.INNER_CIRCLE_RADIUS * math.sin(angle_radians)
            x2 = self.MAIN_CIRCLE_RADIUS * math.cos(angle_radians)
            y2 = self.MAIN_CIRCLE_RADIUS * math.sin(angle_radians)
            
            print(f"Cusp {house_num}: abs_degree={abs_degree}°, reversed_degree={reversed_degree}°, angle_radians={angle_radians} radians, x1={x1}, y1={y1}, x2={x2}, y2={y2}")

            svg += f'''
                <!-- Cusp {house_num} -->
                <line x1="{x1:.2f}" y1="{y1:.2f}"
                    x2="{x2:.2f}" y2="{y2:.2f}"
                    stroke-dasharray="4,4"/>'''

            # Store cusp data for house number placement
            house_positions.append((house_num, reversed_degree))

        # Sort house positions to ensure correct counterclockwise order
        house_positions.sort(key=lambda x: x[1], reverse=True)

        # Add house numbers at the midpoint between cusps
        svg += '''
            </g>
            <g fill="#2B303A" font-size="9" font-family="Arial, sans-serif">'''

        for i in range(len(house_positions)):
            current = house_positions[i]
            next_house = house_positions[(i + 1) % len(house_positions)]

            # Calculate midpoint between current and next cusp
            start_angle = current[1]
            end_angle = next_house[1]
            if end_angle > start_angle:
                end_angle -= 360
            center_angle = (start_angle + end_angle) / 2
            center_radians = math.radians(center_angle - 90)

            # Position house number at midpoint radius
            number_radius = (self.INNER_CIRCLE_RADIUS + self.CENTER_CIRCLE_RADIUS) / 2
            number_x = number_radius * math.cos(center_radians)
            number_y = number_radius * math.sin(center_radians)
            
            text_rotation = center_angle + 180 if center_angle > 90 and center_angle < 270 else center_angle


            # Add the house number
            svg += f'''
                <text x="{number_x:.2f}" y="{number_y:.2f}"
                    text-anchor="middle" dominant-baseline="middle"
                    transform="rotate({text_rotation:.2f} {number_x:.2f} {number_y:.2f})">
                    {current[0]}
                </text>'''

        svg += '''
            </g>'''
        return svg
    
    
    def _add_planets(self, planets_data, chart_rotation):
        planet_positions = []
        for planet_name, planet_data in planets_data.items():
            longitude = planet_data['longitude']
            reversed_longitude = 360 - longitude
            svg_angle = (reversed_longitude - 90) % 360
            angle_radians = math.radians(svg_angle)
            
            symbol_filename = f"static/svg/chart_planets/{planet_name.lower()}.svg"
        
            planet_positions.append({
                'name': planet_name,
                'angle': svg_angle,
                'radians': angle_radians,
                'symbol_path': symbol_filename,
                'radius_offset': 0
            })
        
        # Sort and process positions
        angle_threshold = 15
        base_radius = (self.MAIN_CIRCLE_RADIUS + self.INNER_CIRCLE_RADIUS) / 2
        radius_step = 15
        symbol_size = 16
        
        planet_positions.sort(key=lambda x: x['angle'])
        
        # Process overlaps
        for i, planet in enumerate(planet_positions):
            prev_planet = planet_positions[(i - 1) % len(planet_positions)]
            next_planet = planet_positions[(i + 1) % len(planet_positions)]
            
            prev_dist = min((planet['angle'] - prev_planet['angle']) % 360,
                        (prev_planet['angle'] - planet['angle']) % 360)
            next_dist = min((planet['angle'] - next_planet['angle']) % 360,
                        (next_planet['angle'] - planet['angle']) % 360)
            
            if prev_dist < angle_threshold or next_dist < angle_threshold:
                planet['radius_offset'] = radius_step if i % 2 == 0 else -radius_step
        
        svg = '''
            <!-- Planet positions and degree lines -->
            <g>
                <!-- Degree lines -->
                <g stroke="#2B303A" stroke-width="1">'''
        
        # Draw degree lines
        for planet in planet_positions:
            line_start_x = self.MAIN_CIRCLE_RADIUS * math.cos(planet['radians'])
            line_start_y = self.MAIN_CIRCLE_RADIUS * math.sin(planet['radians'])
            line_end_x = (self.MAIN_CIRCLE_RADIUS - 5) * math.cos(planet['radians'])
            line_end_y = (self.MAIN_CIRCLE_RADIUS - 5) * math.sin(planet['radians'])
            
            svg += f'''
                    <line 
                        x1="{line_start_x:.2f}" 
                        y1="{line_start_y:.2f}" 
                        x2="{line_end_x:.2f}" 
                        y2="{line_end_y:.2f}"
                    />'''
        
        svg += '''
                </g>
                <!-- Planet symbols -->
                <g>'''
        
        # Add planet symbols with center rotation to counter the chart rotation
        for planet in planet_positions:
            adjusted_radius = base_radius + planet['radius_offset']
            x = adjusted_radius * math.cos(planet['radians'])
            y = adjusted_radius * math.sin(planet['radians'])
            
            # Calculate center point of the symbol
            symbol_x = x - symbol_size/2
            symbol_y = y - symbol_size/2
            center_x = symbol_x + symbol_size/2
            center_y = symbol_y + symbol_size/2
            
            # Counter-rotate by chart_rotation to keep symbols upright
            svg += f'''
                    <g transform="translate({center_x} {center_y}) rotate({-chart_rotation})">
                        <image 
                            href="{planet['symbol_path']}"
                            x="{-symbol_size/2}"
                            y="{-symbol_size/2}"
                            width="{symbol_size}"
                            height="{symbol_size}"
                        />
                    </g>'''
        
        svg += '''
                </g>
            </g>'''
        
        return svg
    
    
    def _add_aspects(self, aspects_data, planets_data):
        """
        Add aspect lines between planets.
        """
        # Define aspect styles
        aspect_styles = {
            'Conjunction': {'color': '#FF0000', 'stroke_width': 1, 'dash_array': ''},  # Red solid
            'Square': {'color': '#FF0000', 'stroke_width': 1, 'dash_array': '4,4'},    # Red dashed
            'Sextile': {'color': '#0000FF', 'stroke_width': 1, 'dash_array': ''},      # Blue solid
            'Trine': {'color': '#008000', 'stroke_width': 1, 'dash_array': ''},        # Green solid
            'Opposition': {'color': '#FF0000', 'stroke_width': 1, 'dash_array': ''},   # Red solid
            # Add more aspects as needed
        }
        
        # Calculate planet positions (same as in _add_planets)
        planet_positions = {}
        radius = (self.MAIN_CIRCLE_RADIUS + self.INNER_CIRCLE_RADIUS) / 2
        
        for planet_name, planet_data in planets_data.items():
            longitude = planet_data['longitude']
            reversed_longitude = 360 - longitude
            svg_angle = (reversed_longitude - 90) % 360
            angle_radians = math.radians(svg_angle)
            
            # Store the center position of each planet
            x = radius * math.cos(angle_radians)
            y = radius * math.sin(angle_radians)
            planet_positions[planet_name] = {'x': x, 'y': y}

        # Generate SVG for aspects
        svg = '''
            <!-- Aspect lines -->
            <g class="aspects">'''
        
        # Draw lines for each aspect
        for aspect in aspects_data:
            planet1 = aspect['planet1']
            planet2 = aspect['planet2']
            aspect_type = aspect['aspect']
            
            if planet1 in planet_positions and planet2 in planet_positions:
                pos1 = planet_positions[planet1]
                pos2 = planet_positions[planet2]
                
                # Get style for this aspect type
                style = aspect_styles.get(aspect_type, {
                    'color': '#999999',     # Default color
                    'stroke_width': 1,      # Default width
                    'dash_array': ''        # Default solid line
                })
                
                # Draw the aspect line
                svg += f'''
                    <line
                        x1="{pos1['x']:.2f}"
                        y1="{pos1['y']:.2f}"
                        x2="{pos2['x']:.2f}"
                        y2="{pos2['y']:.2f}"
                        stroke="{style['color']}"
                        stroke-width="{style['stroke_width']}"
                        stroke-dasharray="{style['dash_array']}"
                        opacity="0.6"
                    />'''
        
        svg += '''
            </g>'''
        
        return svg

         
    def _end_svg(self):
        return '''
            </g>
        </svg>'''            
                
                
                
       
       
       
       
       
       
       
   