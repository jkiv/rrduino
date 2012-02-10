#include "Key.h"

void stringToKey(String const& s, Key &k) {
  Sha256.init();
  Sha256.print(s);
  byte* hash_result = Sha256.result();
  for (uint8_t i = 0; i < RRDCLIENT_KEY_SIZE; i++) {
    k.x[i] = hash_result[i];
  }
}

String bytesToHex(const byte* buf, uint16_t length) {
  const char* alphabet = "0123456789abcdef";

  if (length == 0) return "";
  String hexString = "";

  for (uint16_t i = 0; i < length; i++) {
      hexString += alphabet[buf[i]>>4];
      hexString += alphabet[buf[i]&0xf];
  }
  
  return hexString;
}
