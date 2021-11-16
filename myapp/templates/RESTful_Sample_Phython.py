import asyncio
import datetime
import json
import time
import requests

"""
GFDL TODO - please enter below the endpoint received from GFDL team. 
If you dont have one, please contact us on sales@globaldatafeeds.in 
"""  
endpoint = "https://test.lisuns.com:4532/"

"""
//GFDL TODO - please enter below the API Key received from GFDL team. 
If you dont have one, please contact us on sales@globaldatafeeds.in 
"""
accesskey = "79ae1ee0-121b-41d4-ab6d-10b5774481c0"

"""
GFDL TODO : All the functions supported by API are listed below. 
You can uncomment any function (one at a time) to see the flow of request and response
"""

#*****List of functions*****#

function = "GetLastQuote"                          #GFDL : Returns LastTradePrice of Single Symbol (detailed)
#function = "GetLastQuoteShort"                     #GFDL : Returns LastTradePrice of Single Symbol (short)
#function = "GetLastQuoteShortWithClose"            #GFDL : Returns LastTradePrice of Single Symbol (short) with Close of Previous Day
#function = "GetLastQuoteArray"                     #GFDL : Returns LastTradePrice of multiple Symbols – max 25 in single call (detailed)
#function = "GetLastQuoteArrayShort"                #GFDL : Returns LastTradePrice of multiple Symbols – max 25 in single call (short)
#function = "GetLastQuoteArrayShortwithClose"       #GFDL : Returns LastTradePrice of multiple Symbols – max 25 in single call (short) with Previous Close

#function = "GetSnapshot"                           #GFDL : Returns latest Snapshot Data of multiple Symbols – max 25 in single call
#function = "GetHistory"                            #GFDL : Returns historical data (Tick / Minute / EOD)

#function = "GetExchanges"                          #GFDL : Returns array of available exchanges configured for API Key

#function = "GetInstrumentsOnSearch"                #GFDL : Returns array of max. 20 instruments by selected exchange and 'search string'
#function = "GetInstruments"                        #GFDL : Returns array of instruments by selected exchange

#function = "GetInstrumentTypes"                    #GFDL : Returns list of Instrument Types (e.g. FUTIDX, FUTSTK, etc.)
#function = "GetProducts"                           #GFDL : Returns list of Products (e.g. NIFTY, BANKNIFTY, GAIL, etc.)
#function = "GetExpiryDates"                        #GFDL : Returns array of Expiry Dates (e.g. 25JUN2020, 30JUL2020, etc.)
#function = "GetOptionTypes"                        #GFDL : Returns list of Option Types (e.g. CE, PE, etc.)
#function = "GetStrikePrices"                       #GFDL : Returns list of Strike Prices (e.g. 10000, 11000, 75.5, etc.)

#function = "GetServerInfo"                         #GFDL : Returns the server endpoint where user is connected
#function = "GetLimitation"                         #GFDL : Returns user account information (functions allowed, Exchanges allowed, symbol limit, etc.)

#function = "GetMarketMessages"                     #GFDL : Returns array of last messages (Market Messages) related to selected exchange
#function = "GetExchangeMessages"                   #GFDL : Returns array of last messages (Exchange Messages) related to selected exchange

#function = "GetLastQuoteOptionChain"               #GFDL : Returns OptionChain data in realtime
#function = "GetExchangeSnapshot"                   #GFDL : Returns entire Exchange Snapshot in realtime


