#ifndef RRDUINO_CLIENT_H
#define RRDUINO_CLIENT_H

#include <Arduino.h>
#include "Thermistor.h"
#include "BaseRRDuinoClient.h"

class RRDuinoClient : public BaseRRDuinoClient { 
  private:
  
    // Here we're specifying our data sources and variables
    Thermistor _thermistor;
    float _temperature_C;

  public:
    RRDuinoClient(String const& id, String const& key);

    // Virtual interfaces
    virtual void update(); //!< Send an "update" command
    virtual boolean tick(); //!< Gather information before sending an "update"
};

#endif
