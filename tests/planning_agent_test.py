import unittest
import json
# from src.sar_project.agents import base_agent
from src.sar_project.agents.planning_agent import PlanningAgent, WeatherFetcher  # Adjust import path

class TestPlanningAgent(unittest.TestCase):

    def setUp(self):
        self.planning_agent = PlanningAgent()
        self.weather_fetcher = WeatherFetcher()

    def tearDown(self):
        pass

    def test_process_request_generate_strategy(self):
        """Test process_request with 'generate_strategy' action."""
        request_message = {"action": "generate_strategy"}
        output = self.planning_agent.process_request(request_message)

        self.assertIsInstance(output, dict, "Output should be a dictionary")
        self.assertIn("strategy_summary_text_gemini", output, "Output should contain Gemini summary")
        self.assertIn("prioritized_search_areas", output, "Output should contain prioritized areas")

    def test_process_request_create_mission_plan(self):
        """Test process_request with 'create_mission_plan' action."""
        request_message = {"action": "create_mission_plan"}
        output = self.planning_agent.process_request(request_message)

        self.assertIsInstance(output, dict, "Output should be a dictionary")
        self.assertIn("plan_summary_text", output, "Output should contain plan summary")
        self.assertIn("mission_name", output, "Output should contain mission name")
        self.assertIn("prioritized_search_areas", output, "Output should contain prioritized areas")

    def test_process_request_invalid_action(self):
        """Test process_request with an invalid action."""
        request_message = {"action": "invalid_action"}
        output = self.planning_agent.process_request(request_message)

        self.assertIsInstance(output, dict, "Output should be a dictionary")
        self.assertIn("error", output, "Output should contain an error key")
        self.assertEqual(output["error"], "Unknown action requested.", "Error message should be 'Unknown action requested.'")
        self.assertEqual(output["requested_action"], "invalid_action", "Requested action should be returned in error output")

    def test_weather_fetcher_get_weather_valid_location(self):
        """Test WeatherFetcher.get_weather_for_location with a valid location."""
        location_name = "London, UK"
        weather_data = self.weather_fetcher.get_weather_for_location(location_name)

        self.assertIsInstance(weather_data, dict, "Weather data should be a dictionary")
        self.assertNotIn("error", weather_data, "No error should be present for valid location")
        self.assertIn("temp", weather_data.get('temperature', weather_data), "Weather data should contain temperature info")

    def test_weather_fetcher_get_weather_invalid_location(self):
        """Test WeatherFetcher.get_weather_for_location with an invalid location."""
        location_name = "InvalidLocationNameThatShouldNotExist"
        weather_data = self.weather_fetcher.get_weather_for_location(location_name)

        self.assertIsInstance(weather_data, dict, "Weather data should be a dictionary (even on error)")
        self.assertIn("error", weather_data, "Error key should be present for invalid location")


if __name__ == '__main__':
    unittest.main()