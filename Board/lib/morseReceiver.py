from machine import Pin, ADC
from time import ticks_ms, ticks_diff
from sensors import HallSensor


class MorseReceiver:
    def __init__(
        self,
        hall_sensor: HallSensor,
        morse_code,
        morse_variance,
        dot_time,
        dash_time,
        symbol_pause_time,
        letter_pause_time,
        end_message_pause_time,
        verbose=False,
    ):
        self.hall_sensor = hall_sensor
        self.reverse_morse_code = {value: key for key, value in morse_code.items()}
        self.morse_variance = morse_variance
        self.dot_time = dot_time
        self.dash_time = dash_time
        self.symbol_pause_time = symbol_pause_time
        self.letter_pause_time = letter_pause_time
        self.end_message_pause_time = end_message_pause_time
        self.verbose = verbose

        # state variables
        self.reset()

    def reset(self):
        self.received_word = ""
        self.current_symbols = ""
        self.last_signal_time = None
        self.last_pause_time = None
        self.is_receiving = False
        self.is_saving = False
        self.message_received = False
        self.current_time = ticks_ms()

    def log(self, *values):
        if self.verbose:
            print(*values)

    def start_receiving(self):
        self.last_signal_time = self.current_time
        self.is_receiving = True

    def update_current_time(self):
        self.current_time = ticks_ms()
        
    def get_magnet_strength(self):
        return self.hall_sensor.manget_strength

    def handle_signal_on(self):
        if not self.is_receiving:
            self.start_receiving()
        self.signal_duration = ticks_diff(self.current_time, self.last_signal_time)

    def is_dot_or_dash(self):
        return self.signal_duration >= (
            self.dot_time - self.morse_variance
        ) or self.signal_duration >= (self.dash_time - self.morse_variance)

    def handle_signal_off(self):

        self.is_receiving = False
        self.signal_duration = ticks_diff(self.current_time, self.last_signal_time)
        self.log("signal_duration:", self.signal_duration)

        if self.is_dot_or_dash():
            self.last_pause_time = self.current_time
        else:
            self.last_pause_time = None

    def check_pause_duration(self):
        pause_duration = ticks_diff(self.current_time, self.last_pause_time)
        if pause_duration % 20 == 0:
            self.log("pause_duration:", pause_duration)
            
        if pause_duration >= self.end_message_pause_time - self.morse_variance * 2:
            self.last_pause_time = None
            self.is_saving = True
            self.log("--- Start saving ---")

    def check_message_end(self):
        self.update_current_time()
        signal = self.hall_sensor.is_magnet_detected()

        if signal:
            self.handle_signal_on()
        else:
            if self.is_receiving:
                self.handle_signal_off()
            elif self.last_pause_time:
                self.check_pause_duration()

    def decode_symbol(self):
        self.signal_duration = ticks_diff(self.current_time, self.last_signal_time)
        self.log("signal duration:", self.signal_duration)
        if self.signal_duration >= self.dash_time - self.morse_variance:
            return "-", self.signal_duration - (self.dash_time - self.morse_variance)
    
        return ".", self.signal_duration - (self.dot_time - self.morse_variance)

    def check_for_letter_or_message_end(self):
        pause_duration = ticks_diff(self.current_time, self.last_pause_time)
        if pause_duration % 50 == 0:
            self.log("pause_duration:", pause_duration)
        # End of a letter
        if (
            pause_duration >= self.letter_pause_time - self.morse_variance * 1.5
            and self.current_symbols
        ):
            self.log("End of letter")
            self.decode_letter()

        # End of the message
        if pause_duration >= self.end_message_pause_time - self.morse_variance:
            self.last_pause_time = None
            
            if self.is_saving:
                self.log(f"End of first word received: {self.received_word}")
                self.message_received = True
                self.is_saving = True
                message = self.received_word
                self.received_word = ""
                return message, self.get_magnet_strength()
            self.log("End of message, but not saving")

    def decode_letter(self):
        """Decodes the current symbol sequence into a letter."""
        if self.current_symbols in self.reverse_morse_code:
            decoded_letter = self.reverse_morse_code[self.current_symbols]
            self.received_word += decoded_letter
            self.log(f"Decoded letter: {decoded_letter}")
        else:
            self.log(f"Unknown Morse code: {self.current_symbols}")
        self.current_symbols = ""  # Reset the current symbol after decoding

    def handle_morse_reception(self):

        # if morse_state['message_received']:
        # return  # Ignore further signals after receiving the first word

        self.update_current_time()
        signal = (
            self.hall_sensor.is_magnet_detected()
        )  # Use the Hall sensor for signal detection

        if signal:  # Magnet detected (dot or dash)
            self.handle_signal_on()

        else:  # No magnet detected (pause between symbols or letters or words)
            if self.is_receiving:
                # The signal just stopped, so process the duration of the signal
                symbol, deviation = self.decode_symbol()

                self.current_symbols += symbol
                self.log(f"Detected symbol: {symbol}")

                # Reset receiving state after processing the symbol
                self.is_receiving = False
                self.last_pause_time = self.current_time - deviation

            elif self.last_pause_time:
                # Calculate the pause duration since the last signal ended
                return self.check_for_letter_or_message_end()

    def init(self):
        self.hall_sensor.init_hall_sensor(1000)

    def execute(self):
        if self.is_saving:
            # Handle the non-blocking reception of Morse code using the Hall sensor
            return self.handle_morse_reception()
        else:
            self.check_message_end()
