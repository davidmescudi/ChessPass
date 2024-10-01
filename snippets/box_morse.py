from machine import Pin, ADC
from time import ticks_ms, ticks_diff
from config import (
    HALL_VARIANCE_THRESHOLD,
    MORSE_VARIANCE,
    MORSE_CODE,
    DASH_TIME,
    DOT_TIME,
    LETTER_PAUSE_TIME,
    END_MESSAGE_PAUSE_TIME,
)

VERBOSE = True

def log(*values):
    if VERBOSE:
        print(*values)

# Set up the Hall sensor on an ADC pin
hall_sensor = ADC(Pin(27))  # Adjust the pin based on your setup
hall_sensor.atten(ADC.ATTN_11DB)

# Variables for the baseline and variance threshold
sensor_baseline = 0

# Morse code lookup for decoding
reverse_morse_code = {value: key for key, value in MORSE_CODE.items()}

# State variables for receiving Morse code
morse_state = {
    "received_word": "",
    "current_symbols": "",
    "last_signal_time": None,  # Time when the signal (magnet) was last detected
    "last_pause_time": None,  # Time when the signal last went low (pause)
    "is_receiving": False,  # Tracks if we are actively detecting a signal
    "is_saving": False,  # Start receiving only after the word pause
    "message_received": False,  # Stop receiving after the first word
}


# Function to sample the sensor and establish the baseline value
def init_hall_sensor(samples=20):
    global sensor_baseline
    readings = []

    for _ in range(samples):
        readings.append(hall_sensor.read())

    # Calculate the average baseline
    sensor_baseline = sum(readings) // len(readings)
    log(f"Sensor initialized with baseline: {sensor_baseline}")


# Function to detect the presence of the magnet
def is_magnet_detected(hall_sensor=hall_sensor):
    current_reading = hall_sensor.read()
    deviation = abs(current_reading - sensor_baseline)

    # Return True if deviation exceeds the threshold (magnet detected)
    return deviation > HALL_VARIANCE_THRESHOLD


def check_message_end():
    global morse_state

    current_time = ticks_ms()
    signal = is_magnet_detected()

    if signal:
        # Magnet on and on field
        if not morse_state["is_receiving"]:
            # Save time when magnet started
            morse_state["last_signal_time"] = current_time
            morse_state["is_receiving"] = True

        signal_duration = ticks_diff(current_time, morse_state["last_signal_time"])

    else:
        if morse_state["is_receiving"]:

            signal_duration = ticks_diff(current_time, morse_state["last_signal_time"])

            morse_state["is_receiving"] = False
            # if magnet was on for enough time (dot or dash time)
            if signal_duration >= (
                DOT_TIME - MORSE_VARIANCE
            ) or signal_duration >= (DASH_TIME - MORSE_VARIANCE):
                morse_state["last_pause_time"] = current_time
            else:
                morse_state["last_pause_time"] = None

        elif morse_state["last_pause_time"]:
            # manget was on for dot or dash time
            # now we wait for the pause
            pause_duration = ticks_diff(current_time, morse_state["last_pause_time"])

            if pause_duration >= END_MESSAGE_PAUSE_TIME - MORSE_VARIANCE:
                morse_state["last_pause_time"] = None
                morse_state["is_saving"] = True
                log(morse_state)
                log("--- Start saving ---")


# Function to handle Morse code reception using the Hall sensor
def handle_morse_reception():
    global morse_state

    # if morse_state['message_received']:
    # return  # Ignore further signals after receiving the first word

    current_time = ticks_ms()
    signal = is_magnet_detected()  # Use the Hall sensor for signal detection

    if signal:  # Magnet detected (dot or dash)
        if not morse_state["is_receiving"]:
            # We start receiving only once the signal becomes active
            morse_state["last_signal_time"] = current_time
            morse_state["is_receiving"] = True

        # Continue tracking the duration of the signal (dot/dash)
        signal_duration = ticks_diff(current_time, morse_state["last_signal_time"])

        # Do not reset last_signal_time here; we accumulate the time while the signal remains active

    else:  # No magnet detected (pause between symbols or letters or words)
        if morse_state["is_receiving"]:
            # The signal just stopped, so process the duration of the signal
            signal_duration = ticks_diff(current_time, morse_state["last_signal_time"])
            deviation = 0
            log("signal_duration: ", signal_duration)
            if signal_duration >= DASH_TIME - MORSE_VARIANCE:
                morse_state["current_symbols"] += "-"  # Long signal => dash
                deviation = signal_duration - (DASH_TIME - MORSE_VARIANCE)
            elif signal_duration >= DOT_TIME - MORSE_VARIANCE:
                morse_state["current_symbols"] += "."  # Short signal => dot
                deviation = signal_duration - (DOT_TIME - MORSE_VARIANCE)

            # Reset receiving state after processing the symbol
            morse_state["is_receiving"] = False
            log("deviation:", deviation)
            morse_state["last_pause_time"] = (
                current_time - deviation
            )  # Now we track the pause duration TODO!!

        elif morse_state["last_pause_time"]:
            # Calculate the pause duration since the last signal ended
            pause_duration = ticks_diff(current_time, morse_state["last_pause_time"])
            # no need to check for symbol pause since we check for magnet on
            if (
                pause_duration >= LETTER_PAUSE_TIME - MORSE_VARIANCE
                and morse_state["current_symbols"]
            ):
                # End of a letter, decode the current symbol
                if morse_state["current_symbols"] in reverse_morse_code:
                    morse_state["received_word"] += reverse_morse_code[
                        morse_state["current_symbols"]
                    ]
                    log(
                        f"Decoded letter: {reverse_morse_code[morse_state['current_symbols']]}"
                    )
                else:
                    log("Unknown Morse code symbol:", morse_state["current_symbols"])

                # Reset the current symbol after processing
                morse_state["current_symbols"] = ""

            # If the pause is long enough, we assume the word/message is complete
            if pause_duration >= END_MESSAGE_PAUSE_TIME - MORSE_VARIANCE:
                morse_state["last_pause_time"] = None

                if morse_state["is_saving"]:
                    log(f"End of first word received: {morse_state['received_word']}")
                    morse_state["message_received"] = True
                    morse_state["is_saving"] = True
                    message = morse_state["received_word"]
                    morse_state["received_word"] = ""
                    return message


# Main loop for the receiver
def main_loop():
    init_hall_sensor(1000)  # Initialize the sensor baseline

    messages = []
    while True:
        if morse_state["is_saving"]:
            # Handle the non-blocking reception of Morse code using the Hall sensor
            message = handle_morse_reception()
            if message:
                messages.append(message)
                log(messages)
        else:
            check_message_end()


# Start the receiver loop
main_loop()
