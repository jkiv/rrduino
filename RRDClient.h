#ifndef RDDCLIENT_H
#define RDDCLIENT_H

#include <Arduino.h>
#include <Ethernet.h>
#include <sha256.h>
#include <EEPROM.h>


#define RRDCLIENT_NVRAM_OFFSET 0
#define RRDCLIENT_KEY_SIZE 32

typedef struct Key { byte x[RRDCLIENT_KEY_SIZE]; } Key;

class RRDClient : public EthernetClient { 
  private:
    String _id;
    Key _key;
    Key _session_key;
    
    void initializeKey(Key const& default_key);
    void writeKey(Key const& key);
    void readKey(Key &key);
    void advanceSessionKey();
    
  public:
    RRDClient(String const& id, Key const& default_key);
    boolean handshake();
    boolean update(float temperature);

    int read(byte* buf, uint16_t buf_length, unsigned long timeout_ms = 5000);
};

void stringToKey(String const& s, Key &k); //!< helper to convert a string to a key
String bytesToHex(const byte* bytes, uint16_t length); //!< helper to convert blob of data to hex

#endif
