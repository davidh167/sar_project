# Search and Rescue (SAR) Agent Framework - CSC 581


### **--See End of README for Project Updates--**


## Planning Agent
Added a PlanningAgent class that does the following:
- Generating comprehensive search strategies by integrating simulated incident data, operations data (including real-time weather), logistics data, and environmental data.
- Prioritizing search areas based on incident details, environmental factors, and operational conditions to focus search efforts effectively. 
- Suggesting resource allocation for prioritized search areas based on available logistics, optimizing resource utilization. 
- Creating basic mission plans that outline mission objectives, search strategies, resource allocation, communication plans, safety protocols, timelines, and map references. Fetching real-time weather data for the incident location using the OpenWeatherMap API, dynamically adjusting strategies to current conditions. 
- Generating location name variations (typonyms) using Google Gemini (and a basic fallback) to improve weather data retrieval for potentially ambiguous location names. 
- Generating Google Static Map URLs to visually represent the search area and aid in spatial understanding. 
- Providing user-friendly summaries of both search strategies and mission plans using the Gemini API, making complex data easily digestible for SAR personnel. 
- Formatting output as structured JSON for easy integration with other systems and for detailed data access. 
- Processing requests via a process_request method, enabling handling of different actions such as "generate_strategy" and "create_mission_plan" in a modular way. 
- Incorporating safety settings for Gemini API interactions, controlling the generation of potentially harmful content.


## Prerequisites

- Python 3.8 or higher
- pyenv (recommended for Python version management)
- pip (for dependency management)

## Setup and Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd sar-project
```

2. Set up Python environment:
```bash
# Using pyenv (recommended)
pyenv install 3.9.6  # or your preferred version
pyenv local 3.9.6

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -e .
```

4. Configure environment variables:

#### OpenAI:
- Obtain required API keys:
  1. OpenAI API key: Sign up at https://platform.openai.com/signup
- Update your `.env` file with the following:
    ```
    OPENAI_API_KEY=your_openai_api_key_here
    ```
#### Google Gemini:
- Obtain required API keys:
  1. ``` pip install google-generativeai ```
  2. ``` import google.generativeai as genai ```
  3. Google Gemini API Key: Obtain at https://aistudio.google.com/apikey
- Configure with the following:
  ```
  genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
  ```
- Update your `.env` file with the following:
    ```
    GOOGLE_API_KEY=your_gemini_api_key_here
    ```

#### OpenWeatherMaps:
- Obtain required API keys:
  1. ``` pip install pyowm ```
  2. ```
       import pyowm 
       from pyowm.commons import exceptions as pyowm_exceptions
       owm = pyowm.OWM(OPENWEATHERMAP_API_KEY)
       mgr = owm.weather_manager()
     ```
  3. OpenWeatherMaps: Obtain at https://openweathermap.org/api
- Configure with the following:
  ```
  OPENWEATHERMAP_API_KEY = os.getenv("OWM_API_KEY") # Get from OpenWeatherMap
  ```
- Update your `.env` file with the following:
  ```
  OWM_API_KEY=your_owm_api_key_here
  ```

#### GoogleMaps:
- Obtain required API keys:
  1. ``` pip install googlemaps ```
  2. ``` import googlemaps```
  3. Google Maps:  Obtain at: https://developers.google.com/maps/documentation/javascript/get-api-key#console
- Configure with the following:
  ```
  GOOGLE_MAPS_API_KEY = os.getenv("GMAPS_API_KEY") 
  gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
  ```
  - Update your `.env` file with the following:
  ```
  GMAPS_API_KEY=your_google_maps_api_key_here
  ```




Make sure to keep your `.env` file private and never commit it to version control.

## Project Structure

```
sar-project/
├── src/
│   └── sar_project/         # Main package directory
│       └── agents/          # Agent implementations
│       └── config/          # Configuration and settings
│       └── knowledge/       # Knowledge base implementations
├── tests/                   # Test directory
├── pyproject.toml           # Project metadata and build configuration
├── requirements.txt         # Project dependencies
└── .env                     # Environment configuration
```

## Development

This project follows modern Python development practices:

1. Source code is organized in the `src/sar_project` layout
2. Use `pip install -e .` for development installation
3. Run tests with `pytest tests/`
4. Follow the existing code style and structure
5. Make sure to update requirements.txt when adding dependencies

## Asssignment 3 Updates:

Implemented the following features, based on feedback from the previous assignment:

- Added logging to the PlanningAgent class to track the execution of different methods and actions.
- Fixed a bug with Gemini API typonym generation, where the API was not being called correctly. Additionally, fixed unintentional over-correction on Gemini typonym generation.
- Implement previously partially implemented methods in the PlanningAgent class, for better functionality.