"""
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	/* 	GFDL : 	1. 	Below 3 functions return the data of SINGLE SYMBOL - whenever requested.
				2. 	So you will need to send these requests EVERY TIME when you need latest data.
				3. 	GetLastQuote : returns single record of realtime data of single symbol. Contains many fields in response
				4. 	GetLastQuoteShort : returns single record of realtime data of single symbol. Contains limited fields in response
				5. 	GetLastQuoteShortWithClose : returns single record of realtime data of single symbol. Contains limited fields in response
				6.	If you want to get data of multiple symbols, you will need to send 1 request each - for each symbol
				
                //This example shows how to request data using Continuous Format
                //Similarly, you can send NIFTY-II (Near month), NIFTY-III (Far month). 
                //Below Symbol is Continuous Format of NIFTY Futures. It will never expire. So no change in code will be necessary.
                //You can use same naming convention for Futures of Instruments from NFO, CDS, MCX Exchanges
                //CDS Examples : USDINR-I, USDINR-II, USDINR-III
                //MCX Examples : NATURALGAS-I, NATURALGAS-II, NATURALGAS-III
                
                //Similarly, you can send NIFTY20AUGFUT (near month), NIFTY20SEPFUT (far month). 
                //You can use same naming convention for Futures of Instruments from NFO, CDS, MCX Exchanges
                //NFO Options Examples : NIFTY02JUL2010000CE, RELIANCE30JUL201700CE
                //CDS Futures Examples : USDINR20JULFUT, USDINR20AUGFUT, USDINR20SEPFUT
                //CDS Options Examples : USDINR29JUL2075.5CE, EURINR29JUL2080CE
                //MCX Options Examples : CRUDEOIL20JULFUT, CRUDEOIL20AUGFUT, CRUDEOIL20SEPFUT
                //MCX Options Examples : CRUDEOIL20JUL2050PE, GOLD20JUL43700PE	
                //Important : Replace it with appropriate expiry date if this contract is expired

                //Similarly, you can send FUTIDX_NIFTY_27AUG2020_XX_0 (near month), FUTIDX_NIFTY_24SEP2020_XX_0 (far month). 
                //You can use same naming convention for Futures of Instruments from NFO, CDS, MCX Exchanges
                //NFO Options Examples : OPTIDX_NIFTY_02JUL2020_CE_10000, OPTSTK_RELIANCE_30JUL2020_CE_1700
                //CDS Futures Examples : FUTCUR_USDINR_26JUN2020_XX_0, FUTCUR_USDINR_29JUL2020_XX_0, FUTCUR_USDINR_27AUG2020_XX_0
                //CDS Options Examples : OPTCUR_USDINR_29JUL2020_CE_75.5, OPTCUR_EURINR_29JUL2020_CE_80
                //MCX Futures Examples : FUTCOM_CRUDEOIL_20JUL2020__0, FUTCOM_CRUDEOIL_19AUG2020__0, FUTCOM_CRUDEOIL_21SEP2020__0
                //MCX Options Examples : OPTFUT_CRUDEOIL_16JUL2020_PE_2050, OPTFUT_GOLD_27JUL2020_PE_43700
                //Important : Replace it with appropriate expiry date if this contract is expired

                Requesting realtime data of NSE Indices
                -------------------------------------------
                //Use InstrumentIdenfier value "NIFTY 50", "NIFTY BANK", "NIFTY 100", etc.
                //Use NSE_IDX as Exchange
                //Please note that Indices Symbols have white space. For example, between NIFTY & 50, NIFTY & BANK above

                Requesting realtime data of NSE Stocks 
                ------------------------------------------
                //For EQ Series, use InstrumentIdentifier value BAJAJ-AUTO, RELIANCE, AXISBANK, LT, etc..
                //To subscribe to realtime data of any other series, append the series name to symbol name 
                //for example, to request data of RELIANCE CAPITAL from BE Series, use RELCAPITAL.BE
                //EQ Series Symbols are mentioned without any suffix

                // Please see symbol naming conventions here : 
                // https://globaldatafeeds.in/global-datafeeds-apis/global-datafeeds-apis/documentation-support/symbol-naming-convention/
	*/
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""
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


async def GetLastQuoteShort():
    print("----------------------------------------------------")
    print("Work in progress... sending request for GetLastQuoteShort")
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
        strMessage = endpoint+"getlastquoteshort/?accessKey="+accesskey+"&exchange="+ExchangeName+"&instrumentIdentifier="+InstIdentifier+"&xml="+xml
        response = requests.get(strMessage)
        print("Message sent : "+strMessage)
        print("Waiting for response...")
        print("Response :\n" + response.text)
        print("----------------------------------------------------")
        time.sleep(1.5)
        count = count+1


async def GetLastQuoteShortWithClose():
    print("----------------------------------------------------")
    print("Work in progress... sending request for GetLastQuoteShortWithClose")
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
        strMessage = endpoint+"getlastquoteshortwithclose/?accessKey="+accesskey+"&exchange="+ExchangeName+"&instrumentIdentifier="+InstIdentifier+"&xml="+xml
        response = requests.get(strMessage)
        print("Message sent : "+strMessage)
        print("Waiting for response...")
        print("Response :\n" + response.text)
        print("----------------------------------------------------")
        time.sleep(1.5)
        count = count+1


"""
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	/* 	GFDL : 	1. 	Below 3 functions return the data of MULTIPLE SYMBOLS (MAX 25IN SINGLE CALL) - whenever requested.
				2. 	So you will need to send these requests EVERY TIME when you need latest data.
				3. 	GetLastQuoteArray : returns array of realtime data of multiple symbols. Contains many fields in response
				4. 	GetLastQuoteArrayShort : returns array of realtime data of multiple symbols. Contains limited fields in response
				5. 	GetLastQuoteArrayShortWithClose : returns array of realtime data of multiple symbols. Contains limited fields in response
				6.	If you want to get data of multiple symbols (more than 25), you will need to send more requests - 1 each for 25 symbols

                //This example shows how to request data using Continuous Format
                //Similarly, you can send NIFTY-II (Near month), NIFTY-III (Far month). 
                //Below Symbol is Continuous Format of NIFTY Futures. It will never expire. So no change in code will be necessary.
                //You can use same naming convention for Futures of Instruments from NFO, CDS, MCX Exchanges
                //CDS Examples : USDINR-I, USDINR-II, USDINR-III
                //MCX Examples : NATURALGAS-I, NATURALGAS-II, NATURALGAS-III
                
                //Similarly, you can send NIFTY20AUGFUT (near month), NIFTY20SEPFUT (far month). 
                //You can use same naming convention for Futures of Instruments from NFO, CDS, MCX Exchanges
                //NFO Options Examples : NIFTY02JUL2010000CE, RELIANCE30JUL201700CE
                //CDS Futures Examples : USDINR20JULFUT, USDINR20AUGFUT, USDINR20SEPFUT
                //CDS Options Examples : USDINR29JUL2075.5CE, EURINR29JUL2080CE
                //MCX Options Examples : CRUDEOIL20JULFUT, CRUDEOIL20AUGFUT, CRUDEOIL20SEPFUT
                //MCX Options Examples : CRUDEOIL20JUL2050PE, GOLD20JUL43700PE	
                //Important : Replace it with appropriate expiry date if this contract is expired

                //Similarly, you can send FUTIDX_NIFTY_27AUG2020_XX_0 (near month), FUTIDX_NIFTY_24SEP2020_XX_0 (far month). 
                //You can use same naming convention for Futures of Instruments from NFO, CDS, MCX Exchanges
                //NFO Options Examples : OPTIDX_NIFTY_02JUL2020_CE_10000, OPTSTK_RELIANCE_30JUL2020_CE_1700
                //CDS Futures Examples : FUTCUR_USDINR_26JUN2020_XX_0, FUTCUR_USDINR_29JUL2020_XX_0, FUTCUR_USDINR_27AUG2020_XX_0
                //CDS Options Examples : OPTCUR_USDINR_29JUL2020_CE_75.5, OPTCUR_EURINR_29JUL2020_CE_80
                //MCX Futures Examples : FUTCOM_CRUDEOIL_20JUL2020__0, FUTCOM_CRUDEOIL_19AUG2020__0, FUTCOM_CRUDEOIL_21SEP2020__0
                //MCX Options Examples : OPTFUT_CRUDEOIL_16JUL2020_PE_2050, OPTFUT_GOLD_27JUL2020_PE_43700
                //Important : Replace it with appropriate expiry date if this contract is expired

                Requesting realtime data of NSE Indices
                -------------------------------------------
                //Use InstrumentIdenfier value "NIFTY 50", "NIFTY BANK", "NIFTY 100", etc.
                //Use NSE_IDX as Exchange
                //Please note that Indices Symbols have white space. For example, between NIFTY & 50, NIFTY & BANK above

                Requesting realtime data of NSE Stocks 
                ------------------------------------------
                //For EQ Series, use InstrumentIdentifier value BAJAJ-AUTO, RELIANCE, AXISBANK, LT, etc..
                //To subscribe to realtime data of any other series, append the series name to symbol name 
                //for example, to request data of RELIANCE CAPITAL from BE Series, use RELCAPITAL.BE
                //EQ Series Symbols are mentioned without any suffix

                // Please see symbol naming conventions here : 
                // https://globaldatafeeds.in/global-datafeeds-apis/global-datafeeds-apis/documentation-support/symbol-naming-convention/
	*/
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""
async def GetLastQuoteArray():
    print("----------------------------------------------------")
    print("Work in progress... sending request for GetLastQuoteArray")
    print("----------------------------------------------------")
    ExchangeName = "NFO"
    InstIdentifiers = "NIFTY-I+BANKNIFTY-I+RELIANCE-I"
    isShortIdentifier = "false"         #GFDL : When using contractwise symbol like NIFTY20JULFUT, 
                                        #this argument must be sent with value "true" 
    xml="false"                                        
    response = ""
    count = 0
    maxcount = 10                       #Change this number to see more updates. By default, sample will print 10 updates and stop
    while(count<maxcount):
        strMessage = endpoint+"getlastquotearray/?accessKey="+accesskey+"&exchange="+ExchangeName+"&instrumentIdentifiers="+InstIdentifiers+"&xml="+xml
        response = requests.get(strMessage)
        print("Message sent : "+strMessage)
        print("Waiting for response...")
        print("Response :\n" + response.text)
        time.sleep(1.5)
        count = count+1


