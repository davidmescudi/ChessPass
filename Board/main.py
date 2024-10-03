from machine import Pin
import time
from lib import HallSensor, MorseReceiver, DISPLAY_FRAMEBUF, Button
from boot import required_shares, prime_mod
# https://github.com/jqueiroz/python-sslib
from lib.sslib import shamir
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
            shifted += chr((ord(char) - ord("0") + shift) % 10 + ord("0"))
        elif char.isalpha():  # Shift letters a-f or A-F (for hex)
            if char.islower():  # Handle lowercase hex letters
                start = ord("a")
                shifted += chr((ord(char) - start + shift) % 16 + start)
            elif char.isupper():  # Handle uppercase hex letters
                start = ord("A")
                shifted += chr((ord(char) - start + shift) % 16 + start)
        else:
            # Leave any other characters unchanged
            shifted += char
    return shifted


# Global variables
display = DISPLAY_FRAMEBUF(
    DISPLAY_PINS["SPI"],
    DISPLAY_PINS["CS"],
    DISPLAY_PINS["DC"],
    DISPLAY_PINS["BL"],
    DISPLAY_PINS["RST"],
)
is_secret_shown = False
is_receiving_piece_config_mode = True
counter = 0
debounce_time = 300
last_pressed_time = 0
enough_messages = False

left_btn = Pin(22, Pin.IN, Pin.PULL_UP)
right_btn = Pin(23, Pin.IN, Pin.PULL_UP)

def transform_magnet_strength(strength):
    if strength < 2700:
        return 3
    elif 2700 < strength < 2780:
        return 2
    elif strength > 2780:
        return 1

def handle_messages(messages):
    indexes = set([idx for idx,_,_ in messages])
    new_messages = []
    for index in indexes:
        new_message = [message for message in messages if message[0] == index]
        new_messages.append(new_message)
    return new_messages
        
possible_positions = [1,4,5,7,8,9,10,11,13]

def decrypt_secret(shares):
    return {
        "required_shares" : required_shares,
        "prime_mod" : prime_mod,
        "shares" : shares
    }

def handle_secret_display(messages):
    shifted_messages = []
    for idx, msg, str_magnet in messages:
        shifted_messages.append(shift_hex_string(msg, transform_magnet_strength(str_magnet) * possible_positions[idx], decrypt=True))
    if is_secret_shown:
        return
    result = shamir.recover_secret(shamir.from_hex(decrypt_secret(shifted_messages))).decode('ascii')
    display.showSecret(result)

def main_loop():
    global is_receiving_piece_config_mode, last_pressed_time, debounce_time, enough_messages
    hall_sensors = []
    morse_receivers = []

    # Initialize hall sensors and Morse receivers
    for pin_num in ADCS:
        hall_sensor = HallSensor(
            pin_num,
            hall_variance_threshold=HALL_VARIANCE_THRESHOLD,
            verbose=True,
            figure_detection_time=FIGURE_DETECTION_TIME,
            figure_detection_threshold=FIGURE_DETECTION_THRESHOLD,
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

    messages = []
    while True:
        active_figures = 0
        if (right_btn.value() is 0) and (time.ticks_ms() - last_pressed_time) > debounce_time:
            print("right button pressed")
            last_pressed_time = time.ticks_ms()
            if is_receiving_piece_config_mode:
                is_receiving_piece_config_mode = False
                enough_messages = False
                display.showThreeLinesOfText("Put pieces", "in blink", "mode")
                time.sleep(5)
                
        if (left_btn.value() is 0) and (time.ticks_ms() - last_pressed_time) > debounce_time:
            print("left button pressed")
            last_pressed_time = time.ticks_ms()
            if not is_receiving_piece_config_mode:
                [hall_sensor.reset_magnet_strength() for hall_sensor in hall_sensors]
                is_receiving_piece_config_mode = True
                

        if is_receiving_piece_config_mode:
            for morse_receiver in morse_receivers:
                morse_receiver.hall_sensor.measure_magnet_strength()
                morse_receiver.hall_sensor.is_magnet_detected()
                active_figures += morse_receiver.hall_sensor.is_magnet_active_detected()
            display.showActiveFigures(int(active_figures), required_shares)
        elif not enough_messages:
            # Process each morse receiver
            for index, morse_receiver in enumerate(morse_receivers):
                result = morse_receiver.execute()
                if result:
                    message, magnet_strength = result
                    message = message.lower()
                    messages.append((index, message, magnet_strength))
                    print(messages)  # Debugging output
                    if len(messages) >= required_shares * 3:
                        enough_messages = True
                        split_by_index = handle_messages(messages)
                        secret_shares = []
                        for sub_arrays in split_by_index:
                            longest_tuple = max(sub_arrays, key=lambda x: len(x[1]))
                            secret_shares.append(longest_tuple)
                        handle_secret_display(secret_shares)

                        


# Uncomment to run the main loop
main_loop()
