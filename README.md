# Search and Rescue (SAR) Agent Framework - CSC 581

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


## FAQ

### Assignment Questions

**Q: How do I choose a role for my agent?**

**A:** Review the list of SAR roles above and consider which aspects interest you most. Your agent should provide clear value to SAR operations through automation, decision support, or information processing.

**Q: What capabilities should my agent have?**

**A:** Your agent should handle tasks relevant to its role such as: data processing, decision making, communication with other agents, and providing actionable information to human operators.

**Q: Can I add new dependencies?**

**A:** Yes, you can add new Python packages to requirements.txt as needed for your implementation.


### Technical Questions

**Q: Why am I getting API key errors?**

**A:** Ensure you've properly set up your .env file and obtained valid API keys from the services listed above.

**Q: How do I test my agent?**

**A:** Use the provided test framework in the tests/ directory. Write tests that verify your agent's core functionality.

**Q: Can I use external libraries for my agent?**

**A:** Yes, you can use external libraries as long as they are compatible.