async def GetLastQuoteArrayShort():
    print("----------------------------------------------------")
    print("Work in progress... sending request for GetLastQuoteArrayShort")
    print("----------------------------------------------------")
    ExchangeName = "NFO"
    InstIdentifiers = "NIFTY-I+BANKNIFTY-I+RELIANCE-I"
    isShortIdentifier = "false"         #GFDL : When using contractwise symbol like NIFTY20JULFUT, 
                                        #this argument must be sent with value "true" 
    xml="false"                                        
    response = ""
    count = 0
    maxcount = 10                       #Change this number to see more updates. By default, sample will print 10 updates and stop
    while(count<maxcount):
        strMessage = endpoint+"getlastquotearrayshort/?accessKey="+accesskey+"&exchange="+ExchangeName+"&instrumentIdentifiers="+InstIdentifiers+"&xml="+xml
        response = requests.get(strMessage)
        print("Message sent : "+strMessage)
        print("Waiting for response...")
        print("Response :\n" + response.text)
        print("----------------------------------------------------")
        time.sleep(1.5)
        count = count+1


async def GetLastQuoteArrayShortwithClose():
    print("----------------------------------------------------")
    print("Work in progress... sending request for GetLastQuoteArrayShortWithClose")
    print("----------------------------------------------------")
    ExchangeName = "NFO"
    InstIdentifiers = "NIFTY-I+BANKNIFTY-I+RELIANCE-I"
    isShortIdentifier = "false"         #GFDL : When using contractwise symbol like NIFTY20JULFUT, 
                                        #this argument must be sent with value "true" 
    xml="false"                                        
    response = ""
    count = 0
    maxcount = 10                       #Change this number to see more updates. By default, sample will print 10 updates and stop
    while(count<maxcount):
        strMessage = endpoint+"getlastquotearrayshortwithclose/?accessKey="+accesskey+"&exchange="+ExchangeName+"&instrumentIdentifiers="+InstIdentifiers+"&xml="+xml
        response = requests.get(strMessage)
        print("Message sent : "+strMessage)
        print("Waiting for response...")
        print("Response :\n" + response.text)
        print("----------------------------------------------------")
        time.sleep(1.5)
        count = count+1


