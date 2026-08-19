import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

URL = "https://places.googleapis.com/v1/places:searchText"


def search_places(category, location, max_results=20):

    query = f"{category} in {location}"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": (
            "places.id,"
            "places.displayName,"
            "places.formattedAddress,"
            "places.nationalPhoneNumber,"
            "places.rating,"
            "places.userRatingCount,"
            "places.websiteUri,"
            "places.googleMapsUri"
        )
    }

    body = {
        "textQuery": query,
        "pageSize": min(max_results, 20)
    }

    print("\nSearching Google Places...")
    print("Query:", query)

    response = requests.post(
        URL,
        headers=headers,
        json=body,
        timeout=30
    )

    print("HTTP Status:", response.status_code)

    if response.status_code != 200:
        print("\n========== GOOGLE API ERROR ==========")
        print(response.text)
        print("======================================")
        return []

    print("\n========== GOOGLE RAW RESPONSE ==========")
    print(response.text)
    print("==========================================")

    data = response.json()

    places = data.get("places", [])

    print("\nPlaces returned:", len(places))

    return places