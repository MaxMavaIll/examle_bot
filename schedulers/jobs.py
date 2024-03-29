import asyncio
import json
import logging
import environs
import math

from aiogram import Bot
from aiogram.dispatcher.fsm.storage.redis import RedisStorage

import time
from api.requests import MintScanner
from schedulers.exceptions import NoSlashingInfo, raise_error
from schedulers.exceptions import raise_error
from api.functions import get_index_by_moniker, get_index_by_address

# from name_node import skipped_blocks_allowed, time_jail, name 
from api.config import chains

env = environs.Env()
env.read_env()
ADMIN_ID = env.str("ADMINS")


def two_zero(integer):
    if integer < 10:
        return "0" + str(integer)

    else:
        return integer



async def check_val_new():
    pass


async def sends_message_client(bot: list, user_id: int | str, moniker: str, platform: str,
                percentages: int , skipped_blocks_allowed: int, time_to_jail: int, missed_blocks_counter_new: int):

                if not missed_blocks_counter_new:
                    # await bot.send_message(user_id, f"<b>Moniker: {moniker}.</b>"
                    #                         "all good")
                    return
                    
                elif percentages > (skipped_blocks_allowed * 0.7):
                    await bot.send_message(user_id, f"<b>Platform: {platform} ({moniker}).</b>"
                                        f"\nbot: <b>If you don't fix it, your validator will go to jail.</b>"
                                        f"\n    missed_blocks: {percentages}/{skipped_blocks_allowed}"
                                        f"\n    time_before_jail: { two_zero( math.floor(time_to_jail / 60) ) }:{ two_zero( time_to_jail % 60 ) }"
                                        )

                else:
                    await bot.send_message(user_id, f"<b>Platform: {platform} ({moniker}).</b>"
                                        f"\nbot: "
                                        f"\n.   missed_blocks: {percentages}/{skipped_blocks_allowed}"
                                        f"\n    time_before_jail: { two_zero( math.floor(time_to_jail / 60) ) }:{ two_zero( time_to_jail % 60 ) }")
                logging.info("Я закінчив роз силку miss")

