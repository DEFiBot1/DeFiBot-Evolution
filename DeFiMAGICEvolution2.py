import tweepy
import json # The API returns JSON formatted text
import urllib.request as urllib2
import re
import requests
import random
import mysql.connector
import time

#This bot assumes that you are running an ardor node on the same machine as the bot with open API.

#You need to manually create a db in your local host where the table is defined in the following way:
#columns:
# twitter -> varchar(50)
# passphrase -> int(11)
# ardor -> varchar(30)
# magic -> varchar(2)
#The database need could be reduced or completely removed by using Ardor capabilities like a specific MS or Asset to track the magic
mydb = mysql.connector.connect(
  host="localhost",
  user="dbuser",
  password="dbpassword",
  database="dbname"
)

# Store OAuth authentication credentials - get at https://developer.twitter.com/en/apps
access_token = "xxxxxx-xxxxxxx"
access_token_secret = "xxxxxxxxxxx"
consumer_key = "xxxxxxxxxx"
consumer_secret = "xxxxxxxxxxxx"
#NOTE that your account ID0 is the one that will need to have enough Ardor, hold enough assets listed below.
#when you create the adefi, bdefi, cdefi (NOT main asset) remember to add account control on the asset where the
#SEED ID0 account is the whitelisted one. This is needed for the debt and credit assets.
#The BIP32 path is taken from the details testnet one. This can be changed.
#Assets IDs mentioned below need to be changed with your own assets. If actions like DEPOSIT, WITHDRAW, BORROW and CLOSEDEBT are not needed
#Then adefeid, bdefiid, cdefiid, cdefiid can be removed and the respective parts of the code.
seed = "yourSEEDnotPASSPHRASE"
#DeFi main asset
assetid = 12281945935996100528
#Debt asset
adefiid = 3400723260910698384
#Bad Boy asset
bdefiid = 1238452647999617751
#Deposit asset
cdefiid = 17984266549343583758
#Bitswift asset
bcashid = 18124084271428561186

sentences = ["#Ardor has an inbuilt decentralized exchange?",
             "the #Ardor child-chains transactions are paid with the child-chain coin?",
             "the #SmartContracts on #Ardor are called #LightweightContracts and are programmed in Java?",
             "you can issue an #Asset like #DeadFish in 5 minutes and without technical knowledge?",
             "#Ardor has a fully functional decentralized Voting System?",
             "#Ardor has an awesome decentralized Marketplace?",
             "in #Ardor you can pay dividends to your asset holders with 1 click?",
             "assets issued on the #IGNIS chain can be traded or transferred also on the other child-chains?",
             "child-chain coins like #MPG, #Bitswift, #Ignis and #GPS can be exchanged between each-other thanks to the inbuilt Coin Exchange?",
             "on #Ardor you can add and delete shares within a few mouse clicks?",
             "on #Ardor you can sponsor transaction fees for your users, like this bot does, thanks to the Account Property Bundling",
             "that you can find everything about #Ardor account control here: https://ardordocs.jelurida.com/Account_control",
             "#Ardor is based on #NXT, the first pure #ProofOfStake #Blockchain",
             "#DeadFish is endorsed by Aliens?",
             "#DeadFish is a Parody and $Defi is its ticker?",
             "with #Ardor you can send encrypted messages to other accounts?",
             "@Bit_Swift has it’s own chain on #Ardor, and Bitswift Cash is an asset on their chain?",
             "#Triffic will have its own chain on #Ardor on sept 22?",
             "@TarascaD’s Cardgame uses an asset on $Ignis, which is built on #Ardor?"
            ]

# Pass OAuth details to tweepy's OAuth handler
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

TRACKING_KEYWORDS = ['#DeFiMAGIC HELP',
                     '#DeFiMAGIC SEND',
                     '#DeFiMAGIC DETAILS',
                     '#DeFiMAGIC MAGIC',
                     '#DeFiMAGIC CREATE',
                     '#DeFiMAGIC DEPOSIT',
                     '#DeFiMAGIC WITHDRAW',
                     '#DeFiMAGIC BORROW',
                     '#DeFiMAGIC CLOSEDEBT',
                     '#DeFiWOW HELP',
                     '#DeFiWOW SEND',
                     '#DeFiWOW DETAILS',
                     '#DeFiWOW MAGIC',
                     '#DeFiWOW CREATE',
                     '#DeFiWOW DEPOSIT',
                     '#DeFiWOW WITHDRAW',
                     '#DeFiWOW BORROW',
                     '#DeFiWOW CLOSEDEBT'
                     ]
OUTPUT_FILE = "DeFiMAGIClog.txt"
TWEETS_TO_CAPTURE = 300000000


