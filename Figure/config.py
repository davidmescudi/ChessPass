# BOX
HALL_VARIANCE_THRESHOLD = 70
MORSE_VARIANCE = 5 # handle and mitigate desyncronistaion between box and piece
ADCS = [36, 39, 34, 35, 32, 33, 25, 26, 27]

# PIECE
PINS_C3 = {
    "LED": 10,
    "MAGNET": 9,
    "CLK": 8,
    "DT": 20
}

PINS_S3 = {
    "LED": 9,
    "MAGNET": 8,
    "CLK": 7,
    "DT": 44
}

MAGNET_FREQ = 1000 # 1 kHz
INIT_DUTY = 1023

LED_PIN = 10
LED_OFF_DURATION = 200 # miliseconds off when magnet strenght switchted
### TODO Use pwm for led to set 3 states depending on 3 magnet strenght LOW -> MIDDLE -> HIGH

ROT_DEBOUNCE_TIME = 10  # Minimum time (ms) between encoder events

#BOTH
MORSE_CODE = {
    'A': '.-', 
    'B': '-...',
    'C': '-.-.',
    'D': '-..',
    'E': '.',
    'F': '..-.',
    'G': '--.',
    'H': '....',
    'L': '.-..',
    'O': '---',
    '-': '-',
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

DOT_TIME = 70
DASH_TIME = 3*DOT_TIME
SYMBOL_PAUSE_TIME = DOT_TIME
LETTER_PAUSE_TIME = 3 * DOT_TIME
END_MESSAGE_PAUSE_TIME = 7 * DOT_TIME

