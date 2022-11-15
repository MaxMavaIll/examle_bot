
chains = {'Mainnet': {'juno': {'bin': '/root/go/bin/junod', 'node': ['https://juno-rpc.polkachu.com:443']}}, 'Testnet': {}}

name = "juno"
min_signed_per_window = 5
signed_blocks_window = 10000

skipped_blocks_allowed = int( signed_blocks_window * ( (100 - min_signed_per_window) / 100 ) ) # не допуста кількість пропущених блоків
time_jail = skipped_blocks_allowed * 5.5 # відповідь в секундах
