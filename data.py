
RPC_URL = "https://ethereum-sepolia-rpc.publicnode.com"
SEPOLIA_CHAIN_ID = 11155111

USDC_ADDRESS = '0xef84994ef411c4981328ffce5fda41cd3803fae4'
R2USD_ADDRESS = '0x20c54c5f742f123abb49a982bfe0af47edb38756'
SR2USD_ADDRESS = '0xbd6b25c4132f09369c354bee0f7be777d7d434fa'
USDC_TO_R2USD_CONTRACT = '0x20c54c5f742f123abb49a982bfe0af47edb38756'
R2USD_TO_USDC_CONTRACT = '0x07abd582df3d3472aa687a0489729f9f0424b1e3'
STAKE_R2USD_CONTRACT = '0xbd6b25c4132f09369c354bee0f7be777d7d434fa'


USDC_TO_R2USD_METHOD_ID = '0x095e7a95'
R2USD_TO_USDC_METHOD_ID = '0x3df02124'
STAKE_R2USD_METHOD_ID = '0x1a5f0f00'


ERC20_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [
            {"name": "", "type": "bool"}
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {"name": "owner", "type": "address"},
            {"name": "spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [
            {"name": "", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {"name": "account", "type": "address"}
        ],
        "name": "balanceOf",
        "outputs": [
            {"name": "", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [
            {"name": "", "type": "uint8"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]



SWAP_ABI = [
    'function swap(uint256,uint256,uint256) external returns (uint256)'
]