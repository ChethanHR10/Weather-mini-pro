from flask import Flask, request, jsonify, render_template
import requests
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Replace with your actual OpenWeatherMap API key
OPENWEATHER_API_KEY = '0695557b8df808d85e56f3b4f24c15f8'

def get_weather(city_name):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']
        return f"{weather_description}, {temperature}°C"
    else:
        logging.error(f"Failed to get weather for {city_name}: {response.text}")
        return "No data available"

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

def reverse_geocode(lat, lng):
    url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lng}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'address' in data:
            if 'city' in data['address']:
                return data['address']['city']
            elif 'town' in data['address']:
                return data['address']['town']
            elif 'village' in data['address']:
                return data['address']['village']
    logging.warning(f"Reverse geocoding failed for {lat}, {lng}: {response.text}")
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/getWeather')
def get_weather_route():
    location = request.args.get('location')
    weather_data = get_weather(location)
    return jsonify({"weather": weather_data})

@app.route('/getTravelWeather')
def get_travel_weather_route():
    try:
        start_location = request.args.get('start')
        end_location = request.args.get('end')

        # Log the start and end locations
        logging.debug(f"Start location: {start_location}, End location: {end_location}")

        # Get coordinates for start and end locations
        start_url = f"https://nominatim.openstreetmap.org/search?q={start_location}&format=json"
        end_url = f"https://nominatim.openstreetmap.org/search?q={end_location}&format=json"
        start_response = requests.get(start_url).json()
        end_response = requests.get(end_url).json()

        # Log the responses from the geocoding API
        logging.debug(f"Start response: {start_response}")
        logging.debug(f"End response: {end_response}")

        if not start_response or not end_response:
            logging.error("Invalid start or end location")
            return jsonify({"error": "Invalid start or end location"}), 400

        start_lat, start_lng = float(start_response[0]['lat']), float(start_response[0]['lon'])
        end_lat, end_lng = float(end_response[0]['lat']), float(end_response[0]['lon'])

        # Log the coordinates
        logging.debug(f"Start coordinates: ({start_lat}, {start_lng}), End coordinates: ({end_lat}, {end_lng})")

        coordinates = get_route(start_lat, start_lng, end_lat, end_lng)

        # Log the route coordinates
        logging.debug(f"Route coordinates: {coordinates}")

        weather_info = {}
        if coordinates:
            for i in range(0, len(coordinates), max(1, len(coordinates) // 5)):  # Get approx. 5 major points
                lng, lat = coordinates[i]
                city_name = reverse_geocode(lat, lng)
                if city_name:
                    weather_info[city_name] = get_weather(city_name)
                else:
                    weather_info[f"{lat}, {lng}"] = "No city found"

        return jsonify(weather_info)
    
    except Exception as e:
        logging.error(f"Error in /getTravelWeather: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/suggestActivities')
def suggest_activities_route():
    location = request.args.get('location')
    weather = get_weather(location)
    activities = []

    # Suggest activities based on the weather conditions
    if "rain" in weather:
        activities = ["Visit a museum", "Watch a movie", "Indoor rock climbing"]
    elif "clear" in weather:
        activities = ["Go for a walk", "Have a picnic", "Visit a park"]
    elif "cloud" in weather:
        activities = ["Photography", "Visit a cafe", "Explore local markets"]
    else:
        activities = ["Check local events", "Explore indoor activities"]

    return jsonify(activities)

if __name__ == '__main__':
    app.run(debug=True)
