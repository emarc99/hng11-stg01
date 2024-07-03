from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Open-Meteo API base URL
OPEN_METEO_API_URL = "https://api.open-meteo.com/v1/forecast"

# Default location coordinates for Lagos (if IP-based location fails)
DEFAULT_LATITUDE = 6.5244
DEFAULT_LONGITUDE = 3.3792

@app.route('/api/hello', methods=['GET'])
def hello():
    # Get visitor name from query parameter
    visitor_name = request.args.get('visitor_name')

    # Get client IP address from the request object
    client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)

    # Get location from IP address
    try:
        ip_response = requests.get(f"http://ip-api.com/json/{client_ip}")
        ip_data = ip_response.json()
        latitude = ip_data.get('lat', DEFAULT_LATITUDE)
        longitude = ip_data.get('lon', DEFAULT_LONGITUDE)
        location = ip_data.get('city', 'Unknown')
    except Exception as e:
        latitude = DEFAULT_LATITUDE
        longitude = DEFAULT_LONGITUDE
        location = "Unknown"

    # Construct the Open-Meteo API URL
    api_url = f"{OPEN_METEO_API_URL}?latitude={latitude}&longitude={longitude}&current_weather=true&timeformat=unixtime&units=metric"

    # Fetch weather data
    weather_response = requests.get(api_url)

    # Check for successful response
    if weather_response.status_code == 200:
        try:
            # Parse JSON response
            weather_data = weather_response.json()
            current_temp = weather_data["current_weather"]["temperature"]
        except KeyError:
            current_temp = "N/A (Temperature data unavailable)"
        except requests.exceptions.JSONDecodeError:
            current_temp = "N/A (Failed to parse weather data)"
    else:
        current_temp = "N/A (Failed to fetch weather data)"

    # Prepare response data
    response = {
        "client_ip": client_ip,
        "location": location,
        "greeting": f"Hello, {visitor_name}!, the temperature is {current_temp} degrees Celsius in {location}"
    }

    return jsonify(response)