# Celestron Origin Satellite Tracker - Quick Reference

## 🚀 Quick Start

```bash
# 1. Configure your location and API keys
vim config.ini

# 2. Add satellite NORAD IDs to track
echo "25544,48274" > norad_ids.txt  # ISS and Tiangong

# 3. Run the tracker
python main_tracker.py
```

## 📡 Key API Calls Used

### Mount Control
```python
# Move telescope to Alt/Az position (RADIANS!)
await ws_client.goto_alt_azm(alt_rad, az_rad)

# Disable sidereal tracking for satellites
await ws_client.send_command("Mount", "EnableTracking", {"Value": False})

# Check mount status
status = await ws_client.get_mount_status()
is_aligned = status.get("IsAligned")
is_goto_complete = status.get("IsGotoOver")
```

### Camera & Imaging
```python
# Set camera parameters
await ws_client.set_camera_parameters(
    exposure_sec=0.5,   # Short for fast satellites
    iso=800,            # Moderate sensitivity
    binning=2,          # 2x2 binning for sensitivity
    bit_depth=16        # 16-bit for dynamic range
)

# Trigger image capture
await ws_client.run_sample_capture(exposure_sec, iso, binning)

# Download captured image
await ws_client.download_image(origin_file_path, local_save_path)
```

## 🌍 Coordinate Conversions

```python
# Skyfield → Celestron Origin
from skyfield.api import Topos, load, EarthSatellite

# Create observer location
observer = Topos(latitude_degrees=34.05, 
                 longitude_degrees=-118.24,
                 elevation_m=71)

# Calculate satellite position
difference = satellite - observer
apparent_pos = difference.at(time)
el, az, _ = apparent_pos.altaz()

# Convert to Celestron format (RADIANS!)
celestron_alt = el.radians
celestron_azm = az.radians
```

## 📂 File Structure

```
celestial-tracker/
├── config.ini              # Configuration (you create it from config.example.ini)
├── norad_ids.txt           # Satellites to track (you create it)
├── main_tracker.py         # Main application
├── n2yo_api.py             # Satellite data fetching
├── sky_utils.py            # Position calculations
├── celestron_ws_client.py  # Telescope control
├── tle_plan.json           # Generated schedule (runtime)
├── trajectory.json         # Calculated paths (runtime)
└── observations/           # Downloaded images (runtime)
    └── SATNAME_NORAD_TIMESTAMP/
        └── TIMESTAMP_<file name from Origin>
```

## ⚙️ Configuration Parameters

```ini
[OBSERVER]
latitude = 34.0522        # Decimal degrees
longitude = -118.2437     # Decimal degrees
altitude_m = 71           # Meters above sea level

[CELESTRON]
origin_ip = origin.local  # Or IP address like 192.168.1.100

[CAMERA]
exposure_seconds = 0.5    # Short for satellites
iso = 800                 # 100-6400 range
binning = 2               # 1, 2, 3, or 4
bit_depth = 16            # 8, 16, or 24
image_cooldown_seconds = 5
```

## 🔧 Common Operations

### Generate New Schedule
```python
plan, trajectories = generate_pass_schedule()
# Automatically saves to tle_plan.json and trajectory.json
```

### Track Single Pass
```python
await track_satellite_pass(ws_client, pass_info, trajectory)
# Handles pre-positioning, tracking, and imaging
```

### System Health Check
```python
await perform_system_health_check(ws_client)
# Displays comprehensive status table
```

## 📊 Key Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| MIN_ELEVATION_DEG | 20° | Minimum satellite elevation |
| COOLDOWN_SECONDS | 120s | Time between passes |
| PRE_POSITION_LEAD_TIME_SECONDS | 45s | Pre-slew buffer |
| N2YO_REQUEST_DELAY_SECONDS | ~3.9s | API rate limiting |
| watchdog_interval | 5s | Connection monitoring |

## 🐛 Troubleshooting

### Connection Issues
```python
# Check WebSocket URI format
ws://origin.local/SmartScope-1.0/mountControlEndpoint

# Verify telescope is on same network
ping origin.local
```

### Tracking Problems
```python
# Verify mount is aligned
status = await ws_client.get_mount_status()
if not status.get("IsAligned"):
    print("Mount needs alignment!")

# Check coordinates are in RADIANS
assert 0 <= alt_rad <= math.pi/2  # 0-90° in radians
assert 0 <= az_rad <= 2*math.pi   # 0-360° in radians
```

### Image Issues
```python
# Verify storage location exists
Path("observations").mkdir(exist_ok=True)

# Check Origin's internal storage
disk_status = await ws_client.get_disk_status()
free_gb = disk_status.get("FreeBytes", 0) / (1024**3)
```

## 📚 Message Formats

These are the shapes `celestron_ws_client.py` sends and reads. Payload fields sit at the top level of each message.

### Command Format (Alt and Azm in radians)
```json
{
    "Source": "WebApp",
    "Destination": "Mount",
    "Command": "GotoAltAzm",
    "Type": "Command",
    "SequenceID": 1234,
    "Alt": 0.785398,
    "Azm": 3.141592
}
```

### Response Format
```json
{
    "Source": "Mount",
    "Command": "GotoAltAzm",
    "Type": "Response",
    "SequenceID": 1234,
    "ErrorCode": 0,
    "ErrorMessage": ""
}
```

### Notification Format
```json
{
    "Source": "ImageServer",
    "Command": "NewImageReady",
    "Type": "Notification",
    "FileLocation": "<path on Origin>",
    "ImageType": "SAMPLE_CAPTURE"
}
```

## 🎯 Performance Tips

1. **Reduce API Calls**: Use dynamic time windows
2. **Batch Operations**: Download images asynchronously
3. **Pre-position Early**: Start slewing 45s before pass
4. **Short Exposures**: 0.5-1s for moving satellites
5. **Higher ISO**: 800-1600 for dim satellites
6. **Binning**: 2x2 improves sensitivity
7. **Skip Low Passes**: Filter < 20° elevation

## 🔗 External Resources

- [Celestron Origin Product Page](https://www.celestron.com/products/celestron-origin)
- [N2YO Satellite Tracker](https://www.n2yo.com)
- [Skyfield Documentation](https://rhodesmill.org/skyfield/)
- [NORAD Catalog Numbers](https://celestrak.com/satcat/search.php)

## 💡 Pro Tips

1. **Test with ISS First**: NORAD 25544, bright and predictable
2. **Check StarSense**: Ensure auto-alignment completed
3. **Monitor Environment**: Watch humidity vs dew point
4. **Use High Elevation**: Better seeing above 40°
5. **Plan for Weather**: Check cloud cover forecasts
6. **Regular Calibration**: Re-align after equipment changes

---
*Quick Reference v1.0 - For detailed information, see SYSTEM_DOCUMENTATION.md*
