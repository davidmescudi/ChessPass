from sslib import shamir
########################### Change these to your liking ###########################

secret = "Paul und David"
how_many_figures = 3
how_many_figures_required_to_reveal_secret = 2

########################### Below no changes are required ###########################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
result = shamir.to_hex(shamir.split_secret(secret.encode('ascii'), how_many_figures_required_to_reveal_secret, how_many_figures, prime_mod=2**607-1))

required_shares = result['required_shares']
prime_mod = result['prime_mod']
shares = result['shares']

with open("Board/boot.py", "w") as boot_file:
    boot_file.write(f"required_shares = {required_shares}\n")
    boot_file.write(f"prime_mod = '{prime_mod}'")

for idx, share in enumerate(shares):
    filename = f"Figure/boot{idx + 1}.py"
    with open(filename, "w") as share_file:
        share_file.write(f"secret_share = '{share}'\n")