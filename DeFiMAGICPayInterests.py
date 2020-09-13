import json # The API returns JSON formatted text
import time
import requests
import math
import mysql.connector

#This python script has to be manually scheduled in cron to run once a day

mydb = mysql.connector.connect(
  host="localhost",
  user="dbuser",
  password="dbpassword",
  database="dbname"
)

seed = "yourSEEDnotPASSPHRASE"
#Assets IDs mentioned below need to be changed with your own assets
#DeFi main asset
assetid = 12281945935996100528
#Debt asset
adefiid = 3400723260910698384
#Bad Boy asset
bdefiid = 1238452647999617751
#Deposit asset
cdefiid = 17984266549343583758

#Start Account Property Bundler
datain = 'http://localhost:27876/nxt?requestType=deriveAccountFromSeed&mnemonic='+str(seed)+'&bip32Path=m%2F44%27%2F16754%27%2F0%27%2F1%27%2F0'
datain = datain.replace(" ", "%20")
#print(datain)
result = requests.post(datain)
jsondata = json.loads(result.text) 
#print(result.text)
#print(jsondata)
RSaddress0 = jsondata['accountRS']                             
privatekey0 = jsondata['privateKey']
publickey0 = jsondata['publicKey']
#Get users with a debt
datain = 'http://localhost:27876/nxt?requestType=getAssetAccounts&asset='+str(adefiid)
datain = datain.replace(" ", "%20")
print(datain)
result = requests.post(datain)
debtusers = json.loads(result.text) 
#print(result.text)
#print(jsondata)
#Get users with a deposit
datain = 'http://localhost:27876/nxt?requestType=getAssetAccounts&asset='+str(cdefiid)
datain = datain.replace(" ", "%20")
print(datain)
result = requests.post(datain)
creditusers = json.loads(result.text) 
#print(result.text)
#print(jsondata)

for user in creditusers['accountAssets']:
    if user['accountRS'] != RSaddress0:
        positiveint = math.floor(int(user['quantityQNT'])/20/365)
        print(user['quantityQNT'])
        print('User will receive interest for: '+ str(positiveint))
        datain = 'http://localhost:27876/nxt?requestType=transferAsset&privateKey='+str(privatekey0)+'&chain=ignis&asset='+str(assetid)+'&recipient='+str(user['accountRS'])+'&quantityQNT='+str(positiveint)+'&feeNQT=0&deadline=60'
                          
        datain = datain.replace(" ", "%20")
        print(datain)
        result = requests.post(datain)
        jsondata = json.loads(result.text) 
        #print(result.text)
        print(jsondata)