"""
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	/* 	GFDL : 	1. 	GetSnapshot : Returns latest single snapshot of MULTIPLE SYMBOLS (MAX 25 in single call) as per 
					"Periodicity" & "Period" mentioned
					For example, if Periodicity is "Minute" and "Period" is 1 then server will return the data of 
					the requested instrument(s) whenever 1 minute completes.
				2. 	You will need to send this request EVERY TIME when you need latest data.
				3.	To see this function in action, you should run it during market hours				
				
					To know about symbol naming conventions, see GetLastQuote / GetLastQuoteArray functions above
				
					Please see symbol naming conventions here : 
					https://globaldatafeeds.in/global-datafeeds-apis/global-datafeeds-apis/documentation-support/symbol-naming-convention/			
	*/
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""
async def GetSnapshot():
    print("----------------------------------------------------")
    print("Work in progress... sending request for GetSnapshot")
    print("----------------------------------------------------")
    ExchangeName = "NFO"                    #GFDL : Supported Values : NFO, NSE, NSE_IDX, CDS, MCX. Mandatory Parameter
    Periodicity = "MINUTE"                  #GFDL : Supported Values : Minute, Hour
    Period = 1                              #GFDL : Supported Values : 1,2,3,5,10,15,20,30
    InstrumentIdentifiers = "NIFTY-I+BANKNIFTY-I"
    isShortIdentifiers = "false"            #GFDL : When using contractwise symbol like NIFTY20JULFUT, 
                                            #       this argument must be sent with value "true" 
    xml="false"                                        
    response = ""
    count = 0
    maxcount = 10                       #Change this number to see more updates. By default, sample will print 10 updates and stop
    while(count<maxcount):
        strMessage = endpoint+"getsnapshot/?accessKey="+accesskey+"&exchange="+ExchangeName+"&Periodicity="+Periodicity+"&Period="+f'{Period}'+"&isShortIdentifiers="+isShortIdentifiers+"&instrumentIdentifiers="+InstrumentIdentifiers+"&xml="+xml
        response = requests.get(strMessage)
        print("Message sent : "+strMessage)
        print("Waiting for response...")
        print("Response :\n" + response.text)
        print("----------------------------------------------------")
        time.sleep(60)
        count = count+1


"""
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

	/* 	GFDL : 	1. 	GetHistory : Returns historical data of SINGLE SYMBOL as per "Periodicity" & "Period" mentioned
				2.	This is a very powerful function which supports many optional parameters to download full / incremental data

					To know about symbol naming conventions, see SubscribeRealtime / SubscribeSnapshot functions above
				
					Please see symbol naming conventions here : 
					https://globaldatafeeds.in/global-datafeeds-apis/global-datafeeds-apis/documentation-support/symbol-naming-convention/			
	*/
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""