async def add_user_checker(bot: Bot, mint_scanner: MintScanner, #user_id: int, platform: str, moniker: str,
                           storage: RedisStorage, chain: str, network: str):
    logging.info('Я почав розсилку')
    

    async def check_block(old_new, new):
        logging.debug(f"old_new {old_new}")
        if old_new >= 28:
            return 1
        else:
            #checkers[str(user_id)][platform][moniker]['last_check'] = new
            return 0

    async def check(old: int, new: int, skipped_blocks_allowed: int, time_jail: int):
        right_blocks = await check_block(new - old, new)
        logging.debug(f"right_blocks {right_blocks}")
        if right_blocks:
            # old = checkers.get('validators')[str(user_id)][moniker]['last_check']
            # rizn = new - old
            vidsot_skip_blok = (100 * new) / skipped_blocks_allowed
            vidsot_time_to_jail = (
                ((100 - vidsot_skip_blok) * time_jail) / 100) / 60
            # return right_blocks, round(vidsot_skip_blok, 2), round(vidsot_time_to_jail)
            return right_blocks, new, round(vidsot_time_to_jail)
        else:
            return 0, 0, 0


    stake=[]

    all_cons_validators_one =None
    checkers = await storage.redis.get('checkers') or '{}'
    checkers = json.loads(checkers)
    # logging.info(f'\n\n{network, checkers}')

    
    # try:
    #     checkers['validators'][network].keys()
    # except:
    #     checkers['validators'][network] = {}
    #     checkers['validators'][network][]= {}
    # logging.info(f'\n\n{network, checkers}')
    # or chain not in checkers['validators'][network].keys()
    if checkers == {}: 
        logging.info("Масив пустий {} ")
        logging.info(f"Я закінчив роз силку {chain}")
        
        await storage.redis.set('checkers', json.dumps(checkers))
        return

    else:
        for id in checkers['validators'][network][chain]:
            for val in checkers['validators'][network][chain][id]:
                if checkers['validators'][network][chain][id][val]["addr_cons"] is None and len(stake) < 2*2:
                    stake.append(id)
                    stake.append(val)
        
        for user_id in checkers['validators'][network][chain]:
            for moniker in checkers['validators'][network][chain][user_id]:
                skipped_blocks_allowed = chains[network][chain]["parameters"]['skipped_blocks_allowed']
                time_jail = skipped_blocks_allowed * chains[network][chain]["parameters"]['blok_time']


                
                if checkers['validators'][network][chain][user_id][moniker].get('addr_cons') is None and user_id in stake and moniker in stake:
                    if checkers.get('all_missed') is None:
                        data = await mint_scanner.parse_application(chain, moniker)
                        checkers['all_missed'] = data['data']['validators']

                        if not data['ok']:
                            await bot.send_message(ADMIN_ID, "Error happened: " + data['error'] + "\n\n" + f'{moniker=}, {chain=}')
                            raise raise_error(data['error'])

                        missed_blocks_counter = data['missed_blocks_counter']

                    else:
                        data = await mint_scanner.get_repeated_missing_block(chain, checkers['all_missed'][get_index_by_moniker(moniker, checkers['all_missed'])].get('consensus_pubkey').get('key'))
                        missed_blocks_counter = int(data['missed_blocks_counter']['missed_blocks_counter'])
                    
                    logging.info(f'Sleeping for 180 seconds ')
                    await asyncio.sleep(180)
                    data_new = await mint_scanner.get_repeated_missing_block(chain, checkers['all_missed'][get_index_by_moniker(moniker, checkers['all_missed'])].get("consensus_pubkey").get('key'))
                    checkers['validators'][network][chain][str(user_id)][moniker]['addr_cons'] = data_new['missed_blocks_counter']['address']
                    missed_blocks_counter_new = int(data_new['missed_blocks_counter']['missed_blocks_counter'])

                    missed_blocks_counter_new, percentages, time_to_jail = await check( missed_blocks_counter, missed_blocks_counter_new, skipped_blocks_allowed, time_jail)
                    await sends_message_client(bot, user_id, moniker, chain, percentages, skipped_blocks_allowed, time_to_jail, missed_blocks_counter_new)

                    logging.debug(f" old_rezult {type(missed_blocks_counter)} , new_rezult {type(missed_blocks_counter_new)}")
                    logging.info(f'{data_new}')
                    logging.info(f"Get second missed blocks counter {moniker}: {missed_blocks_counter_new} rizn {missed_blocks_counter_new - missed_blocks_counter}")
                    logging.debug(f"missed_blocks: {missed_blocks_counter_new}, percentages: {percentages}, time_to_jail: {time_to_jail} ")
                    
                elif checkers['validators'][network][chain][str(user_id)][moniker].get('addr_cons') is not None:
                
                    logging.debug("cons_true")
                    if all_cons_validators_one is None:
                        all_cons_validators_one = await mint_scanner.get_repeated_missing_blocks(chain, checkers['validators'][network][chain][str(user_id)][moniker].get('addr_cons'))
                        
                        logging.info(f'Sleeping for 180 const')
                        await asyncio.sleep(10)
                        all_cons_validators_second = await mint_scanner.get_repeated_missing_blocks(chain, checkers['validators'][network][chain][str(user_id)][moniker].get('addr_cons'))

                    index = get_index_by_address(checkers['validators'][network][chain][str(user_id)][moniker]['addr_cons'],
                                                all_cons_validators_one['missed_blocks_counters'])

                    cons_val_one = int(all_cons_validators_one['missed_blocks_counters'][index].get('missed_blocks_counter'))
                    # cons_val_one = 0

                    cons_val_two = int(all_cons_validators_second['missed_blocks_counters'][index].get('missed_blocks_counter'))
                    # cons_val_two= 32

                    missed_blocks_counter_new, percentages, time_to_jail = await check( cons_val_one, cons_val_two, skipped_blocks_allowed, time_jail )

                    await sends_message_client(bot, user_id, moniker, chain, percentages, skipped_blocks_allowed, time_to_jail, missed_blocks_counter_new)
                    
                    logging.debug(f"const: {checkers['validators'][network][chain][str(user_id)][moniker]['addr_cons']}")
                    logging.info(f"index cons_validators: {index}")
                    logging.info(f"Missed blocks counter {moniker} : {cons_val_one} const")
                    logging.info(f"Second Missed blocks counter {moniker} : {cons_val_two} const")

        checkers['all_missed'] = None
        checkers['miss_all_blocks'] = None
        logging.info(f"Я закінчив роз силку full \n{checkers}\n")
        await storage.redis.set('checkers', json.dumps(checkers))
    
async def proposals(bot: Bot, mint_scanner: MintScanner, #user_id: int, platform: str, moniker: str,
                           storage: RedisStorage):
                           pass