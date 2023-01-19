from brownie import network, accounts, config, Contract, VRFCoordinatorMock, LinkToken, MockV3Aggregator, interface
import time

FORKED_LOCAL_ENVIRONMENT = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]


def get_account(index=None, id=None):
    # .yaml works like a dictionary :)
    # accounts[0]
    # accounts.add("env")
    # accounts.load("ID")
    if index:
        return accounts[index]

    if id:
        return accounts.load(id)

    if(network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS or network.show_active() in FORKED_LOCAL_ENVIRONMENT):
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken
}


def get_contract(contract_name):
    """ This function will grab the contract addresses from brownie config if defined. 
    otherwise it'll deploy a mock version of that contract and return that mock contract

        Args:
            contract_name(string)

        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed version of this contract

            MockV3Aggregator[-1]
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            # MockV3Aggregator.length
            deploy_mocks()

        contract = contract_type[-1]
        # MockV3Aggregator[-1]
    else:
        contract_address = config["networks"][network.show_active(
        )][contract_name]
        # address
        # ABI
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi)
        # MockV3Aggregator.abi
    return contract


decimals = 8
starting_price = 200000000000


def deploy_mocks(decimals=decimals, initial_value=starting_price):
    account = get_account()
    mock_price_feed = MockV3Aggregator.deploy(
        decimals, initial_value, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    time.sleep(1)
    print("Deployed!")


def fund_with_link(contract_address, account=None, link_token=None, amount=100000000000000000):  # 0.1 Link
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {
                             "from": account, "gas_price": 10000000})
    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    # tx = link_token_contract.transfer(
    #     contract_address, amount, {"from": account})
    tx.wait(1)
    print("Funded contract")
    tx.wait(1)
    return tx
