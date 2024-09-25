# https://github.com/jqueiroz/python-sslib
from sslib import shamir
import json

with open('shamir.json', 'r') as f:
    result = json.load(f)

with open('shamir_fixed.json', 'r') as f:
    result_fixed = json.load(f)

print(result)
print(result_fixed)

decrypt = shamir.recover_secret(shamir.from_base64(result)).decode('ascii')
decrypt_fixed = shamir.recover_secret(shamir.from_base64(result_fixed)).decode('ascii')

print("Dynamic prime: ", decrypt)
print("Fixed prime: ", decrypt_fixed)