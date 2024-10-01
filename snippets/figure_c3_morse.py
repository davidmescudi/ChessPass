from machine import Pin, ADC, PWM
from time import ticks_ms, ticks_diff
from config import (
    PINS_C3,
    LED_PIN,
    LED_OFF_DURATION,
    MAGNET_FREQ,
    INIT_DUTY,
    ROT_DEBOUNCE_TIME,
    MORSE_CODE,
    DASH_TIME,
    DOT_TIME,
    SYMBOL_PAUSE_TIME,
    LETTER_PAUSE_TIME,
    END_MESSAGE_PAUSE_TIME,
)

VERBOSE = True

# Setup pins for LED, PWM, encoder (clk, dt)
led = PWM(Pin(PINS_C3["LED"], Pin.OUT))
pwm_pin = Pin(PINS_C3["MAGNET"])
magnet = PWM(pwm_pin, freq=1000)  # Set frequency to 1kHz

clk = Pin(PINS_C3["CLK"], Pin.IN, Pin.PULL_UP)
dt = Pin(PINS_C3["DT"], Pin.IN, Pin.PULL_UP)

# Initial duty cycle
duty = INIT_DUTY  # (0 to 1023)
magnet.duty(0)

# State variables for Morse code transmission
morse_message = "HELLO"
morse_state = {
    "message": "",
    "char_index": 0,
    "symbol_index": 0,
    "is_magnet_on": False,
    "last_time": ticks_ms(),
    "is_transmitting": False,
    "current_symbols": "",
    "finished": False,
}

# Variables for encoder state, LED control, and debouncing
last_clk = clk.value()
led_off_duration = LED_OFF_DURATION  # Time to keep LED off (in milliseconds)
last_encoder_event_time = 0  # For debouncing
debounce_time = ROT_DEBOUNCE_TIME  # Minimum time (ms) between encoder events
encoder_level = 0
encoder_max_level_time = None
led_blink_last_time = None

def log(*values):
    if VERBOSE:
        print(*values)
    
# Encoder interrupt handler
def encoder_callback(pin):
    global duty, last_clk, last_encoder_event_time, encoder_level, encoder_max_level_time

    # Debouncing: ignore events that happen too quickly
    current_time = ticks_ms()
    if ticks_diff(current_time, last_encoder_event_time) < debounce_time:
        return

    current_clk = clk.value()

    if current_clk == 1 and last_clk == 0:
        # Adjust PWM duty cycle based on encoder direction
        if dt.value() == 0:  # Clockwise rotation
            duty += 50
            encoder_level = min (4, encoder_level + 1)
        else:  # Counter-clockwise rotation
            duty -= 50
            encoder_level = max(0, encoder_level - 1)

        # Limit duty cycle between 0 and 1023
        duty = max(0, min(duty, 1023))
        # pwm.duty(duty)
        log("Duty cycle:", duty)
        log("Encoder Level:", encoder_level)
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
    morse_state["message"] = message
    morse_state["char_index"] = 0
    morse_state["symbol_index"] = 0
    morse_state["is_magnet_on"] = False
    morse_state["last_time"] = ticks_ms()
    morse_state["is_transmitting"] = True
    morse_state["current_symbols"] = ""
    morse_state["finished"] = False
    log(f"Starting Morse code: {message}")


