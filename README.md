# 🛰️ Celestial Tracker - Autonomous Satellite Tracking for Celestron Origin

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Celestron Origin](https://img.shields.io/badge/Celestron-Origin-red.svg)](https://www.celestron.com/products/celestron-origin)

An advanced autonomous satellite tracking system designed specifically for the **Celestron Origin Intelligent Home Observatory**. Track and image satellites automatically through the telescope's WebSocket API.

## ✨ Features

- 🚀 **Autonomous Satellite Tracking** - Automatically tracks satellites across the sky
- 📸 **Automated Imaging** - Captures images during satellite passes
- 🌙 **Smart Scheduling** - Optimized for single-night observation windows
- 🔭 **Origin API Integration** - Controls the mount and camera through the Celestron Origin WebSocket API
- 📊 **Real-time Dashboard** - Web-based monitoring and control interface
- 🌐 **Multi-Satellite Support** - Track ISS, Starlink, and any NORAD-cataloged satellite
- ⚡ **Lean API Use** - Requests pass data only for the upcoming observing window
- 🔄 **Auto-Recovery** - Robust error handling with automatic reconnection

## 🎯 Key Capabilities

### Telescope Control
- Alt/Az positioning from Skyfield-computed trajectories
- Pre-positioning 45 seconds before pass start
- 1Hz position updates during tracking
- Automatic sidereal tracking disable for satellites

### Imaging System
- Configurable exposure, ISO, binning and bit depth (set in `config.ini`)
- Captures triggered at a configurable cooldown during each pass

### Data Management
- Organized observation storage by satellite and timestamp
- Automatic image download from telescope
- JSON-based schedule persistence
- Comprehensive logging with Rich formatting

## 📋 Prerequisites

### Hardware
- **Celestron Origin Intelligent Home Observatory** (6" RASA telescope)
- Network connection to telescope (WiFi or Ethernet)
- Computer running Python 3.10+

### Software
- Python 3.10 or higher
- N2YO API key (free from [n2yo.com](https://www.n2yo.com/api/))

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/ctrevinoi1/celestial-tracker.git
cd celestial-tracker
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Settings
```bash
# Copy sample configuration
cp config.example.ini config.ini

# Edit with your settings
nano config.ini
```

Update these key settings:
- `latitude`, `longitude`, `altitude_m` - Your observation location
- `api_key` - Your N2YO API key
- `origin_ip` - Your telescope's IP address or hostname
- `[WEATHERAPI] api_key` - Optional WeatherAPI.com key for the dashboard weather panel (or set the `WEATHERAPI_KEY` environment variable instead)

### 4. Add Satellites to Track
```bash
# Copy sample NORAD IDs
cp norad_ids.txt.sample norad_ids.txt

# Or create your own list
echo "25544,20580" > norad_ids.txt  # ISS and Hubble
```

### 5. Run the Tracker
```bash
python main_tracker.py
```

## 📁 Project Structure

```
celestial-tracker/
├── main_tracker.py           # Main application entry point
├── celestron_ws_client.py    # WebSocket client for telescope control
├── n2yo_api.py               # Satellite pass prediction API
├── sky_utils.py              # Astronomical calculations
├── logger_setup.py           # Rich logging setup
├── dashboard_server.py       # Web dashboard (optional)
├── run_dashboard.py          # Dashboard launcher
├── config.example.ini        # Configuration template
├── norad_ids.txt.sample      # Sample NORAD ID list
├── requirements.txt          # Python dependencies
├── setup.py                  # Package metadata
├── CONTRIBUTING.md
├── LICENSE
├── docs/                     # Documentation
│   ├── SYSTEM_DOCUMENTATION.md
│   ├── QUICK_REFERENCE.md
│   ├── VALIDATION_SUMMARY.md
│   ├── IMPROVEMENTS_AND_GAPS.md
│   └── README_DOCUMENTATION.md
├── templates/                # Web dashboard templates
└── static/                   # Dashboard CSS and JavaScript
```

The tracker creates `observations/` at runtime for downloaded images.

## 🔧 Configuration

### Basic Configuration (`config.ini`)

```ini
[OBSERVER]
latitude = 34.0522        # Decimal degrees
longitude = -118.2437     # Decimal degrees  
altitude_m = 71          # Meters above sea level

[N2YO]
api_key = YOUR_N2YO_API_KEY_HERE  # From n2yo.com/api

[WEATHERAPI]
api_key = YOUR_WEATHERAPI_KEY_HERE  # Optional, from weatherapi.com

[CELESTRON]
origin_ip = origin.local # Or IP like 192.168.1.100

[CAMERA]
exposure_seconds = 0.5   # Short for fast satellites
iso = 800               # Moderate sensitivity
binning = 2             # 2x2 for better sensitivity
```

## 📊 Web Dashboard (Optional)

Launch the monitoring dashboard:

```bash
# Optional: enables the weather panel
export WEATHERAPI_KEY=YOUR_WEATHERAPI_KEY_HERE

python dashboard_server.py
```

Access at `http://localhost:8000` to view:
- Real-time tracking status
- Upcoming satellite passes
- System health metrics
- Live connection status

## 🛰️ Supported Satellites

Track any satellite with a NORAD catalog number:

| Satellite | NORAD ID | Brightness | Speed |
|-----------|----------|------------|-------|
| ISS | 25544 | Very Bright | Medium |
| Hubble | 20580 | Moderate | Slow |
| Starlink | Various | Bright | Fast |
| Tiangong | 48274 | Bright | Medium |

Find more at [celestrak.com](https://celestrak.com/satcat/search.php)

## 📈 Performance

- **API Pacing**: N2YO requests spaced to stay under 950 calls/hour
- **Position Updates**: 1 Hz during tracking

## 🔬 Technical Details

### Coordinate System
- Uses Skyfield for precise astronomical calculations
- Converts topocentric Alt/Az to radians for mount control
- J2000 epoch for RA/Dec coordinates
- WGS84 for observer location

### API Integration
- WebSocket connection on port 80
- JSON command, response and notification messages
- Automatic reconnection with exponential backoff
- Error handling and logging

## 📚 Documentation

Comprehensive documentation is available:

- [System Documentation](docs/SYSTEM_DOCUMENTATION.md) - Full technical details
- [Quick Reference](docs/QUICK_REFERENCE.md) - Common operations
- [Validation Summary](docs/VALIDATION_SUMMARY.md) - Code review summary
- [Improvements Roadmap](docs/IMPROVEMENTS_AND_GAPS.md) - Future enhancements

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🐛 Troubleshooting

### Common Issues

**Connection Failed**
- Verify telescope is on same network
- Check firewall settings
- Try IP address instead of hostname

**No Satellites Scheduled**
- Verify location settings are correct
- Check N2YO API key is valid
- Ensure observation time window is appropriate

**Tracking Errors**
- Confirm mount is aligned (StarSense)
- Check coordinates are in correct format
- Verify telescope has clear view of sky

See [Quick Reference](docs/QUICK_REFERENCE.md#-troubleshooting) for more solutions.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Celestron](https://www.celestron.com) for the Origin telescope and API
- [N2YO.com](https://www.n2yo.com) for satellite tracking data
- [Skyfield](https://rhodesmill.org/skyfield/) for astronomical calculations
- [Rich](https://github.com/Textualize/rich) for beautiful terminal output

## 📞 Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/ctrevinoi1/celestial-tracker/issues)
- 💬 [Discussions](https://github.com/ctrevinoi1/celestial-tracker/discussions)

## ⚠️ Disclaimer

This is an independent personal project and is not an official Celestron product. Celestron Origin is a trademark of Celestron, LLC.

---

<p align="center">
  Made with ❤️ for the astronomy community
  <br>
  🌟 Star this repository if you find it useful! 🌟
</p>
