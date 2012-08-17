#include <Arduino.h>
#include <SPI.h>
#include <Ethernet.h>
#include <sha256.h>

#include "config.h"
#include "Thermistor.h"
#include "Key.h"
#include "BaseRRDuinoClient.h"
#include "RRDuinoClient.h"

RRDuinoClient client(CLIENT_ID, CLIENT_KEY);
byte mac[6] = CLIENT_MAC;

void setup() {
  Serial.begin(9600);

  while (Ethernet.begin(mac) == 0) {
    Serial.println("FAIL: Ethernet.begin()");
    delay(5000);
  }

  client.tickInterval(CAPTURE_DELAY_MS);
  client.setTimeout(5000);
  
  //
  Serial.print(SERVER_IP);
  Serial.print(':');
  Serial.println(SERVER_PORT);
}
  
void loop() {

  unsigned long last_tick;

  // Connect to server
  if (!client.connect(SERVER_IP, SERVER_PORT)) {
    Serial.println("FAIL: client.connect()");
    delay(5000);
    return;
  }
  
  // Perform initial handshake
  if (!client.handshake()) {
    Serial.println("FAIL: client.handshake()");
    return;
  }
 
  while(client.connected()) {
    // Remember when we are
    last_tick = millis();

    // Tick ..
    if (client.tick()) {
      // .. and send an `update` command if necessary
      client.update();
    }
    
    // Wait the difference, such that the total time between ticks is
    //   as close to client.tickInterval() as possible
    delay(client.tickInterval() - (millis()-last_tick));
  }
  
  client.stop();
  
  Serial.println("Disconnected");
}