async def GetHistory():
    print("----------------------------------------------------")
    print("Work in progress... sending request for GetHistory")
    print("----------------------------------------------------")
    ExchangeName = "NFO"                #GFDL : Supported Values : NFO, NSE, NSE_IDX, CDS, MCX. Mandatory Parameter
    InstrumentIdentifier = "NIFTY-I"
    Periodicity = "Minute"              #GFDL : Supported values are : Tick, Minute, Hour, Day, Week, Month
    isShortIdentifier = "false"			#GFDL : When using contractwise symbol like NIFTY20JULFUT, 
                                        #this argument must be sent with value "true" 
    Period = 1                          #GFDL : Supported values : 1,2,3,4,5,10,12,15,20,30
    Max = 10                            #Specify this argument to control the number of records returned.
                                        #For example, send Max:10 to request only latest 10 records

    #Below code will set Start Time of request to 10 hours before current time
    #This may not work on weekends, change value suitably
    From = round(time.time()-36000)     #Start time of the History as per Epoch time (1st January 1970)
                                        #Visit https://www.epochconverter.com/ to get formulae to convert human readable 
                                        #time to Epoch and vice versa (scroll to end of their home page)

                                        #If you need entire possible history, send From value as 0

    to = 0                              #End time of the History as per Epoch. 
                                        #To request data till latest moment, skip this argument or send time in Future (e.g. current time + 1 hour)
    xml="false"                                        
    response = ""
    #Given below are various usecases of GetHistory function calls. Uncomment and use the one as per requirement
    # 1 : below request will fetch latest 10 bars of 1 minute of NIFTY-I.
    strMessage = endpoint+"gethistory/?accessKey="+accesskey+"&exchange="+ExchangeName+"&Periodicity="+Periodicity+"&Period="+f'{Period}'+"&isShortIdentifier="+isShortIdentifier+"&instrumentIdentifier="+InstrumentIdentifier+"&max="+f'{Max}'+"&xml="+xml

    # 2: below request will fetch latest 10 Ticks of NIFTY-I
    #strMessage = endpoint+"gethistory/?accessKey="+accesskey+"&exchange="+ExchangeName+"&Periodicity=Tick"+"&Period="+f'{Period}'+"&isShortIdentifier="+isShortIdentifier+"&instrumentIdentifier="+InstrumentIdentifier+"&max="+f'{Max}'+"&xml="+xml

    # 3: below request will fetch some 1 minute bars using From & To parameters of NIFTY-I
    #In below request, it sets the From time to 10 hours before current time
    #strMessage = endpoint+"gethistory/?accessKey="+accesskey+"&exchange="+ExchangeName+"&Periodicity=Tick"+"&Period="+f'{Period}'+"&isShortIdentifier="+isShortIdentifier+"&instrumentIdentifier="+InstrumentIdentifier+"&from="+f'{From}'+"&xml="+xml

    # 4: below request will fetch all available bars of 1 minute of NIFTY-I.
    #strMessage = endpoint+"gethistory/?accessKey="+accesskey+"&exchange="+ExchangeName+"&Periodicity=Tick"+"&Period="+f'{Period}'+"&isShortIdentifier="+isShortIdentifier+"&instrumentIdentifier="+InstrumentIdentifier+"&from=0"+"&xml="+xml

    response = requests.get(strMessage)
    print("Message sent : "+strMessage)
    print("Waiting for response...")
    print("Response :\n" + response.text)
    print("----------------------------------------------------")

"""
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	/* 	GFDL : 	1. 	GetExchanges : Returns array of Exchanges allowed for your API Key
	*/
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""

async def GetExchanges():
    print("----------------------------------------------------")
    print("Work in progress... sending request for GetExchanges")
    print("----------------------------------------------------")
    xml="false"                                        
    response = ""
    strMessage = endpoint+"getexchanges/?accessKey="+accesskey+"&xml="+xml
    response = requests.get(strMessage)
    print("Message sent : "+strMessage)
    print("Waiting for response...")
    print("Response :\n" + response.text)
    print("----------------------------------------------------")

"""
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	//GetInstrumentsOnSearch();				//GFDL : Returns array of max. 20 instruments by selected exchange and 'search string'
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""

