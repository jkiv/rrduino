#ifndef THERMISTOR_H
#define THERMISTOR_H

#include <Arduino.h>

#define THERMISTOR_SAMPLE_COUNT 10
#define THERMISTOR_SAMPLE_DELAY 10
#define THERMISTOR_R_SERIES     10000 
#define THERMISTOR_T_NOMINAL    25
#define THERMISTOR_R_NOMINAL    10000
#define THERMISTOR_BETA         3950

class Thermistor
{
  private:
    int _pin;
    
  public:
    Thermistor(int pin);
    float read();
};

#endif
