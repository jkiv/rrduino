#include "RDDClient.h"

RRDClient::RRDClient(String const& id, Key const& default_key)
{
  // Write the key to memory if it is not the same as default_key
  initializeKey(default_key);
  
  // Load the key from memory into _key
  readKey(_key);
}

void RRDClient::initializeKey(Key const& default_key) {
  boolean key_has_changed = true;
  
  // Is the key in memory different?
  for(int i = 0; i < RRDCLIENT_KEY_SIZE; i++) {
    key_has_changed |= (EEPROM.read(RRDCLIENT_NVRAM_OFFSET + i) != default_key.x[i]);
  }
  
  // If the key in memory has changed, write it to memory
  if (key_has_changed) {
    writeKey(default_key);
  }
}

void RRDClient::writeKey(Key const& key) {
  for(int i = 0; i < RRDCLIENT_KEY_SIZE; i++) {
    // Only write if it has changed
    if (EEPROM.read(RRDCLIENT_NVRAM_OFFSET + i) != key.x[i]) {
      EEPROM.write(RRDCLIENT_NVRAM_OFFSET + i, key.x[i]);
    }
  }
}

void RRDClient::readKey(Key &key) {
  for(int i = 0; i < RRDCLIENT_KEY_SIZE; i++) {
    key.x[i] = EEPROM.read(RRDCLIENT_NVRAM_OFFSET + i);
  }
}

int RRDClient::read(byte* buffer, uint16_t buffer_length, unsigned long timeout_ms) {
  uint16_t bytesRead = 0;
  byte c;
  unsigned long last_time_available = millis();
  
  while(bytesRead < buffer_length) {
    if (available()) {
      last_time_available = millis();
      buffer[bytesRead] = EthernetClient::read();
      bytesRead++;
    }
    else if (!connected()) {
      // Nothing is available and we're not connected
      break;
    }
    else if (millis() - last_time_available > timeout_ms) {
      // Nothing is available, we're connected, but it's been too long
      break;
    }
  }
  
  return bytesRead;
}

boolean RRDClient::handshake() {
  write('h');
  write(' ');
  print(_id);
  write('\n'); // end of message
  
  byte* hmac_result;  
  Key   key_material;
  
  if (read(key_material.x, RRDCLIENT_KEY_SIZE) != RRDCLIENT_KEY_SIZE) {
    return false;
  }
  
  // Do several rounds on the key material
  for(int i = 0; i < 4096; i++) {
    Sha256.initHmac(_key.x, RRDCLIENT_KEY_SIZE);
    
    for (uint8_t j = 0; j < RRDCLIENT_KEY_SIZE; j++) {
      Sha256.write(key_material.x[j]);
    }
    hmac_result = Sha256.resultHmac();
    
    for (uint8_t j = 0; j < RRDCLIENT_KEY_SIZE; j++) {
      key_material.x[j] = hmac_result[j];
    }
  }
  
  // Our session key is now the mangled key material (sorry cryptographers)
  for (uint8_t i = 0; i < RRDCLIENT_KEY_SIZE; i++) {
    _key.x[i] = key_material.x[i];
  }
  
  return true;
}

boolean RRDClient::update(float temperature) {
  // HMAC
  Sha256.initHmac(_key.x, RRDCLIENT_KEY_SIZE);
  Sha256.print("temperature ");
  Sha256.print(temperature);
  
  String hmac = bytesToHex(Sha256.resultHmac(), RRDCLIENT_KEY_SIZE);
  
  // Send to server
  write('u');
  write(' ');
  
  // .. temperature
  print("temperature ");
  print(temperature);
  
  // .. hmac
  write(' ');
  print(hmac);
  write('\n'); // end of message
  
  return true;
}

void RRDClient::advanceSessionKey() {
    // Hash the session key to advance it to the next key
    //  - we do this after each send
    //  - the server does this after each successful received message
    
    byte* hmac_result; 
    
    Sha256.initHmac(_key.x, RRDCLIENT_KEY_SIZE);
    
    for (uint8_t i = 0; i < RRDCLIENT_KEY_SIZE; i++) {
      Sha256.write(_key.x[i]);
    }
    
    hmac_result = Sha256.resultHmac();
    
    for (uint8_t i = 0; i < RRDCLIENT_KEY_SIZE; i++) {
      _key.x[i] = hmac_result[i];
    }
}

void stringToKey(String const& s, Key &k) {
  Sha256.init();
  Sha256.print(s);
  byte* hash_result = Sha256.result();
  for (uint8_t i = 0; i < RRDCLIENT_KEY_SIZE; i++) {
    k.x[i] = hash_result[i];
  }
}

String bytesToHex(const byte* buf, uint8_t length) {
  const char* alphabet = "0123456789abcdef";

  if (length == 0) return "";
  String hexString = "";

  for (int i = 0; i < length; i++) {
      hexString += alphabet[buf[i]>>4];
      hexString += alphabet[buf[i]&0xf];
  }
  
  return hexString;
}
