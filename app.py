import googlemaps
from flask import Flask, request, jsonify, render_template
import requests
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

OPENWEATHER_API_KEY = '0695557b8df808d85e56f3b4f24c15f8'
GOOGLE_MAPS_API_KEY = 'AIzaSyCt_OIjEj7jUZKPl7gjJVMyh8HOwn0oPWQ'
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

def get_weather(city_name):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']
        rain_status = data.get('rain', {}).get('1h', 0) > 0  # Check for rain in the last hour
        return f"{weather_description}, {temperature}°C", rain_status
    else:
        logging.error(f"Failed to get weather for {city_name}: {response.text}")
        return "No data available", False

def get_route(start_lat, start_lng, end_lat, end_lng):
    url = f"http://router.project-osrm.org/route/v1/driving/{start_lng},{start_lat};{end_lng},{end_lat}?overview=full&geometries=geojson"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'routes' in data and len(data['routes']) > 0:
            return data['routes'][0]['geometry']['coordinates']
        else:
            logging.error("No routes found in the response.")
    else:
        logging.error(f"Failed to get route: {response.text}")
    return None

def get_coordinates(location):
    try:
        geocode_result = gmaps.geocode(location)
        if geocode_result:
            lat = geocode_result[0]['geometry']['location']['lat']
            lng = geocode_result[0]['geometry']['location']['lng']
            return lat, lng
    except Exception as e:
        logging.error(f"Error getting coordinates for {location}: {e}")
    return None, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/getWeather')
def get_weather_route():
    location = request.args.get('location')
    weather_data, rain_status = get_weather(location)
    return jsonify({"weather": weather_data, "rain": rain_status})

@app.route('/getTravelWeather')
def get_travel_weather_route():
    try:
        start_location = request.args.get('start')
        end_location = request.args.get('end')

        # Log the start and end locations
        logging.debug(f"Start location: {start_location}, End location: {end_location}")

        # Get coordinates for start and end locations
        start_lat, start_lng = get_coordinates(start_location)
        end_lat, end_lng = get_coordinates(end_location)

        if start_lat is None or end_lat is None:
            logging.error("Invalid start or end location")
            return jsonify({"error": "Invalid start or end location"}), 400

        # Log the coordinates
        logging.debug(f"Start coordinates: ({start_lat}, {start_lng}), End coordinates: ({end_lat}, {end_lng})")

        coordinates = get_route(start_lat, start_lng, end_lat, end_lng)

        # Log the route coordinates
        logging.debug(f"Route coordinates: {coordinates}")

        weather_info = []
        visited_places = set()
        if coordinates:
            distance_threshold = 100  # Reduced distance threshold to capture more places
            total_distance = len(coordinates)  # Simplified for example; in practice, calculate actual distance
            skip_factor = max(1, total_distance // distance_threshold)

            # Always include the start and end coordinates
            coordinates_to_check = [coordinates[0]] + coordinates[1:-1:skip_factor] + [coordinates[-1]]

            for coord in coordinates_to_check:
                lng, lat = coord
                city_name = get_city_name(lat, lng)
                if city_name and city_name not in visited_places:
                    visited_places.add(city_name)
                    weather_data, rain_status = get_weather(city_name)
                    if weather_data != "No data available":
                        weather_info.append({"location": city_name, "weather": weather_data, "rain": rain_status})

        return jsonify(weather_info)

    except Exception as e:
        logging.error(f"Error in /getTravelWeather: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def get_city_name(lat, lng):
    try:
        reverse_geocode_result = gmaps.reverse_geocode((lat, lng))
        if reverse_geocode_result:
            for result in reverse_geocode_result:
                address_components = result['address_components']
                city = None
                for component in address_components:
                    if 'locality' in component['types'] or 'sublocality' in component['types']:
                        city = component['long_name']
                        break
                if city:
                    return city
    except Exception as e:
        logging.warning(f"Reverse geocoding failed for {lat}, {lng}: {e}")
    return None

@app.route('/suggestActivities')
def suggest_activities_route():
    location = request.args.get('location')
    weather, _ = get_weather(location)
    activities = []

    # Suggest activities based on the weather conditions
    if "rain" in weather:
        activities = ["Visit a museum", "Watch a movie", "Indoor rock climbing"]
    elif "clear" in weather:
        activities = ["Go for a walk", "Have a picnic", "Visit a park"]
    elif "overcast clouds" in weather:
        activities = ["Have a picnic", "Visit a mall"]
    elif "cloud" in weather:
        activities = ["Photography", "Visit a cafe", "Spend time with friends"]
    else:
        activities = ["Check local events", "Explore indoor activities"]

    return jsonify(activities)

if __name__ == '__main__':
    app.run(debug=True)
