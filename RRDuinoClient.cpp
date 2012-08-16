#include "RRDuinoClient.h"

RRDuinoClient::RRDuinoClient(String const& id, String const& key)
  : BaseRRDuinoClient(id, key),
    _thermistor(A0),
    _temperature_C(0)
{
}

boolean RRDuinoClient::tick() {
  _temperature_C = _thermistor.read();

  return true;
}

void RRDuinoClient::update() {
  initializeMessage("u", true);
  addUpdateField("temperature", _temperature_C, true);
  finalizeMessage(true);
}
