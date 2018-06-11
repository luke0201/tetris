import time
from web3 import Web3, HTTPProvider
from solc import compile_source

# Code
contract_source_code = '''
contract RockScissorPaper {
    uint public amountRaised;
    address[] public MemberAddresses;
    uint32[] public MemberData;

    function RockScissorPaper() public {
        amountRaised = 0;
    }

    /**
     * Gather betting money and save player's informations(address, data)
     */
    function participatingInGame(uint32 _data) public payable{
        require(0<=_data && _data<=3);
        require(amountRaised <= amountRaised + msg.value);

        amountRaised += msg.value;
        MemberAddresses.push(msg.sender);
        MemberData.push(_data);
    }

    /**
     * Gamer start
     */
    function gameStart() public {
        uint32[] memory RSP = new uint32[](3);  // RSP[0,1,2]: number of rocks, scissors, papers 
        uint32[] memory WinnerIndexs = new uint32[](MemberAddresses.length);
        uint32 i;
        uint32 j;
        uint32 NumberOfWinners = 0;

        // initialize RSP array
        RSP[0] = 0;
        RSP[1] = 0;
        RSP[2] = 0;


        for(i = 0; i < MemberData.length; i++) {
            // RSP[MemberData[i]]++;
            if(MemberData[i]==0x00) {
                require(RSP[0]<=RSP[0]+1);
                RSP[0]++;
            }
            else if(MemberData[i]==0x01) {
                require(RSP[1]<=RSP[1]+1);
                RSP[1]++;
            }
            else if(MemberData[i]==0x02) {
                require(RSP[2]<=RSP[2]+1);
                RSP[2]++;
            }
        }
        for(i = 0; i < 3; i++) {
            if(RSP[i]==0) {
                // i+2 is winner
                if(RSP[(i+2)%3]!=0 && RSP[(i+1)%3]!=0) {
                    for(j = 0; j < MemberAddresses.length; j++) {
                        if(MemberData[j] == (i+2)%3) {
                            require(NumberOfWinners <= NumberOfWinners+1);
                            WinnerIndexs[NumberOfWinners]=j;
                            NumberOfWinners++;
                        }
                    }
                }
            }
        }

        uint reward;
        if(NumberOfWinners!=0) {
            reward = amountRaised/NumberOfWinners;
            for(i = 0; i < NumberOfWinners; i++) {
                MemberAddresses[WinnerIndexs[i]].transfer(amountRaised/NumberOfWinners);
            }

        }
        else {  // there is no winner
            for(i = 0; i < MemberAddresses.length; i++)
                MemberAddresses[i].transfer(amountRaised/MemberAddresses.length);
        }
    
        amountRaised = 0;
        delete WinnerIndexs;
        delete MemberAddresses;
        delete MemberData;
    }
}
'''

# Web3 setting
rpc_url = "http://localhost:8123"
w3 = Web3(HTTPProvider(rpc_url))
w3.personal.unlockAccount(w3.eth.accounts[0], "heiler", 0)	# address, password, ?

# Compile
compiled_sol = compile_source(contract_source_code)
contract_interface = compiled_sol['<stdin>:RockScissorPaper']

contract = w3.eth.contract(abi=contract_interface['abi'],
                           bytecode=contract_interface['bin'],
                           bytecode_runtime=contract_interface['bin-runtime'])

# Deploy
tx_hash = contract.deploy(transaction={'from': w3.eth.accounts[0]})

print("tx_hash: {}".format(tx_hash))
print("Finish deploying")

# Mining to write smart contract code to the block
w3.miner.start(1)
time.sleep(8)
w3.miner.stop()