async def GetInstrumentsOnSearch():
    print("----------------------------------------------------")
    print("Work in progress... sending request for GetInstrumentsOnSearch")
    print("----------------------------------------------------")
    xml="false"                                        
    response = ""
    ExchangeName = "NFO"        #GFDL : Supported Values : NFO, NSE, NSE_IDX, CDS, MCX. Mandatory Parameter
    Search = "NIFTY"            #GFDL : This is the search string
    InstrumentType = "FUTIDX"	#GFDL : Optional argument to filter the search by products like FUTIDX, FUTSTK, OPTIDX, OPTSTK, 	
                                #FUTCUR, FUTCOM, etc.
    Product = "NIFTY"			#GFDL : Optional argument to filter the search by products like NIFTY, RELIANCE, etc.
    OptionType = "PE"			#GFDL : Optional argument to filter the search by OptionTypes like CE, PE
    Expiry = "30JUL2020"	    #GFDL : Optional argument to filter the search by Expiry like 30JUL2020
    StrikePrice = 10000 	    #GFDL : Optional argument to filter the search by Strike Price like 10000, 75.5, 1250, etc.
    OnlyActive = "TRUE"	        #GFDL : Optional argument (default=True) to control returned data. If false, 
                                #even expired contracts are returned

    strMessage = endpoint+"getinstrumentsonsearch/?accessKey="+ accesskey +"&exchange="+ ExchangeName +"&search="+ Search +"&xml="+xml
    response = requests.get(strMessage)
    print("Message sent : "+strMessage)
    print("Waiting for response...")
    print("Response :\n" + response.text)
    print("----------------------------------------------------")

"""
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	/*
	//GetInstruments();						//GFDL : Returns array of instruments by selected exchange 
	
	//VERY VERY IMPORTANT : Huge data of several MB is returned if GetInstruments is called without any optional arguments (NSE & NFO)
							It is strongly advised that users build a local symbol cache at their end and refresh with our server		
							only "on need basis". This will result in faster response time and smoother experience for endusers
	*/
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""

async def GetInstruments():
    print("----------------------------------------------------")
    print("Work in progress... sending request for GetInstruments")
    print("----------------------------------------------------")
    xml="false"                                        
    response = ""
    ExchangeName = "NFO"        #GFDL : Supported Values : NFO, NSE, NSE_IDX, CDS, MCX. Mandatory Parameter
    Search = "NIFTY"            #GFDL : This is the search string
    InstrumentType = "FUTIDX"	#GFDL : Optional argument to filter the search by products like FUTIDX, FUTSTK, OPTIDX, OPTSTK, 	
                                #FUTCUR, FUTCOM, etc.
    Product = "NIFTY"			#GFDL : Optional argument to filter the search by products like NIFTY, RELIANCE, etc.
    OptionType = "PE"			#GFDL : Optional argument to filter the search by OptionTypes like CE, PE
    Expiry = "30JUL2020"	    #GFDL : Optional argument to filter the search by Expiry like 30JUL2020
    StrikePrice = 10000 	    #GFDL : Optional argument to filter the search by Strike Price like 10000, 75.5, 1250, etc.
    OnlyActive = "TRUE"	        #GFDL : Optional argument (default=True) to control returned data. If false, 
                                #even expired contracts are returned

    strMessage = endpoint+"getinstruments/?accessKey="+ accesskey +"&exchange="+ ExchangeName +"&InstrumentType="+ InstrumentType +"&xml="+xml
    response = requests.get(strMessage)
    print("Message sent : "+strMessage)
    print("Waiting for response...")
    print("Response :\n" + response.text)
    print("----------------------------------------------------")


"""
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	//GetInstrumentTypes();					//GFDL : Returns list of Instrument Types (e.g. FUTIDX, FUTSTK, etc.)
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""

async def GetInstrumentTypes():
    print("----------------------------------------------------")
    print("Work in progress... sending request for GetInstrumentTypes")
    print("----------------------------------------------------")
    ExchangeName="NFO"
    xml="false"                                        
    response = ""
    strMessage = endpoint+"getexchanges/?accessKey="+accesskey+"&exchange="+ExchangeName+"&xml="+xml
    response = requests.get(strMessage)
    print("Message sent : "+strMessage)
    print("Waiting for response...")
    print("Response :\n" + response.text)
    print("----------------------------------------------------")

"""
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	//GetProducts();						//GFDL : Returns list of Products (e.g. NIFTY, BANKNIFTY, GAIL, etc.)
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""

async def GetProducts():
    print("----------------------------------------------------")
    print("Work in progress... sending request for GetProducts")
    print("----------------------------------------------------")
    ExchangeName="NFO"
    xml="false"                                        
    response = ""
    strMessage = endpoint+"getproducts/?accessKey="+accesskey+"&exchange="+ExchangeName+"&xml="+xml
    response = requests.get(strMessage)
    print("Message sent : "+strMessage)
    print("Waiting for response...")
    print("Response :\n" + response.text)
    print("----------------------------------------------------")


"""
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	//GetExpiryDates();						//GFDL : Returns array of Expiry Dates (e.g. 25JUN2020, 30JUL2020, etc.)
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""
async def GetExpiryDates():
    print("----------------------------------------------------")
    print("Work in progress... sending request for GetExpiryDates")
    print("----------------------------------------------------")
    ExchangeName="NFO"
    xml="false"                                        
    response = ""
    strMessage = endpoint+"getexpirydates/?accessKey="+accesskey+"&exchange="+ExchangeName+"&xml="+xml
    response = requests.get(strMessage)
    print("Message sent : "+strMessage)
    print("Waiting for response...")
    print("Response :\n" + response.text)
    print("----------------------------------------------------")


