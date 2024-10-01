from machine import Pin, ADC
from time import ticks_ms, ticks_diff

# Set up the Hall sensor on an ADC pin
hall_sensor = ADC(Pin(27))  # Adjust the pin based on your setup
hall_sensor.atten(ADC.ATTN_11DB)

# Variables for the baseline and variance threshold
sensor_baseline = 0
variance_threshold = 70  # Adjust based on the sensor's natural variance

# Define Morse code timings (same as transmitter)
variance_morse_threshhold = 10
dot_time = 200   # 200ms for dot
dash_time = 3*dot_time  # 600ms for dash
symbol_pause_time = dot_time  # 200ms between symbols
letter_pause_time = 3*dot_time  # 600ms between letters
end_message_pause = 7*dot_time  # Pause longer than 1200ms indicates the end of a message

# Morse code
morse_code = {
    'A': '.-', 
    'B': '-...',
    'C': '-.-.',
    'D': '-..',
    'E': '.',
    'F': '..-.',
    'G': '--.',
    'H': '....',
    'I': '..',
    'J': '.---',
    'K': '-.-',
    'L': '.-..',
    'M': '--',
    'N': '-.',
    'O': '---',
    'P': '.--.',
    'Q': '--.-',
    'R': '.-.',
    'S': '...',
    'T': '-',
    'U': '..-',
    'V': '...-',
    'W': '.--',
    'X': '-..-',
    'Y': '-.--',
    'Z': '--..',
    '1': '.----',
    '2': '..---',
    '3': '...--',
    '4': '....-',
    '5': '.....',
    '6': '-....',
    '7': '--...',
    '8': '---..',
    '9': '----.',
    '0': '-----'
}

# Morse code lookup for decoding
reverse_morse_code = { value: key for key, value in morse_code.items()}

# State variables for receiving Morse code
morse_state = {
    'received_word': "",
    'current_symbols': "",
    'last_signal_time': None,  # Time when the signal (magnet) was last detected
    'last_pause_time': None,   # Time when the signal last went low (pause)
    'is_receiving': False,     # Tracks if we are actively detecting a signal
    'message_received': False, # Stop receiving after the first word
}

# Function to sample the sensor and establish the baseline value
def init_hall_sensor(samples=20):
    global sensor_baseline
    readings = []
    
    for _ in range(samples):
        readings.append(hall_sensor.read())
    
    # Calculate the average baseline
    sensor_baseline = sum(readings) // len(readings)
    print(f"Sensor initialized with baseline: {sensor_baseline}")

# Function to detect the presence of the magnet
def is_magnet_detected():
    current_reading = hall_sensor.read()
    deviation = abs(current_reading - sensor_baseline)
    
    # Return True if deviation exceeds the threshold (magnet detected)
    return deviation > variance_threshold

# Function to handle Morse code reception using the Hall sensor
def handle_morse_reception():
    global morse_state

    #if morse_state['message_received']:
        #return  # Ignore further signals after receiving the first word

    current_time = ticks_ms()
    signal = is_magnet_detected()  # Use the Hall sensor for signal detection

    if signal:  # Magnet detected (dot or dash)
        if not morse_state['is_receiving']:
            # We start receiving only once the signal becomes active
            morse_state['last_signal_time'] = current_time
            morse_state['is_receiving'] = True

        # Continue tracking the duration of the signal (dot/dash)
        signal_duration = ticks_diff(current_time, morse_state['last_signal_time'])
        
        # Do not reset last_signal_time here; we accumulate the time while the signal remains active

    else:  # No magnet detected (pause between symbols or letters)
        if morse_state['is_receiving']:
            # The signal just stopped, so process the duration of the signal
            signal_duration = ticks_diff(current_time, morse_state['last_signal_time'])
            variance = 0
            print("signal_duration: ", signal_duration)
            if signal_duration >= dash_time - variance_morse_threshhold:
                morse_state['current_symbols'] += '-'  # Long signal => dash
                variance = signal_duration - (dash_time - variance_morse_threshhold)
            elif signal_duration >= dot_time - variance_morse_threshhold:
                morse_state['current_symbols'] += '.'  # Short signal => dot
                variance = signal_duration - (dot_time - variance_morse_threshhold)
            
            # Reset receiving state after processing the symbol
            morse_state['is_receiving'] = False
            morse_state['last_pause_time'] = current_time # - variance  # Now we track the pause duration TODO!!

        elif morse_state['last_pause_time']:
            # Calculate the pause duration since the last signal ended
            pause_duration = ticks_diff(current_time, morse_state['last_pause_time'])
            print("pause_duration: ", pause_duration)
            if pause_duration >= symbol_pause_time - variance_morse_threshhold:
                # End of a symbol
                ##!!!!!TODO
                
                if pause_duration >= letter_pause_time - variance_morse_threshhold:
                    # End of a letter, decode the current symbol
                    if morse_state['current_symbols'] in reverse_morse_code:
                        morse_state['received_word'] += reverse_morse_code[morse_state['current_symbols']]
                        print(f"Decoded letter: {reverse_morse_code[morse_state['current_symbols']]}")
                    else:
                        print("Unknown Morse code symbol:", morse_state['current_symbols'])
                    
                    # Reset the current symbol after processing
                    morse_state['current_symbols'] = ""

                    # If the pause is long enough, we assume the word/message is complete
                    if pause_duration >= end_message_pause - variance_morse_threshhold:
                        print(f"End of first word received: {morse_state['received_word']}")
                        morse_state['message_received'] = True
                        return  # Stop further reception

# Main loop for the receiver
def main_loop():
    init_hall_sensor(1000)  # Initialize the sensor baseline
    
    while True:
        # Handle the non-blocking reception of Morse code using the Hall sensor
        handle_morse_reception()

# Start the receiver loop
main_loop()

