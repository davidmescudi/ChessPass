from machine import Pin, Timer
from time import ticks_ms
from lib import HallSensor, MorseReceiver, DISPLAY_FRAMEBUF, Button
from lib.config import (
    DISPLAY_PINS,
    HALL_VARIANCE_THRESHOLD,
    MORSE_VARIANCE,
    ADCS,
    MORSE_CODE,
    DOT_TIME,
    DASH_TIME,
    SYMBOL_PAUSE_TIME,
    LETTER_PAUSE_TIME,
    END_MESSAGE_PAUSE_TIME,
    FIGURE_DETECTION_TIME,
    FIGURE_DETECTION_THRESHOLD,
)

def shift_hex_string(s, shift, decrypt=False):
    if decrypt:
        shift = (-1) * shift
    shifted = ""
    for char in s:
        if char.isdigit():  # Shift digits 0-9
            shifted += chr((ord(char) - ord('0') + shift) % 10 + ord('0'))
        elif char.isalpha():  # Shift letters a-f or A-F (for hex)
            if char.islower():  # Handle lowercase hex letters
                start = ord('a')
                shifted += chr((ord(char) - start + shift) % 16 + start)
            elif char.isupper():  # Handle uppercase hex letters
                start = ord('A')
                shifted += chr((ord(char) - start + shift) % 16 + start)
        else:
            # Leave any other characters unchanged
            shifted += char
    return shifted

display = DISPLAY_FRAMEBUF(DISPLAY_PINS['SPI'], DISPLAY_PINS['CS'], DISPLAY_PINS['DC'], DISPLAY_PINS['BL'] , DISPLAY_PINS['RST'])
# Global variables
required_shares = 2
display = DISPLAY_FRAMEBUF(DISPLAY_PINS['SPI'], DISPLAY_PINS['CS'], DISPLAY_PINS['DC'], DISPLAY_PINS['BL'], DISPLAY_PINS['RST'])
is_secret_shown = False
is_receiving_piece_config_mode = True
right_btn = Pin(3, Pin.IN, Pin.PULL_UP)

def left_button():
    print("Left Button pressed")
    display.showText("Left Button")

def right_button():
    print("Right Button pressedt")
    display.showText("Right Button")

left_btn = Button(pin_num=1, callback=left_button)
right_btn = Button(pin_num=3, callback=right_button)

# Display initial state
display.showText("Receive Morse")


def handle_display(activeFigures, messages):
    if not len(messages) < required_shares:
        if activeFigures > 0:
            display.showActiveFigures(activeFigures, required_shares)
        else:
            display.showLogo()
    else:
        shifted_messages = []
        for message in messages:
            # TODO: aus messages position und magnetstärke erhalten
            shifted_messages.append(shift_hex_string(message, 1, decrypt=True))
        if is_secret_shown:
            return
        display.showSecret(shifted_messages)
        
def get_magnet_configs(hall_sensor):
    pass

def main_loop():
    global is_receiving_piece_config_mode, switch_mode_flag
    hall_sensors = []
    morse_receivers = []
    
    # Initialize hall sensors and Morse receivers
    for pin_num in ADCS:
        hall_sensor = HallSensor(
            pin_num,
            hall_variance_threshold=HALL_VARIANCE_THRESHOLD,
            verbose=True,
            figure_detection_time=FIGURE_DETECTION_TIME,
            figure_detection_threshold=FIGURE_DETECTION_THRESHOLD
        )
        hall_sensors.append(hall_sensor)
        morse_receivers.append(
            MorseReceiver(
                hall_sensor,
                MORSE_CODE,
                MORSE_VARIANCE,
                DOT_TIME,
                DASH_TIME,
                SYMBOL_PAUSE_TIME,
                LETTER_PAUSE_TIME,
                END_MESSAGE_PAUSE_TIME,
                verbose=True,
            )
        )

    # Initialize Morse receivers
    for morse_receiver in morse_receivers:
        morse_receiver.init()
    
    messages = set()

    while True:
        active_figures = 0
        

        if is_receiving_piece_config_mode:
            pass
        else:
            # Process each morse receiver
            for index, morse_receiver in enumerate(morse_receivers):
                message = morse_receiver.execute()
                if message:
                    message = message.lower()
                    messages.add((index, message))
                    print(messages)  # Debugging output
            
            # Update the display
            handle_display(active_figures, messages)

# Uncomment to run the main loop
main_loop()
