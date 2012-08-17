#ifndef BASE_RDDUINO_CLIENT_H
#define BASE_RDDUINO_CLIENT_H

#include <Arduino.h>
#include <Ethernet.h>
#include <sha256.h>
#include "Key.h"

#define KEY_ITERATIONS 128

class BaseRRDuinoClient : public EthernetClient { 
  private:
    String _id;
    Key _key;
    Key _session_key;

    unsigned long _tick_interval;

    int read(byte* buf, uint16_t buf_length, unsigned long timeout_ms = 5000);

  protected:
    // Key-related functions
    Key sessionKey() { return _session_key; };
    void advanceSessionKey();

    // Message-related functions
    void initializeMessage(String const& message_type, boolean requires_hmac = false);
    void addMessageValue(String const& key, float value, boolean requires_hmac = false);
    void addMessageValue(String const& key, int value, boolean requires_hmac = false);
    void addMessageValue(String const& key, String const& value, boolean requires_hmac = false);
    void finalizeMessage(boolean requires_hmac = false);

  public:
    BaseRRDuinoClient(String const& id, String const& key);

    // Getters/Setters
    unsigned long tickInterval(unsigned long tick_interval) { return _tick_interval }; //!< Get wait time between calls to tick()
    void tickInterval(unsigned long tick_interval) { _tick_interval = tick_interval; }; //!< Set wait time between calls to tick()

    // Protocol-related functions
    boolean handshake(); //!< Performs the 'hello' and session key generation handshake

    // Virtual interfaces
    virtual void update() = 0; //!< Send an "update" command
    virtual boolean tick() = 0; //!< Gather information before sending an "update"
};

#endif
