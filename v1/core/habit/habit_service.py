from database.data import User, Habit, Habit_Log
from datetime import datetime, timedelta
from flask_sse import sse
from flask import jsonify
import redis
import time
from typing import Optional, Dict, Tuple, Union

# Connect to Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)


class HabitEngine:
    """
    Core engine for handling habit-related operations such as logging progress, streaks,
    statistics, and timeboxing.
    """

    def post_log(self, username: str, habit_name: str, habit_id: str, log: str) -> Tuple[Dict[str, Union[str, dict]], int]:
        """Post a log for a specific habit."""

        # Validate log content
        if not log:
            return {"message": "Log content cannot be empty"}, 400

        log = log.lower()
        if log != 'done':
            return {"message": "Log content should be 'done'"}, 409

        habit = Habit.habits.find_one({'habit_id': habit_id})
        if not habit:
            return {"message": "Habit not found"}, 404

        habit_frequency: Optional[str] = habit.get('frequency')
        if not habit_frequency:
            return {"message": "No frequency found, update frequency for the habit and try again"}, 404

        if habit_frequency not in ['daily', 'weekly', 'monthly']:
            return {"message": "Frequency must be 'daily', 'weekly', or 'monthly'"}, 409

        try:
            today: datetime = datetime.utcnow()
            log_entry: Optional[dict] = Habit_Log.habit_logs.find_one(
                {"habit_id": habit_id},
                sort=[("timestamp", -1)]
            )
            start_date: Optional[datetime] = log_entry.get("timestamp") if log_entry else None

            if log_entry and not start_date:
                return {"message": f"Habit log entry found but missing timestamp: {log_entry}"}, 400

            elif habit_frequency == 'daily':
                if not start_date or today - start_date >= timedelta(days=1):
                    result = Habit_Log(username, habit_name, habit_id, log).insert_log()
                    return result
                else:
                    return {"message": f"You can't log more than 1 '{habit_frequency}' log per day"}, 409

            elif habit_frequency == 'weekly':
                if not start_date or today - start_date >= timedelta(weeks=1):
                    result = Habit_Log(username, habit_name, habit_id, log).insert_log()
                    return result
                else:
                    return {"message": f"You can't log more than 1 '{habit_frequency}' log per week"}, 409

            elif habit_frequency == 'monthly':
                if not start_date or today - start_date >= timedelta(days=30):
                    result = Habit_Log(username, habit_name, habit_id, log).insert_log()
                    return result
                else:
                    return {"message": f"You can't log more than 1 '{habit_frequency}' log per month"}, 409

        except Exception as e:
            return {"message": f"Error posting log: {str(e)}"}, 500

    def log_history(self, habit_id: str) -> Union[Dict[str, str], Tuple[Dict[str, str], int]]:
        """
        Fetches log history for a given habit ID.
        """
        logs = Habit_Log.habit_logs.find({'habit_id': habit_id})
        if logs is None:
            return {"message": "No logs found"}, 404
        return logs

    def streak(self, habit_id: str) -> Dict[str, str]:
        """
        Calculate the current streak for a habit.
        """
        habit = Habit.habits.find_one({'habit_id': habit_id})
        if not habit:
            return {"message": "Habit not found"}, 404

        habit_name: Optional[str] = habit.get('habit_name')
        habit_frequency: Optional[str] = habit.get('frequency')
        logs = Habit_Log.habit_logs.find({'habit_id': habit_id}).sort('timestamp', 1)

        if not logs:
            return {"message": "No logs found for this habit"}, 404

        streak: int = 0
        last_log_date: Optional[datetime] = None
        last_log_week: Optional[int] = None
        last_log_month: Optional[int] = None
        last_log_year: Optional[int] = None

        for log in logs:
            log_date: Optional[datetime] = log.get('timestamp')
            if not log_date or log.get('log') != 'done':
                continue

            if habit_frequency == 'daily':
                if last_log_date is None or log_date - last_log_date == timedelta(days=1):
                    streak += 1
                    last_log_date = log_date
                else:
                    break

            elif habit_frequency == 'weekly':
                log_week: int = log_date.isocalendar()[1]
                log_year: int = log_date.year

                if last_log_week is None or (
                    log_week == last_log_week + 1 and log_year == last_log_year
                ) or (
                    log_week == 1 and log_year == last_log_year + 1):
                    streak += 1
                    last_log_week = log_week
                    last_log_year = log_year
                else:
                    break

            elif habit_frequency == 'monthly':
                log_month: int = log_date.month
                log_year: int = log_date.year
                if last_log_month is None or (
                    log_month == last_log_month + 1 and log_year == last_log_year
                ) or (
                    log_month == 1 and log_year == last_log_year + 1):
                    streak += 1
                    last_log_month = log_month
                    last_log_year = log_year
                else:
                    break

        return {"streak_count": f"Your streak for '{habit_name}' is '{streak}'"}

    def statistics(self, habit_id: str) -> Tuple[Dict[str, Union[str, dict]], int]:
        """
        Calculate and return progress statistics for a habit.
        """
        habit = Habit.habits.find_one({'habit_id': habit_id})
        if not habit:
            return jsonify({"message": "Habit not found"}), 404

        habit_frequency: Optional[str] = habit.get('frequency')
        if not habit_frequency:
            return jsonify({"message": "No frequency found, update frequency for the habit and try again"}), 404
        elif habit_frequency not in ['daily', 'weekly', 'monthly']:
            return jsonify({"message": "Frequency must be 'daily', 'weekly', or 'monthly'"}), 409

        log_entry = Habit_Log.habit_logs.find_one(
            {"habit_id": habit_id},
            sort=[("timestamp", -1)]
        )
        start_date: Optional[datetime] = log_entry.get("timestamp") if log_entry else None
        if not start_date:
            return jsonify({"message": "Habit start date is missing"}), 400

        logs = Habit_Log.habit_logs.find({'habit_id': habit_id}).sort('timestamp', 1)
        if not logs:
            return jsonify({"message": "No logs found for this habit"}), 404

        total_periods: int = 0
        completed: int = 0
        adherence: float = 0.0

        today: datetime = datetime.utcnow()

        if habit_frequency == 'daily':
            while start_date <= today:
                total_periods += 1
                for log in logs:
                    if log.get('log') == 'done' and start_date <= log.get('timestamp') < start_date + timedelta(days=1):
                        completed += 1
                start_date += timedelta(days=1)

        elif habit_frequency == 'weekly':
            while start_date <= today:
                total_periods += 1
                for log in logs:
                    if log.get('log') == 'done' and start_date <= log.get('timestamp') < start_date + timedelta(weeks=1):
                        completed += 1
                start_date += timedelta(weeks=1)

        elif habit_frequency == 'monthly':
            while start_date <= today:
                total_periods += 1
                for log in logs:
                    if log.get('log') == 'done' and start_date <= log.get('timestamp') < (start_date.replace(month=start_date.month + 1) if start_date.month < 12 else start_date.replace(year=start_date.year + 1, month=1)):
                        completed += 1
                if start_date.month == 12:
                    start_date = start_date.replace(year=start_date.year + 1, month=1)
                else:
                    start_date = start_date.replace(month=start_date.month + 1)

        if total_periods > 0:
            adherence = (completed / total_periods) * 100

        stats = {
            "habit_name": habit.get("habit_name", "Unknown"),
            "total_periods": total_periods,
            "completed": completed,
            "adherence_rate": round(adherence, 2),
            "habit_frequency": habit_frequency,
        }

        return {"message": "Habit statistics calculated successfully", "data": stats}, 200
