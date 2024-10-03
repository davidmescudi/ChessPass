from lib import HallSensor, MorseReceiver
from lib import DISPLAY, DISPLAY_FRAMEBUF
from lib.sslib import shamir
from boot import required_shares, prime_mod
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
    FIGURE_DETECTION_THRESHOLD
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
            shifted_messages.append(shift_hex_string(message, message.position * message.strength, decrypt=True))
        display.showSecret(shifted_messages)

def main_loop():
    hall_sensors = []
    morse_receivers = []
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

    for morse_receiver in morse_receivers:
        morse_receiver.init()
    
    
    messages = []
    while True:
        active_figures = 0
        for morse_receiver in morse_receivers:
            active_figures += morse_receiver.hall_sensor.is_magnet_active_detected()
            message = morse_receiver.execute()
            if message:
                message = message.lower()
                messages.append(message)
                print(messages)
        handle_display(active_figures, messages)


main_loop()
