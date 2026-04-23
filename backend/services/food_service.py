"""
Food service — fetches recipes from Spoonacular matching the mood.
"""
import requests
from config import Config

BASE_URL = "https://api.spoonacular.com/recipes"


def get_recipes(query: str, limit: int = 4) -> list[dict]:
    """Search Spoonacular for recipes matching mood-based query."""
    if not Config.SPOONACULAR_API_KEY:
        return []
    try:
        r = requests.get(
            f"{BASE_URL}/complexSearch",
            params={
                "apiKey"        : Config.SPOONACULAR_API_KEY,
                "query"         : query,
                "number"        : limit,
                "addRecipeInfo" : True,
                "fillIngredients": False,
            },
            timeout=10,
        )
        if r.status_code != 200:
            return []

        items = r.json().get("results", [])
        return [
            {
                "title"    : recipe.get("title"),
                "ready_in" : recipe.get("readyInMinutes"),
                "servings" : recipe.get("servings"),
                "thumbnail": recipe.get("image"),
                "url"      : f"https://spoonacular.com/recipes/{recipe.get('title','').replace(' ','-').lower()}-{recipe.get('id')}",
                "source"   : "spoonacular",
            }
            for recipe in items
        ]
    except Exception:
        return []