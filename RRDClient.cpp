#include "RRDClient.h"

RRDClient::RRDClient(String const& id, String const& key)
  : _id(id)
{
  stringToKey(key, _key);
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

void RRDClient::finalizeMessage(boolean requires_hmac) {
    if (requires_hmac) {
      String hmac = bytesToHex(Sha256.resultHmac(), RRDCLIENT_KEY_SIZE);

      // Finish off message with the HMAC
      write(' ');
      print(hmac);

      // Advance the session key
      advanceSessionKey();
    }

    // Finish the message off with a delimiter
    write('\n');
}

void RRDClient::advanceSessionKey() {
    // Hash the session key to advance it to the next key
    
    byte* hmac_result; 
    
    Sha256.initHmac(_session_key.x, RRDCLIENT_KEY_SIZE);
    
    // Write the key to the digest
    for (uint8_t i = 0; i < RRDCLIENT_KEY_SIZE; i++) {
      Sha256.write(_session_key.x[i]);
    }
    
    // Copy digest result back to the key
    hmac_result = Sha256.resultHmac();

    for (uint8_t i = 0; i < RRDCLIENT_KEY_SIZE; i++) {
      _session_key.x[i] = hmac_result[i];
    }
}


// Protocol ///////////////////////////////////////////////////////////////////

boolean RRDClient::handshake() {
  // Send 'hello'
  print("h ");
  print(_id);
  finalizeMessage(false);
  
  byte* hmac_result;  
  Key   key_material;
  
  // Get the key material in response
  if (read(key_material.x, RRDCLIENT_KEY_SIZE) != RRDCLIENT_KEY_SIZE) {
    return false;
  }
  
  // Do several rounds on the key material to generate session key (sorry cryptographers)
  for(int i = 0; i < 128; i++) {
    Sha256.initHmac(_key.x, RRDCLIENT_KEY_SIZE);
    
    // Write the key material for digest
    for (uint8_t j = 0; j < RRDCLIENT_KEY_SIZE; j++) {
      Sha256.write(key_material.x[j]);
    }
    
    // Copy digest back into key material for another round
    hmac_result = Sha256.resultHmac();

    for (uint8_t j = 0; j < RRDCLIENT_KEY_SIZE; j++) {
      key_material.x[j] = hmac_result[j];
    }
  }
  
  // Our session key is now the mangled key material (sorry cryptographers)
  for (uint8_t i = 0; i < RRDCLIENT_KEY_SIZE; i++) {
    _session_key.x[i] = key_material.x[i];
  }
  
  return true;
}

boolean RRDClient::update(float temperature) {
  // Write to digest
  Sha256.initHmac(_session_key.x, RRDCLIENT_KEY_SIZE);
  Sha256.print("u temperature ");
  Sha256.print(temperature);

  // Send message 
  print("u temperature ");
  print(temperature);

  // Send footer
  finalizeMessage(true);
  
  return true;
}
