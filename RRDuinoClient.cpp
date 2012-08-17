#include "RRDuinoClient.h"

RRDuinoClient::RRDuinoClient(String const& id, String const& key)
  : RRDuinoClient(id, key),
    _thermistor(A0),
    _temperature_C(0)
{
}

void RRDuinoClient::tick() {
  _temperature_C = _thermistor.read();

  return true;
}

void RRDuinoClient::update() {
  initializeMessage("u", true);
  addMessageValue("temperature", _temperature_C, true);
  finalizeMessage(true);
}