"""
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	//GetOptionTypes();			//GFDL : Returns list of Option Types (e.g. CE, PE, etc.)
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""

async def GetOptionTypes():
    print("----------------------------------------------------")
    print("Work in progress... sending request for GetOptionTypes")
    print("----------------------------------------------------")
    ExchangeName="NFO"
    xml="false"                                        
    response = ""
    strMessage = endpoint+"getoptiontypes/?accessKey="+accesskey+"&exchange="+ExchangeName+"&xml="+xml
    response = requests.get(strMessage)
    print("Message sent : "+strMessage)
    print("Waiting for response...")
    print("Response :\n" + response.text)
    print("----------------------------------------------------")


"""
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	//GetStrikePrices();		//GFDL : Returns list of Strike Prices (e.g. 10000, 11000, 75.5, etc.)
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""

async def GetStrikePrices():
    print("----------------------------------------------------")
    print("Work in progress... sending request for GetStrikePrices")
    print("----------------------------------------------------")
    ExchangeName="NFO"
    xml="false"                                        
    response = ""
    strMessage = endpoint+"getstrikeprices/?accessKey="+accesskey+"&exchange="+ExchangeName+"&xml="+xml
    response = requests.get(strMessage)
    print("Message sent : "+strMessage)
    print("Waiting for response...")
    print("Response :\n" + response.text)
    print("----------------------------------------------------")


"""
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	//GetServerInfo();			//GFDL : Returns the server endpoint where user is connected
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""

async def GetServerInfo():
    print("----------------------------------------------------")
    print("Work in progress... sending request for GetServerInfo")
    print("----------------------------------------------------")
    xml="false"                                        
    response = ""
    strMessage = endpoint+"getserverinfo/?accessKey="+accesskey+"&xml="+xml
    response = requests.get(strMessage)
    print("Message sent : "+strMessage)
    print("Waiting for response...")
    print("Response :\n" + response.text)
    print("----------------------------------------------------")


"""
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	//GetLimitation();			//GFDL : Returns user account information (functions allowed, Exchanges allowed, symbol limit, etc.)
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""

async def GetLimitation():
    print("----------------------------------------------------")
    print("Work in progress... sending request for GetLimitation")
    print("----------------------------------------------------")
    xml="false"                                        
    response = ""
    strMessage = endpoint+"getlimitation/?accessKey="+accesskey+"&xml="+xml
    response = requests.get(strMessage)
    print("Message sent : "+strMessage)
    print("Waiting for response...")
    print("Response :\n" + response.text)
    print("----------------------------------------------------")


"""
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	//GetMarketMessages();					//GFDL : Returns array of last messages (Market Messages) related to selected exchange
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""

async def GetMarketMessages():
    print("----------------------------------------------------")
    print("Work in progress... sending request for GetMarketMessages")
    print("----------------------------------------------------")
    ExchangeName="NSE"
    xml="false"                                        
    response = ""
    strMessage = endpoint+"getmarketmessages/?accessKey="+accesskey+"&exchange="+ExchangeName+"&xml="+xml
    response = requests.get(strMessage)
    print("Message sent : "+strMessage)
    print("Waiting for response...")
    print("Response :\n" + response.text)
    print("----------------------------------------------------")


"""
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	//GetExchangeMessages();				//GFDL : Returns array of last messages (Exchange Messages) related to selected exchange
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""

async def GetExchangeMessages():
    print("----------------------------------------------------")
    print("Work in progress... sending request for GetExchangeMessages")
    print("----------------------------------------------------")
    ExchangeName="NSE"
    xml="false"                                        
    response = ""
    strMessage = endpoint+"getexchangemessages/?accessKey="+accesskey+"&exchange="+ExchangeName+"&xml="+xml
    response = requests.get(strMessage)
    print("Message sent : "+strMessage)
    print("Waiting for response...")
    print("Response :\n" + response.text)
    print("----------------------------------------------------")


