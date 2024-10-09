# https://github.com/jqueiroz/python-sslib
from lib.sslib import shamir

result_fixed = {"required_shares": 2, "prime_mod": "01000000000000000000000000000000000000000000000085", "shares": ["1-ade023dadbcf2f11364e809abe9c9f21be24a0362ea775de", "2-5bc0478b4f29e9b1f962d20613c60fdc1819cb3b08f6a907", "3-09a06b3bc284a452bc77237168ef8096720ef63fe345dc30"]}
decrypt_fixed = shamir.recover_secret(shamir.from_hex(result_fixed)).decode('ascii')

print("Fixed prime: ", decrypt_fixed)
