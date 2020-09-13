# DeFiBot-Evolution
Based on the DeFiBOT created for the Ardor Hackathon in 2020, this adds more functionalities.

This bot allows users on twitter to create and send to other twitter users the DeFi (or any other asset) on the Ardor blockchain.
For the twitter users it's completely invisible what happens in the background. The twitter users just send to other users and the bot takes care of transferring the asset to the ardor account associated to the destination twitter account. If the account is not created, it will be created in the moment the send action is triggered.
Here the possible actions:

#DeFiMAGIC CREATE to create a new account
#DeFiMAGIC DETAILS to know more about your account.
#DeFiMAGIC MAGIC to get Free DeFi tokens.
#DeFiMAGIC SEND <amount> twitter account to send DeFi to another user.
#DeFiMAGIC DEPOSIT <amount> to deposit DeFi at a 5% interest rate.
#DeFiMAGIC WITHDRAW <amount> to withdraw your deposited DeFi.
#DeFiMAGIC BORROW <amount> to borrow some DeFi at 5% interest rate. Max 10 times the value of DeFi owned.
#DeFiMAGIC CLOSEDEBT <amount> to pay back your debt.
  
To get started, a couple of actions have to be performed manually beforehand.

1) a new SEED has to be created on the Ardor platform. The account with ID0 is the one that needs to be used by the bot for holding the assets and distributing. The IDs from 1 on, are the ones assigned to the twitter users. The BIP32 path is the one used one the Ardor testnet, this can be of course modified to match the Ardor livenet or any other.
2) a mySql database has to be running on the same node where the bot is running. The database needs to contain a table defined in the following way:
#columns:
twitter -> varchar(50)
passphrase -> int(11)
ardor -> varchar(30)
magic -> varchar(2)
(this can be better defined)
3) an Ardor full needs to be running on the same server with open API
4) the Interest payment/withdrawal python script needs to be set in crontab to run once a day 
