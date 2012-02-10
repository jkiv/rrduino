#ifndef RDDCLIENT_H
#define RDDCLIENT_H

#include <Arduino.h>
#include <Ethernet.h>
#include <sha256.h>
#include "Key.h"


class RRDClient : public EthernetClient { 
  private:
    String _id;
    Key _key;
    Key _session_key;

    int read(byte* buf, uint16_t buf_length, unsigned long timeout_ms = 5000);

  protected:
    void advanceSessionKey();
    void finalizeMessage(boolean requires_hmac = false);
    
  public:
    RRDClient(String const& id, String const& key);
    boolean handshake(); //!< Performs the 'hello' and session key generation handshake
    boolean update(float temperature); //!< Send an "update" command
};

#endif
