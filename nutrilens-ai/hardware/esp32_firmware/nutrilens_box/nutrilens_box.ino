/**
 * ============================================================
 * NutriLens AI — Smart Freshness Box Firmware
 * ESP32 with DHT22 (Temp/Humidity), MQ-135 (Gas), LDR (Light)
 * ============================================================
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

// ──────────────────────────────────────────────
// CONFIGURATION
// ──────────────────────────────────────────────
const char* WIFI_SSID     = "ENQUISTIC 0496";
const char* WIFI_PASSWORD = "a04P#750";
const char* API_BASE_URL  = "http://192.168.137.1:8000";
const char* DEVICE_ID     = "ESP32_BOX_001";

const unsigned long SEND_INTERVAL_MS = 5000; // 30 seconds
// ──────────────────────────────────────────────
// PIN DEFINITIONS
// ──────────────────────────────────────────────
#define DHT_PIN    4
#define DHT_TYPE   DHT22
#define MQ135_PIN  34
#define LDR_PIN    35

// ──────────────────────────────────────────────
// GLOBALS
// ──────────────────────────────────────────────
DHT dht(DHT_PIN, DHT_TYPE);
unsigned long lastSendTime = 0;
const float ADC_MAX = 4095.0;

// ──────────────────────────────────────────────
// SETUP
// ──────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n=== NutriLens Smart Freshness Box ===");
  dht.begin();
  connectWiFi();
}

// ──────────────────────────────────────────────
// MAIN LOOP
// ──────────────────────────────────────────────
void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi lost — reconnecting...");
    connectWiFi();
  }

  unsigned long now = millis();
  if (now - lastSendTime >= SEND_INTERVAL_MS) {
    lastSendTime = now;
    readAndSendSensorData();
  }
}

// ──────────────────────────────────────────────
// WiFi
// ──────────────────────────────────────────────
void connectWiFi() {
  // Don't try to reconnect if already connecting
  if (WiFi.status() == WL_CONNECTED) {
    return;
  }

  // Disconnect first to ensure clean state
  WiFi.disconnect(true);
  delay(1000);

  Serial.printf("Connecting to WiFi: %s", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;

    // Check for connection failure
    if (WiFi.status() == WL_CONNECT_FAILED) {
      Serial.println("\n❌ WiFi connection failed - wrong password or network not found");
      return;
    }
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("\n✅ Connected! IP: %s\n", WiFi.localIP().toString().c_str());
  } else {
    Serial.printf("\n❌ WiFi failed after %d attempts. Status: %d\n", attempts, WiFi.status());
  }
}

// ──────────────────────────────────────────────
// Sensor reading & API submission
// ──────────────────────────────────────────────
void readAndSendSensorData() {
  float temperature = dht.readTemperature();
  float humidity    = dht.readHumidity();

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("⚠️  DHT22 read failed — skipping.");
    return;
  }

  int   mq135Raw  = analogRead(MQ135_PIN);
  float gasLevel  = map(mq135Raw, 0, 4095, 0, 1000);

  int   ldrRaw    = analogRead(LDR_PIN);
  float lightLevel = (ldrRaw / ADC_MAX) * 100.0;

  Serial.println("\n─── Sensor Readings ───");
  Serial.printf("  Temperature : %.1f °C\n",  temperature);
  Serial.printf("  Humidity    : %.1f %%\n",  humidity);
  Serial.printf("  Gas Level   : %.1f PPM (raw: %d)\n", gasLevel, mq135Raw);
  Serial.printf("  Light Level : %.1f %%\n",  lightLevel);

  StaticJsonDocument<256> doc;
  doc["device_id"]   = DEVICE_ID;
  doc["temperature"] = round(temperature * 10) / 10.0;
  doc["humidity"]    = round(humidity    * 10) / 10.0;
  doc["gas_level"]   = round(gasLevel    * 10) / 10.0;
  doc["light_level"] = round(lightLevel  * 10) / 10.0;

  String payload;
  serializeJson(doc, payload);

  String endpoint = String(API_BASE_URL) + "/api/sensor/ingest-public";
  sendToAPI(endpoint, payload);
}

// ──────────────────────────────────────────────
// HTTP POST
// ──────────────────────────────────────────────
void sendToAPI(const String& url, const String& payload) {
  HTTPClient http;
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(10000);

  Serial.printf("\n📡 POST → %s\n", url.c_str());

  int httpCode = http.POST(payload);

  if (httpCode > 0) {
    String response = http.getString();
    if (httpCode == 200 || httpCode == 201) {
      Serial.printf("✅ Success %d: %s\n", httpCode, response.c_str());
    } else {
      Serial.printf("⚠️  Error %d: %s\n", httpCode, response.c_str());
    }
  } else {
    Serial.printf("❌ Connection failed: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();
}
