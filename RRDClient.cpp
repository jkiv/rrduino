#include "RRDClient.h"

RRDClient::RRDClient(String const& id, String const& key)
  : _id(id)
{
  stringToKey(key, _key);
}

/** Reads at most 'buffer_length' bytes into 'buffer'. Reading will stop
 * after 'timeout_ms' milliseconds of no data being available to read.
 * @returns number of bytes read into 'buffer'
 */
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

/** Finalizes the message. If 'requires_hmac' is true, then the HMAC
 * result is sent. When the HMAC is sent, the session key is advanced
 * such that it is one value ahead of the server. Finally, regardless of
 * the value of 'requires_hmac', a newline (the end-of-message delimeter)
 * is sent.
 * 
 * Note: using HMAC assumes Sha256 has already been initialized and fed
 *       with the data. We simply call resultHmac() here.
 */
void RRDClient::finalizeMessage(boolean requires_hmac) {
    if (requires_hmac) {
      String hmac = bytesToHex(Sha256.resultHmac(), RRDCLIENT_KEY_SIZE);

      // Send the HMAC portion of the message: ' HMAC'
      write(' ');
      print(hmac);

      // Advance the session key
      advanceSessionKey();
    }

    // Finish the message off with a delimiter
    write('\n');
}

/** Advances the session key. This is done by hashing the
 * session key with itself (sorry cryptographers).
 */
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

/** Performs the handshake. Here, the client identifies itself
 * and the server provides the session key material. The session
 * key is derived from this key material by hashing it with the
 * master key a large number of times (sorry cryptographers).
 * 
 * @returns whether or not the handshake was successful
 */
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
  // TODO we can simplify this by adding a `key' parameter to advanceSessionKey() and using
  //      it in the following loop (instead of repeating ourselves...)
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

/** Sends an update command
 * TODO: this should be defined in a subclass for the particular
 *       function (or at least take arbitrary key/value pairs)
 * 
 * @returns whether or not the update command was successful.
 */
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
  
  // TODO: server verification
  
  return true;
}
