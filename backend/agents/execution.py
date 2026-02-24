from tools import book_rapido, schedule_meal


def execute_plan(plan: dict):
    route = plan.get("route", "")
    meal = plan.get("meal", "")
    
    ride_result = None
    if "bike" in route.lower() or "rapido" in route.lower():
        ride_result = book_rapido(route)
    
    meal_result = schedule_meal(meal)
    
    return {
        "ride": ride_result,
        "meal": meal_result,
        "execution_status": "completed"
    }
