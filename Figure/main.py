from machine import Pin, ADC, PWM, freq
from time import ticks_ms, ticks_diff, sleep_ms
from boot import secret_share
# Load right pins because we used two different esp32 namley s3 (240 MHz) and c3(160 MHz) that differ in pins
if freq() == 240000000:
    from config import PINS_S3 as PINS
else:
    from config import PINS_C3 as PINS

from config import (
    LED_BLINK_INTERVAL,
    MAGNET_FREQ,
    INIT_DUTY,
    ROT_DEBOUNCE_TIME,
    MORSE_CODE,
    DASH_TIME,
    DOT_TIME,
    SYMBOL_PAUSE_TIME,
    LETTER_PAUSE_TIME,
    END_MESSAGE_PAUSE_TIME,
    MAGNET_DUTY_MAPPING,
    LED_DUTY_MAPPING,
    ENCODER_LEVEL,
    ENCODER_MAX_LEVEL,
    ENCODER_MIN_LEVEL,
    SHUTDOWN_TIME,
    MAGNET_MAX_DUTY,
    TRANSMIT_MAGNET_STRENGTH_TIME
)
VERBOSE = True

# Setup pins for LED, PWM, encoder (clk, dt)
led = PWM(Pin(PINS["LED"], Pin.OUT))
magnet = PWM(Pin(PINS["MAGNET"]), freq=MAGNET_FREQ)
magnet.duty(0)

clk = Pin(PINS["CLK"], Pin.IN, Pin.PULL_UP)
dt = Pin(PINS["DT"], Pin.IN, Pin.PULL_UP)

# Initial duty cycle
magnet_duty = INIT_DUTY  # (0 to 1023) magnet strenght for morsing


# State variables for Morse code transmission
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
is_shutdown = False
last_clk = clk.value()
last_encoder_event_time = 0  # For debouncing
debounce_time = ROT_DEBOUNCE_TIME  # Minimum time (ms) between encoder events
encoder_level = ENCODER_LEVEL
encoder_max_level_time = None
led_blink_last_time = None


def log(*values):
    if VERBOSE:
        print(*values)


# Encoder interrupt handler
def encoder_callback(pin):
    global magnet_duty, last_clk, last_encoder_event_time, encoder_level, encoder_max_level_time, is_shutdown

    # reactivate if is shutdowned
    is_shutdown = False
    # Debouncing: ignore events that happen too quickly
    current_time = ticks_ms()
    if ticks_diff(current_time, last_encoder_event_time) < debounce_time:
        return

    current_clk = clk.value()

    if current_clk == 1 and last_clk == 0:
        # Adjust PWM duty cycle based on encoder direction
        if dt.value() == 0:  # Clockwise rotation
            encoder_level = min(ENCODER_MAX_LEVEL, encoder_level + 1)
        else:  # Counter-clockwise rotation
            encoder_level = max(ENCODER_MIN_LEVEL, encoder_level - 1)
            
        # Limit duty cycle between 0 and 1023
        magnet_duty = MAGNET_DUTY_MAPPING[encoder_level]#
        magnet.duty(magnet_duty)
        # pwm.duty(duty)
        log("Duty cycle:", magnet_duty)
        log("Encoder Level:", encoder_level)
        # Restart Morse code transmission
        if (encoder_level < 4 and morse_state["is_transmitting"]):
            morse_state["is_transmitting"] = False
    # Update the last state and time
    last_clk = current_clk
    last_encoder_event_time = current_time


# Set up an interrupt on the `clk` pin for both rising and falling edges
clk.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=encoder_callback)


# Function to handle LED reactivation after brief off time
def handle_led_timeout():
    global encoder_level, encoder_max_level_time, led_blink_last_time
    encoder_to_led_duty_mapping = LED_DUTY_MAPPING

    current_time = ticks_ms()

    if encoder_level == ENCODER_MAX_LEVEL:
        if encoder_max_level_time is None:
            encoder_max_level_time = current_time
        if led_blink_last_time is None:
            led.duty(encoder_to_led_duty_mapping[encoder_level])
            led_blink_last_time = current_time
        else:
            time_since_last_blink = ticks_diff(current_time, led_blink_last_time)

            if led.duty() == 0 and time_since_last_blink >= LED_BLINK_INTERVAL:
                led.duty(encoder_to_led_duty_mapping[encoder_level])
                led_blink_last_time = current_time
            elif led.duty() > 0 and time_since_last_blink >= LED_BLINK_INTERVAL:
                led.duty(0)  # Turn the LED off
                led_blink_last_time = current_time  # Reset the blink timer
    else:
        led.duty(encoder_to_led_duty_mapping[encoder_level])
        led_blink_last_time = None
        encoder_max_level_time = None


def handle_shutdown():
    global encoder_level, encoder_max_level_time, is_shutdown

    current_time = ticks_ms()
    if encoder_level == ENCODER_MAX_LEVEL:
        if not morse_state["is_transmitting"]:
            start_morse()
        if encoder_max_level_time is None:
            encoder_max_level_time = current_time
            log("Current time set", encoder_max_level_time)
        #elif ticks_diff(current_time, encoder_max_level_time) >= SHUTDOWN_TIME:
            #log("Shutdown")
            #is_shutdown = True
            #led.duty(0)
            #magnet.duty(0)
            #clk.off()
            #dt.off()
    else:
        encoder_max_level_time = None


# Function to start Morse code transmission
def start_morse():
    global morse_state
    morse_state["message"] = secret_share
    morse_state["char_index"] = 0
    morse_state["symbol_index"] = 0
    morse_state["is_magnet_on"] = False
    morse_state["last_time"] = ticks_ms()
    morse_state["is_transmitting"] = True
    morse_state["current_symbols"] = ""
    morse_state["finished"] = False
    log(f"Starting Morse code: {secret_share}")


# Non-blocking Morse code transmission function
def handle_morse_transmission():
    global morse_state, magnet_duty

    if not morse_state["is_transmitting"]:
        return
    
        
    current_time = ticks_ms()
    
    if morse_state["finished"]:
        # add time to transmit magnet strenght
        morse_state["finished"] = False
        morse_state["last_time"] = current_time + TRANSMIT_MAGNET_STRENGTH_TIME
        magnet.duty(magnet_duty)
        # TODO pause after magnet_strenght transmission

    # Check if it's time for the next step in Morse code transmission
    if ticks_diff(current_time, morse_state["last_time"]) >= 0:
        if morse_state["current_symbols"] == "":
            # New letter to process
            if morse_state["char_index"] < len(morse_state["message"]):
                char = morse_state["message"][morse_state["char_index"]]
    
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
                magnet.duty(MAGNET_MAX_DUTY)  # Short signal for dot
                morse_state["last_time"] = current_time + DOT_TIME
            elif symbol == "-":
                magnet.duty(MAGNET_MAX_DUTY)  # Longer signal for dash
                morse_state["last_time"] = current_time + DASH_TIME
            return


# Call this in the main loop to handle the Morse code and LED asynchronously
def main_loop():
    while True:
        if is_shutdown:
            # slower execution
            sleep_ms(10)
            continue 
        # Handle the Morse code transmission without blocking
        handle_morse_transmission()

        # Handle the LED timeout
        handle_led_timeout()
        handle_shutdown()
        


# Example: start Morse code for "HELLO"
main_loop()  # This will run the main loop
