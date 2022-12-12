import environs


env = environs.Env()
env.read_env()
API_TOKEN = env.str("MINT_SCAN_API_TOKEN")

nodes = {
    'juno': ["/root/go/bin/junod", "https://juno-rpc.polkachu.com:443"],
    'bostrom': ['/root/go/bin/cyber', 'https://rpc.bostrom.cybernode.ai:443'],
    'uptick': ['/root/go/bin/uptickd', 'https://uptick-testnet.nodejumper.io:443']
    #"juno_cyb": ["/root/go/bin/junod", "https://juno-rpc.polkachu.com:443"],
    # "stargaze": ["/root/go/bin/starsd", "https://stargaze-rpc.polkachu.com:443"],
    #"umee": ["/root/go/bin/umeed", "https://umee-rpc.polkachu.com:443"],
}
