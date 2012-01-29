#include <Arduino.h>
#include <SPI.h>
#include <Ethernet.h>
#include <sha256.h>
#include <EEPROM.h>

#include "config.h"
#include "Thermistor.h"
#include "RDDClient.h"

Key key;
byte mac[6] = CLIENT_MAC;

void setup() {
  Serial.begin(9600);
  
  if (Ethernet.begin(mac) == 0) {
    Serial.println("Failed to configure Ethernet using DHCP");
    for(;;);
  }
  
  stringToKey(CLIENT_KEY, key);
}
  
void loop() {
  
  RRDClient  client(CLIENT_ID, key);
  Thermistor thermistor(A0);
  
  float temperature_C = 0.0f; // temperature reading
  long capture_start  = 0;
  long wait_time      = 0;
  
  // Connect to server
  if (!client.connect(SERVER_IP, SERVER_PORT)) {
    Serial.print("Could not connect to server at ");
    Serial.println(SERVER_IP);
    return;
  }
  
  // Perform initial handshake
  if (!client.handshake()) {
    Serial.println("Handshake failed.");
    return;
  }
  
  // Continually get data
  while(client.connected()) {
    // Tick!
    capture_start = millis();
    
    // Get the temperature
    temperature_C = thermistor.read();
    
    // Send the temperature
    client.update(temperature_C);
    
    // Tock! How long did that take?
    // We'll wait the remainder such that the total elapsed time is CAPTURE_DELAY
    wait_time = CAPTURE_DELAY - (capture_start - millis());

    if (wait_time > 0) {
      delay(wait_time);
    }
  }
}
