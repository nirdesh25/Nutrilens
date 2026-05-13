# NutriLens AI — Smart Freshness Box Hardware Guide

## Components List

### Core Module (Main Box)
| Component | Model | Purpose | Pin |
|---|---|---|---|
| Microcontroller | ESP32 DevKit v1 | WiFi + main controller | — |
| Temperature & Humidity | DHT22 | Food storage conditions | GPIO 4 |
| Gas Sensor | MQ-135 | Spoilage gas detection | GPIO 34 (ADC) |
| Light Sensor | LDR (10kΩ) | Box open/close detection | GPIO 35 (ADC) |
| Status LED | Built-in blue LED | Connection / error feedback | GPIO 2 |
| Power | USB-C 5V / 3.3V regulator | Power supply | — |

### Milk Quality Add-on (Optional)
| Component | Model | Purpose | Pin |
|---|---|---|---|
| pH Probe | Analog pH Sensor Module | Milk acidity measurement | GPIO 32 (ADC) |
| Temperature | DS18B20 (waterproof) | Liquid temperature | GPIO 5 (1-Wire) |
| Turbidity | Turbidity Sensor Module | Cloudiness detection | GPIO 33 (ADC) |

---

## Wiring Diagrams

### DHT22
```
DHT22 Pin 1 (VCC)  → ESP32 3.3V
DHT22 Pin 2 (DATA) → ESP32 GPIO 4 + 10kΩ pull-up to 3.3V
DHT22 Pin 4 (GND)  → ESP32 GND
```

### MQ-135 (Gas Sensor)
```
MQ-135 VCC  → ESP32 5V (VIN)
MQ-135 GND  → ESP32 GND
MQ-135 AOUT → ESP32 GPIO 34   (analog read, 0–3.3V range)
MQ-135 DOUT → (not used)
```
> ⚠️ MQ-135 heater requires 5V. Use VIN if powering via USB, or a separate 5V rail.

### LDR (Light Dependent Resistor)
```
3.3V ─── [LDR 10kΩ] ─── GPIO 35 ─── [10kΩ resistor] ─── GND
```
Forms a voltage divider. More light → higher voltage at GPIO 35.

### pH Sensor (Milk Module)
```
pH Module VCC → ESP32 3.3V (or 5V per module spec)
pH Module GND → ESP32 GND
pH Module PO  → ESP32 GPIO 32  (analog output)
```
> Calibrate using pH 4.0 and pH 7.0 buffer solutions. Adjust `PH_OFFSET` and `PH_SCALE` in the firmware.

### DS18B20 (Waterproof Temperature)
```
DS18B20 Red (VCC)  → ESP32 3.3V
DS18B20 Black (GND) → ESP32 GND
DS18B20 Yellow (DATA) → ESP32 GPIO 5 + 4.7kΩ pull-up to 3.3V
```

---

## Firmware Setup

1. Install **Arduino IDE** and add the **ESP32 board support**:
   - File → Preferences → Additional Boards Manager URLs:
     `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - Tools → Board → Boards Manager → search "esp32" → Install

2. Install these libraries via **Tools → Manage Libraries**:
   - `DHT sensor library` by Adafruit
   - `Adafruit Unified Sensor`
   - `ArduinoJson` by Benoit Blanchon
   - `OneWire` by Paul Stoffregen *(milk module only)*
   - `DallasTemperature` by Miles Burton *(milk module only)*

3. Open `nutrilens_box.ino` in Arduino IDE.

4. Edit the configuration block at the top:
   ```cpp
   const char* WIFI_SSID    = "YourWiFiName";
   const char* WIFI_PASSWORD = "YourWiFiPassword";
   const char* API_BASE_URL = "http://YOUR_SERVER_IP:8000";
   const char* AUTH_TOKEN   = "your-jwt-token";
   ```

5. Select **Board**: `ESP32 Dev Module`  
   Select **Port**: your COM/ttyUSB port  
   Click **Upload**.

6. Open **Serial Monitor** at **115200 baud** to watch live readings.

---

## Getting Your JWT Token

The firmware needs a valid Bearer token to POST to the NutriLens API.

```bash
# Register / login via the API to get a token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "yourpassword"}'

# Copy the "access_token" value from the response into AUTH_TOKEN in the sketch
```

> **Production note:** For long-running devices, implement token refresh logic or create a dedicated device account with a very long expiry. A device-specific API key system is the cleanest long-term solution.

---

## Sensor Calibration

### MQ-135 (Gas)
- Allow the sensor to **warm up for 24–48 hours** before taking accurate readings.
- The `map()` function in the sketch gives a rough 0–1000 PPM range. For precise readings, consult the MQ-135 datasheet and calibrate using known gas concentrations.

### pH Probe
- Use **pH 4.0 and pH 7.0 buffer solutions** (available from lab supply stores).
- Submerge probe, note the ADC voltage output at each known pH, then calculate `PH_OFFSET` and `PH_SCALE` to match.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| DHT22 returns NaN | Check pull-up resistor (10kΩ); ensure correct GPIO |
| Gas sensor always high | Sensor needs 24h burn-in; check 5V supply |
| WiFi won't connect | Verify SSID/password; ESP32 only supports 2.4GHz |
| API returns 401 | Token expired; regenerate JWT from login endpoint |
| pH reading wildly off | Recalibrate; clean probe with distilled water first |
