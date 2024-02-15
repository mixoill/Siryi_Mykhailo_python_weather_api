import datetime as dt
import json

import requests
from flask import Flask, jsonify, request

# create your API token, and set it up in Postman collection as part of the Body section
API_TOKEN = ""
# you can get API keys for free here - https://api-ninjas.com/api/jokes
RSA_KEY = ""

app = Flask(__name__)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA L2: python Saas.</h2></p>"


@app.route("/content/api/v1/integration/generate", methods=["POST"])
def weather_endpoint():
    start_dt = dt.datetime.now()
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    token = json_data.get("token")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    name = ""
    if json_data.get("name"):
        name = json_data.get("name")
        
    city = ""
    if json_data.get("city"):
        city = json_data.get("city")
        
    weather_date = ""
    if json_data.get("weather_date"):
        weather_date = json_data.get("weather_date")

    url_base_url = "https://api.api-ninjas.com"
    url_api_version = "v1"
    url_api = "weather"
    url = f"{url_base_url}/{url_api_version}/{url_api}?city={city}&date={weather_date}"
    headers = {
        'X-Api-Key': RSA_KEY
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == requests.codes.ok:
        response_json = response.json()
        message = ''
        if response_json['temp'] > 10:
            message = "It's warm outside"
        elif 0 < response_json['temp'] < 10:
            message = "It's not cold, but I advise you to put on warm clothes"
        else:
            message = "It's cold. NO. IT'S VERY COLD"

        message2 = ''
        if response_json['wind_speed'] < 5:
            message2 = "Don't worry, wind won't blow you away"
        else:
            message2 = "I think if you go outside, the wind will blow you away. But you will have a chance to travel around Earth"
        result = {
            "requester_name": name,
            "event_start_datetime": start_dt.isoformat(),
            "location": city,
            "date": weather_date,
            "weather": {
                "temp": f"{response_json['temp']} degrees",
                "humidity": f"{response_json['humidity']}",
                "max_temp": f"{response_json['max_temp']} degrees",
                "wind_speed": f"{response_json['wind_speed']} km per hour"
            },
            "message": f"{message}. {message2}"
        }
        return result


