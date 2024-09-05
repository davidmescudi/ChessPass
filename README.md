# ChessPass
This repository contains two ESP32 projects, each implemented using MicroPython. Each project is stored in a separate subdirectory:

1. **Board**
2. **Figure**

Both components can be found in their corresponding subdirectories in this repository. Simply upload all the contents of a subdirectory to your ESP32.

**Connect the components to the pins specified in the code, or adjust the pin assignments in the code to match your specific setup.**

---

## Project 1: **Board**

### Description
This project is built for an ESP32 with an e-ink display, 3 buttons for menu navigation, and 9 hall sensors. The display shows a list of items that can be navigated using the buttons, while the hall sensors constantly read their values in the background.

### Hardware Components
- [**ESP32** (DEBO JT ESP32)](https://www.reichelt.de/nodemcu-esp32-wifi-und-bluetooth-modul-debo-jt-esp32-p219897.html)
- [**E-ink Display** (Waveshare 2.9inch E-Paper E-Ink Display, 296×128, Red / Black / White, SPI)](https://www.waveshare.com/pico-epaper-2.9-b.htm)
- [**3 simple Buttons**](https://www.amazon.de/Taktilen-Druckschalter-Taktiler-Drucktastenschalter-Tactile/dp/B082ZL867J)
- [**9 linear Hall Sensors** (TRU COMPONENTS Hallsensor AH49EUA)](https://www.conrad.de/de/p/tru-components-hallsensor-ah49eua-4-5-6-v-dc-messbereich-0-0125-0-0205-t-to-92-loeten-1569218.html)

---

## Project 2: **Figure**

### Description
This project is designed to control an electromagnet using PWM signals. A potentiometer is used to adjust the power of the electromagnet in real-time by controlling the duty cycle of the PWM signal.

### Hardware Components
- [**ESP32** (Xiao ESP32S3)](https://www.reichelt.de/xiao-esp32s3-dual-core-wifi-bt5-0-xiao-esp32s3-p358354.html)
- [**Electromagnet** (ARD MAGNET 25N)](https://www.reichelt.de/arduino-elektromagnet-bis-2-5-kg-ard-magnet-25n-p284396.html)
- [**Potentiometer** (STEC12E07)](https://www.reichelt.de/drehimpulsegeber-24-impulse-24-rastungen-vertikal-stec12e07-p73922.html)