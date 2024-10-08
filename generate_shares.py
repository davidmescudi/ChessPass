from sslib import shamir
# ["A1","A2","A3","B1","B2","B3","C1","C2","C3"] starting from 0 (A1) to 8(C3)
possible_positions = [1,4,5,7,8,9,10,11,13]

########################### Change these to your liking ###########################

secret = "https://is.gd/u1TXB0"
how_many_figures = 3
# ["A1","A2","A3","B1","B2","B3","C1","C2","C3"] starting from 0 (A1) to 8(C3)
positions = [possible_positions[8], possible_positions[4], possible_positions[0]]
# simply a integer from 1,2,3 represents how strong the magnet needs to be
magnet_strengths = [2,3,1]
how_many_figures_required_to_reveal_secret = 2

########################### Below no changes are required ###########################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
def shift_hex_string(s, shift, decrypt=False):
    if decrypt:
        shift = (-1) * shift
    shifted = ""
    for char in s:
        if char.isdigit():  # Shift digits 0-9
            shifted += chr((ord(char) - ord('0') + shift) % 10 + ord('0'))
        elif char.isalpha():  # Shift letters a-f or A-F (for hex)
            if char.islower():  # Handle lowercase hex letters
                start = ord('a')
                shifted += chr((ord(char) - start + shift) % 16 + start)
            elif char.isupper():  # Handle uppercase hex letters
                start = ord('A')
                shifted += chr((ord(char) - start + shift) % 16 + start)
        else:
            # Leave any other characters unchanged
            shifted += char
    return shifted

result = shamir.to_hex(shamir.split_secret(secret.encode('ascii'), how_many_figures_required_to_reveal_secret, how_many_figures))

required_shares = result['required_shares']
prime_mod = result['prime_mod']
shares = result['shares']

with open("Board/boot.py", "w") as boot_file:
    boot_file.write(f"required_shares = {required_shares}\n")
    boot_file.write(f"prime_mod = '{prime_mod}'")

for idx, share in enumerate(shares):
    filename = f"Figure/boot{idx + 1}.py"
    shifted_share = shift_hex_string(share, positions[idx] * magnet_strengths[idx])
    with open(filename, "w") as share_file:
        share_file.write(f"secret_share = '{shifted_share}'\n")

########################### How to decrypt example ###########################
#####################################################################################
#secret_share_1 = '...'
#secret_share_2 = '...'
#secret_share_3 = '...'

#test = {
#    "required_shares" : 2,
#    "prime_mod" : '7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff',
#    "shares" : [
#        shift_hex_string(secret_share_1, positions[0] * magnet_strengths[0], decrypt=True),
#        shift_hex_string(secret_share_2, positions[1] * magnet_strengths[1], decrypt=True),
#        shift_hex_string(secret_share_3, positions[2] * magnet_strengths[2], decrypt=True)
#    ]
#}

# decrypt_fixed = shamir.recover_secret(shamir.from_hex(test)).decode('ascii')