# ChessPass

This repository contains two ESP32 projects, both implemented using MicroPython. Each project is stored in a separate subdirectory:

1. **Board**
2. **Figure**

Both components can be found in their corresponding subdirectories in this repository. Simply upload all the contents of a subdirectory to your ESP32.

## Directory Structure

- **`Board/`** – Contains the MicroPython implementation for the board component.
- **`Figure/`** – Contains the MicroPython implementation for the figure component.
- **`schematics/`** – Includes schematic drawings for the project.
- **`pinout/`** – Contains pinout diagrams for the components used.
- **`snippets/`** – A collection of test scripts and prototype experiments used during development.
- **`sslib/`** – A [shared library](https://github.com/jqueiroz/python-sslib) that appears in two locations:
  - At the top level, used by `generate_shares.py`.
  - Inside the **Board** directory, where modifications were made for MicroPython compatibility due to unsupported functions in the original library.

### Usage Notes

- **Wiring:** Ensure that all components are connected to the correct pins as specified in the code. If needed, adjust the pin assignments in the scripts to match your specific setup.
- **Testing:** The `snippets/` directory contains small test scripts used for initial component testing before full project assembly. Some files, often named `test`, were specifically used to validate prototype functionality.

### Disclaimer

Some of the code inside the `snippets/` directory may have been sourced from external sources, and we may not always have retained the original references. While most sources are credited in comments, we cannot guarantee complete attribution.  

If you recognize any code that requires proper attribution, please let us know so we can credit the original authors accordingly.

---

Feel free to contribute or open an issue if you encounter any problems!
## Prototype Manual

### Prerequisites

- Ensure the batteries inside the figures are sufficiently charged, or connect a USB-C cable to the back of each figure for power delivery/charging.
- To modify the secret, the number of distributed shares, the number of required shares, or adjust the electromagnet strength and field for each chess piece, use the included `/generate_shares.py` script. This script will replace the `boot.py` file inside the `/Board/` directory and generate multiple `bootX.py` files in the `/Figure/` directory, depending on the number of distributed shares selected. After running the script, upload the newly generated `boot.py` files to the microcontrollers, ensuring you replace the existing `boot.py` files and rename the `bootX.py` files to `boot.py` on the corresponding chess piece.

### Running the Prototype

1. **Powering the Chessboard:** Connect the chessboard to a power source using the provided USB-A to Micro-USB cable. Plug it into a wall outlet or power bank.
   
2. **Turning on the Chess Pieces:** The chess pieces will turn on automatically when the batteries are sufficiently charged and the head is turned in the right direction. When a figure is running, the integrated LED will either:
   - Be off (indicating the electromagnet is off).
   - Light up (the LED brightness corresponds to the electromagnet's strength. For demonstration purposes, the chess pieces currently have three distinct levels of electromagnet strength).
   - Blink (this signals that the head has been turned to its maximum limit. In this state, the chess piece will continuously transmit the secret using Morse code through the electromagnet).

3. **Placing the Chess Pieces:** Place the required number of chess pieces (`n out of m`) on their corresponding squares on the chessboard. The display on the box will prompt you to only set the strength of the magnet and place the chess pieces on the field. At this point, the LED should be on and **not blinking**. Please leave the figures for at least ten seconds in this state on the chess board.

4. **Transmitting Secret Shares:** When all chess pieces are placed on the board:
   1. Press the right button on the chessboard to start the transmission phase.
   2. On each chess piece, turn the head until the LED starts blinking.

5. **Displaying the Secret:** If the correct pieces are positioned on the appropriate squares, the display will show the decrypted secret. Depending on the length of the secret, this process may take some amount of time.

**If the the configuration was wrong or an error happend, follow the instructions on the display. In case you missed the instruction on the display, simply press the left button to restart.**

---

## Project 1: **Board**

### Description
This project is built for an ESP32 with an Nokia 5110 display, 3 buttons for menu navigation, and 9 hall sensors. The display shows a list of items that can be navigated using the buttons, while the hall sensors constantly read their values in the background.

### Hardware Components
- [**ESP32** (DEBO JT ESP32)](https://www.reichelt.de/nodemcu-esp32-wifi-und-bluetooth-modul-debo-jt-esp32-p219897.html)
- [**Nokia 5110**](https://naltronic.de/displays/lcd/613/84x48-lcd-display-pcd8544-modul-fuer-nokia-5110-display-arduino-raspberry-pi)
- [**3 simple Buttons**](https://www.amazon.de/Taktilen-Druckschalter-Taktiler-Drucktastenschalter-Tactile/dp/B082ZL867J)
- [**9 linear Hall Sensors** (TRU COMPONENTS Hallsensor AH49EUA)](https://www.conrad.de/de/p/tru-components-hallsensor-ah49eua-4-5-6-v-dc-messbereich-0-0125-0-0205-t-to-92-loeten-1569218.html)

---

## Project 2: **Figure**

### Description
This project is designed to control an electromagnet using PWM signals. A potentiometer is used to adjust the power of the electromagnet in real-time by controlling the duty cycle of the PWM signal.

### Hardware Components
- [**ESP32** (Xiao ESP32S3 or C3)](https://www.reichelt.de/xiao-esp32s3-dual-core-wifi-bt5-0-xiao-esp32s3-p358354.html)
- [**Electromagnet** (ARD MAGNET 25N)](https://www.reichelt.de/arduino-elektromagnet-bis-2-5-kg-ard-magnet-25n-p284396.html)
- [**Rotary encoder** (STEC12E07)](https://www.reichelt.de/drehimpulsegeber-24-impulse-24-rastungen-vertikal-stec12e07-p73922.html)