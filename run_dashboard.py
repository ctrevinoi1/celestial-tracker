#!/usr/bin/env python3
# Run dashboard server
import os
import uvicorn
from dashboard_server import app

if __name__ == "__main__":
    print("Starting Celestron Satellite Tracker Dashboard")
    print("Dashboard will be available at http://localhost:8000")
    print("Press Ctrl+C to stop")
    
    # Weather data needs a WeatherAPI.com key: export WEATHERAPI_KEY in your shell,
    # or set api_key under [WEATHERAPI] in config.ini. Do not hardcode it here.
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 