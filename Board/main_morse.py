from lib import HallSensor, MorseReceiver
from lib.config import (
    HALL_VARIANCE_THRESHOLD,
    MORSE_VARIANCE,
    ADCS,
    MORSE_CODE,
    DOT_TIME,
    DASH_TIME,
    SYMBOL_PAUSE_TIME,
    LETTER_PAUSE_TIME,
    END_MESSAGE_PAUSE_TIME,
)


def main_loop():

    hall_sensors = []
    morse_receivers = []
    for pin_num in ADCS:
        hall_sensor = HallSensor(
            pin_num,
            hall_variance_threshold=HALL_VARIANCE_THRESHOLD,
            verbose=True,
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
        for morse_receiver in morse_receivers:
            message = morse_receiver.execute()
            if message:
                message = message.lower()
                messages.append(message)
                print(messages)


main_loop()
