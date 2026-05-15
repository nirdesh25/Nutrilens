/*
 * ============================================================
 * NutriLens AI — Milk Quality Sensor Firmware (ESP32)
 * Optional add-on module for the Smart Freshness Box
 * ============================================================
 * 
 * HARDWARE CONNECTIONS:
 *   pH Sensor (analog)  → GPIO 32 (ADC1_CH4)
 *   DS18B20 (1-Wire)    → GPIO 5
 *   Turbidity Sensor    → GPIO 33 (ADC1_CH5 — analog)
 *
 * ADDITIONAL LIBRARIES:
 *   - OneWire by Paul Stoffregen
 *   - DallasTemperature by Miles Burton
 * ============================================================
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// ──────────────────────────────────────────────
// CONFIGURATION
// ──────────────────────────────────────────────
const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* API_BASE_URL  = "http://10.232.19.235:8000";
const char* AUTH_TOKEN    = "YOUR_BEARER_TOKEN_HERE";

const unsigned long SEND_INTERVAL_MS = 60000;  // Every 60 seconds

// ──────────────────────────────────────────────
// PIN DEFINITIONS
// ──────────────────────────────────────────────
#define PH_PIN          32
#define DS18B20_PIN      5
#define TURBIDITY_PIN   33
#define STATUS_LED_PIN   2

// ──────────────────────────────────────────────
// GLOBALS
// ──────────────────────────────────────────────
OneWire oneWire(DS18B20_PIN);
DallasTemperature tempSensor(&oneWire);
unsigned long lastSendTime = 0;

const float ADC_MAX = 4095.0;

// ──────────────────────────────────────────────
// pH calibration (adjust for your pH probe)
// A typical pH sensor outputs 0–3V for pH 0–14
// These constants need calibration per sensor.
// ──────────────────────────────────────────────
const float PH_OFFSET = 0.0;   // Fine-tune after calibration
const float PH_SCALE  = 3.5;   // Scale factor (voltage → pH)

// ──────────────────────────────────────────────
// SETUP
// ──────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n=== NutriLens Milk Quality Sensor ===");

  pinMode(STATUS_LED_PIN, OUTPUT);
  tempSensor.begin();

  connectWiFi();
}

// ──────────────────────────────────────────────
// MAIN LOOP
// ──────────────────────────────────────────────
void loop() {
  if (WiFi.status() != WL_CONNECTED) connectWiFi();

  if (millis() - lastSendTime >= SEND_INTERVAL_MS) {
    lastSendTime = millis();
    readAndSendMilkData();
  }
}

// ──────────────────────────────────────────────
// Sensor reading
// ──────────────────────────────────────────────
void readAndSendMilkData() {
  // --- pH ---
  int phRaw      = analogRead(PH_PIN);
  float phVoltage = (phRaw / ADC_MAX) * 3.3;
  float phValue   = (phVoltage * PH_SCALE) + PH_OFFSET;
  phValue = constrain(phValue, 0.0, 14.0);

  // --- Temperature (DS18B20 — more accurate than DHT for liquid sensing) ---
  tempSensor.requestTemperatures();
  float temperature = tempSensor.getTempCByIndex(0);

  // --- Turbidity ---
  int turbRaw   = analogRead(TURBIDITY_PIN);
  float turbPct = (turbRaw / ADC_MAX) * 100.0;
  // Turbidity > 60% is cloudy (1), ≤ 60% is clear (0)
  int turbidity = (turbPct > 60.0) ? 1 : 0;

  // --- Heuristic flags (binary for Milk Quality model) ---
  // These require physical inspection; set to 1 (good) as default.
  // A future vision module could detect taste/odor proxies.
  int taste = 1;   // 1 = normal
  int odor  = 1;   // 1 = normal
  int fat   = 1;   // 1 = high fat
  int color = 255; // 255 = White (Calibrated for Milk Quality dataset)

  Serial.println("\n─── [NutriLens] Sending Data ───");
  Serial.printf("  pH: %.2f | Temp: %.1f C | Turb: %d | Color: %d\n", phValue, temperature, turbidity, color);

  // Build JSON
  StaticJsonDocument<256> doc;
  doc["ph"]          = round(phValue * 100) / 100.0;
  doc["temperature"] = round(temperature * 10) / 10.0;
  doc["taste"]       = taste;
  doc["odor"]        = odor;
  doc["fat"]         = fat;
  doc["turbidity"]   = turbidity;
  doc["color"]       = color;

  String payload;
  serializeJson(doc, payload);

  String endpoint = String(API_BASE_URL) + "/api/sensor/milk-quality";
  sendToAPI(endpoint, payload);
}

// ──────────────────────────────────────────────
// HTTP POST helper
// ──────────────────────────────────────────────
void sendToAPI(const String& url, const String& payload) {
  HTTPClient http;
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("Authorization", String("Bearer ") + AUTH_TOKEN);
  http.setTimeout(10000);

  int httpCode = http.POST(payload);
  if (httpCode > 0) {
    String response = http.getString();
    Serial.printf("📡 %d → %s\n", httpCode, response.c_str());
  } else {
    Serial.printf("❌ HTTP error: %s\n", http.errorToString(httpCode).c_str());
  }
  http.end();
}

// ──────────────────────────────────────────────
void connectWiFi() {
  Serial.printf("Connecting to %s", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("\n✅ IP: %s\n", WiFi.localIP().toString().c_str());
  } else {
    Serial.println("\n❌ WiFi failed.");
  }
}
