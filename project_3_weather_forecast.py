#Import function, requires pip install requests.
import requests

#State abbreviations dictionary.
STATE_ABBREVIATIONS = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut",
    "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana",
    "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
    "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts",
    "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska",
    "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina",
    "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island",
    "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee",
    "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming"}

def normalize_state(state_input):
    """
    Converts state abbreviations (VA) into full names (Virginia).
    If already a full name, just returns it.
    """
    state_input = state_input.strip()

    # If user typed abbreviation like VA
    if state_input.upper() in STATE_ABBREVIATIONS:
        return STATE_ABBREVIATIONS[state_input.upper()]

    # Otherwise assume it's already a full name
    return state_input

# Base URLs for the APIs
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def get_location(city, state):
    """
    This function takes a city and state, then uses the Open-Meteo
    geocoding API to find the latitude and longitude.

    It loops through results to make sure the location is in the
    United States AND matches the state entered by the user.
    """

    params = {
        "name": city,
        "count": 10,          # get multiple results in case of duplicates
        "language": "en",
        "format": "json"
    }

    # Send request to geocoding API
    response = requests.get(GEOCODING_URL, params=params, timeout=10)
    response.raise_for_status()  # raises error if request fails

    data = response.json()

    # If no results were returned, location doesn't exist
    if "results" not in data:
        return None

    # Loop through possible matches
    for place in data["results"]:
        country = place.get("country", "")
        state_name = place.get("admin1", "")

        # Check for correct country AND state
        if country.lower() == "united states" and state_name.lower() == state.lower():
            return place

    # If nothing matched exactly, return None
    return None


def get_forecast(lat, lon):
    """
    This function takes latitude and longitude and requests
    a 10-day forecast from Open-Meteo.
    """

    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "temperature_unit": "fahrenheit",   # required by assignment
        "precipitation_unit": "inch",       # required by assignment
        "timezone": "auto",
        "forecast_days": 10                 # exactly 10 days
    }

    response = requests.get(FORECAST_URL, params=params, timeout=10)
    response.raise_for_status()

    return response.json()


def display_forecast(city, state, data):
    """
    This function formats and prints the weather data in a table.
    """

    daily = data.get("daily", {})

    dates = daily.get("time", [])
    max_temps = daily.get("temperature_2m_max", [])
    min_temps = daily.get("temperature_2m_min", [])
    rain = daily.get("precipitation_sum", [])

    # Header
    print(f"\n--- 10-Day Forecast for {city}, {state} ---")
    print("Date         | Max Temp | Min Temp | Rain")
    print("-" * 50)

    # Loop through each day and print nicely formatted row
    for i in range(len(dates)):
        print(
            f"{dates[i]} | "
            f"{max_temps[i]:>7.1f}°F | "
            f"{min_temps[i]:>7.1f}°F | "
            f"{rain[i]:>6.3f}inch"
        )


def main():
    print("10-Day Weather Forecast")

    try:
        # 🔁 OUTER LOOP (repeat entire program)
        while True:

            # 🔁 INNER LOOP (get valid location)
            while True:
                city = input("\nEnter city: ").strip()
                state_input = input("Enter state: ").strip()
                state = normalize_state(state_input)

                if city == "" or state == "":
                    print("Error: Both city and state must be provided.")
                    continue

                location = get_location(city, state)

                if location is None:
                    print(f"Location '{city}, {state}' not found. Try again.")
                    continue

                break  # valid location found

            # Get forecast
            lat = location["latitude"]
            lon = location["longitude"]

            forecast_data = get_forecast(lat, lon)

            # Display results
            display_forecast(location["name"], location["admin1"], forecast_data)

            # 🔁 ASK USER IF THEY WANT ANOTHER FORECAST
            again = input("\nWould you like another forecast? (y/n): ").strip().lower()

            if again != "y":
                print("Goodbye!")
                break

        # Step 2: Get forecast using coordinates
        lat = location["latitude"]
        lon = location["longitude"]

        forecast_data = get_forecast(lat, lon)

        # Step 3: Display results
        display_forecast(location["name"], location["admin1"], forecast_data)

    # Required error handling
    except requests.exceptions.Timeout:
        print("Error: Request timed out.")
    except requests.exceptions.ConnectionError:
        print("Error: Connection failed.")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    except KeyError:
        print("Error: Unexpected API response format.")
    except Exception as e:
        print(f"Unexpected error: {e}")


# Run the program
if __name__ == "__main__":
    main()