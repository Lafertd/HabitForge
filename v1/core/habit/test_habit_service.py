import unittest
from unittest.mock import patch, MagicMock
from typing import Dict
from HabitForge.v1.core.habit.habit_service import HabitEngine  # Assuming HabitEngine is in habit_service.py


# Import the function reference without calling it directly
log_history = HabitEngine.log_history

class TestHabit(unittest.TestCase):
    @patch('habit_service.HabitEngine.log_history.Habit_Log.habit_logs.find')  # Ensure this matches where the find method is used
    def test_log_found(self, find_mock):
        # Mock Habit_Log.habit_logs.find() method behavior
        mocked_logs = MagicMock()

        # Simulate logs count > 0
        mocked_logs.count.return_value = 1  # Indicate that logs are found
        find_mock.return_value = mocked_logs  # Make the find method return the mocked logs

        # Arrange
        habit_id = 456734  # Dummy habit ID for testing
        expected = mocked_logs  # Expected result is the mocked logs

        # Act
        result = log_history(habit_id)  # Call the log_history function with the mock

        # Assert
        self.assertEqual(result, expected)  # Check if the result matches the mocked logs

if __name__ == "__main__":
    unittest.main()
