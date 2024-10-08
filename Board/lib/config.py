# BOX
HALL_VARIANCE_THRESHOLD = 70
MORSE_VARIANCE = 20  # handle and mitigate desyncronistaion between box and piece
ADCS = [36, 39, 34, 35, 32, 33, 25, 26, 27]

MAGNET_STRENGTH_MAPPING = [
    [2710, 2800], # 0/A1 2698,2740,2841
    [2790, 2850], # 1/A2 2779,2807,2880
    [2720, 2810], # 2/A3 2708,2752,2850
    [2720, 2810], # 3/B1 2703, 2747, 2850
    [2730, 2810], # 4/B2 2720, 2756, 2848
    [2750, 2840], # 5/B3 2735,2774,2871
    [2805, 2870], # 6/C1 2795,2820,2897
    [2763, 2850], # 7/C2 # 2752, 2787, 2880
    [2705, 2800]  # 8/C3
]


# PIECE
PINS_C3 = {"LED": 10, "MAGNET": 9, "CLK": 8, "DT": 20}

PINS_S3 = {"LED": 9, "MAGNET": 8, "CLK": 7, "DT": 44}

SHUTDOWN_TIME = 10000
ENCODER_MAX_LEVEL = 4
ENCODER_MIN_LEVEL = 0
ENCODER_LEVEL = 0
MAGNET_FREQ = 1000  # 1 kHz
INIT_DUTY = 0
MAGNET_DUTY_MAPPING = [0, 900, 1000, 1023, 0]
MAGNET_MAX_DUTY = 1023
TRANSMIT_MAGNET_STRENGTH_TIME = 2000  # ms


LED_DUTY_MAPPING = [0, 255, 511, 1023, 1023]
LED_BLINK_INTERVAL = 200  # miliseconds off when magnet strenght switchted
### TODO Use pwm for led to set 3 states depending on 3 magnet strenght LOW -> MIDDLE -> HIGH

ROT_DEBOUNCE_TIME = 20  # Minimum time (ms) between encoder events


# BOTH
MORSE_CODE = {
    "a": ".-",
    "b": "-...",
    "c": "-.-.",
    "d": "-..",
    "e": ".",
    "f": "..-.",
    "g": "--.",
    "h": "....",
    "i": "..",
    "j": ".---",
    "k": "-.-",
    "l": ".-..",
    "m": "--",
    "n": "-.",
    "o": "---",
    "p": ".--.",
    "q": "--.-",
    "r": ".-.",
    "s": "...",
    "t": "-",
    "u": "..-",
    "v": "...-",
    "w": ".--",
    "x": "-..-",
    "y": "-.--",
    "z": "--..",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    "0": "--.--",
    "-": "-....-",
}

DOT_TIME = 70
DASH_TIME = 3 * DOT_TIME
SYMBOL_PAUSE_TIME = DOT_TIME
LETTER_PAUSE_TIME = 3 * DOT_TIME
END_MESSAGE_PAUSE_TIME = 5 * DOT_TIME
MAGNET_STRENGTH_PAUSE_TIME = 7 * DOT_TIME

FIGURE_DETECTION_TIME = 1000
FIGURE_DETECTION_THRESHOLD = 0.3

DISPLAY_PINS = {"SPI": 1, "CS": 15, "DC": 16, "RST": 4, "BL": 17}
