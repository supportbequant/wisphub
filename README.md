# wisphub
Simple synchronization script between BQN and a Wisphub billing

## Installation

The script requires python 3.10 or later with requests package

### In Arch Linux:
`$ sudo pacman -S python3`
`$ sudo pip3 install requests`

### In Windows:
1. In elevated (administration) shell:
`> winget install python`
2. In normal shell:
`> pip install requests`

#### In Mac OS:
1. Download package for Mac from python official site:
https://www.python.org/downloads/macos/
2. Install package (enter Administrator password when requested)
3. In command shell:
`$ pip3 install requests`

## Setup

Create an API toekn in Wisphub billing
Enable REST API in BQN

## Running the script

Every time a synchronization is needded:

`python3 ./wisphub-bqn-sync.py -b <bqn-ip> <bqn-rest-user> <bqn-rest-password> <wisphub-api-token>`

The first time the script is run and everytime there are changes in policy limits, go to BQN Status->Radius/REST/Billing->Policies, look for policies of type "undefined" and click in their names to configure the speed limits in the BQN rate policy

## Known limitations

- Policy speed limits cannot be obtained from Wisphub. They must be configured in the BQN.
- Multiple IP addresses in same client are not supported.
- The first time it may take minutes to run. Following executions will send to BQN only client changes and will be quicker.
- If the synchronization fails, no retry is attempted (must be done externally).
- No scheduling of script execution (must be done externally).

## Relation of BQN entities to Wisphub schema

- BQN Rate policies are identified by Wisphub "plan_internet"->"nombre", with spaces replaced by undescores.
- BQN subscribers are identified by "nombre" in Wisphub.
- Clients in "estado" == "Suspendido" have their traffic blocked by BQN (Wisphub_block policy).