# Non-blocking Morse code transmission function
def handle_morse_transmission():
    global morse_state, duty

    if not morse_state["is_transmitting"]:
        return

    current_time = ticks_ms()

    # Check if it's time for the next step in Morse code transmission
    if ticks_diff(current_time, morse_state["last_time"]) >= 0:
        if morse_state["current_symbols"] == "":
            # New letter to process
            if morse_state["char_index"] < len(morse_state["message"]):
                char = morse_state["message"][morse_state["char_index"]].upper()
                if char == " ":
                    # Handle space between words
                    morse_state["last_time"] = current_time + END_MESSAGE_PAUSE_TIME
                    morse_state["char_index"] += 1
                    return
                morse_state["current_symbols"] = MORSE_CODE.get(char, "")
                morse_state["symbol_index"] = 0
                log(f"Sending: {char}, Symbols: {morse_state['current_symbols']}")
            else:
                # End of message, insert word pause before repeating
                morse_state["last_time"] = current_time + END_MESSAGE_PAUSE_TIME
                morse_state["char_index"] = 0  # Reset to repeat
                morse_state["finished"] = True
                log("Finished sending, word pause")
                return

        # Turn off the signal after symbol
        if morse_state["is_magnet_on"]:
            morse_state["is_magnet_on"] = False
            magnet.duty(0)
            log("Turn magnet off")
            # Turn off the signal after the complete letter
            if morse_state["symbol_index"] >= len(morse_state["current_symbols"]):
                log(
                    f"Current symbols '{morse_state['current_symbols']}' finished. Letter pause"
                )
                morse_state["last_time"] = current_time + LETTER_PAUSE_TIME
                morse_state["symbol_index"] = 0
                morse_state["char_index"] += 1
                morse_state["current_symbols"] = ""
                return

            # Turn off the signal after dot or dash
            log(f"Symbol finished. Symbol pause")
            morse_state["last_time"] = current_time + SYMBOL_PAUSE_TIME

            return

        # Get the current symbol (dot or dash)
        symbol = morse_state["current_symbols"][morse_state["symbol_index"]]

        if symbol in [".", "-"]:
            log("Turn magnet on")
            log("Send symbol:", symbol)
            morse_state["symbol_index"] += 1
            morse_state["is_magnet_on"] = True
            if symbol == ".":
                magnet.duty(duty)  # Short signal for dot
                morse_state["last_time"] = current_time + DOT_TIME
            elif symbol == "-":
                magnet.duty(duty)  # Longer signal for dash
                morse_state["last_time"] = current_time + DASH_TIME
            return


# Function to handle LED reactivation after brief off time
def handle_led_timeout():
    global encoder_level, encoder_max_level_time, led_blink_last_time
    encoder_to_led_duty_mapping = [0,255,511,1023,1023]
    
    current_time = ticks_ms()

    if encoder_level == 4:
        if encoder_max_level_time is None: encoder_max_level_time = current_time
        if led_blink_last_time is None:
            led.duty(encoder_to_led_duty_mapping[encoder_level])
            led_blink_last_time = current_time
        else:
            time_since_last_blink = ticks_diff(current_time, led_blink_last_time)

            if led.duty() == 0 and time_since_last_blink >= 200:
                led.duty(encoder_to_led_duty_mapping[encoder_level])
                led_blink_last_time = current_time
            elif led.duty() > 0 and time_since_last_blink >= 200:
                led.duty(0)  # Turn the LED off
                led_blink_last_time = current_time  # Reset the blink timer
    else:
        led.duty(encoder_to_led_duty_mapping[encoder_level])
        led_blink_last_time = None
        encoder_max_level_time = None

def handle_shutdown():
    global encoder_level, encoder_max_level_time

    current_time = ticks_ms()
    if encoder_level == 4 and encoder_max_level_time is None:
        encoder_max_level_time = current_time
        log("Current time set", encoder_max_level_time)
    elif encoder_level == 4 and ticks_diff(current_time, encoder_max_level_time) >= 10000:
        log("Entering deep sleep")
        # TODO: deactivate all components e.g. led.deinit()
        encoder_max_level_time = None
    elif encoder_level < 4:
        encoder_max_level_time = None

# Call this in the main loop to handle the Morse code and LED asynchronously
def main_loop():
    while True:
        # Handle the Morse code transmission without blocking
        handle_morse_transmission()

        # Handle the LED timeout
        handle_led_timeout()
        handle_shutdown()

# Example: start Morse code for "HELLO"
start_morse(morse_message)
main_loop()  # This will run the main loop
