#include <WiFi.h>
#include <HTTPClient.h>
#include <esp32cam.h>

const char* WIFI_SSID = "PRABHALA HOME-2.4G";
const char* WIFI_PASS = "siva@2000";

// FastAPI endpoint
String SERVER_URL = "http://192.168.1.40:8000/recognize";

// ----- Use LOW RES to avoid reboot -----
static auto lowRes = esp32cam::Resolution::find(320, 240);

void setup() {
  Serial.begin(115200);
  Serial.println("");

  using namespace esp32cam;
  Config cfg;
  cfg.setPins(pins::AiThinker);
  cfg.setResolution(lowRes);  // SAFE!
  cfg.setJpeg(80);
  cfg.setBufferCount(2);

  bool ok = Camera.begin(cfg);
  Serial.println(ok ? "CAMERA OK" : "CAMERA FAIL");
  if (!ok) while (true);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  Serial.print("Connecting");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    delay(2000);
    return;
  }

  auto frame = esp32cam::Camera.capture();
  if (!frame) {
    Serial.println("Capture failed");
    delay(100);
    return;
  }

  Serial.printf("Frame OK: %dx%d (%d bytes)\n",
                frame->getWidth(),
                frame->getHeight(),
                frame->size());

  HTTPClient http;
  http.begin(SERVER_URL);
  http.addHeader("Content-Type", "image/jpeg");

  int response = http.POST(frame->data(), frame->size());

  Serial.print("Server Response: ");
  Serial.println(response);

  http.end();
  delay(300);
}

