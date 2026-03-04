def book_rapido(route):
    return {
        "provider": "Rapido",
        "status": "confirmed",
        "eta": "12 mins",
        "pickup": "Home"
    }


def schedule_meal(meal):
    return {
        "provider": "FoodService",
        "status": "scheduled",
        "meal": meal
    }