for user in debtusers['accountAssets']:
    if user['accountRS'] != RSaddress0:
        useraccount = user['accountRS']
        negativeint = math.ceil(int(user['quantityQNT'])/20/365)
        print(user['quantityQNT'])
        print(negativeint)
        mycursor = mydb.cursor()
        mycursor.execute("SELECT passphrase FROM accounts where ardor='{}'".format(useraccount))
        myresult = mycursor.fetchall()
        userid = myresult[0][0]
        print(userid)
        #derive user account details
        datain = 'http://localhost:27876/nxt?requestType=deriveAccountFromSeed&mnemonic='+str(seed)+'&bip32Path=m%2F44%27%2F16754%27%2F0%27%2F1%27%2F'+str(userid)
        datain = datain.replace(" ", "%20")
        #print(datain)
        result = requests.post(datain)
        jsondata = json.loads(result.text) 
        #print(result.text)
        #print(jsondata)
        RSaddress = jsondata['accountRS']                             
        privatekey = jsondata['privateKey']
        publickey = jsondata['publicKey']
        try:
            datain = 'http://localhost:27876/nxt?requestType=getAccountAssets&account='+str(RSaddress)+'&asset='+str(assetid)
            datain = datain.replace(" ", "%20")
            print(datain)
            result = requests.post(datain)
            jsondata = json.loads(result.text) 
            #print(result.text)
            print('Get DeFi amount')
            print(jsondata)
            AssetOwned = 0
        except Exception as error:
            print(error)
        else:
            if 'quantityQNT' in jsondata:
              AssetOwned = jsondata['quantityQNT']
            print("Account has "+str(AssetOwned)+" DeFi")
        #Get previous pending payments
        try:
            datain = 'http://localhost:27876/nxt?requestType=getAccountAssets&account='+str(RSaddress)+'&asset='+str(bdefiid)
            datain = datain.replace(" ", "%20")
            print(datain)
            result = requests.post(datain)
            jsondata = json.loads(result.text) 
            #print(result.text)
            print('Get DeFiB amount')
            print(jsondata)
            BAssetOwned = 0
        except Exception as error:
            print(error)
        else:
            if 'quantityQNT' in jsondata:
              BAssetOwned = jsondata['quantityQNT']
            print("Account has "+str(BAssetOwned)+" DeFi pending interests to pay")
        totalnegative = negativeint+int(BAssetOwned)
        print('Negative interest to pay'+str(totalnegative))
        
        if int(AssetOwned) >= totalnegative:
            datain = 'http://localhost:27876/nxt?requestType=transferAsset&privateKey='+str(privatekey)+'&chain=ignis&asset='+str(assetid)+'&recipient='+str(RSaddress0)+'&quantityQNT='+str(totalnegative)+'&feeNQT=0&deadline=60'                 
            datain = datain.replace(" ", "%20")
            print(datain)
            result = requests.post(datain)
            jsondata = json.loads(result.text) 
            #print(result.text)
            print('Paying debts')
            print(jsondata)
        else:
            #Get height
            datain = 'http://localhost:27876/nxt?requestType=getBlockchainStatus'
            datain = datain.replace(" ", "%20")
            print(datain)
            result = requests.post(datain)
            jsondata = json.loads(result.text) 
            #print(result.text)
            print(jsondata)
            print("transfer asset C transaction")
            height = jsondata['numberOfBlocks']
            #transfer bdefi asset
            datain = 'http://localhost:27876/nxt?requestType=transferAsset&phased=true&phasingVotingModel=0&phasingQuorum=1&phasingWhitelisted='+str(RSaddress0)+'&phasingFinishHeight='+str(int(height)+60)+'&privateKey='+str(privatekey0)+'&chain=ignis&asset='+str(bdefiid)+'&recipient='+str(RSaddress)+'&quantityQNT='+str(negativeint)+'&feeNQT=0&deadline=60'                 
            datain = datain.replace(" ", "%20")
            print(datain)
            result = requests.post(datain)
            jsondata = json.loads(result.text) 
            #print(result.text)
            print('Adding DeFiB to user debt '+str(negativeint))
            print(jsondata)
            transactionid = jsondata['fullHash']
                          
            notconfirmed = True
            while notconfirmed:
              time.sleep(1)
              datain = 'http://localhost:27876/nxt?requestType=getTransaction&chain=ignis&fullHash='+str(transactionid)
              datain = datain.replace(" ", "%20")
              print(datain)
              result = requests.post(datain)
              jsondata = json.loads(result.text) 
              #print(result.text)
              print(jsondata)
              print("check confirmations")
              confirmations = 0
              if 'confirmations' in jsondata:
                confirmations = jsondata['confirmations']
              if confirmations>0:
                notconfirmed = False
            
            #Approve Transaction defib
            datain = 'http://localhost:27876/nxt?requestType=approveTransaction&privateKey='+str(privatekey7)+'&phasedTransaction=2:'+str(transactionid)+'&chain=ignis&feeNQT=0&deadline=60'
            datain = datain.replace(" ", "%20")
            print(datain)
            result = requests.post(datain)
            jsondata = json.loads(result.text) 
            #print(result.text)
            print(jsondata)
            print("transfer asset C approval transaction")