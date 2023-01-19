from scripts.helpfulScripts import get_account, get_contract, fund_with_link
from brownie import Lottery, config, network
import time


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account, "gas_price": 1000000000, "gas_limit": 12000000},
        publish_source=config["networks"][network.show_active()].get("verify", False))
    # Direct "get_conract()" function to check behind the scenes whether we are on a testnet
    # in which case we take directly from config file or are we on localnet
    # in which case we use the addresses of the local chain
    if network.show_active() != "development":
        time.sleep(1)
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    start_tx = lottery.startLottery(
        {"from": account, "gas_price": 1000000000, "gas_limit": 12000000})
    start_tx.wait(1)
    print("Lottery has started")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 100000
    tx = lottery.enter({"from": account, "value": value,
                        "gas_price": 1000000000,
                       "gas_limit": 12000000})
    tx.wait(1)
    print("You entered the lottery")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # Fund the contract
    # Then end the lottery
    tx = fund_with_link(lottery.address)
    tx.wait(1)

    ending_tx = lottery.endLottery(
        {"from": account, "gas_price": 1000000000, "gas_limit": 12000000})
    # ending_tx.wait(1)
    # time.sleep(60)
    # print(f"{lottery.recentWinner()} is the recent winner")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
