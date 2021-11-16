import time 
import requests

async def GetLastQuote():
    print("----------------------------------------------------")
    print("Work in progress... sending request for GetLastQuote")
    print("----------------------------------------------------")
    ExchangeName = "NFO"
    InstIdentifier = "NIFTY-I"
    isShortIdentifier = "false"         #GFDL : When using contractwise symbol like NIFTY20JULFUT, 
                                        #this argument must be sent with value "true" 
    xml="false"                                        
    response = ""
    count = 0
    maxcount = 10                       #Change this number to see more updates. By default, sample will print 10 updates and stop
    while(count<maxcount):
        strMessage = endpoint+"getlastquote/?accessKey="+accesskey+"&exchange="+ExchangeName+"&instrumentIdentifier="+InstIdentifier+"&xml="+xml
        response = requests.get(strMessage)
        print("Message sent : "+strMessage)
        print("Waiting for response...")
        print("Response :\n" + response.text)
        print("----------------------------------------------------")
        time.sleep(1.5)
        count = count+1

"""
GFDL TODO - please enter below the endpoint received from GFDL team. 
If you dont have one, please contact us on sales@globaldatafeeds.in 
"""  
endpoint = "http://test.lisuns.com:4531/"
 
"""
//GFDL TODO - please enter below the API Key received from GFDL team. 
If you dont have one, please contact us on sales@globaldatafeeds.in 
"""
accesskey = "79ae1ee0-121b-41d4-ab6d-10b5774481c0"


GetLastQuote()