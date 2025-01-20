import math 
from app.routes.constants import SIGN_SYMBOLS, TRIPLICITIES, PLANET_SYMBOLS, DEFAULT_ASPECT_CONFIG, ZODIAC_SIGNS
from typing import Dict, Any
 
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


        # Just call _start_svg and _end_svg since everything is now in _start_svg
        svg = self._start_svg(abs_degree, asc_sign)
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
                x1 = self.OUTER_CIRCLE_RADIUS * math.cos(angle_radians)
                y1 = self.OUTER_CIRCLE_RADIUS * math.sin(angle_radians)
                x2 = (self.OUTER_CIRCLE_RADIUS - 5) * math.cos(angle_radians)  # Shorter inner radius
                y2 = (self.OUTER_CIRCLE_RADIUS - 5) * math.sin(angle_radians)
                
                svg += f'''
                    <line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" />'''
        
        svg += '''
            </g>'''
        return svg


    
    def _start_svg(self, abs_degree, asc_sign):
        """
        Start the SVG generation with the zodiac wheel and fixed elements.
        Rotate the wheel to align the Ascendant degree correctly at 9 o'clock,
        and adjust for its relative degree within the sign.
        """
        # Calculate the reversed absolute degree
        reversed_abs_degree = 360 - abs_degree

        # Rotate the chart to place reversed absolute degree at 270° (9 o'clock)
        rotation = -(reversed_abs_degree - 270)

        print(f"\n=== Debug Info ===")
        print(f"ASC degree: {abs_degree}° (Absolute)")
        print(f"ASC sign: {asc_sign}")
        print(f"Reversed Absolute Degree: {reversed_abs_degree}°")
        print(f"Final Rotation: {rotation}°")


        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">
            <!-- Background -->
            <rect width="400" height="400" fill="#fff"/>
            
            <!-- Fixed group for the cross and degree markers -->
            <g transform="translate(200,200)">
            
                <!-- Rotating group for zodiac wheel -->
                <g transform="rotate({rotation})">
                    {self._add_base_circles()}
                    {self._add_zodiac_divisions()}
                    {self._add_zodiac_divisions_and_names()}
                    {self._add_degree_markers()}
                </g>
                
                <!-- Fixed elements after rotating group -->
                <!-- Cross lines -->
                <line x1="-{self.OUTER_CIRCLE_RADIUS}" y1="0" x2="{self.OUTER_CIRCLE_RADIUS}" y2="0" 
                    stroke="red" stroke-width="1"/>
                <line x1="0" y1="-{self.OUTER_CIRCLE_RADIUS}" x2="0" y2="{self.OUTER_CIRCLE_RADIUS}" 
                    stroke="blue" stroke-width="1"/>
                    
                <!-- Fixed ASC marker -->
                <text x="{-self.OUTER_CIRCLE_RADIUS-10}" y="0" 
                    text-anchor="middle" dominant-baseline="middle" 
                    font-size="8" fill="red">ASC</text>
            </g>
        </svg>'''



    def _add_base_circles(self):
        return f'''
            <!-- Outer black circle -->
            <circle cx="0" cy="0" r="{self.OUTER_CIRCLE_RADIUS}" fill="black" stroke="#222222" stroke-width="1"/>
            <circle cx="0" cy="0" r="{self.MAIN_CIRCLE_RADIUS}" fill="white" stroke="#222222" stroke-width="1"/>
            <circle cx="0" cy="0" r="{self.INNER_CIRCLE_RADIUS}" fill="white" stroke="#222222" stroke-width="1"/>
            <circle cx="0" cy="0" r="{self.CENTER_CIRCLE_RADIUS}" fill="white" stroke="#222222" stroke-width="1"/>
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


    def _add_zodiac_divisions_and_names(self):
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


                        
    def _end_svg(self):
        return '''
            </g>
        </svg>'''            
                
                
                
       
       
       
       
       
       
       
   