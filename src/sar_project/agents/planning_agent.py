import json
import random
import google.generativeai as genai
import googlemaps
import pyowm
from dotenv import load_dotenv
import os
from src.sar_project.agents.base_agent import *
from urllib.parse import quote_plus
from pyowm.commons import exceptions as pyowm_exceptions


# Load environment variables from .env file
load_dotenv()

# --- REPLACE WITH YOUR ACTUAL API KEYS ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Get from Google AI Studio or Google Cloud
GOOGLE_MAPS_API_KEY = os.getenv("GMAPS_API_KEY") # Get from Google Cloud Console
OPENWEATHERMAP_API_KEY = os.getenv("OWM_API_KEY") # Get from OpenWeatherMap

genai.configure(api_key=GEMINI_API_KEY)
generation_config = genai.GenerationConfig(
    temperature=0.4,
    top_p=1,
    top_k=32,
    max_output_tokens=400,
)

safety_settings = [
    {
        "category": genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT,
        "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    },
    {
        "category": genai.types.HarmCategory. HARM_CATEGORY_HATE_SPEECH,
        "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    },
    {
        "category": genai.types.HarmCategory. HARM_CATEGORY_SEXUALLY_EXPLICIT,
        "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    },
    {
        "category": genai.types.HarmCategory. HARM_CATEGORY_DANGEROUS_CONTENT,
        "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    },
]

model = genai.GenerativeModel(model_name="gemini-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)


class PlanningAgent(SARBaseAgent):
    """
    Agent to support a Planning Section Chief, now with modular structure and request processing.
    """

    def __init__(self, name="planning_chief_agent"):
        system_message = """You are an AI assistant acting as a Planning Section Chief for Search and Rescue (SAR) operations.
        Your responsibilities are to develop effective search strategies and create mission plans.

        Your skills include: strategic thinking, analysis, documentation, resource management, scenario planning, and data interpretation.

        You will receive information from various sources (Incident Commander, Operations Section Chief, Logistics Section Chief) and use this to:
        1.  Develop search strategies.
        2.  Create mission plans.
        3.  Ensure the accuracy of resource allocation predictions.
        4.  Maximize the percentage of mission objectives met.
        5.  Maintain the quality and timeliness of mission documentation.
        6.  Develop effective contingency plans.
        7.  Ensure the accuracy of search area predictions.

        You will collaborate with the Operations Section Chief and Logistics Section Chief. You maintain all mission documentation.
        You should provide clear, concise, and actionable search strategies.

        Remember, you are operating with incomplete information and under time pressure in dynamic incident scenarios.
        """

        super().__init__(
            name=name,
            role="planning_section_agent",
            system_message=system_message
        )
        self.role_description = {
            "role_name": "Planning Section Chief",
            "responsibilities": [
                "Develop search strategies",
                "Create mission plans",
                "Ensure accuracy of resource allocation predictions",
                "Maximize mission objectives met",
                "Maintain mission documentation",
                "Develop contingency plans",
                "Ensure accuracy of search area predictions"
            ],
            "skills": [
                "Strategic thinking",
                "Analysis",
                "Documentation",
                "Resource management",
                "Scenario planning",
                "Data interpretation"
            ],
            "collaborates_with": [
                "Operations Section Chief",
                "Logistics Section Chief"
            ],
            "maintains_documentation": True,
            "operates_under_conditions": [
                "Incomplete information",
                "Time pressure",
                "Dynamic incident scenarios"
            ]
        }
        self.weather_fetcher = WeatherFetcher()  # Instantiate the WeatherFetcher class

    def process_request(self, message):
        """
        Process incoming requests and dispatch to appropriate functions.

        Expected message format:
        {
            "action": "generate_strategy" or "create_mission_plan",
            "request_details": {}          // (Optional) For future expansion
        }
        """
        try:
            action = message.get("action")

            if action == "generate_strategy":
                return self._generate_and_format_strategy()
            elif action == "create_mission_plan":
                strategy_data = self._generate_and_format_strategy()  # Generate strategy first
                return self._create_mission_plan(strategy_data)  # Then create plan from strategy
            else:
                return {"error": "Unknown action requested.", "requested_action": action}

        except Exception as e:
            return {"error": f"Error processing request: {e}", "message_details": message}

    def _generate_and_format_strategy(self):
        """
        Internal method to orchestrate the search strategy generation and formatting process.

        Returns:
            dict:  JSON-like dictionary containing the complete search strategy data.
        """
        incident_data = self._get_incident_data()
        operations_data = self._get_operations_data(incident_data["location"])
        logistics_data = self._get_logistics_data()
        environmental_data = self._get_environmental_data(incident_data["location"])
        map_url = self._get_static_map_url(incident_data["location"])

        search_area_description, search_radius = self._calculate_search_area(incident_data)
        prioritized_areas = self._prioritize_search_areas(search_radius, incident_data, environmental_data, operations_data)
        resource_allocation_suggestions = self._suggest_resource_allocation(prioritized_areas, logistics_data)

        strategy_json_data = self._format_output_json(
            incident_data, operations_data, logistics_data, environmental_data,
            search_area_description, prioritized_areas, resource_allocation_suggestions, map_url
        )

        strategy_json_data["mission_objective"] = incident_data["mission_objective"]

        gemini_summary_text = self._generate_gemini_summary(strategy_json_data)
        strategy_json_data["strategy_summary_text_gemini"] = gemini_summary_text

        strategy_summary = "See Gemini-generated summary in JSON output for a user-friendly version." # Brief original summary

        strategy_json_data["strategy_summary_text_original"] = strategy_summary

        return strategy_json_data

    def _create_mission_plan(self, strategy_data):
        """
        Creates a basic mission plan based on the generated search strategy.

        Args:
            strategy_data (dict): JSON-like dictionary containing the search strategy.

        Returns:
            dict: JSON-like dictionary containing the mission plan details.
        """

        try:
            plan_details = {
                "mission_name": f"SAR Mission - {strategy_data['incident_details']['incident_type']} - {strategy_data['incident_details']['location']}",
                "date_prepared": "2024-08-04",  # Example - could use current date dynamically
                "objective": strategy_data['mission_objective'],
                "search_strategy_summary": strategy_data['strategy_summary_text_gemini'],  # Use Gemini summary
                "prioritized_search_areas": strategy_data['prioritized_search_areas'],
                "resource_allocation": strategy_data['suggested_resource_allocation'],
                "communication_plan": {
                    "primary_channel": "VHF Channel 16",
                    "secondary_channel": "Satellite phone",
                    "digital_platform": "SARNet App",
                    "backup_communication": "Runner if digital fails"
                },
                "safety_protocols": [
                    "Team check-in every hour",
                    "Emergency contact protocols in place",
                    "Wildlife awareness briefings",
                    "First aid kits with each team"
                ],
                "timeline": {  # Very basic timeline - can be significantly enhanced
                    "start_time": "07:00 PST",
                    "briefing_time": "06:30 PST",
                    "debriefing_time": "18:00 PST",
                    "end_of_day": "19:00 PST"
                },
                "map_url": strategy_data['map_url']  # Include map for visual reference
            }

            plan_summary_text = f"""
            Mission Plan Summary:
    
            Mission Name: {plan_details['mission_name']}
            Objective: {plan_details['objective']}
    
            Key Search Areas:
            {chr(10).join([f"- {area['area']} (Priority: {area['priority']})" for area in plan_details['prioritized_search_areas']])}
    
            Resource Allocation:
            {chr(10).join([f"- {res['area']}: {', '.join(res['suggested_resources'])}" for res in plan_details['resource_allocation']])}
    
            See full JSON output for detailed communication, safety, and timeline information.
            """
            plan_details["plan_summary_text"] = plan_summary_text

            return plan_details
        except Exception as e:
            print(f"Error creating mission plan: {e}")
            return {"error": f"Error creating mission plan: {e}"}

    def _get_incident_data(self):
        """Simulates and returns incident data from the Incident Commander."""
        incident_data = {
            "incident_type": "Missing Person",
            "priority": "High",
            "location": "Crystal Cove State Park, CA",
            "mission_objective": "Locate and rescue missing hiker",
            "time_reported": "2024-08-03 14:00 PST",
            "search_area_size_km2": 10,
            "reporting_person": "Park Ranger John Doe",
            "last_known_location": "Trailhead near park entrance",
            "possible_scenarios": ["Lost on trail", "Injury", "Medical emergency"],
            "special_instructions": "Search near marked trails first, then expand to backcountry. Be aware of steep cliffs and wildlife.",
            "missing_person_description": {
                "name": "Alice Smith",
                "age": 34,
                "gender": "Female",
                "clothing": "Red jacket, blue jeans, hiking boots",
                "items": ["backpack", "water bottle", "cell phone (likely dead)"],
                "health_conditions": ["asthma", "allergies to bees"],
                "experience_level": "Experienced hiker"
            }
        }
        return incident_data

    def _get_real_weather_data(self, location_name):
        """Fetches and returns real-time weather data from OpenWeatherMap API."""
        try:

            weather_data = self.weather_fetcher.get_weather_for_location(location_name, use_gemini=True)  # Use Gemini
            return weather_data

        except pyowm.commons.exceptions.APIRequestError as e:
            print(f"API request error: {str(e)}")
            return {"error": f"API request error: {str(e)}"}
        except pyowm.commons.exceptions.APIResponseError as e:
            print(f"API response error: {str(e)}")
            return {"error": f"API response error: {str(e)}"}
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}

    def _get_static_map_url(self, location_name, search_radius_km=3):
        """Generates and returns a URL for a Google Static Map."""
        gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
        try:
            geocode_result = gmaps.geocode(location_name)
            if geocode_result:
                lat = geocode_result[0]['geometry']['location']['lat']
                lng = geocode_result[0]['geometry']['location']['lng']
                center_coords = f"{lat},{lng}"
                map_url_str = f"https://maps.googleapis.com/maps/api/staticmap?size=400x400&center={center_coords}&zoom=12&maptype=terrain&markers=color:red%7Clabel:P%7C{quote_plus(center_coords)}&key={GOOGLE_MAPS_API_KEY}"
                return map_url_str
            else:
                return "Error: Could not geocode location."
        except Exception as e:
            return f"Error generating map URL: {e}"


    def _get_operations_data(self, location_name):
        """Simulates and returns data from the Operations Section Chief, including real weather."""
        weather_data = self._get_real_weather_data(location_name)
        operations_data = {
            "available_search_teams": ["Team Alpha", "Team Bravo", "Team Charlie"],
            "current_weather_data": weather_data,
            "visibility": "Good" if weather_data.get("cloud_coverage_percent", 0) < 70 else "Moderate",
            "areas_already_searched": ["Parking Area 1", "Main Trails near Reservoir"]
        }
        return operations_data

    def _get_logistics_data(self):
        """Simulates and returns data from the Logistics Section Chief."""
        logistics_data = {
            "available_resources": {
                "ground_teams": 5,
                "search_dogs": 2,
                "helicopters": 1,
                "drones_with_thermal": 3,
                "paramedics": 3,
                "communication_units": 4
            },
            "resource_locations": {
                "ground_teams_base": "Park HQ",
                "helicopters_base": "Nearby airport",
                "drones_staging": "Open field near trailhead"
            },
            "communication_channels": {
                "primary": "VHF Channel 16",
                "secondary": "Satellite phone",
                "digital": "SARNet App"
            },
            "medical_supplies_status": "Adequate",
            "fuel_status": "Full",
            "transportation": "Trucks and SUVs available at Park HQ"
        }
        return logistics_data

    def _get_environmental_data(self, location):
        """Simulates and returns environmental data for the location."""
        environmental_data = {
            "location": location,
            "terrain_type": "Coastal mountains, mixed forest and trails",
            "vegetation_density": "Moderate to dense",
            "elevation_range_meters": "0-600",
            "water_sources": ["Freshwater creek", "Small reservoir"],
            "wildlife_hazards": ["Mountain lions", "Snakes", "Poison oak"],
            "daylight_hours": "6:00 AM to 8:00 PM",
            "typical_weather_patterns": "Morning fog, sunny afternoons"
        }
        return environmental_data

    def _calculate_search_area(self, incident_data):
        """Calculates and returns a simplistic search area based on last known location."""
        # ... (calculate_search_area - same as before) ... # Removed for brevity, keep your original calculate_search_area
        location = incident_data["last_known_location"]
        search_radius_km = 3
        search_area_description = f"Initial search area: Approximately a {search_radius_km}km radius around {location}."
        return search_area_description, search_radius_km

    def _prioritize_search_areas(self, search_radius_km, incident_data, environmental_data, operations_data):
        """Prioritizes and returns search areas based on various factors."""
        # ... (prioritize_search_areas - same as before) ... # Removed for brevity, keep your original prioritize_search_areas
        last_known_location = incident_data["last_known_location"]
        terrain = environmental_data["terrain_type"]
        weather_data = operations_data["current_weather_data"]

        prioritized_areas = [
            {"area": last_known_location, "priority": "High", "rationale": "Proximity to last known point."},
            {"area": "Densely forested areas within search radius", "priority": "Medium", "rationale": f"Terrain type: {terrain} may impede visibility."},
            {"area": "Water bodies within search radius", "priority": "Medium", "rationale": "Potential hazard area."},
            {"area": "Trails radiating outwards from last known location", "priority": "Low", "rationale": "Possible direction of travel."}
        ]

        if weather_data.get("rain_1h_mm", 0) > 0.1 or weather_data.get("snow_1h_mm", 0) > 0.1:
            for area in prioritized_areas:
                if "forested" in area["area"].lower():
                    area["priority"] = "High"
                if "trails" in area["area"].lower():
                    area["priority"] = "Medium"
        return prioritized_areas


    def _suggest_resource_allocation(self, prioritized_areas, logistics_data):
        """Suggests and returns resource allocation based on prioritized areas and available resources."""
        # ... (suggest_resource_allocation - same as before) ... # Removed for brevity, keep your original suggest_resource_allocation
        suggestions = []
        available_resources = logistics_data["available_resources"]

        priority_levels = ["High", "Medium", "Low"]
        resource_types = ["ground_teams", "search_dogs", "drones_with_thermal"]

        resource_counts = {resource_type: available_resources.get(resource_type, 0) for resource_type in resource_types}
        total_resources = sum(resource_counts.values())

        if total_resources > 0:
            resources_allocated = 0
            for area in prioritized_areas:
                if resources_allocated < total_resources:
                    allocated_count = 0
                    if area["priority"] == "High":
                        allocated_count = min(2, total_resources - resources_allocated)
                    elif area["priority"] == "Medium":
                        allocated_count = min(1, total_resources - resources_allocated)

                    if allocated_count > 0:
                        allocated_resources_list = []
                        resource_units = ["team" if "team" in r_type else "unit" for r_type in resource_types]
                        for i in range(allocated_count):
                            resource_type_index = resources_allocated % len(resource_types)
                            allocated_resources_list.append(f"1 {resource_units[resource_type_index]} ({resource_types[resource_type_index]})")

                        suggestions.append({
                            "area": area["area"],
                            "suggested_resources": allocated_resources_list,
                            "rationale": f"Priority: {area['priority']}, Available resources."
                        })
                        resources_allocated += allocated_count
        else:
            suggestions.append({"area": "All areas", "suggested_resources": ["None - Resources depleted"], "rationale": "No resources available for allocation."})
        return suggestions


    def _generate_gemini_summary(self, strategy_json):
        """Generates and returns a user-friendly summary using Gemini API."""
        prompt_content = f"""
        You are a helpful AI assistant for a Planning Section Chief in search and rescue operations.
        Based on the following structured information about a search strategy, generate a concise, human-readable summary for the Planning Section Chief.

        Focus on:
        - Clearly stating the incident and missing person details.
        - Summarizing the key prioritized search areas and the rationale behind them.
        - Presenting the suggested resource allocation in an actionable way.
        - Including the current weather conditions and a link to a map of the search area if available.
        - Maintain a professional and informative tone appropriate for emergency response personnel.

        Structured Search Strategy Information (JSON):
        ```json
        {json.dumps(strategy_json, indent=2)}
        ```
        """

        gemini_response = model.generate_content([prompt_content])
        if gemini_response.text:
            return gemini_response.text
        else:
            return "Error: Could not generate summary from Gemini API."

    def _format_output_json(self, incident_data, operations_data, logistics_data, environmental_data,
                             search_area_description, prioritized_areas, resource_allocation_suggestions, map_url):
        """Formats and returns the output as a JSON-like dictionary."""
        output_json = {
            "incident_details": incident_data,
            "operations_details": operations_data,
            "logistics_details": logistics_data,
            "environmental_details": environmental_data,
            "calculated_search_area": search_area_description,
            "prioritized_search_areas": prioritized_areas,
            "suggested_resource_allocation": resource_allocation_suggestions,
            "map_url": map_url
        }
        return output_json


    def generate_search_strategy(self):
        """
        Generates the complete search strategy (deprecated - use process_request now).
        This method is kept for backward compatibility but process_request is the preferred entry point.
        """
        return self._generate_and_format_strategy() # Simply calls the internal method

class WeatherFetcher: # Example Class for demonstration
    def __init__(self):
        pass # Add any class initializations if needed

    def _get_real_weather_data(self, location_name, use_gemini=True): # Added use_gemini parameter
        """
        Fetches and returns real-time weather data from OpenWeatherMap API.
        Implements a location narrowing system to find suitable place names,
        optionally using Gemini for variations.

        Args:
            location_name (str): The initial location name provided by the user.
            use_gemini (bool):  Whether to use Gemini to generate location variations.
                                 Defaults to True.

        Returns:
            dict: A dictionary containing either the weather data or an error message,
                  and potentially a 'gemini_note' string.
        """
        gemini_used_flag = False
        used_location_name = None # To store the name that actually worked
        try:
            owm = pyowm.OWM(OPENWEATHERMAP_API_KEY)
            mgr = owm.weather_manager()

            if use_gemini:
                location_names_to_try = self._generate_location_typonyms_gemini(location_name) # Gemini version
                if len(location_names_to_try) > 1: # If Gemini generated variations
                    gemini_used_flag = True
            else:
                location_names_to_try = self._generate_location_typonyms_basic(location_name) # Basic version

            if not location_names_to_try: # Fallback if no typonyms generated (shouldn't usually happen)
                location_names_to_try = [location_name] # At least try the original name

            for current_location_name in location_names_to_try:
                try:
                    observation = mgr.weather_at_place(current_location_name)
                    weather = observation.weather  # Get the Weather object
                    weather_dict = weather.to_dict()  # Get weather data as a dictionary
                    if gemini_used_flag:
                        gemini_note = f"ORIGINAL NAME: '{location_name}' wasn't found, Gemini used '{current_location_name}' to get weather info."
                        weather_dict["gemini_note"] = gemini_note # Add the informative note
                    return weather_dict
                except pyowm_exceptions.NotFoundError:
                    print(f"Location '{current_location_name}' not found, trying next...")  # Optional logging
                    continue  # Try the next location name in the list

            # If no location is found after trying all typonyms:
            error_message = f"Location '{location_name}' and variations not found."
            if gemini_used_flag:
                error_message += " Gemini variations were used but none were successful."
            error_message += " Please check the location name and try again with a more general or correctly formatted name (e.g., 'City,Country')."
            return {"error": error_message, "gemini_used": gemini_used_flag} # Include flag in error too

        except Exception as e:  # Catch broader exceptions like API key issues, network problems etc.
            return {"error": f"Error fetching weather data: {e}", "gemini_used": gemini_used_flag} # Include flag in error too

    def _generate_location_typonyms_gemini(self, location_name):
        """
        Generates location name variations using Google Gemini.

        Args:
            location_name (str): The original location name.

        Returns:
            list: A list of location names to try, generated by Gemini.
        """
        # --- Gemini Prompt ---
        prompt = f"""
        Generate a list of alternative location names that are geographically related to "{location_name}".
        These names should be suitable for use in a weather API that might not recognize very specific locations.
        Provide variations that range from more specific to more general, if applicable.
        Return the locations as a comma-separated list.

        Example Input: Crystal Cove State Park, CA
        Example Output: Crystal Cove State Park, CA, Crystal Cove, Newport Beach, CA, Orange County, CA, California, USA
        """

        try:
            # --- Call Gemini API ---
            response = model.generate_content(prompt)
            gemini_output = response.text
            print(f"Gemini Output for '{location_name}': {gemini_output}") # Log Gemini output for debugging

            # --- Process Gemini Output ---
            typonyms = [name.strip() for name in gemini_output.split(',')]
            return typonyms

        except Exception as e:
            print(f"Error during Gemini API call: {e}")
            return self._generate_location_typonyms_basic(location_name) # Fallback to basic method if Gemini fails


    def _generate_location_typonyms_basic(self, location_name):
        """
        Generates a list of potentially valid location names by narrowing down
        the original location name. This is a basic implementation.

        Args:
            location_name (str): The original location name.

        Returns:
            list: A list of location names to try, starting from the most specific
                  to more general.
        """
        location_parts = [part.strip() for part in location_name.split(',')]
        typonyms = []

        if len(location_parts) >= 2:  # Assume format like "City, State/Country"
            # Try most specific first
            typonyms.append(location_name)  # Original name
            typonyms.append(f"{location_parts[0]},{location_parts[-1]}")  # City,Country/State (less specific region)
            typonyms.append(location_parts[-1])  # Country/State only (most general region)
            typonyms.append(location_parts[0])  # City only (sometimes city name alone is enough)

        elif len(location_parts) == 1:  # Just a single location name part
            typonyms.append(location_name)  # Try the single name as is

        else:  # Empty or unexpected format
            typonyms.append(location_name)  # Just try the input as is

        return typonyms


    def get_weather_for_location(self, location_name, use_gemini=True): # Added use_gemini parameter here too
        return self._get_real_weather_data(location_name, use_gemini) # Pass use_gemini down


if __name__ == "__main__":
    # Instantiate the agent
    planning_agent = PlanningAgent()

    # Example request message to generate a strategy (as before)
    strategy_request_message = {"action": "generate_strategy"}

    # Process the strategy request
    strategy_output = planning_agent.process_request(strategy_request_message)

    print("\n--- Search Strategy Details (JSON Output from process_request) ---")
    print(json.dumps(strategy_output, indent=4))

    # Example request message to create a mission plan
    plan_request_message = {"action": "create_mission_plan"}

    # Process the plan request
    plan_output = planning_agent.process_request(plan_request_message)

    print("\n\n--- Mission Plan Details (JSON Output from process_request) ---")
    print(json.dumps(plan_output, indent=4))

