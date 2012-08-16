#include "BaseRRDuinoClient.h"

BaseRRDuinoClient::BaseRRDuinoClient(String const& id, String const& key)
  : _id(id)
{
  stringToKey(key, _key);
}

/** Reads at most 'buffer_length' bytes into 'buffer'. Reading will stop
 * after 'timeout_ms' milliseconds of no data being available to read.
 * @returns number of bytes read into 'buffer'
 */
int BaseRRDuinoClient::read(byte* buffer, uint16_t buffer_length, unsigned long timeout_ms) {
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

/** Advances the session key. This is done by hashing the
 * session key with the master key (sorry cryptographers).
 */
void BaseRRDuinoClient::advanceSessionKey() {
  // Hash the session key to advance it to the next key
  
  byte* hmac_result; 
  
  Sha256.initHmac(_key.x, RRDUINO_CLIENT_KEY_SIZE);
  
  // Write the key to the digest
  for (uint8_t i = 0; i < RRDUINO_CLIENT_KEY_SIZE; i++) {
    Sha256.write(_session_key.x[i]);
  }
  
  // Copy digest result back to the key
  hmac_result = Sha256.resultHmac();

  for (uint8_t i = 0; i < RRDUINO_CLIENT_KEY_SIZE; i++) {
    _session_key.x[i] = hmac_result[i];
  }
}


// Protocol ///////////////////////////////////////////////////////////////////

/** Performs the handshake. Here, the client identifies itself
 * and the server provides the session key material. The session
 * key is derived from this key material by hashing it with the
 * master key a large number of times (sorry cryptographers).
 * 
 * @returns whether or not the handshake was successful
 */
boolean BaseRRDuinoClient::handshake() {
  // Send 'hello'
  print("h ");
  print(_id);
  finalizeMessage(false);
  
  byte* hmac_result;  
  Key   key_material;
  
  // Get the key material in response
  if (read(key_material.x, RRDUINO_CLIENT_KEY_SIZE) != RRDUINO_CLIENT_KEY_SIZE) {
    return false;
  }
  
  // Do several rounds on the key material to generate session key (sorry cryptographers)
  // TODO we can simplify this by adding a `key' parameter to advanceSessionKey() and using
  //      it in the following loop (instead of repeating ourselves...)
  Sha256.initHmac(_key.x, RRDUINO_CLIENT_KEY_SIZE);

  for(int i = 0; i < KEY_ITERATIONS; i++) {
    
    // Write the key material for digest
    for (uint8_t j = 0; j < RRDUINO_CLIENT_KEY_SIZE; j++) {
      Sha256.write(key_material.x[j]);
    }
    
    // Copy digest back into key material for another round
    hmac_result = Sha256.resultHmac();

    for (uint8_t j = 0; j < RRDUINO_CLIENT_KEY_SIZE; j++) {
      key_material.x[j] = hmac_result[j];
    }
  }
  
  // Our session key is now the mangled key material (sorry cryptographers)
  for (uint8_t i = 0; i < RRDUINO_CLIENT_KEY_SIZE; i++) {
    _session_key.x[i] = key_material.x[i];
  }
  
  return true;
}

//!< Initializes message of 'message_type'.
void BaseRRDuinoClient::initializeMessage(String const& message_type, boolean requires_hmac) {
  print(message_type);

  if (requires_hmac) {
    Sha256.initHmac(_session_key.x, RRDUINO_CLIENT_KEY_SIZE);
    Sha256.print(message_type);
  }
}

void BaseRRDuinoClient::addUpdateField(String const& key, float value, boolean requires_hmac) {
  write(' ');
  print(key);
  write(' ');
  print(value);

  if (requires_hmac) {
    Sha256.initHmac(_session_key.x, RRDUINO_CLIENT_KEY_SIZE);
    Sha256.write(' ');
    Sha256.print(key);
    Sha256.write(' ');
    Sha256.print(value);
  }
}

void BaseRRDuinoClient::addUpdateField(String const& key, int value, boolean requires_hmac) {
  write(' ');
  print(key);
  write(' ');
  print(value);

  if (requires_hmac) {
    Sha256.initHmac(_session_key.x, RRDUINO_CLIENT_KEY_SIZE);
    Sha256.write(' ');
    Sha256.print(key);
    Sha256.write(' ');
    Sha256.print(value);
  }
}

void BaseRRDuinoClient::addUpdateField(String const& key, String const& value, boolean requires_hmac) {
  write(' ');
  print(key);
  write(' ');
  print(value);

  if (requires_hmac) {
    Sha256.initHmac(_session_key.x, RRDUINO_CLIENT_KEY_SIZE);
    Sha256.write(' ');
    Sha256.print(key);
    Sha256.write(' ');
    Sha256.print(value);
  }
} 

/** Finalizes the message. If 'requires_hmac' is true, then the HMAC
 * result is sent. When the HMAC is sent, the session key is advanced
 * such that it is one value ahead of the server. Finally, regardless of
 * the value of 'requires_hmac', a newline (the end-of-message delimeter)
 * is sent.
 * 
 * Note: using HMAC assumes Sha256 has already been initialized and fed
 *       with the data. We simply call resultHmac() here.
 */
void BaseRRDuinoClient::finalizeMessage(boolean requires_hmac) {
  if (requires_hmac) {
    String hmac = bytesToHex(Sha256.resultHmac(), RRDUINO_CLIENT_KEY_SIZE);

    // Send the HMAC portion of the message: ' HMAC'
    write(' ');
    print(hmac);

    // Advance the session key
    advanceSessionKey();
  }

  // Finish the message off with a delimiter
  write('\n');
}
