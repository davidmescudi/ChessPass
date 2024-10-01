from machine import Pin, ADC, PWM
from time import ticks_ms, ticks_diff

# Setup pins for LED, PWM, encoder (clk, dt)
led = Pin(10, Pin.OUT)
led.on()  # LED initially on
pwm_pin = Pin(9)
pwm = PWM(pwm_pin, freq=1000)  # Set frequency to 1kHz

clk = Pin(8, Pin.IN, Pin.PULL_UP)
dt = Pin(20, Pin.IN, Pin.PULL_UP)

# Initial duty cycle
duty = 1023  # (0 to 1023)
pwm.duty(0)

# Morse code dictionary
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

# State variables for Morse code transmission
morse_message = "HELLO"
morse_state = {
    'message': "",
    'char_index': 0,
    'symbol_index': 0,
    'is_magnet_on' : False,
    'last_time': ticks_ms(),
    'is_transmitting': False,
    'current_symbols': "",
    'finished': False
}

# Variables for encoder state, LED control, and debouncing
last_clk = clk.value()
led_last_turned_off = None  # To track the last time the LED was turned off
led_off_duration = 200  # Time to keep LED off (in milliseconds)
last_encoder_event_time = 0  # For debouncing
debounce_time = 10  # Minimum time (ms) between encoder events

# Encoder interrupt handler
def encoder_callback(pin):
    global duty, last_clk, led_last_turned_off, last_encoder_event_time

    # Debouncing: ignore events that happen too quickly
    current_time = ticks_ms()
    if ticks_diff(current_time, last_encoder_event_time) < debounce_time:
        return

    current_clk = clk.value()

    if current_clk == 1 and last_clk == 0:
        # Turn LED off briefly and track the time
        led.off()
        led_last_turned_off = ticks_ms()

        # Adjust PWM duty cycle based on encoder direction
        if dt.value() == 0:  # Clockwise rotation
            duty += 50
        else:  # Counter-clockwise rotation
            duty -= 50
            
        # Limit duty cycle between 0 and 1023
        duty = max(0, min(duty, 1023))
        #pwm.duty(duty)
        print("Duty cycle:", duty)

        # Restart Morse code transmission
        start_morse(morse_message)

    # Update the last state and time
    last_clk = current_clk
    last_encoder_event_time = current_time

# Set up an interrupt on the `clk` pin for both rising and falling edges
clk.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=encoder_callback)

# Function to start Morse code transmission
def start_morse(message):
    global morse_state
    morse_state['message'] = message
    morse_state['char_index'] = 0
    morse_state['symbol_index'] = 0
    morse_state['is_magnet_on'] = False
    morse_state['last_time'] = ticks_ms()
    morse_state['is_transmitting'] = True
    morse_state['current_symbols'] = ""
    morse_state['finished'] = False
    print(f"Starting Morse code: {message}")

# Non-blocking Morse code transmission function
def handle_morse_transmission():
    global morse_state, duty

    if not morse_state['is_transmitting']:
        return
    
    current_time = ticks_ms()

    # Time interval (dot = 200ms, dash = 600ms)
    dot_time = 200
    dash_time = 3*dot_time
    symbol_pause_time = dot_time
    letter_pause_time = 3*dot_time
    word_pause_time = 7*dot_time

    # Check if it's time for the next step in Morse code transmission
    if ticks_diff(current_time, morse_state['last_time']) >= 0:
        if morse_state['current_symbols'] == "":
            # New letter to process
            if morse_state['char_index'] < len(morse_state['message']):
                char = morse_state['message'][morse_state['char_index']].upper()
                if char == ' ':
                    # Handle space between words
                    morse_state['last_time'] = current_time + word_pause_time
                    morse_state['char_index'] += 1
                    return
                morse_state['current_symbols'] = morse_code.get(char, "")
                morse_state['symbol_index'] = 0
                print(f"Sending: {char}, Symbols: {morse_state['current_symbols']}")
            else:
                # End of message, insert word pause before repeating
                morse_state['last_time'] = current_time + word_pause_time
                morse_state['char_index'] = 0  # Reset to repeat
                morse_state['finished'] = True
                print("Finished sending, word pause")
                return

        # Turn off the signal after symbol
        if morse_state["is_magnet_on"]:
            morse_state["is_magnet_on"] = False
            pwm.duty(0)
            print("Turn magnet off")
            # Turn off the signal after the complete letter
            if morse_state['symbol_index'] >= len(morse_state['current_symbols']):
                print(f"Current symbols '{morse_state['current_symbols']}' finished. Letter pause")
                morse_state['last_time'] = current_time + letter_pause_time
                morse_state['symbol_index'] = 0
                morse_state['char_index'] += 1
                morse_state['current_symbols'] = ""
                return
            
            # Turn off the signal after dot or dash
            print(f"Symbol finished. Symbol pause")
            morse_state['last_time'] = current_time + symbol_pause_time
            
            return
            
        # Get the current symbol (dot or dash)
        symbol = morse_state['current_symbols'][morse_state['symbol_index']]
        
        if symbol in ['.', '-']:
            print("Turn magnet on")
            print("Send symbol:", symbol)
            morse_state['symbol_index'] += 1
            morse_state['is_magnet_on'] = True
            if symbol == '.':
                pwm.duty(duty)  # Short signal for dot
                morse_state['last_time'] = current_time + dot_time
            elif symbol == '-':
                pwm.duty(duty)  # Longer signal for dash
                morse_state['last_time'] = current_time + dash_time
            return

# Function to handle LED reactivation after brief off time
def handle_led_timeout():
    global led_last_turned_off

    if led_last_turned_off is not None:
        # Check if it's time to turn the LED back on
        if ticks_diff(ticks_ms(), led_last_turned_off) >= led_off_duration:
            led.on()  # Turn LED back on
            led_last_turned_off = None  # Reset the timeout

# Call this in the main loop to handle the Morse code and LED asynchronously
def main_loop():
    while True:
        # Handle the Morse code transmission without blocking
        handle_morse_transmission()

        # Handle the LED timeout
        handle_led_timeout()

# Example: start Morse code for "HELLO"
start_morse(morse_message)
main_loop()  # This will run the main loop