class MyStreamListener(tweepy.StreamListener):
    """
    Twitter listener, collects streaming tweets and output to a file
    """
    def __init__(self, api=None):
        super(MyStreamListener, self).__init__()
        self.num_tweets = 0
        self.file = open(OUTPUT_FILE, "w")
    
    global cnt
    global users
    global users2
    global usermessaged
    global ardoraccounts
    global addresslenght
    
    cnt = 0
    users = []
    users2 = []
    usermessaged = []
    ardoraccounts = []
    
    #Start Account Property Bundler
    datain = 'http://localhost:27876/nxt?requestType=deriveAccountFromSeed&mnemonic='+str(seed)+'&bip32Path=m%2F44%27%2F16754%27%2F0%27%2F1%27%2F0'
    datain = datain.replace(" ", "%20")
    print(datain)
    result = requests.post(datain)
    jsondata = json.loads(result.text) 
    #print(result.text)
    print(jsondata)
    RSaddress0 = jsondata['accountRS']                             
    privatekey0 = jsondata['privateKey']
    publickey0 = jsondata['publicKey']
    datain = 'http://localhost:27876/nxt?requestType=startBundler&chain=2&minRateNQTPerFXT=0&privateKey='+str(privatekey0)+'&filter=PropertyBundler'
    datain = datain.replace(" ", "%20")
    print(datain)
    result = requests.post(datain)
    jsondata = json.loads(result.text) 
    #print(result.text)
    print(jsondata)
    
    def on_status(self, status):
        global cnt
        tweet = status._json
        #self.file.write( json.dumps(tweet) + '\n' )
        self.num_tweets += 1
        
        if self.num_tweets <= TWEETS_TO_CAPTURE:
            print(tweet);
            text = tweet['text'];
            print(text);
            words = text.split(" ")
            print(words)
            #print(words[1])
            if 'HELP' in words:
              print("Use: /n #DeFiBOT CREATE to create a new account /n #DeFiBOT SEND <twitter account> to send DeFi to another user")
              
              try:
                #api.update_status(status="Hey @"+tweet['user']['screen_name']+" message received");
                api.send_direct_message(recipient_id=tweet['user']['id'],text="Use:"+"\n\n"+"#DeFiMAGIC CREATE to create a new account"+"\n"+"#DeFiMAGIC DETAILS to know more about your account."+"\n"+"#DeFiMAGIC MAGIC to get Free DeFi tokens."+"\n"+"#DeFiMAGIC SEND <amount> twitter account to send DeFi to another user."+"\n"+"#DeFiMAGIC DEPOSIT <amount> to deposit DeFi at a 5% interest rate."+"\n"+"#DeFiMAGIC WITHDRAW <amount> to withdraw your deposited DeFi."+"\n"+"#DeFiMAGIC BORROW <amount> to borrow some DeFi at 5% interest rate. Max 10 times the value of DeFi owned."+"\n"+"#DeFiMAGIC CLOSEDEBT <amount> to pay back your debt.");
              except Exception as error:
                print(error)
                api.update_status("@"+tweet['user']['screen_name']+" Not following me??? Better do that or check your privacy settings to get my DM.", tweet['id'])
              else:
                print('Message Sent')
            elif 'CREATE' in words:
              print("We're in CREATE")
              #print(mydb)
              mycursor = mydb.cursor()
              #print("mycursor")
              userid = tweet['user']['id']
              #print(userid)
              mycursor.execute("SELECT ardor FROM accounts where twitter={}".format(userid))
              #print("execute")
              myresult = mycursor.fetchall()
              #print("fetchall")
              #myresult = mycursor.fetchone()
              print('MyResult: {}'.format(myresult))
              if not myresult:
                  mycursor = mydb.cursor()
                  mycursor.execute("SELECT COALESCE(max(passphrase), 0) FROM accounts")
                  print("Account will be created")
                  myresult = mycursor.fetchone()
                  print(myresult[0])
                  accountid=int(myresult[0])+1
                  print(accountid)
                  try:
                      datain = 'http://localhost:27876/nxt?requestType=deriveAccountFromSeed&mnemonic='+str(seed)+'&bip32Path=m%2F44%27%2F16754%27%2F0%27%2F1%27%2F'+str(accountid)
                      datain = datain.replace(" ", "%20")
                      print(datain)
                      
                      result = requests.post(datain)
                      jsondata = json.loads(result.text) 
                      #print(result.text)
                      print(jsondata)
                      RSaddress = jsondata['accountRS']
                      privatekey = jsondata['privateKey']
                      publickey = jsondata['publicKey']
                      #print(jsondata["bundlerRateNQTPerFXT"])
                      
                      datain = 'http://localhost:27876/nxt?requestType=deriveAccountFromSeed&mnemonic='+str(seed)+'&bip32Path=m%2F44%27%2F16754%27%2F0%27%2F1%27%2F0'
                      datain = datain.replace(" ", "%20")
                      print(datain)
                      result = requests.post(datain)
                      jsondata = json.loads(result.text) 
                      #print(result.text)
                      print(jsondata)
                      RSaddress0 = jsondata['accountRS']
                      privatekey0 = jsondata['privateKey']
                      publickey0 = jsondata['publicKey']
                      
                      #set account property
                      datain = 'http://localhost:27876/nxt?requestType=setAccountProperty&chain=2&recipient='+str(RSaddress)+'&property=bundling&privateKey='+str(privatekey0)+'&feeNQT=-1&feeRateNQTPerFXT=-1&deadline=60'
                      datain = datain.replace(" ", "%20")
                      print(datain)
                      result = requests.post(datain)
                      jsondata = json.loads(result.text) 
                      #print(result.text)
                      print(jsondata)
                      #rate = jsondata['bundlerRateNQTPerFXT'] * 0.01;
                      rate = round(int(jsondata['bundlerRateNQTPerFXT']) * 0.01);
                      
                      datain = 'http://localhost:27876/nxt?requestType=setAccountProperty&chain=2&recipient='+str(RSaddress)+'&property=bundling&privateKey='+str(privatekey0)+'&feeNQT='+str(rate)+'&deadline=60'
                      datain = datain.replace(" ", "%20")
                      print(datain)
                      result = requests.post(datain)
                      jsondata = json.loads(result.text) 
                      #print(result.text)
                      print(jsondata)
                      
                  except Exception as error:
                      print(error)
                  else:
                    
                      print("Your account has been created. If you want to know the details of your wallet tweet #DeFiMAGIC DETAILS")
                      #api.update_status(status="Hey @"+tweet['user']['screen_name']+" your #Ardor account has been created", in_reply_to_status_id = tweet['id'])
                      try:
                        api.send_direct_message(recipient_id=tweet['user']['id'],text="Your Ardor account is:"+"\n"+RSaddress+"\n\n"+"Your PrivateKey is:"+"\n"+privatekey+"\n\n"+"Your PublicKey is: "+publickey)
                      except Exception as error:
                        print(error)
                        api.update_status("@"+tweet['user']['screen_name']+" Not following me??? Better do that or check your privacy settings to get my DM.", tweet['id'])
                      else:
                        print('Message Sent')
                      #api.send_direct_message(recipient_id=tweet['user']['id'],text="Your Ardor account is: "+RSaddress+"\n"+"Your PrivateKey is: "+privatekey)
                      mycursor = mydb.cursor()
                      sql2="INSERT INTO accounts (twitter,passphrase,ardor,magic) VALUES ('"+str(userid)+"','"+str(accountid)+"','"+RSaddress+"','0')"
                      print(sql2)
                      #mycursor.execute(sql,val)
                      mycursor.execute(sql2)
                      print("execute")
                      mydb.commit()
                      print(mycursor.rowcount, "record inserted.")
                      
              else:
                  print("in else")
                  print(myresult[0][0])
                  addressresult = myresult[0][0]
                  api.send_direct_message(recipient_id=tweet['user']['id'],text="Your already have an Ardor account which is: "+addressresult)
                  
            elif 'DETAILS' in words:
              print("We're in DETAILS")
              mycursor = mydb.cursor()
              print("mycursor")
              userid = tweet['user']['id']
              print(userid)
              mycursor.execute("SELECT passphrase FROM accounts where twitter={}".format(userid))
              print("execute")
              myresult = mycursor.fetchall()
              print("fetchall")
              #myresult = mycursor.fetchone()
              print('MyResult: {}'.format(myresult))
              if not myresult:
                  try:
                    api.send_direct_message(recipient_id=tweet['user']['id'],text="Uhm... Your don't have an Ardor account yet, try using"+"\n"+"#DeFiMAGIC CREATE")
                  except Exception as error:
                    print(error)
                    api.update_status("@"+tweet['user']['screen_name']+" Not following me??? Better do that or check your privacy settings to get my DM.", tweet['id'])
                  else:
                    print('Message Sent')
                      
              else:
                  mycursor3 = mydb.cursor()
                  mycursor3.execute("SELECT ardor FROM accounts where twitter={}".format(userid))
                  myresult3 = mycursor3.fetchall()
                  try:
                      #print("in try")
                      datain = 'http://localhost:27876/nxt?requestType=getAccountAssets&account='+str(myresult3[0][0])+'&asset='+str(assetid)
                      datain = datain.replace(" ", "%20")
                      print(datain)
                      
                      result = requests.post(datain)
                      jsondata = json.loads(result.text) 
                      #print(result.text)
                      print(jsondata)
                      AssetOwned = 0
                      AssetOwned = jsondata['quantityQNT']
                      print(AssetOwned)
                  except Exception as error:
                      print(error)
                  else:
                      print("Account has "+str(AssetOwned)+" DeFi")
                  try:
                      #print("in try")
                      datain = 'http://localhost:27876/nxt?requestType=getAccountAssets&account='+str(myresult3[0][0])+'&asset='+str(bdefiid)
                      datain = datain.replace(" ", "%20")
                      print(datain)
                      
                      result = requests.post(datain)
                      jsondata = json.loads(result.text) 
                      #print(result.text)
                      print(jsondata)
                      BAssetOwned = 0
                      BAssetOwned = jsondata['quantityQNT']
                      print(BAssetOwned)
                  except Exception as error:
                      print(error)
                  else:
                      print("Account has "+str(BAssetOwned)+" DeFi pending interest to pay!!!")
                  try:
                      #print("in try")
                      datain = 'http://localhost:27876/nxt?requestType=getAccountAssets&account='+str(myresult3[0][0])+'&asset='+str(cdefiid)
                      datain = datain.replace(" ", "%20")
                      print(datain)
                      
                      result = requests.post(datain)
                      jsondata = json.loads(result.text) 
                      #print(result.text)
                      print(jsondata)
                      CAssetOwned = 0
                      CAssetOwned = jsondata['quantityQNT']
                      print(CAssetOwned)
                  except Exception as error:
                      print(error)
                  else:
                      print("Account has "+str(CAssetOwned)+" DeFi Deposited")
                  try:
                      #print("in try")
                      datain = 'http://localhost:27876/nxt?requestType=getAccountAssets&account='+str(myresult3[0][0])+'&asset='+str(adefiid)
                      datain = datain.replace(" ", "%20")
                      print(datain)
                      
                      result = requests.post(datain)
                      jsondata = json.loads(result.text) 
                      #print(result.text)
                      print(jsondata)
                      AAssetOwned = 0
                      AAssetOwned = jsondata['quantityQNT']
                      print(AAssetOwned)
                  except Exception as error:
                      print(error)
                  else:
                      print("Account has "+str(AAssetOwned)+" DeFi Borrowed")
                
                  idresult = myresult[0][0]
                  try:
                      datain = 'http://localhost:27876/nxt?requestType=deriveAccountFromSeed&mnemonic='+str(seed)+'&bip32Path=m%2F44%27%2F16754%27%2F0%27%2F1%27%2F'+str(idresult)
                      datain = datain.replace(" ", "%20")
                      print(datain)
                      
                      result = requests.post(datain)
                      jsondata = json.loads(result.text) 
                      #print(result.text)
                      print(jsondata)
                      RSaddress = jsondata['accountRS']
                      privatekey = jsondata['privateKey']
                      publickey = jsondata['publicKey']
                      #print(jsondata["bundlerRateNQTPerFXT"])
                  except Exception as error:
                      print(error)
                  else:
                      print("Account details sent")
                      #api.update_status(status="Hey @"+tweet['user']['screen_name']+" your #Ardor account has been created", in_reply_to_status_id = tweet['id'])
                      try:
                        api.send_direct_message(recipient_id=tweet['user']['id'],text="Your Ardor account is: "+"\n"+RSaddress+"\n\n"+"Your PrivateKey is:"+"\n"+privatekey+"\n\n"+"Your PublicKey is:"+"\n"+publickey+"\n\n"+"You own:"+"\n"+str(AssetOwned)+" DeFi"+"\n\n"+"You deposited:"+"\n"+str(CAssetOwned)+" DeFi"+"\n\n"+"You borrowed:"+"\n"+str(AAssetOwned)+" DeFi"+"\n\n"+"You owe DeadFish Bank:"+"\n"+str(BAssetOwned)+" DeFi interests on your debt."+"\n\n"+"Check what's happening on your account by visiting https://ardor.jelurida.com/ or installing an Ardor wallet")
                      except Exception as error:
                        print(error)
                        api.update_status("@"+tweet['user']['screen_name']+" Not following me??? Better do that or check your privacy settings to get my DM.", tweet['id'])
                      else:
                        print('Message Sent to'+tweet['user']['id'])
             
            
            
            elif 'MAGIC' in words:
              print("We're in MAGIC")
              mycursor = mydb.cursor()
              #print("mycursor")
              userid = tweet['user']['id']
              #print(userid)
              mycursor.execute("SELECT passphrase FROM accounts where twitter={}".format(userid))
              #print("execute")
              myresult = mycursor.fetchall()
              #print("fetchall")
              #myresult = mycursor.fetchone()
              print('MyResult: {}'.format(myresult))
              if not myresult:
                  try:
                    api.send_direct_message(recipient_id=tweet['user']['id'],text="Uhm... Your don't have an Ardor account yet, try using"+"\n"+"#DeFiMAGIC CREATE")
                  except Exception as error:
                    print(error)
                    api.update_status("@"+tweet['user']['screen_name']+" Not following me??? Better do that or check your privacy settings to get my DM", tweet['id'])
                  else:
                    print('Message Sent')
                      
              else:
                  mycursor3 = mydb.cursor()
                  mycursor3.execute("SELECT ardor FROM accounts where twitter={}".format(userid))
                  myresult3 = mycursor3.fetchall()
                  mycursor6 = mydb.cursor()
                  mycursor6.execute("SELECT magic FROM accounts where twitter={}".format(userid))
                  myresult6 = mycursor6.fetchall()
                  mycursor7 = mydb.cursor()
                  mycursor7.execute("SELECT passphrase FROM accounts where twitter={}".format(userid))
                  myresult7 = mycursor7.fetchall()
                  mycursorc = mydb.cursor()
                  mycursorc.execute("SELECT sum(magic) FROM accounts")
                  myresultc = mycursorc.fetchall()
                  magics = round(myresultc[0][0])
                  print(magics)
                  receiveraddress = myresult3[0][0]
                  if magics > 25600:
                      amount = 10000
                      amountbcash = 0
                  if magics <= 25600:
                      amount = 390625
                      amountbcash = 0
                  if magics <= 12800:
                      amount = 781250
                      amountbcash = 0
                  if magics <= 6400:
                      amount = 1562500
                      amountbcash = 0
                  if magics <= 3200:
                      amount = 3125000
                      amountbcash = 0
                  if magics <= 1600:
                      amount = 6250000
                      amountbcash = 0
                  if magics <= 800:
                      amount = 12500000
                      amountbcash = 0
                  if magics <= 400:
                      amount = 25000000
                      amountbcash = 0
                  if magics <= 200:
                      amount = 50000000
                      amountbcash = 250
                  if magics <= 100:
                      amount = 100000000
                      amountbcash = 500
                  if int(myresult6[0][0]) != 1:
                    try:
                        #Get info of sender
                        print("in try magic")
                        datain = 'http://localhost:27876/nxt?requestType=deriveAccountFromSeed&mnemonic='+str(seed)+'&bip32Path=m%2F44%27%2F16754%27%2F0%27%2F1%27%2F0'
                        datain = datain.replace(" ", "%20")
                        print(datain)
                        result = requests.post(datain)
                        jsondata = json.loads(result.text) 
                        #print(result.text)
                        #print(jsondata)
                        RSaddress0 = jsondata['accountRS']
                        privatekey0 = jsondata['privateKey']
                        publickey0 = jsondata['publicKey']
                        
                        #Get info of receiver
                        
                        datain = 'http://localhost:27876/nxt?requestType=deriveAccountFromSeed&mnemonic='+str(seed)+'&bip32Path=m%2F44%27%2F16754%27%2F0%27%2F1%27%2F'+str(myresult7[0][0])
                        datain = datain.replace(" ", "%20")
                        print(datain)
                        result = requests.post(datain)
                        jsondata = json.loads(result.text) 
                        #print(result.text)
                        #print(jsondata)
                        #RSaddress7 = jsondata['accountRS']
                        #privatekey7 = jsondata['privateKey']
                        publickey7 = jsondata['publicKey']
                        
                        datain = 'http://localhost:27876/nxt?requestType=transferAsset&privateKey='+str(privatekey0)+'&chain=ignis&asset='+str(assetid)+'&recipient='+str(receiveraddress)+'&recipientPublicKey='+str(publickey7)+'&quantityQNT='+str(amount)+'&feeNQT=0&deadline=60'
                          
                        datain = datain.replace(" ", "%20")
                        print(datain)
                        result = requests.post(datain)
                        jsondata = json.loads(result.text) 
                        #print(result.text)
                        print(jsondata)
                        
                        if amountbcash>0:
                          datain = 'http://localhost:27876/nxt?requestType=transferAsset&privateKey='+str(privatekey0)+'&chain=ignis&asset='+str(bcashid)+'&recipient='+str(receiveraddress)+'&recipientPublicKey='+str(publickey7)+'&quantityQNT='+str(amountbcash*1000000)+'&feeNQT=0&deadline=60'        
                          datain = datain.replace(" ", "%20")
                          print(datain)
                          result = requests.post(datain)
                          jsondata = json.loads(result.text) 
                          #print(result.text)
                          print(jsondata)
                        
                        
                    except Exception as error:
                        print(error)
                    
                    else:
                        print("MAGIC sent")
                        #api.update_status(status="Hey @"+tweet['user']['screen_name']+" your #Ardor account has been created", in_reply_to_status_id = tweet['id'])
                        mycursor = mydb.cursor()
                        
                        sql2="UPDATE accounts SET magic = "+str(1)+" where ardor='"+str(receiveraddress)+"'"
                        print(sql2)
                        #mycursor.execute(sql,val)
                        mycursor.execute(sql2)
                        print("execute")
                        mydb.commit()
                        print(mycursor.rowcount, "record updated.")
                        message="MAGIC! You received "+str(amount)+" DeFi"
                        if amountbcash>0:
                          message=message+" and "+str(amountbcash)+"Bitswift CASH!!!"
                        print(message)
                        try:
                          api.send_direct_message(recipient_id=tweet['user']['id'],text=message)
                        except Exception as error:
                          print(error)
                          api.update_status("@"+tweet['user']['screen_name']+" Not following me??? Better do that or check your privacy settings to get my DM", tweet['id'])
                        else:
                          api.update_status("@"+tweet['user']['screen_name']+" You are MAGIC receiver number "+str(magics+1)+"!", tweet['id'])
                          print('Message Sent') 
                  else:
                    print("user has already MAGIC")
                    print(magics)
                    try:
                      api.send_direct_message(recipient_id=tweet['user']['id'],text="Hey hey hey... You already got MAGIC!")
                    except Exception as error:
                      print(error)
                      api.update_status("@"+tweet['user']['screen_name']+" Not following me??? Better do that or check your privacy settings to get my DM", tweet['id'])
                    else:
                      print('Message MAGIC Sent to user') 
                
            elif 'SEND' in words:
              print("We're in SEND")
              
              userid = tweet['user']['id']
              receiver = tweet['entities']['user_mentions'][-1]['id']
              receivername = tweet['entities']['user_mentions'][-1]['name']
              print(receiver)
              print(userid)
              mycursor = mydb.cursor()
              mycursor.execute("SELECT passphrase FROM accounts where twitter={}".format(userid))
              myresult = mycursor.fetchall()
              mycursor2 = mydb.cursor()
              mycursor2.execute("SELECT passphrase FROM accounts where twitter={}".format(receiver))
              myresult2 = mycursor2.fetchall()
              mycursor3 = mydb.cursor()
              mycursor3.execute("SELECT ardor FROM accounts where twitter={}".format(userid))
              myresult3 = mycursor3.fetchall()
              mycursor5 = mydb.cursor()
              mycursor5.execute("SELECT ardor FROM accounts where twitter={}".format(receiver))
              myresult5 = mycursor5.fetchall()
              #myresult = mycursor.fetchone()
              print('MyResult: {}'.format(myresult))
              print('MyResult2: {}'.format(myresult2))
              print('MyResult3: {}'.format(myresult3))
              print('MyResult5: {}'.format(myresult5))
              
              #accountid=myresult[0][0]
              try:
                receiveraddress = myresult5[0][0]
              except Exception as error:
                print(error)
              else:
                print("ok storing variable")
              """
              try:
                accountid = myresult[0][0]
              except Exception as error:
                print(error)
              else:
                print("ok storing variable")
              """
              #print(receiveraddress)
              if not myresult:
                  try:
                    api.send_direct_message(recipient_id=tweet['user']['id'],text="Your don't have an Ardor account yet, try using"+"\n\n"+"#DeFiMAGIC CREATE")
                  except Exception as error:
                    print(error)
                    api.update_status("@"+tweet['user']['screen_name']+" Not following me??? Better do that or check your privacy settings to get my DM", tweet['id'])
                  else:
                    print('Message Sent to user')
                      
              else:
                  accountid=myresult[0][0]
                  #check amount of Defi owned by sender
                  print("in else when user has an account")
                  try:
                      print("in try")
                      datain = 'http://localhost:27876/nxt?requestType=getAccountAssets&account='+str(myresult3[0][0])+'&asset='+str(assetid)
                      datain = datain.replace(" ", "%20")
                      print(datain)
                      
                      result = requests.post(datain)
                      jsondata = json.loads(result.text) 
                      #print(result.text)
                      print(jsondata)
                      AssetOwned = 0
                  except Exception as error:
                      print(error)
                  else:
                      if 'quantityQNT' in jsondata:
                        AssetOwned = jsondata['quantityQNT']
                      print("Account has "+str(AssetOwned)+" DeFi")
                  #Check unpaid debts
                  try:
                      print("in try")
                      datain = 'http://localhost:27876/nxt?requestType=getAccountAssets&account='+str(myresult3[0][0])+'&asset='+str(bdefiid)
                      datain = datain.replace(" ", "%20")
                      print(datain)
                      
                      bresult = requests.post(datain)
                      bjsondata = json.loads(bresult.text) 
                      #print(result.text)
                      print(bjsondata)
                      BAssetOwned = 0
                  except Exception as error:
                      print(error)
                  else:
                      if 'quantityQNT' in bjsondata:
                        BAssetOwned = bjsondata['quantityQNT']
                      print("Account has "+str(AssetOwned)+" DeFi")
                  #check if receiver has an account
                  if not myresult2:
                    #Create account for receiver
                    mycursor4 = mydb.cursor()
                    mycursor4.execute("SELECT COALESCE(max(passphrase), 0) FROM accounts")
                    print("Receiver Account will be created")
                    
                    myresult4 = mycursor4.fetchone()
                    print(myresult4[0])
                    
                    accountidreceiver=int(myresult4[0])+1
                    print(accountid)
                    try:
                        datain = 'http://localhost:27876/nxt?requestType=deriveAccountFromSeed&mnemonic='+str(seed)+'&bip32Path=m%2F44%27%2F16754%27%2F0%27%2F1%27%2F'+str(accountidreceiver)
                        datain = datain.replace(" ", "%20")
                        print(datain)
                        
                        result = requests.post(datain)
                        jsondata = json.loads(result.text) 
                        #print(result.text)
                        print(jsondata)
                        RSaddress = jsondata['accountRS']
                        privatekey = jsondata['privateKey']
                        publickey = jsondata['publicKey']
                        receiveraddress = RSaddress
                        #print(jsondata["bundlerRateNQTPerFXT"])
                        
                        datain = 'http://localhost:27876/nxt?requestType=deriveAccountFromSeed&mnemonic='+str(seed)+'&bip32Path=m%2F44%27%2F16754%27%2F0%27%2F1%27%2F0'
                        datain = datain.replace(" ", "%20")
                        print(datain)
                        result = requests.post(datain)
                        jsondata = json.loads(result.text) 
                        #print(result.text)
                        print(jsondata)
                        RSaddress0 = jsondata['accountRS']
                        privatekey0 = jsondata['privateKey']
                        publickey0 = jsondata['publicKey']
                        
                        #set account property
                        datain = 'http://localhost:27876/nxt?requestType=setAccountProperty&chain=2&recipient='+str(RSaddress)+'&property=bundling&privateKey='+str(privatekey0)+'&feeNQT=0&deadline=60'
                        datain = datain.replace(" ", "%20")
                        print(datain)
                        result = requests.post(datain)
                        jsondata = json.loads(result.text) 
                        #print(result.text)
                        print(jsondata)
                        
                    except Exception as error:
                        print(error)
                    else:
                        print("Your account has been created. If you want to know the details of your wallet tweet #DeFiMAGIC DETAILS")
                        try:
                          print("in try")
                          api.send_direct_message(recipient_id=receiver,text="Your Ardor account is:"+"\n"+RSaddress+"\n\n"+"Your PrivateKey is:"+"\n"+privatekey+"\n\n"+"To know more about your account tweet: #DeFiMAGIC DETAILS")
                        except Exception as error:
                          print(error)
                          #api.update_status("@"+tweet['user']['screen_name']+" Follow me or check your privacy settings to get my DM.", tweet['id'])
                        else:
                          print('Message Sent to receiver')
                        mycursor = mydb.cursor()
                        
                        sql2="INSERT INTO accounts (twitter,passphrase,ardor,magic) VALUES ('"+str(receiver)+"','"+str(accountidreceiver)+"','"+RSaddress+"','0')"
                        print(sql2)
                        #mycursor.execute(sql,val)
                        mycursor.execute(sql2)
                        print("execute")
                        mydb.commit()
                        print(mycursor.rowcount, "record inserted.")
                  
                  
                  #Transfer
                  print("transferiing asset")
                  #print(words[2])
                  #amounttosend = round(float(words[2]))
                  amountid = words.index('SEND')
                  print(words[amountid+1])
                  amounttosend = round(float(words[amountid+1]))
                  print(amounttosend)
                  print(AssetOwned)
                  if int(BAssetOwned) > 0:
                    print("the guy has unpaid debts")
                    api.update_status("@"+tweet['user']['screen_name']+" Yo! You have to pay your pending debts first to #DeadFishBank. Booo...", tweet['id'])
                    try:
                      api.send_direct_message(recipient_id=tweet['user']['id'],text="Make sure you have "+str(BAssetOwned)+" DeFi in your account so you close your debt and you account will be unlocked within 24 hours.")
                      #api.send_direct_message(recipient_id=receiver,text="Wow! Your friend "+tweet['user']['name']+" sent you "+str(amounttosend)+" DeFi")
                    except Exception as error:
                      print(error)
                      #api.update_status("@"+tweet['user']['screen_name']+" Not following me??? Better do that or check your privacy settings to get my DM.", tweet['id'])
                    else:
                      print('Messages sent')
                  elif int(AssetOwned) > int(amounttosend):
                    print("enough funds")
                    #idresult = myresult[0][0]
                    try:
                        #find privatekey of sender
                        datain = 'http://localhost:27876/nxt?requestType=deriveAccountFromSeed&mnemonic='+str(seed)+'&bip32Path=m%2F44%27%2F16754%27%2F0%27%2F1%27%2F'+str(accountid)
                        datain = datain.replace(" ", "%20")
                        print(datain)
                        
                        result = requests.post(datain)
                        jsondata = json.loads(result.text) 
                        #print(result.text)
                        print(jsondata)
                        RSaddress = jsondata['accountRS']
                        privatekey = jsondata['privateKey']
                        publickey = jsondata['publicKey']
                        #print(jsondata["bundlerRateNQTPerFXT"])
                    except Exception as error:
                        print(error)
                    else:
                        print("Sending DEFI")
                        #api.update_status(status="Hey @"+tweet['user']['screen_name']+" your #Ardor account has been created", in_reply_to_status_id = tweet['id'])
                        #Try to transfer asset
                        mycursor = mydb.cursor()
                        
                        #sql2="INSERT INTO accounts (twitter,passphrase,ardor) VALUES ('"+str(userid)+"','"+str(accountid)+"','"+RSaddress+"')"
                        #print(sql2)
                        
                        #mycursor.execute(sql2)
                        #print("execute")
                        #mydb.commit()
                        #print(mycursor.rowcount, "record inserted.")
                        
                        mycursor7 = mydb.cursor()
                        mycursor7.execute("SELECT passphrase FROM accounts where twitter={}".format(receiver))
                        myresult7 = mycursor7.fetchall()
                        
                        #Get receiver details
                        datain = 'http://localhost:27876/nxt?requestType=deriveAccountFromSeed&mnemonic='+str(seed)+'&bip32Path=m%2F44%27%2F16754%27%2F0%27%2F1%27%2F'+str(myresult7[0][0])
                        datain = datain.replace(" ", "%20")
                        print(datain)
                        result = requests.post(datain)
                        jsondata = json.loads(result.text) 
                        #print(result.text)
                        #print(jsondata)
                        #RSaddress7 = jsondata['accountRS']
                        #privatekey7 = jsondata['privateKey']
                        publickey7 = jsondata['publicKey']
                        
                        try:
                          datain = 'http://localhost:27876/nxt?requestType=transferAsset&privateKey='+str(privatekey)+'&chain=ignis&asset='+str(assetid)+'&recipient='+str(receiveraddress)+'&recipientPublicKey='+str(publickey7)+'&quantityQNT='+str(amounttosend)+'&feeNQT=0&deadline=60'
                          datain = datain.replace(" ", "%20")
                          print(datain)
                          result = requests.post(datain)
                          jsondata = json.loads(result.text) 
                          #print(result.text)
                          print(jsondata)
                          print("transfer asset transaction")
                        except Exception as error:
                          print(error)
                        else:
                          print("send messages if transaction successfull")
                          api.update_status("@"+tweet['user']['screen_name']+" Very generous! Did you know that "+random.choice(sentences)+" ", tweet['id'])
                          try:
                            api.send_direct_message(recipient_id=tweet['user']['id'],text="Nice! You sent "+str(amounttosend)+" DeFi to "+receivername+". That's a nice gesture")
                            api.send_direct_message(recipient_id=receiver,text="Wow! Your friend "+tweet['user']['name']+" sent you "+str(amounttosend)+" DeFi"+"\n\n"+"Check what's happening on your account by visiting https://ardor.jelurida.com/ or installing an Ardor wallet")
                          except Exception as error:
                            print(error)
                            #api.update_status("@"+tweet['user']['screen_name']+" Not following me??? Better do that or check your privacy settings to get my DM.", tweet['id'])
                          else:
                            print('Messages sent')
                  else:
                    try:
                      api.send_direct_message(recipient_id=tweet['user']['id'],text="Your don't have enough DeFi my friend... shame! Did you try with some MAGIC?")
                    except Exception as error:
                      print(error)
                      api.update_status("@"+tweet['user']['screen_name']+" Not following me??? Better do that or check your privacy settings to get my DM", tweet['id'])
                    else:
                      print('Message about not enough DeFi Sent to'+tweet['user']['id'])

            elif 'DEPOSIT' in words:
              print("We're in DEPOSIT")     
              userid = tweet['user']['id']
            
              print(userid)
              mycursor = mydb.cursor()
              mycursor.execute("SELECT passphrase FROM accounts where twitter={}".format(userid))
              myresult = mycursor.fetchall()
              
              mycursor3 = mydb.cursor()
              mycursor3.execute("SELECT ardor FROM accounts where twitter={}".format(userid))
              myresult3 = mycursor3.fetchall()
              
              print('MyResult: {}'.format(myresult))
              
              print('MyResult3: {}'.format(myresult3))
              
              
              #accountid=myresult[0][0]
              try:
                senderaddress = myresult3[0][0]
              except Exception as error:
                print(error)
              else:
                print("ok storing variable")
              
              
              if not myresult:
                  try:
                    api.send_direct_message(recipient_id=tweet['user']['id'],text="Your don't have an Ardor account yet, try using"+"\n\n"+"#DeFiMAGIC CREATE")
                  except Exception as error:
                    print(error)
                    api.update_status("@"+tweet['user']['screen_name']+" Not following me??? Better do that or check your privacy settings to get my DM", tweet['id'])
                  else:
                    print('Message Sent to user')
                      
              else:
                  accountid=myresult[0][0]
                  #check amount of Defi owned by sender
                  print("in else when user has an account")
                  try:
                      print("in try")
                      datain = 'http://localhost:27876/nxt?requestType=getAccountAssets&account='+str(myresult3[0][0])+'&asset='+str(assetid)
                      datain = datain.replace(" ", "%20")
                      print(datain)
                      
                      result = requests.post(datain)
                      jsondata = json.loads(result.text) 
                      #print(result.text)
                      print(jsondata)
                      AssetOwned = 0
                      
                      
                  except Exception as error:
                      print(error)
                  else:
                      if 'quantityQNT' in jsondata:
                        AssetOwned = jsondata['quantityQNT']
                      print("Account has "+str(AssetOwned)+" DeFi")
                  #Check unpaid debts
                  try:
                      datain = 'http://localhost:27876/nxt?requestType=getAccountAssets&account='+str(myresult3[0][0])+'&asset='+str(bdefiid)
                      datain = datain.replace(" ", "%20")
                      print(datain)
                      
                      bresult = requests.post(datain)
                      bjsondata = json.loads(bresult.text) 
                      #print(result.text)
                      print(bjsondata)
                      BAssetOwned = 0
                  except Exception as error:
                      print(error)
                  else:
                      if 'quantityQNT' in bjsondata:
                        BAssetOwned = bjsondata['quantityQNT']
                      print("Account has "+str(AssetOwned)+" DeFi pending depts to pay")
                  
                  
                  
                  #Deposit
                  print("depositing asset")
                  #print(words[2])
                  #amounttosend = round(float(words[2]))
                  amountid = words.index('DEPOSIT')
                  print(words[amountid+1])
                  amounttodeposit = round(float(words[amountid+1]))
                  print(amounttodeposit)
                  print(AssetOwned)
                  if int(BAssetOwned) > 0:
                    print("the guy has unpaid debts")
                    api.update_status("@"+tweet['user']['screen_name']+" Yo! You have to pay your pending debts first to #DeadFishBank. Booo...", tweet['id'])
                    try:
                      api.send_direct_message(recipient_id=tweet['user']['id'],text="Make sure you have "+str(BAssetOwned)+" DeFi in your account so you close your debt and you account will be unlocked within 24 hours.")
                      #api.send_direct_message(recipient_id=receiver,text="Wow! Your friend "+tweet['user']['name']+" sent you "+str(amounttosend)+" DeFi")
                    except Exception as error:
                      print(error)
                      #api.update_status("@"+tweet['user']['screen_name']+" Not following me??? Better do that or check your privacy settings to get my DM.", tweet['id'])
                    else:
                      print('Messages sent')
                  elif int(AssetOwned) > int(amounttodeposit):
                    print("enough funds")
                    #idresult = myresult[0][0]
                    try:
                        #find privatekey of sender
                        datain = 'http://localhost:27876/nxt?requestType=deriveAccountFromSeed&mnemonic='+str(seed)+'&bip32Path=m%2F44%27%2F16754%27%2F0%27%2F1%27%2F'+str(accountid)
                        datain = datain.replace(" ", "%20")
                        print(datain)
                        
                        result = requests.post(datain)
                        jsondata = json.loads(result.text) 
                        #print(result.text)
                        print(jsondata)
                        RSaddress = jsondata['accountRS']
                        privatekey = jsondata['privateKey']
                        publickey = jsondata['publicKey']
                        #print(jsondata["bundlerRateNQTPerFXT"])
                    except Exception as error:
                        print(error)
                    else:
                        print("Depositing DEFI")
                        
                        
                        
                        #Get receiver details
                        datain = 'http://localhost:27876/nxt?requestType=deriveAccountFromSeed&mnemonic='+str(seed)+'&bip32Path=m%2F44%27%2F16754%27%2F0%27%2F1%27%2F0'
                        datain = datain.replace(" ", "%20")
                        print(datain)
                        result = requests.post(datain)
                        jsondata = json.loads(result.text) 
                        #print(result.text)
                        #print(jsondata)
                        RSaddress7 = jsondata['accountRS']
                        privatekey7 = jsondata['privateKey']
                        publickey7 = jsondata['publicKey']
                        
                        try:
                          datain = 'http://localhost:27876/nxt?requestType=transferAsset&privateKey='+str(privatekey)+'&chain=ignis&asset='+str(assetid)+'&recipient='+str(RSaddress7)+'&recipientPublicKey='+str(publickey7)+'&quantityQNT='+str(amounttodeposit)+'&feeNQT=0&deadline=60'
                          datain = datain.replace(" ", "%20")
                          print(datain)
                          result = requests.post(datain)
                          jsondata = json.loads(result.text) 
                          #print(result.text)
                          print(jsondata)
                          print("transfer asset transaction")
                          #height = jsondata['ecBlockHeight']
                          #print(height)
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
                          #Transfer defic
                          datain = 'http://localhost:27876/nxt?requestType=transferAsset&phased=true&phasingVotingModel=0&phasingQuorum=1&phasingWhitelisted='+str(RSaddress7)+'&phasingFinishHeight='+str(int(height)+60)+'&privateKey='+str(privatekey7)+'&chain=ignis&asset='+str(cdefiid)+'&recipient='+str(senderaddress)+'&quantityQNT='+str(amounttodeposit)+'&feeNQT=0&deadline=60'
                          datain = datain.replace(" ", "%20")
                          print(datain)
                          result = requests.post(datain)
                          jsondata = json.loads(result.text) 
                          #print(result.text)
                          print(jsondata)
                          print("transfer asset C transaction")
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
                          
                          #Approve Transaction defic
                          datain = 'http://localhost:27876/nxt?requestType=approveTransaction&privateKey='+str(privatekey7)+'&phasedTransaction=2:'+str(transactionid)+'&chain=ignis&feeNQT=0&deadline=60'
                          datain = datain.replace(" ", "%20")
                          print(datain)
                          result = requests.post(datain)
                          jsondata = json.loads(result.text) 
                          #print(result.text)
                          print(jsondata)
                          print("transfer asset C approval transaction")
                          
                        except Exception as error:
                          print(error)
                        else:
                          print("send messages if transaction successfull")
                          api.update_status("@"+tweet['user']['screen_name']+" Very nice! Your deposit was successful. 5% interest on your way, paid daily.", tweet['id'])
                          try:
                            api.send_direct_message(recipient_id=tweet['user']['id'],text="Nice! You deposited "+str(amounttodeposit)+" DeFi.")
                            #api.send_direct_message(recipient_id=receiver,text="Wow! Your friend "+tweet['user']['name']+" sent you "+str(amounttosend)+" DeFi")
                          except Exception as error:
                            print(error)
                            #api.update_status("@"+tweet['user']['screen_name']+" Not following me??? Better do that or check your privacy settings to get my DM.", tweet['id'])
                          else:
                            print('Messages sent')
                  else:
                    try:
                      api.send_direct_message(recipient_id=tweet['user']['id'],text="Your don't have enough DeFi my friend... shame! Did you try with some MAGIC?")
                    except Exception as error:
                      print(error)
                      api.update_status("@"+tweet['user']['screen_name']+" Not following me??? Better do that or check your privacy settings to get my DM", tweet['id'])
                    else:
                      print('Message about not enough DeFi Sent to'+tweet['user']['id'])


            elif 'WITHDRAW' in words:
              print("We're in WITHDRAW")     
              userid = tweet['user']['id']
            
              print(userid)
              mycursor = mydb.cursor()
              mycursor.execute("SELECT passphrase FROM accounts where twitter={}".format(userid))
              myresult = mycursor.fetchall()
              
              mycursor3 = mydb.cursor()
              mycursor3.execute("SELECT ardor FROM accounts where twitter={}".format(userid))
              myresult3 = mycursor3.fetchall()
              
              print('MyResult: {}'.format(myresult))
              
              print('MyResult3: {}'.format(myresult3))
              
              
              #accountid=myresult[0][0]
              try:
                senderaddress = myresult3[0][0]
              except Exception as error:
                print(error)
              else:
                print("ok storing variable")
              
              
              if not myresult:
                  try:
                    api.send_direct_message(recipient_id=tweet['user']['id'],text="Your don't have an Ardor account yet, try using"+"\n\n"+"#DeFiMAGIC CREATE")
                  except Exception as error:
                    print(error)
                    api.update_status("@"+tweet['user']['screen_name']+" Not following me??? Better do that or check your privacy settings to get my DM", tweet['id'])
                  else:
                    print('Message Sent to user')
                      
              else:
                  accountid=myresult[0][0]
                  #check amount of Defi owned by sender
                  print("in else when user has an account")
                  try:
                      print("checking if user has cdefi")
                      datain = 'http://localhost:27876/nxt?requestType=getAccountAssets&account='+str(myresult3[0][0])+'&asset='+str(cdefiid)
                      datain = datain.replace(" ", "%20")
                      print(datain)
                      
                      result = requests.post(datain)
                      jsondata = json.loads(result.text) 
                      #print(result.text)
                      print(jsondata)
                      CAssetOwned = 0
                      
                      
                  except Exception as error:
                      print(error)
                  else:
                      if 'quantityQNT' in jsondata:
                        CAssetOwned = jsondata['quantityQNT']
                      print("Account has "+str(CAssetOwned)+" Deposited DeFi")
                  #check if receiver has an account
                  
                  
                  
                  #Deposit
                  print("withdrawing asset")
                  #print(words[2])
                  #amounttosend = round(float(words[2]))
                  amountid = words.index('WITHDRAW')
                  print(words[amountid+1])
                  amounttowithdraw = round(float(words[amountid+1]))
                  print(amounttowithdraw)
                  print(CAssetOwned)
                  if int(CAssetOwned) > int(amounttowithdraw):
                    print("enough funds")
                    #idresult = myresult[0][0]
                    try:
                        #find privatekey of sender
                        datain = 'http://localhost:27876/nxt?requestType=deriveAccountFromSeed&mnemonic='+str(seed)+'&bip32Path=m%2F44%27%2F16754%27%2F0%27%2F1%27%2F'+str(accountid)
                        datain = datain.replace(" ", "%20")
                        print(datain)
                        
                        result = requests.post(datain)
                        jsondata = json.loads(result.text) 
                        #print(result.text)
                        print(jsondata)
                        RSaddress = jsondata['accountRS']
                        privatekey = jsondata['privateKey']
                        publickey = jsondata['publicKey']
                        #print(jsondata["bundlerRateNQTPerFXT"])
                    except Exception as error:
                        print(error)
                    else:
                        print("Withdrawing DEFI")
                        
                        
                        
                        #Get bank details 
                        datain = 'http://localhost:27876/nxt?requestType=deriveAccountFromSeed&mnemonic='+str(seed)+'&bip32Path=m%2F44%27%2F16754%27%2F0%27%2F1%27%2F0'
                        datain = datain.replace(" ", "%20")
                        print(datain)
                        result = requests.post(datain)
                        jsondata = json.loads(result.text) 
                        #print(result.text)
                        #print(jsondata)
                        RSaddress7 = jsondata['accountRS']
                        privatekey7 = jsondata['privateKey']
                        publickey7 = jsondata['publicKey']
                        
                        try:
                          
                          datain = 'http://localhost:27876/nxt?requestType=getBlockchainStatus'
                          datain = datain.replace(" ", "%20")
                          print(datain)
                          result = requests.post(datain)
                          jsondata = json.loads(result.text) 
                          #print(result.text)
                          print(jsondata)
                          print("transfer asset C transaction")
                          height = jsondata['numberOfBlocks']
                          #Transfer defic
                          datain = 'http://localhost:27876/nxt?requestType=transferAsset&phased=true&phasingVotingModel=0&phasingQuorum=1&phasingWhitelisted='+str(RSaddress7)+'&phasingFinishHeight='+str(int(height)+60)+'&privateKey='+str(privatekey)+'&chain=ignis&asset='+str(cdefiid)+'&recipient='+str(RSaddress7)+'&quantityQNT='+str(amounttowithdraw)+'&feeNQT=0&deadline=60'
                          datain = datain.replace(" ", "%20")
                          print(datain)
                          result = requests.post(datain)
                          jsondata = json.loads(result.text) 
                          #print(result.text)
                          print(jsondata)
                          print("withdraw asset C transaction")
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
                          
                          #Approve Transaction defic
                          datain = 'http://localhost:27876/nxt?requestType=approveTransaction&privateKey='+str(privatekey7)+'&phasedTransaction=2:'+str(transactionid)+'&chain=ignis&feeNQT=0&deadline=60'
                          datain = datain.replace(" ", "%20")
                          print(datain)
                          result = requests.post(datain)
                          jsondata = json.loads(result.text) 
                          #print(result.text)
                          print(jsondata)
                          print("transfer asset C approval transaction")
                          
                          #Transfer DeFi
                          datain = 'http://localhost:27876/nxt?requestType=transferAsset&privateKey='+str(privatekey7)+'&chain=ignis&asset='+str(assetid)+'&recipient='+str(RSaddress)+'&recipientPublicKey='+str(publickey)+'&quantityQNT='+str(amounttowithdraw)+'&feeNQT=0&deadline=60'
                          datain = datain.replace(" ", "%20")
                          print(datain)
                          result = requests.post(datain)
                          jsondata = json.loads(result.text) 
                          #print(result.text)
                          print(jsondata)
                          print("withdraw asset transaction")
                          #height = jsondata['ecBlockHeight']
                          #print(height)
                          #Get height
                          
                        except Exception as error:
                          print(error)
                        else:
                          print("send messages if transaction successfull")
                          api.update_status("@"+tweet['user']['screen_name']+" Very nice! Your withdraw was successful.", tweet['id'])
                          try:
                            api.send_direct_message(recipient_id=tweet['user']['id'],text="Nice! You withdrew "+str(amounttowithdraw)+" DeFi.")
                            #api.send_direct_message(recipient_id=receiver,text="Wow! Your friend "+tweet['user']['name']+" sent you "+str(amounttosend)+" DeFi")
                          except Exception as error:
                            print(error)
                            #api.update_status("@"+tweet['user']['screen_name']+" Not following me??? Better do that or check your privacy settings to get my DM.", tweet['id'])
                          else:
                            print('Messages sent')
                  else:
                    try:
                      api.send_direct_message(recipient_id=tweet['user']['id'],text="Your don't have enough Deposited DeFi my friend...")
                    except Exception as error:
                      print(error)
                      api.update_status("@"+tweet['user']['screen_name']+" Not following me??? Better do that or check your privacy settings to get my DM", tweet['id'])
                    else:
                      print('Message about not enough Deposited DeFi Sent to'+tweet['user']['id'])

            elif 'BORROW' in words:
              print("We're in BORROW")     
              userid = tweet['user']['id']
            
              print(userid)
              mycursor = mydb.cursor()
              mycursor.execute("SELECT passphrase FROM accounts where twitter={}".format(userid))
              myresult = mycursor.fetchall()
              
              mycursor3 = mydb.cursor()
              mycursor3.execute("SELECT ardor FROM accounts where twitter={}".format(userid))
              myresult3 = mycursor3.fetchall()
              
              print('MyResult: {}'.format(myresult))
              
              print('MyResult3: {}'.format(myresult3))
              
              
              #accountid=myresult[0][0]
              try:
                senderaddress = myresult3[0][0]
              except Exception as error:
                print(error)
              else:
                print("ok storing variable")
              
              
              if not myresult:
                  try:
                    api.send_direct_message(recipient_id=tweet['user']['id'],text="Your don't have an Ardor account yet, try using"+"\n\n"+"#DeFiMAGIC CREATE")
                  except Exception as error:
                    print(error)
                    api.update_status("@"+tweet['user']['screen_name']+" Not following me??? Better do that or check your privacy settings to get my DM", tweet['id'])
                  else:
                    print('Message Sent to user')
                      
              else:
                  accountid=myresult[0][0]
                  #check amount of Defi owned by sender
                  print("in else when user has an account")
                  try:
                      print("in try")
                      datain = 'http://localhost:27876/nxt?requestType=getAccountAssets&account='+str(myresult3[0][0])+'&asset='+str(assetid)
                      datain = datain.replace(" ", "%20")
                      print(datain)
                      
                      result = requests.post(datain)
                      jsondata = json.loads(result.text) 
                      #print(result.text)
                      print(jsondata)
                      AssetOwned = 0
                      
                      
                  except Exception as error:
                      print(error)
                  else:
                      if 'quantityQNT' in jsondata:
                        AssetOwned = jsondata['quantityQNT']
                      print("Account has "+str(AssetOwned)+" DeFi")
                  #check if user has already open debts
                  try:
                      print("in try")
                      datain = 'http://localhost:27876/nxt?requestType=getAccountAssets&account='+str(myresult3[0][0])+'&asset='+str(adefiid)
                      datain = datain.replace(" ", "%20")
                      print(datain)
                      
                      result = requests.post(datain)
                      jsondata = json.loads(result.text) 
                      #print(result.text)
                      print(jsondata)
                      PreviousDebt = 0
                      
                      
                  except Exception as error:
                      print(error)
                  else:
                      if 'quantityQNT' in jsondata:
                        PreviousDebt = jsondata['quantityQNT']
                      print("Account has "+str(PreviousDebt)+" DeFi debt")
                  #Check unpaid debts
                  try:
                      datain = 'http://localhost:27876/nxt?requestType=getAccountAssets&account='+str(myresult3[0][0])+'&asset='+str(bdefiid)
                      datain = datain.replace(" ", "%20")
                      print(datain)
                      
                      bresult = requests.post(datain)
                      bjsondata = json.loads(bresult.text) 
                      #print(result.text)
                      print(bjsondata)
                      BAssetOwned = 0
                  except Exception as error:
                      print(error)
                  else:
                      if 'quantityQNT' in bjsondata:
                        BAssetOwned = bjsondata['quantityQNT']
                      print("Account has "+str(AssetOwned)+" DeFi pending depts to pay")
                  
                  
                  
                  #Borrow
                  print("borrowing asset")
                  #print(words[2])
                  #amounttosend = round(float(words[2]))
                  amountid = words.index('BORROW')
                  print(words[amountid+1])
                  amounttoborrow = round(float(words[amountid+1]))
                  print(amounttoborrow)
                  print(AssetOwned)
                  maxdebt = (int(AssetOwned)*10)-PreviousDebt
                  if int(BAssetOwned) > 0:
                    print("the guy has unpaid debts")
                    api.update_status("@"+tweet['user']['screen_name']+" Yo! You have to pay your pending debts first to #DeadFishBank. Booo...", tweet['id'])
                    try:
                      api.send_direct_message(recipient_id=tweet['user']['id'],text="Make sure you have "+str(BAssetOwned)+" DeFi in your account so you close your debt and you account will be unlocked within 24 hours.")
                      #api.send_direct_message(recipient_id=receiver,text="Wow! Your friend "+tweet['user']['name']+" sent you "+str(amounttosend)+" DeFi")
                    except Exception as error:
                      print(error)
                      #api.update_status("@"+tweet['user']['screen_name']+" Not following me??? Better do that or check your privacy settings to get my DM.", tweet['id'])
                    else:
                      print('Messages sent')
                  elif int(amounttoborrow) <= maxdebt:
                    print("enough collaterals")
                    #idresult = myresult[0][0]
                    try:
                        #find privatekey of user
                        datain = 'http://localhost:27876/nxt?requestType=deriveAccountFromSeed&mnemonic='+str(seed)+'&bip32Path=m%2F44%27%2F16754%27%2F0%27%2F1%27%2F'+str(accountid)
                        datain = datain.replace(" ", "%20")
                        print(datain)
                        
                        result = requests.post(datain)
                        jsondata = json.loads(result.text) 
                        #print(result.text)
                        print(jsondata)
                        RSaddress = jsondata['accountRS']
                        privatekey = jsondata['privateKey']
                        publickey = jsondata['publicKey']
                        #print(jsondata["bundlerRateNQTPerFXT"])
                    except Exception as error:
                        print(error)
                    else:
                        print("Depositing DEFI")
                        
                        
                        
                        #Get bank details
                        datain = 'http://localhost:27876/nxt?requestType=deriveAccountFromSeed&mnemonic='+str(seed)+'&bip32Path=m%2F44%27%2F16754%27%2F0%27%2F1%27%2F0'
                        datain = datain.replace(" ", "%20")
                        print(datain)
                        result = requests.post(datain)
                        jsondata = json.loads(result.text) 
                        #print(result.text)
                        #print(jsondata)
                        RSaddress7 = jsondata['accountRS']
                        privatekey7 = jsondata['privateKey']
                        publickey7 = jsondata['publicKey']
                        
                        try:

                          datain = 'http://localhost:27876/nxt?requestType=getBlockchainStatus'
                          datain = datain.replace(" ", "%20")
                          print(datain)
                          result = requests.post(datain)
                          jsondata = json.loads(result.text) 
                          #print(result.text)
                          print(jsondata)
                          
                          height = jsondata['numberOfBlocks']
                          #Transfer defia
                          datain = 'http://localhost:27876/nxt?requestType=transferAsset&phased=true&phasingVotingModel=0&phasingQuorum=1&phasingWhitelisted='+str(RSaddress7)+'&phasingFinishHeight='+str(int(height)+60)+'&privateKey='+str(privatekey7)+'&chain=ignis&asset='+str(adefiid)+'&recipient='+str(senderaddress)+'&quantityQNT='+str(amounttoborrow)+'&feeNQT=0&deadline=60'
                          datain = datain.replace(" ", "%20")
                          print(datain)
                          result = requests.post(datain)
                          jsondata = json.loads(result.text) 
                          #print(result.text)
                          print(jsondata)
                          print("transfer asset A transaction")
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
                          
                          #Approve Transaction defia
                          datain = 'http://localhost:27876/nxt?requestType=approveTransaction&privateKey='+str(privatekey7)+'&phasedTransaction=2:'+str(transactionid)+'&chain=ignis&feeNQT=0&deadline=60'
                          datain = datain.replace(" ", "%20")
                          print(datain)
                          result = requests.post(datain)
                          jsondata = json.loads(result.text) 
                          #print(result.text)
                          print(jsondata)
                          print("transfer asset A approval transaction")
                          #Transfer defi
                          datain = 'http://localhost:27876/nxt?requestType=transferAsset&privateKey='+str(privatekey7)+'&chain=ignis&asset='+str(assetid)+'&recipient='+str(RSaddress)+'&recipientPublicKey='+str(publickey)+'&quantityQNT='+str(amounttoborrow)+'&feeNQT=0&deadline=60'
                          datain = datain.replace(" ", "%20")
                          print(datain)
                          result = requests.post(datain)
                          jsondata = json.loads(result.text) 
                          #print(result.text)
                          print(jsondata)
                          print("transfer asset transaction")
                          #height = jsondata['ecBlockHeight']
                          #print(height)
                          #Get height
                          
                        except Exception as error:
                          print(error)
                        else:
                          print("send messages if transaction successfull")
                          api.update_status("@"+tweet['user']['screen_name']+" Very nice! Your borrowing was successful. It will cost you 5% yearly interest, paid daily.", tweet['id'])
                          try:
                            api.send_direct_message(recipient_id=tweet['user']['id'],text="Nice! You borrowed "+str(amounttoborrow)+" DeFi.")
                            #api.send_direct_message(recipient_id=receiver,text="Wow! Your friend "+tweet['user']['name']+" sent you "+str(amounttosend)+" DeFi")
                          except Exception as error:
                            print(error)
                            #api.update_status("@"+tweet['user']['screen_name']+" Not following me??? Better do that or check your privacy settings to get my DM.", tweet['id'])
                          else:
                            print('Messages sent')
                  else:
                    try:
                      api.send_direct_message(recipient_id=tweet['user']['id'],text="Your don't have enough DeFi my friend or you have reached your maximum debt! Did you already try with some MAGIC?")
                    except Exception as error:
                      print(error)
                      api.update_status("@"+tweet['user']['screen_name']+" Not following me??? Better do that or check your privacy settings to get my DM", tweet['id'])
                    else:
                      print('Message about not enough DeFi or max debt reached Sent to'+tweet['user']['id'])


            elif 'CLOSEDEBT' in words:
              print("We're in CLOSEDEBT")     
              userid = tweet['user']['id']
            
              print(userid)
              mycursor = mydb.cursor()
              mycursor.execute("SELECT passphrase FROM accounts where twitter={}".format(userid))
              myresult = mycursor.fetchall()
              
              mycursor3 = mydb.cursor()
              mycursor3.execute("SELECT ardor FROM accounts where twitter={}".format(userid))
              myresult3 = mycursor3.fetchall()
              
              print('MyResult: {}'.format(myresult))
              
              print('MyResult3: {}'.format(myresult3))
              
              
              #accountid=myresult[0][0]
              try:
                senderaddress = myresult3[0][0]
              except Exception as error:
                print(error)
              else:
                print("ok storing variable")
              
              
              if not myresult:
                  try:
                    api.send_direct_message(recipient_id=tweet['user']['id'],text="Your don't have an Ardor account yet, try using"+"\n\n"+"#DeFiMAGIC CREATE")
                  except Exception as error:
                    print(error)
                    api.update_status("@"+tweet['user']['screen_name']+" Not following me??? Better do that or check your privacy settings to get my DM", tweet['id'])
                  else:
                    print('Message Sent to user')
                      
              else:
                  accountid=myresult[0][0]
                  #check amount of Defi owned by sender
                  print("in else when user has an account")
                  try:
                      print("in try")
                      datain = 'http://localhost:27876/nxt?requestType=getAccountAssets&account='+str(myresult3[0][0])+'&asset='+str(assetid)
                      datain = datain.replace(" ", "%20")
                      print(datain)
                      
                      result = requests.post(datain)
                      jsondata = json.loads(result.text) 
                      #print(result.text)
                      print(jsondata)
                      AssetOwned = 0
                      
                      
                  except Exception as error:
                      print(error)
                  else:
                      if 'quantityQNT' in jsondata:
                        AssetOwned = jsondata['quantityQNT']
                      print("Account has "+str(AssetOwned)+" DeFi")
                  #check if user has already open debts
                  try:
                      print("in try")
                      datain = 'http://localhost:27876/nxt?requestType=getAccountAssets&account='+str(myresult3[0][0])+'&asset='+str(adefiid)
                      datain = datain.replace(" ", "%20")
                      print(datain)
                      
                      result = requests.post(datain)
                      jsondata = json.loads(result.text) 
                      #print(result.text)
                      print(jsondata)
                      PreviousDebt = 0
                      
                      
                  except Exception as error:
                      print(error)
                  else:
                      if 'quantityQNT' in jsondata:
                        PreviousDebt = jsondata['quantityQNT']
                      print("Account has "+str(PreviousDebt)+" DeFi debt")
                  #check if receiver has an account
                  
                  
                  
                  #Closing debt
                  print("closing debt")
                  #print(words[2])
                  #amounttosend = round(float(words[2]))
                  amountid = words.index('CLOSEDEBT')
                  print(words[amountid+1])
                  amounttoclose = round(float(words[amountid+1]))
                  print(amounttoclose)
                  print(AssetOwned)
                  #maxdebt = (int(AssetOwned)*10)-PreviousDebt
                  if (int(AssetOwned) > int(amounttoclose)) and (int(amounttoclose) <= int(PreviousDebt)):
                    print("enough to return")
                    #idresult = myresult[0][0]
                    try:
                        #find privatekey of user
                        datain = 'http://localhost:27876/nxt?requestType=deriveAccountFromSeed&mnemonic='+str(seed)+'&bip32Path=m%2F44%27%2F16754%27%2F0%27%2F1%27%2F'+str(accountid)
                        datain = datain.replace(" ", "%20")
                        print(datain)
                        
                        result = requests.post(datain)
                        jsondata = json.loads(result.text) 
                        #print(result.text)
                        print(jsondata)
                        RSaddress = jsondata['accountRS']
                        privatekey = jsondata['privateKey']
                        publickey = jsondata['publicKey']
                        #print(jsondata["bundlerRateNQTPerFXT"])
                    except Exception as error:
                        print(error)
                    else:
                        print("Returning DEFI")
                        
                        
                        
                        #Get bank details
                        datain = 'http://localhost:27876/nxt?requestType=deriveAccountFromSeed&mnemonic='+str(seed)+'&bip32Path=m%2F44%27%2F16754%27%2F0%27%2F1%27%2F0'
                        datain = datain.replace(" ", "%20")
                        print(datain)
                        result = requests.post(datain)
                        jsondata = json.loads(result.text) 
                        #print(result.text)
                        #print(jsondata)
                        RSaddress7 = jsondata['accountRS']
                        privatekey7 = jsondata['privateKey']
                        publickey7 = jsondata['publicKey']
                        
                        try:

                          datain = 'http://localhost:27876/nxt?requestType=getBlockchainStatus'
                          datain = datain.replace(" ", "%20")
                          print(datain)
                          result = requests.post(datain)
                          jsondata = json.loads(result.text) 
                          #print(result.text)
                          print(jsondata)
                          
                          height = jsondata['numberOfBlocks']
                          #Transfer defia
                          datain = 'http://localhost:27876/nxt?requestType=transferAsset&phased=true&phasingVotingModel=0&phasingQuorum=1&phasingWhitelisted='+str(RSaddress7)+'&phasingFinishHeight='+str(int(height)+60)+'&privateKey='+str(privatekey)+'&chain=ignis&asset='+str(adefiid)+'&recipient='+str(RSaddress7)+'&quantityQNT='+str(amounttoclose)+'&feeNQT=0&deadline=60'
                          datain = datain.replace(" ", "%20")
                          print(datain)
                          result = requests.post(datain)
                          jsondata = json.loads(result.text) 
                          #print(result.text)
                          print(jsondata)
                          print("transfer asset A transaction")
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
                          
                          #Approve Transaction defia
                          datain = 'http://localhost:27876/nxt?requestType=approveTransaction&privateKey='+str(privatekey7)+'&phasedTransaction=2:'+str(transactionid)+'&chain=ignis&feeNQT=0&deadline=60'
                          datain = datain.replace(" ", "%20")
                          print(datain)
                          result = requests.post(datain)
                          jsondata = json.loads(result.text) 
                          #print(result.text)
                          print(jsondata)
                          print("transfer asset A approval transaction")
                          #Transfer defi
                          datain = 'http://localhost:27876/nxt?requestType=transferAsset&privateKey='+str(privatekey)+'&chain=ignis&asset='+str(assetid)+'&recipient='+str(RSaddress7)+'&recipientPublicKey='+str(publickey7)+'&quantityQNT='+str(amounttoclose)+'&feeNQT=0&deadline=60'
                          datain = datain.replace(" ", "%20")
                          print(datain)
                          result = requests.post(datain)
                          jsondata = json.loads(result.text) 
                          #print(result.text)
                          print(jsondata)
                          print("transfer asset transaction")
                          #height = jsondata['ecBlockHeight']
                          #print(height)
                          #Get height
                          
                        except Exception as error:
                          print(error)
                        else:
                          print("send messages if transaction successfull")
                          api.update_status("@"+tweet['user']['screen_name']+" Very nice! Your closed part of your debt.", tweet['id'])
                          try:
                            api.send_direct_message(recipient_id=tweet['user']['id'],text="Nice! You closed part of your debt for "+str(amounttoclose)+" DeFi.")
                            #api.send_direct_message(recipient_id=receiver,text="Wow! Your friend "+tweet['user']['name']+" sent you "+str(amounttosend)+" DeFi")
                          except Exception as error:
                            print(error)
                            #api.update_status("@"+tweet['user']['screen_name']+" Not following me??? Better do that or check your privacy settings to get my DM.", tweet['id'])
                          else:
                            print('Messages sent')
                  else:
                    try:
                      api.send_direct_message(recipient_id=tweet['user']['id'],text="Your don't have enough DeFi my friend or you don't have that much debt!")
                    except Exception as error:
                      print(error)
                      api.update_status("@"+tweet['user']['screen_name']+" Not following me??? Better do that or check your privacy settings to get my DM", tweet['id'])
                    else:
                      print('Message about not enough DeFi or not enough debt Sent to'+tweet['user']['id'])


    
        # Stops streaming when it reaches the limit
        if self.num_tweets <= TWEETS_TO_CAPTURE:
            if self.num_tweets % 100 == 0: # just to see some progress...
                print('Numer of tweets captured so far: {}'.format(self.num_tweets))
                return True
            else:
                return False
            self.file.close()

    def on_error(self, status):
        print(status)


# Initialize Stream listener
l = MyStreamListener()

# Create you Stream object with authentication
stream = tweepy.Stream(auth, l)

# Filter Twitter Streams to capture data by the keywords:
while True:
    try:
        stream.filter(track=TRACKING_KEYWORDS, stall_warnings=True)
    except Exception as e:
        pass
