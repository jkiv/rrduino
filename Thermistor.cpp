#include "Thermistor.h"

Thermistor::Thermistor(int pin)
  : _pin(pin)
{
  analogReference(EXTERNAL); // Connect VREF to 3.3V for less noise
}

float Thermistor::read() {
  // Based on ladyada's thermistor tutorial:
  //   http://www.ladyada.net/learn/sensors/thermistor.html

  int samples[THERMISTOR_SAMPLE_COUNT];
  float temperature = 0.0f;
  
  // Average THERMISTOR_SAMPLE_COUNT samples
  for (uint8_t i = 0; i < THERMISTOR_SAMPLE_COUNT; i++) {
    temperature += analogRead(_pin);
    delay(THERMISTOR_SAMPLE_DELAY);
  }
  
  temperature /= THERMISTOR_SAMPLE_COUNT;
  
  // convert the reading to resistance
  temperature = 1023 / temperature - 1;
  temperature = THERMISTOR_R_SERIES / temperature;
  
  // Convert reading to temperature
  temperature = temperature / THERMISTOR_R_NOMINAL;     // (R/Ro)
  temperature = log(temperature);                       // ln(R/Ro)
  temperature /= THERMISTOR_BETA;                       // 1/B * ln(R/Ro)
  temperature += 1.0 / (THERMISTOR_T_NOMINAL + 273.15); // + (1/To)
  temperature = 1.0 / temperature;                      // Invert
  temperature -= 273.15;                                // convert to degrees Celcius
  
  return temperature;
}
