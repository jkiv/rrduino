#include "RRDuinoClient.h"

RRDuinoClient::RRDuinoClient(String const& id, String const& key)
  : BaseRRDuinoClient(id, key),
    _thermistor(A0),
    _temperature_C(0)
{
  // Use the constructor to initialize your data sources...
}

boolean RRDuinoClient::tick() {
  // When tick() is called, we update our data.
  _temperature_C = _thermistor.read();

  // Returning true causes an update() call to be made; returning false does not.
  return true;
}

void RRDuinoClient::update() {
  // Start the update message by initializing it.
  initializeMessage("u", true);
  
  // Add different fields to your update command.
  addUpdateField("temperature", _temperature_C, true);
  
  // Finalize the message.
  finalizeMessage(true);
}
