import asyncio
import json
import logging
from typing import Union


async def load_block(parsing_application: str, url: str) -> Union[dict, None]:
    logging.info(f'\n{url}\n')
    
    if parsing_application == 'root/go/bin/cyber':
        valid = "'.validators[] | select(.status==\"BOND_STATUS_BONDED\")'"
        #cmd = f'''{parsing_application} q staking validators -oj --limit=3000 --node https://juno-rpc.polkachu.com:443 | jq '.validators[] | select(.status=="BOND_STATUS_BONDED")' '''
        cmd = [parsing_application, 'q', 'staking', 'validators', '-oj', '--limit=3000', '--node', url, '|', '/usr/bin/jq', valid ]
    else:
        #cmd = f"{parsing_application} q staking validators --node {url} --limit 300 -o json"
        cmd = [parsing_application, 'q', 'staking', 'validators', '--node', url, '--limit', '1000', '-o', 'json' ]
    return await run_app(cmd)


def get_index_by_network( validators: list, user_id: str):
    mass = {}

    for network in validators:
        for chain in validators[network]:
            for id in validators[network][chain]:
                # logging.info(f'{type(id)}, {validators}, {user_id}, {type(user_id)}')
                for moniker in validators[network][chain][id]:
                    if id == str(user_id):
                        


                        if network not in mass:
                            mass[network] = {}
                            # logging.debug(mass)

                        if chain not in mass[network]:
                            mass[network][chain] = {}
                            # logging.debug(mass)


                        if str(id) not in mass[network][chain]:
                            mass[network][chain][str(id)] = [moniker]
                            # logging.debug(mass)
                        else:
                            mass[network][chain][str(id)].append(moniker)
                        

                    # current_moniker = network.get("description").get("moniker")
                    # #logging.info(f"{index} - {current_moniker}. Seeking: {moniker}")
                    # if network.get("description").get("moniker") == moniker:
    return mass 

def get_index_by_moniker(moniker: str, validators: list):
    for index, val in enumerate(validators):
        current_moniker = val.get("description").get("moniker")
        #logging.info(f"{index} - {current_moniker}. Seeking: {moniker}")
        if val.get("description").get("moniker") == moniker:
            return index 

def get_index_by_address(address: str, addresses: list):
    for index, val in enumerate(addresses):
        #logging.info(f'{index}. {val}')
        current_moniker = val.get("address")
        #logging.info(f"{index} - {current_moniker}. Seeking: {address}")
        if current_moniker == address:
            return index 

def get_consensus_pubkey(validator):
    return validator.get("consensus_pubkey").get("key")


async def slashing_signing_info(parsing_application, key, url):
    p_variable = {
        "@type": "/cosmos.crypto.ed25519.PubKey",
        "key": key,
    }
    p_json = json.dumps(p_variable)

    cmd = [parsing_application, 'q', 'slashing', 'signing-info', p_json, '--node', url, '-o', 'json']
    result = await run_app(cmd)
    return result

async def slashing_signing_infos(parsing_application, url):

    cmd = [parsing_application, 'q', 'slashing', 'signing-infos', '--node', url, '--limit', '1000', '-o', 'json']
    result = await run_app(cmd)
    return result["info"]

def get_missed_block_counter(result: dict):
    if missed_blocks_counter := result.get("missed_blocks_counter"):
        return int(missed_blocks_counter)


async def run_app(cmd: list) -> dict:
    # result = subprocess.run(cmd.split(), stdout=subprocess.PIPE)
    # return result.stdout.decode('utf-8')
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    logging.info("cmd: %s", " ".join(cmd))
    logging.info(f"stdout: {stdout.decode('utf-8')[:1000]}")
    logging.error(f"stderr: {stderr.decode('utf-8')}")
    result = stdout.decode('utf-8')
    if result:
        result = json.loads(result)
        return result