"""
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	//GetLastQuoteOptionChain();			//GFDL : Returns OptionChain data in realtime
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""

async def GetLastQuoteOptionChain():
    print("----------------------------------------------------")
    print("Work in progress... sending request for GetLastQuoteOptionChain")
    print("----------------------------------------------------")
    ExchangeName = "NFO"				#GFDL : Supported Values : NFO, NSE, NSE_IDX, CDS, MCX. Mandatory Parameter
    product = "RELIANCE"			#GFDL : Mandatory Parameter. Example, RELIANCE, BANKNIFTY, NIFTY
    Expiry = "23JAN2020"			#GFDL : Optional field, in DDMMMYYYY format. If absent, result is sent for all active Expiries
    OptionType = "CE"				#GFDL : Optional field, CE or PE. If absent, result is sent for all Option Types
    StrikePrice = 10000			    #GFDL : Optional field, as a number. If absent, result is sent for all strike prices
    xml="false"                                        
    response = ""
    strMessage = endpoint+"getlastquoteoptionchain/?accessKey="+accesskey+"&exchange="+ExchangeName+"&product="+product+"&xml="+xml
    response = requests.get(strMessage)
    print("Message sent : "+strMessage)
    print("Waiting for response...")
    print("Response :\n" + response.text)
    print("----------------------------------------------------")


"""
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	//GetExchangeSnapshot();				//GFDL : Returns entire Exchange Snapshot in realtime
											// This function can return maximum 5 snapshots in single call. You will need to
											// use "From" and "To" parameters to control the dataset required
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""

async def GetExchangeSnapshot():
    print("----------------------------------------------------")
    print("Work in progress... sending request for GetExchangeSnapshot")
    print("----------------------------------------------------")
    xml="false"                                        
    response = ""
    ExchangeName = "NFO"				#GFDL : Supported Values : NFO, NSE, NSE_IDX, CDS, MCX. Mandatory Parameter
    Periodicity = "Minute"		    #GFDL : Mandatory Parameter. Supported Values : Minute, Hour. Default = Minute
    Period = 1					    #GFDL : Mandatory Parameter. Supported Values : 1,2,5,10,15,30. Default = 1
    InstrumentType = "FUTIDX"	    #GFDL : Optional Parameter. FUTIDX, FUTSTK, OPTIDX, OPTSTK, FUTCOM, FUTCUR, etc. 
                                    #If not mentioned, results are sent for all instrument types
    From: 1567655100			    #GFDL : Epoch value of time in seconds since 1st January 1970. For example, 1567655100 is 
                                    #epoch value for Thursday, September 5, 2019 9:15:00 AM in GMT+05:30 timezone. 
                                    #Optional field to control snapshot start time.
                                    #Please note that max. 5 snapshots are returned in single call
    To: 0			                #GFDL : Epoch value of time in seconds since 1st January 1970. For example, 1567655100 is 
                                    #epoch value for Thursday, September 5, 2019 9:15:00 AM in GMT+05:30 timezone. 
                                    #Optional field to control snapshot end time.
    nonTraded = "false"			    #GFDL : true/false. When true, results are sent with data of even non traded instruments. 
                                    #When false, data of only traded instruments during that period is sent 
                                    #Optional Parameter, default value is "false"
    strMessage = endpoint+"getexchangesnapshot/?accessKey="+accesskey+"&exchange="+ExchangeName+"&period="+f'{Period}'+"&periodicity="+Periodicity+"&xml="+xml
    response = requests.get(strMessage)
    print("Message sent : "+strMessage)
    print("Waiting for response...")
    print("Response :\n" + response.text)
    print("----------------------------------------------------")


"""
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""

async def functionCall():
    if function == "SubscribeSnapshot":
        await SubscribeSnapshot()
    elif function == "SubscribeRealtime":
        await SubscribeRealtime()
    elif function == "GetServerInfo":
        await GetServerInfo()
    elif function == "GetLimitation":
        await GetLimitation()
    elif function == "GetSnapshot":
        await GetSnapshot()
    elif function == "GetLastQuote":
        await GetLastQuote()
    elif function == "GetLastQuoteShort":
        await GetLastQuoteShort()
    elif function == "GetLastQuoteShortWithClose":
        await GetLastQuoteShortWithClose()
    elif function == "GetLastQuoteArray":
        await GetLastQuoteArray()
    elif function == "GetLastQuoteArrayShort":
        await GetLastQuoteArrayShort()
    elif function == "GetLastQuoteArrayShortwithClose":
        await GetLastQuoteArrayShortwithClose()
    elif function == "GetMarketMessages":
        await GetMarketMessages()
    elif function == "GetExchangeMessages":
        await GetExchangeMessages()
    elif function == "GetStrikePrices":
        await GetStrikePrices()
    elif function == "GetOptionTypes":
        await GetOptionTypes()
    elif function == "GetExpiryDates":
        await GetExpiryDates()
    elif function == "GetProducts":
        await GetProducts()
    elif function == "GetInstrumentTypes":
        await GetInstrumentTypes()
    elif function == "GetInstruments":
        await GetInstruments()
    elif function == "GetExchanges":
        await GetExchanges()
    elif function == "GetHistory":
        await GetHistory()
    elif function == "GetInstrumentsOnSearch":
        await GetInstrumentsOnSearch()
    elif function == "GetLastQuoteOptionChain":
        await GetLastQuoteOptionChain()
    elif function == "GetExchangeSnapshot":
        await GetExchangeSnapshot()

asyncio.get_event_loop().run_until_complete(functionCall())
