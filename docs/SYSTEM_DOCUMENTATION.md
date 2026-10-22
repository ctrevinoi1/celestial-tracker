# Celestron Origin Satellite Tracking System Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Hardware Specifications](#hardware-specifications)
3. [API Alignment](#api-alignment)
4. [System Architecture](#system-architecture)
5. [Operational Workflow](#operational-workflow)
6. [Key Components](#key-components)
7. [Data Management](#data-management)
8. [Performance Optimizations](#performance-optimizations)
9. [Future Enhancements](#future-enhancements)

## System Overview

This satellite tracking system is designed specifically for the **Celestron Origin Intelligent Home Observatory**, enabling autonomous tracking and imaging of satellites during their visible passes. The system integrates with the N2YO satellite tracking API for orbital predictions and the Celestron Origin WebSocket API for telescope control.

### Core Capabilities
- **Autonomous satellite tracking** using real-time orbital calculations
- **Automated imaging** during satellite passes
- **Intelligent scheduling** optimized for single-night observation windows
- **Local and remote image storage** with organized directory structure

## Hardware Specifications

### Celestron Origin Telescope
- **Optical Design**: 6-inch Rowe-Ackermann Schmidt Astrograph (RASA)
- **Focal Ratio**: f/2.2 (optimized for fast imaging)
- **Camera**: 6.4-megapixel color CMOS sensor
- **Mount Type**: Motorized Alt-Azimuth mount
- **Alignment Technology**: StarSense autonomous alignment
- **Processing**: Onboard AI for real-time image stacking and enhancement
- **Control Interface**: WebSocket API over WiFi
- **Storage**: Internal storage with network transfer capabilities

## API Alignment

### Celestron Origin WebSocket API Integration

The tracker uses these Celestron Origin WebSocket API commands:

#### 1. **Mount Control (Mount.GotoAltAzm)**
```python
async def goto_alt_azm(self, alt_rad: float, az_rad: float):
    payload = {"Alt": alt_rad, "Azm": az_rad}
    return await self.send_command("Mount", "GotoAltAzm", payload)
```
Alt and Azm are sent in radians.

#### 2. **Tracking Control (Mount.EnableTracking)**
```python
# Disables sidereal tracking for satellite operations
tracking_off_resp = await ws_client.send_command(
    "Mount", "EnableTracking", {"Value": False}
)
```
Sidereal tracking is turned off because satellites move faster than stars.

#### 3. **Camera Control (Camera.SetCaptureParameters)**
```python
payload = {
    "Exposure": exposure_sec,
    "ISO": iso,
    "Binning": binning,
    "BitDepth": bit_depth
}
```
Values come from the `[CAMERA]` section of `config.ini`.

#### 4. **Image Capture (TaskController.RunSampleCapture)**
```python
payload = {
    "ExposureTime": exposure_sec,
    "ISO": iso,
    "Binning": binning
}
```

#### 5. **System Health Monitoring**
The startup health check calls endpoints including:
- `System.GetVersion` - Firmware version checking
- `Mount.GetStatus` - Mount position and tracking status
- `Camera.GetCameraInfo` - Camera capabilities
- `Environment.GetStatus` - Temperature and humidity monitoring
- `Disk.GetStatus` - Storage availability
- `OrientationSensor.GetStatus` - OTA angle monitoring

## System Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Main Application                         │
│                    (main_tracker.py)                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   N2YO API   │  │  Sky Utils   │  │   WebSocket  │      │
│  │  Integration │  │  (Skyfield)  │  │    Client    │      │
│  │ (n2yo_api.py)│  │(sky_utils.py)│  │(celestron_ws │      │
│  └──────────────┘  └──────────────┘  │  _client.py) │      │
│                                       └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                 ┌────────────────────────┐
                 │   Celestron Origin     │
                 │   Telescope (Hardware) │
                 └────────────────────────┘
```

### Key Modules

1. **main_tracker.py**
   - Orchestrates the entire tracking operation
   - Manages schedule generation and execution
   - Handles pre-positioning and tracking logic

2. **n2yo_api.py**
   - Interfaces with N2YO.com for satellite pass predictions
   - Fetches TLE (Two-Line Element) data
   - Retrieves visual pass information

3. **sky_utils.py**
   - Calculates precise satellite positions using Skyfield
   - Converts between coordinate systems
   - Filters passes by elevation constraints

4. **celestron_ws_client.py**
   - WebSocket communication with Celestron Origin
   - Command execution and response handling
   - Notification queue management
   - Connection health monitoring

## Operational Workflow

### 1. Initialization Phase
```python
# System startup sequence
1. Load configuration from config.ini
2. Establish WebSocket connection to Origin telescope
3. Perform comprehensive system health check
4. Report mount alignment status in the health table
5. Disable sidereal tracking for satellite operations
```

### 2. Schedule Generation (Optimized)
```python
# Dynamic time window calculation
now = datetime.now(timezone.utc)
target_5_am = now.replace(hour=5, minute=0, second=0, microsecond=0)
if now.hour >= 5:
    target_5_am += timedelta(days=1)

# Calculate precise API query window
duration_to_target_5_am = target_5_am - now
days_to_query = max(1, ceil(duration_to_target_5_am.total_seconds() / 86400))
```
**Optimization**: Only fetches passes for the upcoming observation window (until 05:00 UTC), reducing API calls and processing time.

### 3. Pass Tracking Execution
```python
# For each scheduled pass:
1. Pre-position telescope 45 seconds before pass start
2. Wait for exact pass start time
3. Track satellite with 1-second position updates
4. Capture images at configured intervals
5. Process notifications for image completion
6. Download and store captured images
```

### 4. Coordinate Transformation
```python
# Skyfield calculates topocentric position
apparent_pos = (satellite - observer_location).at(time)
el, az, _ = apparent_pos.altaz()

# Direct conversion to Celestron API format
trajectory_point = {
    "timestamp": int(current_time.timestamp()),
    "azimuth_deg": az.degrees,
    "elevation_deg": el.degrees,
    "az_rad_celestron": az.radians,  # API expects radians
    "el_rad_celestron": el.radians,  # API expects radians
    "ra_hours": ra.hours,
    "dec_deg_sky": dec.degrees
}
```

## Key Components

### Configuration Management
```ini
[OBSERVER]
latitude = 34.0522
longitude = -118.2437
altitude_m = 71

[CELESTRON]
origin_ip = origin.local
norad_file_path = norad_ids.txt
tle_plan_file = tle_plan.json
trajectory_file = trajectory.json

[CAMERA]
exposure_seconds = 0.5
iso = 800
binning = 2
bit_depth = 16
image_cooldown_seconds = 5
```

### Pass Filtering Logic
- **Minimum Elevation**: 20° above horizon (configurable)
- **Time Constraints**: Only passes within observation window
- **Cooldown Period**: 2-minute minimum between passes
- **Overlap Prevention**: Refined trajectory timing prevents conflicts

## Data Management

### Image Storage Structure
```
observations/
├── ISS_25544_20240315_183045/
│   ├── 20240315_183045_<file name from Origin>
│   ├── 20240315_183045_<file name from Origin>
│   └── ...
├── STARLINK-1234_45678_20240315_190230/
│   └── ...
```

### Storage Locations
1. **Local Storage**: Images downloaded to `observations/` directory
2. **Origin Storage**: Raw captures stored on telescope's internal storage
3. **Metadata**: Pass details and trajectories saved as JSON files

### Image Download Process
```python
# Asynchronous image download
async def download_image(self, file_location_on_origin: str, save_path: str):
    # Downloads over HTTP from the Origin host in the WebSocket URI
    # Saves to local filesystem with organized naming
```

## Performance Optimizations

### 1. **Dynamic Time Window** ✅ Implemented
- Decreases schedule generation time
- Lowers memory usage for trajectory data

### 2. **Parallel Processing**
- Asynchronous WebSocket communication
- Concurrent image downloads
- Non-blocking notification handling

### 3. **Resource Management**
- API rate limiting (950 requests/hour max)
- Automatic reconnection with exponential backoff

### 4. **Pre-positioning Strategy**
- 45-second lead time for mount positioning
- Reduces tracking lag at pass start
- Improves capture of fast-moving satellites

## Future Enhancements

### Recommended Improvements

1. **Advanced Tracking Algorithms**
   - Implement predictive tracking for smoother motion
   - Add interpolation between 1-second position updates
   - Consider mount acceleration/deceleration profiles

2. **Image Processing Pipeline**
   - Integrate with Origin's AI stacking capabilities
   - Add automatic satellite detection in images
   - Implement streak detection and measurement

3. **Enhanced Scheduling**
   - Priority-based pass selection
   - Weather integration for cloud detection
   - Collision detection for overlapping passes

4. **Real-time Monitoring**
   - Web dashboard for tracking status
   - Live image preview during captures
   - Performance metrics and statistics

5. **Multi-telescope Support**
   - Coordinate multiple Origin telescopes
   - Distributed tracking of different satellites
   - Synchronized observations

## Validation and Testing

### What the Code Does

- **WebSocket Connection**: Automatic reconnection with backoff
- **Coordinate System**: Radians for mount control
- **Time Synchronization**: UTC timestamps throughout
- **Image Storage**: Downloads into one folder per pass
- **Pass Scheduling**: Elevation filtering and a cooldown between passes
- **Mount Control**: Alt/Az updates at 1 Hz during a pass
- **Camera Operation**: Exposure and capture settings from `config.ini`
- **Error Handling**: Logged failures and reconnection

### Testing Recommendations

1. **Unit Tests**
   - Coordinate transformation accuracy
   - TLE parsing validation
   - Schedule generation logic

2. **Integration Tests**
   - End-to-end pass tracking simulation
   - API response handling
   - Image download verification

3. **Field Tests**
   - ISS pass tracking (bright, predictable)
   - Starlink satellite tracking (dimmer, faster)
   - Multiple pass scheduling

## Conclusion

This tracker drives the Celestron Origin's alt-azimuth mount and camera over the WebSocket API, sending coordinates in radians, with health monitoring, reconnection and pass scheduling around those calls. It has no automated test suite yet.
