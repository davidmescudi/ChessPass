# https://github.com/jqueiroz/python-sslib
from sslib import shamir
import json

required_shares = 2
distributed_shares = 3

result_fixed_prime = shamir.to_base64(shamir.split_secret("Paul und David".encode('ascii'), required_shares, distributed_shares, prime_mod=2**607-1))
result = shamir.to_base64(shamir.split_secret("David und Paul".encode('ascii'), required_shares, distributed_shares))

print("Result: ", result)
print("Result fixed prime: ", result_fixed_prime)

with open('shamir.json', 'w') as f:
    json.dump(result, f)

with open('shamir_fixed.json', 'w') as f:
    json.dump(result_fixed_prime, f)
