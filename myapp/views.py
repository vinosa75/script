from django.db.models.query import prefetch_related_objects
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User,auth
from django.shortcuts import redirect,render
from django.contrib import messages
from nsepython import *
import nsepython
from myapp.models import HistoryOIChange,HistoryOITotal,LiveOIChange,LiveOITotal,LiveOITotalAllSymbol,LiveEquityResult

import pandas as pd
from truedata_ws.websocket.TD import TD
from copy import deepcopy
import time
import logging
from datetime import datetime as dt
import datetime
from nsetools import Nse
from nsepython import *
import nsepython

from datetime import timedelta
import websocket
from datetime import date

import random

#<Code>

# Create your views here.
def testhtml(request):
    print(request.GET)
    item = request.GET['symbol']
    counter = request.GET['counter']
    print(item)

    def OITotal(df,item,dte):
        print("inside oitotal")
        print(df)
        ce = df.loc[df['type'] == "CE"]
        pe = df.loc[df['type'] == "PE"]

        column = ce["oi"]
        max_value = column.max()

        cedf1 = ce.loc[ce['oi'] == max_value]
        print(cedf1['strike'].iloc[0])
        pedf1 = pe.loc[pe['strike']==cedf1['strike'].iloc[0]]
        
        if pedf1.empty == True:
            print("dataframe is empty")
            return False


        celtt = cedf1['ltt'].iloc[0]
         
        ceoi1 = cedf1['oi'].iloc[0]
        
        cestrike = cedf1['strike'].iloc[0]
        print(pedf1['oi'])
        peoi1 = pedf1['oi'].iloc[0]

        print("place1 crossed")

        column = pe["oi"]
        max_value = column.max()

        print("max crossed") 

        pedf2 = pe.loc[pe['oi'] == max_value]
        cedf2 = ce.loc[ce['strike']==pedf2['strike'].iloc[0]]

        if cedf2.empty == True:
            print("dataframe is empty")
            return False

        print("cedf2 crossed") 

        peltt = pedf2['ltt'].iloc[0]
        peoi2 = pedf2['oi'].iloc[0]
        pestrike = pedf2['strike'].iloc[0]
        ceoi2 = cedf2['oi'].iloc[0]

        print("ceoi2 crossed") 
        OITot = {"celtt":celtt,"ceoi1":ceoi1,"cestrike":cestrike,"peoi1":peoi1,"peltt":peltt,"peoi2":peoi2,"pestrike":pestrike,"ceoi2":ceoi2}
        
        return OITot

    # Calculation of Change in OI
    def OIChange(df,item,dte):


        ce = df.loc[df['type'] == "CE"]
        pe = df.loc[df['type'] == "PE"]

        column = ce["oi_change"]
        max_value = column.max()

        cedf1 = ce.loc[ce['oi_change'] == max_value]

        print(cedf1['strike'].iloc[0])

        pedf1 = pe.loc[pe['strike']==cedf1['strike'].iloc[0]]

        if pedf1.empty == True:
            print("dataframe is empty")
            return False

        celtt = cedf1['ltt'].iloc[0]
        ceoi1 = cedf1['oi_change'].iloc[0]
        cestrike = cedf1['strike'].iloc[0]
        peoi1 = pedf1['oi_change'].iloc[0]

        column = pe["oi_change"]
        max_value = column.max()

        pedf2 = pe.loc[pe['oi_change'] == max_value]
        cedf2 = ce.loc[ce['strike']==pedf2['strike'].iloc[0]]
        
        if cedf2.empty == True:
            print("dataframe is empty")
            return False

        print("change started 3")

        peltt = pedf2['ltt'].iloc[0]
        print("change started 4")
        peoi2 = pedf2['oi_change'].iloc[0]
        print("change started 5")
        pestrike = pedf2['strike'].iloc[0]
        print("change started 6")
        print(cedf2)
        ceoi2 = cedf2['oi_change'].iloc[0]
        print("change started 7")

        

        OIChan = {"celtt":celtt,"ceoi1":ceoi1,"cestrike":cestrike,"peoi1":peoi1,"peltt":peltt,"peoi2":peoi2,"pestrike":pestrike,"ceoi2":ceoi2}
        
        return OIChan

    # Fetching the F&NO symbol list
    TrueDatausername = 'tdws135'
    TrueDatapassword = 'saaral@135'

    import pendulum
    import calendar
    from datetime import date

    sampleDict = {}
    count=1

    # LiveEquityResult.objects.all().delete()
    # sym = list(LiveOITotal.objects.values_list('symbol', flat=True))

    exceptionList = ['NIFTY','BANKNIFTY','FINNIFTY']
    # if item not in sym:
    try:
        if item in exceptionList:
                if calendar.day_name[date.today().weekday()] == "Thrusday":
                    expiry = date.today()
                    dte = datetime.datetime.strptime(expiry, '%d-%b-%Y')
                else:
                    expiry = pendulum.now().next(pendulum.THURSDAY).strftime('%d-%b-%Y')
                    dte = datetime.datetime.strptime(expiry, '%d-%b-%Y')
        else:
            expiry = "30-Sep-2021"
            dte = datetime.datetime.strptime(expiry, '%d-%b-%Y')

        td_obj = TD(TrueDatausername, TrueDatapassword, log_level= logging.WARNING )
        nifty_chain = td_obj.start_option_chain(item , dt(dte.year,dte.month,dte.day),chain_length=80,bid_ask=True)
        time.sleep(4)
        df = nifty_chain.get_option_chain()

        nifty_chain.stop_option_chain()
        td_obj.disconnect()
        sampleDict[item] = df

        print(count)
        print(item)
        count = count + 1

        # Total OI Calculation from Option chain
        FutureData = {}

        # value1 = LiveOIChange.objects.all()
        # value2 = LiveOITotal.objects.all()

        OIChangeValue = OIChange(df,item,dte)
        
        if OIChangeValue == False:
            return render(request,"testhtml.html",{'symbol':item,'counter':counter})

        OITotalValue = OITotal(df,item,dte)

        if OITotalValue == False:
            return render(request,"testhtml.html",{'symbol':item,'counter':counter})


        strikeGap =float(df['strike'].unique()[1]) - float(df['strike'].unique()[0])

        FutureData[item] = [OITotalValue['cestrike'],OITotalValue['pestrike'],strikeGap]

        print(FutureData)

        print("strike gap crossed")

        # Percentage calculation from equity data
        newDict = {}
        # for key,value in FutureData.items():
        # Call 1 percent 
        callone = float(OITotalValue['cestrike']) - (float(strikeGap))*0.1
        # Call 1/2 percent 
        callhalf = float(OITotalValue['cestrike']) - (float(strikeGap))*0.05
        # Put 1 percent
        putone = float(OITotalValue['pestrike']) + (float(strikeGap))*0.1
        # Put 1/2 percent
        puthalf = float(OITotalValue['pestrike']) + (float(strikeGap))*0.05

        newDict[item] = [float(OITotalValue['cestrike']),float(OITotalValue['pestrike']),callone,putone,callhalf,puthalf]
        
        print("equity calculation crossed")
        # # Fetching today's date
        dat = dt.today()
        # # Deleting past historical data in the database
        HistoryOIChange.objects.filter(time__lte = dt.combine(dat, dt.min.time())).delete()
        HistoryOITotal.objects.filter(time__lte = dt.combine(dat, dt.min.time())).delete()
        
        value1 = LiveOIChange.objects.filter(symbol=item)


        if len(value1) > 0:

            if (value1[0].callstrike != OIChangeValue['cestrike']) or (value1[0].putstrike != OIChangeValue['pestrike']):
                # Adding to history table
                ChangeOIHistory = HistoryOIChange(time=value1[0].time,call1=value1[0].call1,call2=value1[0].call2,put1=value1[0].put1,put2=value1[0].put2,callstrike=value1[0].callstrike,putstrike=value1[0].putstrike,symbol=value1[0].symbol,expiry=value1[0].expiry)
                ChangeOIHistory.save()

                # deleting live table data
                value1 = LiveOIChange.objects.filter(symbol=item).delete()

                # Creating in live data
                ChangeOICreation = LiveOIChange(time=OIChangeValue['celtt'],call1=OIChangeValue['ceoi1'],call2=OIChangeValue['ceoi2'],put1=OIChangeValue['peoi1'],put2=OIChangeValue['peoi2'],callstrike=OIChangeValue['cestrike'],putstrike=OIChangeValue['pestrike'],symbol=item,expiry=dte)
                ChangeOICreation.save() 

            else:
                # deleting live table data
                value1 = LiveOIChange.objects.filter(symbol=item).delete()

                # Creating in live data
                ChangeOICreation = LiveOIChange(time=OIChangeValue['celtt'],call1=OIChangeValue['ceoi1'],call2=OIChangeValue['ceoi2'],put1=OIChangeValue['peoi1'],put2=OIChangeValue['peoi2'],callstrike=OIChangeValue['cestrike'],putstrike=OIChangeValue['pestrike'],symbol=item,expiry=dte)
                ChangeOICreation.save() 
        else:
            ChangeOICreation = LiveOIChange(time=OIChangeValue['celtt'],call1=OIChangeValue['ceoi1'],call2=OIChangeValue['ceoi2'],put1=OIChangeValue['peoi1'],put2=OIChangeValue['peoi2'],callstrike=OIChangeValue['cestrike'],putstrike=OIChangeValue['pestrike'],symbol=item,expiry=dte)
            ChangeOICreation.save()


        print("value1 crossed")

        value2 = LiveOITotal.objects.filter(symbol=item)

        if len(value2) > 0:

            if (value2[0].callstrike != OITotalValue['cestrike']) or (value2[0].putstrike != OITotalValue['pestrike']):
                # Adding to history table
                TotalOIHistory = HistoryOITotal(time=value2[0].time,call1=value2[0].call1,call2=value2[0].call2,put1=value2[0].put1,put2=value2[0].put2,callstrike=value2[0].callstrike,putstrike=value2[0].putstrike,symbol=value2[0].symbol,expiry=value2[0].expiry)
                TotalOIHistory.save()

                # deleting live table data
                value1 = LiveOITotal.objects.filter(symbol=item).delete()

                # Creating in live data
                TotalOICreation = LiveOITotal(time=OITotalValue['celtt'],call1=OITotalValue['ceoi1'],call2=OITotalValue['ceoi2'],put1=OITotalValue['peoi1'],put2=OITotalValue['peoi2'],callstrike=OITotalValue['cestrike'],putstrike=OITotalValue['pestrike'],symbol=item,expiry=dte,strikegap=strikeGap)
                TotalOICreation.save()

                # Live data for equity
                LiveOITotalAllSymbol.objects.filter(symbol=item).delete()
                TotalOICreationAll = LiveOITotalAllSymbol(time=OITotalValue['celtt'],call1=OITotalValue['ceoi1'],call2=OITotalValue['ceoi2'],put1=OITotalValue['peoi1'],put2=OITotalValue['peoi2'],callstrike=OITotalValue['cestrike'],putstrike=OITotalValue['pestrike'],symbol=item,expiry=dte,callone=callone,putone=putone,callhalf=callhalf,puthalf=puthalf)
                TotalOICreationAll.save()


            else:
                # deleting live table data
                value1 = LiveOITotal.objects.filter(symbol=item).delete()

                # Creating in live data
                TotalOICreation = LiveOITotal(time=OITotalValue['celtt'],call1=OITotalValue['ceoi1'],call2=OITotalValue['ceoi2'],put1=OITotalValue['peoi1'],put2=OITotalValue['peoi2'],callstrike=OITotalValue['cestrike'],putstrike=OITotalValue['pestrike'],symbol=item,expiry=dte,strikegap=strikeGap)
                TotalOICreation.save()

                # Live data for equity
                LiveOITotalAllSymbol.objects.filter(symbol=item).delete()
                TotalOICreationAll = LiveOITotalAllSymbol(time=OITotalValue['celtt'],call1=OITotalValue['ceoi1'],call2=OITotalValue['ceoi2'],put1=OITotalValue['peoi1'],put2=OITotalValue['peoi2'],callstrike=OITotalValue['cestrike'],putstrike=OITotalValue['pestrike'],symbol=item,expiry=dte,callone=callone,putone=putone,callhalf=callhalf,puthalf=puthalf)
                TotalOICreationAll.save()

        else:
            TotalOICreation = LiveOITotal(time=OITotalValue['celtt'],call1=OITotalValue['ceoi1'],call2=OITotalValue['ceoi2'],put1=OITotalValue['peoi1'],put2=OITotalValue['peoi2'],callstrike=OITotalValue['cestrike'],putstrike=OITotalValue['pestrike'],symbol=item,expiry=dte,strikegap=strikeGap)
            TotalOICreation.save()

            # Live data for equity
            LiveOITotalAllSymbol.objects.filter(symbol=item).delete()
            TotalOICreationAll = LiveOITotalAllSymbol(time=OITotalValue['celtt'],call1=OITotalValue['ceoi1'],call2=OITotalValue['ceoi2'],put1=OITotalValue['peoi1'],put2=OITotalValue['peoi2'],callstrike=OITotalValue['cestrike'],putstrike=OITotalValue['pestrike'],symbol=item,expiry=dte,callone=callone,putone=putone,callhalf=callhalf,puthalf=puthalf)
            TotalOICreationAll.save()

        print("value2 crossed")

    except websocket.WebSocketConnectionClosedException as e:
        print('This caught the websocket exception ')
        td_obj.disconnect()
        return render(request,"testhtml.html",{'symbol':item,'counter':counter}) 
    except IndexError as e:
        print('This caught the exception')
        td_obj.disconnect()
        return render(request,"testhtml.html",{'symbol':item,'counter':counter}) 
    except Exception:
        print("Exception")
        td_obj.disconnect()
        return render(request,"testhtml.html",{'symbol':item,'counter':counter}) 

    return render(request,"testhtml.html",{'symbol':item,'counter':counter}) 

def optionChainClick(request):

    nse = Nse()
    fnolist = nse.get_fno_lot_sizes()

    remove_list = ['HEROMOTOCO','PFC','BEL','MANAPPURAM','EXIDEIND','PETRONET', 'TATAPOWER', 'ONGC', 'VEDL', 'LALPATHLAB', 'ITC', 'INDHOTEL', 'IDEA','POWERGRID', 'COALINDIA', 'CANBK','HINDPETRO','BANKBARODA','RECLTD','CUB']
    # remove_list = []
    fnolist = [i for i in fnolist if i not in remove_list]

    return render(request,"optionChainProgress.html",{'fnolist':fnolist}) 


def mainView(request):
    nse = Nse()
    fnolist = nse.get_fno_lot_sizes()
    print(len(fnolist))
    return render(request,"main.html",{'fnolist':fnolist})


def ajaxNot1(request):
    
    n1 = random.randint(20,30)
    print(n1)

    def OITotal(df,item,dte):
        print("inside oitotal")
        print(df)
        ce = df.loc[df['type'] == "CE"]
        pe = df.loc[df['type'] == "PE"]

        column = ce["oi"]
        max_value = column.max()

        cedf1 = ce.loc[ce['oi'] == max_value]
        print(cedf1['strike'].iloc[0])
        pedf1 = pe.loc[pe['strike']==cedf1['strike'].iloc[0]]
        
        if pedf1.empty == True:
            print("dataframe is empty")
            return False


        celtt = cedf1['ltt'].iloc[0]
         
        ceoi1 = cedf1['oi'].iloc[0]
        
        cestrike = cedf1['strike'].iloc[0]
        print(pedf1['oi'])
        peoi1 = pedf1['oi'].iloc[0]

        print("place1 crossed")

        column = pe["oi"]
        max_value = column.max()

        print("max crossed") 

        pedf2 = pe.loc[pe['oi'] == max_value]
        cedf2 = ce.loc[ce['strike']==pedf2['strike'].iloc[0]]

        if cedf2.empty == True:
            print("dataframe is empty")
            return False

        print("cedf2 crossed") 

        peltt = pedf2['ltt'].iloc[0]
        peoi2 = pedf2['oi'].iloc[0]
        pestrike = pedf2['strike'].iloc[0]
        ceoi2 = cedf2['oi'].iloc[0]

        print("ceoi2 crossed") 
        OITot = {"celtt":celtt,"ceoi1":ceoi1,"cestrike":cestrike,"peoi1":peoi1,"peltt":peltt,"peoi2":peoi2,"pestrike":pestrike,"ceoi2":ceoi2}
        
        return OITot

    # Calculation of Change in OI
    def OIChange(df,item,dte):


        ce = df.loc[df['type'] == "CE"]
        pe = df.loc[df['type'] == "PE"]

        column = ce["oi_change"]
        max_value = column.max()

        cedf1 = ce.loc[ce['oi_change'] == max_value]

        print(cedf1['strike'].iloc[0])

        pedf1 = pe.loc[pe['strike']==cedf1['strike'].iloc[0]]

        if pedf1.empty == True:
            print("dataframe is empty")
            return False

        celtt = cedf1['ltt'].iloc[0]
        ceoi1 = cedf1['oi_change'].iloc[0]
        cestrike = cedf1['strike'].iloc[0]
        peoi1 = pedf1['oi_change'].iloc[0]

        column = pe["oi_change"]
        max_value = column.max()

        pedf2 = pe.loc[pe['oi_change'] == max_value]
        cedf2 = ce.loc[ce['strike']==pedf2['strike'].iloc[0]]
        
        if cedf2.empty == True:
            print("dataframe is empty")
            return False

        print("change started 3")

        peltt = pedf2['ltt'].iloc[0]
        print("change started 4")
        peoi2 = pedf2['oi_change'].iloc[0]
        print("change started 5")
        pestrike = pedf2['strike'].iloc[0]
        print("change started 6")
        print(cedf2)
        ceoi2 = cedf2['oi_change'].iloc[0]
        print("change started 7")

        

        OIChan = {"celtt":celtt,"ceoi1":ceoi1,"cestrike":cestrike,"peoi1":peoi1,"peltt":peltt,"peoi2":peoi2,"pestrike":pestrike,"ceoi2":ceoi2}
        
        return OIChan

    # Fetching the F&NO symbol list
    TrueDatausername = 'tdws127'
    TrueDatapassword = 'saaral@127'

    print("Before nse")

    nse = Nse()
    fnolist = nse.get_fno_lot_sizes()
    
    print("After nse")

    # Removing 3 symbols from the list as they are not required for equity comparision
    
    remove_list = ['HEROMOTOCO','PFC','BEL','MANAPPURAM','EXIDEIND','PETRONET', 'TATAPOWER', 'ONGC', 'VEDL', 'LALPATHLAB', 'ITC', 'INDHOTEL', 'IDEA','POWERGRID', 'COALINDIA', 'CANBK','HINDPETRO','BANKBARODA','RECLTD','CUB']
    # remove_list = []
    fnolist = [i for i in fnolist if i not in remove_list]

    fnolist = ['MRF']

    # Taking the first date from the expiry list.
    # print(fnolist)

    print("Before expiry")


    import pendulum
    import calendar
    from datetime import date

    ex_list = nsepython.expiry_list('NIFTY')
    print(ex_list)
    expiry = ex_list[0]
    print(expiry)

    dte = datetime.datetime.strptime(expiry, '%d-%b-%Y')

    sampleDict = {}
    count=1

    print("After expiry")
    # fnolist = fnolist[5:10]
    print(fnolist)

    
    # LiveEquityResult.objects.all().delete()
    # sym = list(LiveOITotal.objects.values_list('symbol', flat=True))

    exceptionList = ['NIFTY','BANKNIFTY','FINNIFTY']
    for item in fnolist :
        # if item not in sym:
        try:
            if item in exceptionList:
                    if calendar.day_name[date.today().weekday()] == "Thrusday":
                        expiry = date.today()
                        dte = datetime.datetime.strptime(expiry, '%d-%b-%Y')
                    else:
                        expiry = pendulum.now().next(pendulum.THURSDAY).strftime('%d-%b-%Y')
                        dte = datetime.datetime.strptime(expiry, '%d-%b-%Y')
            else:
                expiry = "30-Sep-2021"
                dte = datetime.datetime.strptime(expiry, '%d-%b-%Y')

            td_obj = TD(TrueDatausername, TrueDatapassword, log_level= logging.WARNING )
            nifty_chain = td_obj.start_option_chain(item , dt(dte.year,dte.month,dte.day),chain_length=50,bid_ask=True)
            time.sleep(4)
            df = nifty_chain.get_option_chain()

            nifty_chain.stop_option_chain()
            td_obj.disconnect()
            sampleDict[item] = df

            print(count)
            print(item)
            count = count + 1

            # Total OI Calculation from Option chain
            FutureData = {}

            # value1 = LiveOIChange.objects.all()
            # value2 = LiveOITotal.objects.all()

            OIChangeValue = OIChange(df,item,dte)
            
            if OIChangeValue == False:
                continue

            OITotalValue = OITotal(df,item,dte)

            if OITotalValue == False:
                continue


            # StrikeGap
            # Fourrows = df.iloc[:4]
            # print(Fourrows)
            # CEFiltered = Fourrows[Fourrows["type"] == "CE"]
            # print(CEFiltered)
            # strikeGap = float(CEFiltered.iloc[1]["strike"]) - float(CEFiltered.iloc[0]["strike"])
            # print(strikeGap)
            strikeGap =float(df['strike'].unique()[1]) - float(df['strike'].unique()[0])

            FutureData[item] = [OITotalValue['cestrike'],OITotalValue['pestrike'],strikeGap]

            print(FutureData)

            print("strike gap crossed")

            # Percentage calculation from equity data
            newDict = {}
            # for key,value in FutureData.items():
            # Call 1 percent 
            callone = float(OITotalValue['cestrike']) - (float(strikeGap))*0.1
            # Call 1/2 percent 
            callhalf = float(OITotalValue['cestrike']) - (float(strikeGap))*0.05
            # Put 1 percent
            putone = float(OITotalValue['pestrike']) + (float(strikeGap))*0.1
            # Put 1/2 percent
            puthalf = float(OITotalValue['pestrike']) + (float(strikeGap))*0.05

            newDict[item] = [float(OITotalValue['cestrike']),float(OITotalValue['pestrike']),callone,putone,callhalf,puthalf]
            
            print("equity calculation crossed")
            # # Fetching today's date
            dat = dt.today()
            # # Deleting past historical data in the database
            HistoryOIChange.objects.filter(time__lte = dt.combine(dat, dt.min.time())).delete()
            HistoryOITotal.objects.filter(time__lte = dt.combine(dat, dt.min.time())).delete()
            
            value1 = LiveOIChange.objects.filter(symbol=item)


            if len(value1) > 0:

                if (value1[0].callstrike != OIChangeValue['cestrike']) or (value1[0].putstrike != OIChangeValue['pestrike']):
                    # Adding to history table
                    ChangeOIHistory = HistoryOIChange(time=value1[0].time,call1=value1[0].call1,call2=value1[0].call2,put1=value1[0].put1,put2=value1[0].put2,callstrike=value1[0].callstrike,putstrike=value1[0].putstrike,symbol=value1[0].symbol,expiry=value1[0].expiry)
                    ChangeOIHistory.save()

                    # deleting live table data
                    value1 = LiveOIChange.objects.filter(symbol=item).delete()

                    # Creating in live data
                    ChangeOICreation = LiveOIChange(time=OIChangeValue['celtt'],call1=OIChangeValue['ceoi1'],call2=OIChangeValue['ceoi2'],put1=OIChangeValue['peoi1'],put2=OIChangeValue['peoi2'],callstrike=OIChangeValue['cestrike'],putstrike=OIChangeValue['pestrike'],symbol=item,expiry=dte)
                    ChangeOICreation.save() 

                else:
                    # deleting live table data
                    value1 = LiveOIChange.objects.filter(symbol=item).delete()

                    # Creating in live data
                    ChangeOICreation = LiveOIChange(time=OIChangeValue['celtt'],call1=OIChangeValue['ceoi1'],call2=OIChangeValue['ceoi2'],put1=OIChangeValue['peoi1'],put2=OIChangeValue['peoi2'],callstrike=OIChangeValue['cestrike'],putstrike=OIChangeValue['pestrike'],symbol=item,expiry=dte)
                    ChangeOICreation.save() 
            else:
                ChangeOICreation = LiveOIChange(time=OIChangeValue['celtt'],call1=OIChangeValue['ceoi1'],call2=OIChangeValue['ceoi2'],put1=OIChangeValue['peoi1'],put2=OIChangeValue['peoi2'],callstrike=OIChangeValue['cestrike'],putstrike=OIChangeValue['pestrike'],symbol=item,expiry=dte)
                ChangeOICreation.save()


            print("value1 crossed")

            value2 = LiveOITotal.objects.filter(symbol=item)

            if len(value2) > 0:

                if (value2[0].callstrike != OITotalValue['cestrike']) or (value2[0].putstrike != OITotalValue['pestrike']):
                    # Adding to history table
                    TotalOIHistory = HistoryOITotal(time=value2[0].time,call1=value2[0].call1,call2=value2[0].call2,put1=value2[0].put1,put2=value2[0].put2,callstrike=value2[0].callstrike,putstrike=value2[0].putstrike,symbol=value2[0].symbol,expiry=value2[0].expiry)
                    TotalOIHistory.save()

                    # deleting live table data
                    value1 = LiveOITotal.objects.filter(symbol=item).delete()

                    # Creating in live data
                    TotalOICreation = LiveOITotal(time=OITotalValue['celtt'],call1=OITotalValue['ceoi1'],call2=OITotalValue['ceoi2'],put1=OITotalValue['peoi1'],put2=OITotalValue['peoi2'],callstrike=OITotalValue['cestrike'],putstrike=OITotalValue['pestrike'],symbol=item,expiry=dte)
                    TotalOICreation.save()

                    # Live data for equity
                    LiveOITotalAllSymbol.objects.filter(symbol=item).delete()
                    TotalOICreationAll = LiveOITotalAllSymbol(time=OITotalValue['celtt'],call1=OITotalValue['ceoi1'],call2=OITotalValue['ceoi2'],put1=OITotalValue['peoi1'],put2=OITotalValue['peoi2'],callstrike=OITotalValue['cestrike'],putstrike=OITotalValue['pestrike'],symbol=item,expiry=dte,callone=callone,putone=putone,callhalf=callhalf,puthalf=puthalf)
                    TotalOICreationAll.save()


                else:
                    # deleting live table data
                    value1 = LiveOITotal.objects.filter(symbol=item).delete()

                    # Creating in live data
                    TotalOICreation = LiveOITotal(time=OITotalValue['celtt'],call1=OITotalValue['ceoi1'],call2=OITotalValue['ceoi2'],put1=OITotalValue['peoi1'],put2=OITotalValue['peoi2'],callstrike=OITotalValue['cestrike'],putstrike=OITotalValue['pestrike'],symbol=item,expiry=dte)
                    TotalOICreation.save()

                    # Live data for equity
                    LiveOITotalAllSymbol.objects.filter(symbol=item).delete()
                    TotalOICreationAll = LiveOITotalAllSymbol(time=OITotalValue['celtt'],call1=OITotalValue['ceoi1'],call2=OITotalValue['ceoi2'],put1=OITotalValue['peoi1'],put2=OITotalValue['peoi2'],callstrike=OITotalValue['cestrike'],putstrike=OITotalValue['pestrike'],symbol=item,expiry=dte,callone=callone,putone=putone,callhalf=callhalf,puthalf=puthalf)
                    TotalOICreationAll.save()

            else:
                TotalOICreation = LiveOITotal(time=OITotalValue['celtt'],call1=OITotalValue['ceoi1'],call2=OITotalValue['ceoi2'],put1=OITotalValue['peoi1'],put2=OITotalValue['peoi2'],callstrike=OITotalValue['cestrike'],putstrike=OITotalValue['pestrike'],symbol=item,expiry=dte)
                TotalOICreation.save()

                # Live data for equity
                LiveOITotalAllSymbol.objects.filter(symbol=item).delete()
                TotalOICreationAll = LiveOITotalAllSymbol(time=OITotalValue['celtt'],call1=OITotalValue['ceoi1'],call2=OITotalValue['ceoi2'],put1=OITotalValue['peoi1'],put2=OITotalValue['peoi2'],callstrike=OITotalValue['cestrike'],putstrike=OITotalValue['pestrike'],symbol=item,expiry=dte,callone=callone,putone=putone,callhalf=callhalf,puthalf=puthalf)
                TotalOICreationAll.save()

            print("value2 crossed")

        except websocket.WebSocketConnectionClosedException as e:
            print('This caught the websocket exception ')
            td_obj.disconnect()
            continue
        except IndexError as e:
            print('This caught the exception')
            td_obj.disconnect()
            continue
        except Exception:
                print("Exception")
                td_obj.disconnect()
                continue


    return render(request,"notification1.html",{"n1":n1})

def ajaxNot2(request):
    n2 = random.randint(50,60)
    print(n2)
    
    # TrueDatausername = 'wssand020'
    # TrueDatapassword = 'vinosa020'

    TrueDatausername = 'tdws127'
    TrueDatapassword = 'saaral@127'

    nse = Nse()
    fnolist = nse.get_fno_lot_sizes()

    symbols = list(fnolist.keys())

    # Default production port is 8082 in the library. Other ports may be given t oyou during trial.
    realtime_port = 8082

    td_app = TD(TrueDatausername, TrueDatapassword, live_port=realtime_port, historical_api=False)

    print('Starting Real Time Feed.... ')
    print(f'Port > {realtime_port}')

    req_ids = td_app.start_live_data(symbols)
    live_data_objs = {}

    time.sleep(1)

    liveData = {}
    for req_id in req_ids:
        # print(td_app.live_data[req_id])
        if (td_app.live_data[req_id].ltp) == None:
            continue
        else:
            liveData[td_app.live_data[req_id].symbol] = [td_app.live_data[req_id].ltp,td_app.live_data[req_id].day_open,td_app.live_data[req_id].day_high,td_app.live_data[req_id].day_low,td_app.live_data[req_id].prev_day_close,dt.now().strftime('%H:%M:%S')]

    td_app.disconnect()

    callOnePercent = {}
    putOnePercent = {}
    callHalfPercent = {}
    putHalfPercent = {}
    callCrossed = {}
    putCrossed = {}

    print()

    
    # LiveEquityResult.objects.all().delete()
    LiveEquityResult.objects.filter(date__lte = date.today()).delete()

    for e in LiveOITotalAllSymbol.objects.all():
        print(e.symbol)

        removeList = ["NIFTY","BANKNIFTY","FINNIFTY"]
        
        if e.symbol in liveData and e.symbol not in removeList:
            # Call
            print(liveData[e.symbol])
            print(liveData[e.symbol][0])

            if liveData[e.symbol][0] > float(e.callstrike):
                if LiveEquityResult.objects.filter(symbol=e.symbol,strike="Call Crossed").exists():
                    pass
                else:
                    print("Call crossed")
                    callCrossed[e.symbol] = liveData[e.symbol]
                    print(liveData[e.symbol])
                    print(liveData[e.symbol][0])
                    print(liveData[e.symbol][1])
                    print(liveData[e.symbol][2])
                    print(liveData[e.symbol][3])
                    print(liveData[e.symbol][4])
                    callcross = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Call Crossed",time=liveData[e.symbol][5],date=date.today())
                    callcross.save()
                
            elif liveData[e.symbol][0] >= float(e.callone) and liveData[e.symbol][0] <= float(e.callstrike):
                if LiveEquityResult.objects.filter(symbol=e.symbol,strike="Call Crossed").exists():
                    pass
                else:
                    if LiveEquityResult.objects.filter(symbol=e.symbol,strike="Call 1 percent").exists():
                        pass
                    else:
                        print("Call 1 percent")
                        callOnePercent[e.symbol] = liveData[e.symbol]
                        callone = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Call 1 percent",time=liveData[e.symbol][5],date=date.today())
                        callone.save()

            elif liveData[e.symbol][0] >= float(e.callhalf) and liveData[e.symbol][0] <= float(e.callstrike):
                if LiveEquityResult.objects.filter(symbol=e.symbol,strike="Call Crossed").exists():
                    pass
                else:
                    if LiveEquityResult.objects.filter(symbol=e.symbol,strike="Call 1/2 percent").exists():
                        pass
                    else:
                        print("Call 1/2 percent")
                        callHalfPercent[e.symbol] = liveData[e.symbol]
                        callhalf = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Call 1/2 percent",time=liveData[e.symbol][5],date=date.today())
                        callhalf.save()

            # Put
            elif liveData[e.symbol][0] < float(e.putstrike):
                if LiveEquityResult.objects.filter(symbol=e.symbol,strike="Put Crossed").exists():
                    pass
                else:
                    print("Put crossed")
                    putCrossed[e.symbol] = liveData[e.symbol]
                    putcross = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Put crossed",time=liveData[e.symbol][5],date=date.today())
                    putcross.save()

            elif liveData[e.symbol][0] <= float(e.putone) and liveData[e.symbol][0] >= float(e.putstrike):
                if LiveEquityResult.objects.filter(symbol=e.symbol,strike="Put Crossed").exists():
                    pass
                else:
                    if LiveEquityResult.objects.filter(symbol=e.symbol,strike="Put 1 percent").exists():
                        pass
                    else:
                        print("Put 1 percent")
                        putOnePercent[e.symbol] = liveData[e.symbol]
                        putone = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Put 1 percent",time=liveData[e.symbol][5],date=date.today())
                        putone.save()
                        print("saved")

            elif liveData[e.symbol][0] <= float(e.puthalf) and liveData[e.symbol][0] >= float(e.putstrike):
                if LiveEquityResult.objects.filter(symbol=e.symbol,strike="Put Crossed").exists():
                    pass
                else:
                    if LiveEquityResult.objects.filter(symbol=e.symbol,strike="Put 1/2 percent").exists():
                        pass
                    else:
                        print("Put 1/2 percent")
                        putHalfPercent[e.symbol] = liveData[e.symbol]
                        puthalf = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Put 1/2 percent",time=liveData[e.symbol][5],date=date.today())
                        puthalf.save()

    OITotalValue ={}
    OIChangeValue = {}
    value1 = {}
    value2 = {}
    strikeGap = {}
    callOnePercent = LiveEquityResult.objects.filter(strike="Call 1 percent")
    putOnePercent = LiveEquityResult.objects.filter(strike="Put 1 percent")
    callHalfPercent = LiveEquityResult.objects.filter(strike="Call 1/2 percent")
    putHalfPercent = LiveEquityResult.objects.filter(strike="Put 1/2 percent")
    callCrossed = LiveEquityResult.objects.filter(strike="Call Crossed")
    putCrossed = LiveEquityResult.objects.filter(strike="Put Crossed")

    return render(request,"notification2.html",{"n2":n2,'OITotalValue': OITotalValue,'OIChangeValue': OIChangeValue,'value1':value1,'value2':value2,'strikeGap':strikeGap,'callOnePercent':callOnePercent,'putOnePercent':putOnePercent,'callCrossed':callCrossed,'putCrossed':putCrossed,'putHalfPercent':putHalfPercent,'callHalfPercent':callHalfPercent})

def selected_equity(request):

    # # Fetching today's date
    # dat = dt.today()

    # # Deleting past historical data in the database
    # HistoryOIChange.objects.filter(time__lte = dt.combine(dat, dt.min.time())).delete()
    # HistoryOITotal.objects.filter(time__lte = dt.combine(dat, dt.min.time())).delete()

    # # Getting the Symbol & Expiry selected by user.
    # print(request)

    # symbol = request.POST['symbol']
    # expiry = request.POST['expiry_selected']

    # # Converting the expiry date format to required format to store in DB  
    # new_date=datetime.datetime.strptime(expiry, '%d-%b-%Y').strftime('%Y-%m-%d')

    # TrueDatausername = 'tdws127'
    # TrueDatapassword = 'saaral@127'
    # td_obj = TD(TrueDatausername, TrueDatapassword , log_level= logging.WARNING )

    # # Changing the expiry dateformat
    # # Fetching the option chain data
    # dte = datetime.datetime.strptime(expiry, '%d-%b-%Y')
    # nifty_chain = td_obj.start_option_chain( symbol, dt(dte.year,dte.month,dte.day),chain_length = 50,bid_ask=True)
    # time.sleep(3)
    # print("Getting option chain")
    # df = nifty_chain.get_option_chain()

    # # calculating the strike gap
    # Fourrows = df.iloc[:4]
    # CEFiltered = Fourrows[Fourrows["type"] == "CE"]
    # strikeGap = int(CEFiltered.iloc[1]["strike"]) - int(CEFiltered.iloc[0]["strike"])

    # # Disconnecting user
    # td_obj.disconnect()

    # #  Calcuation of Total OI
    # def OITotal():
    #     print(df)
    #     ce = df.loc[df['type'] == "CE"]
    #     pe = df.loc[df['type'] == "PE"]

    #     column = ce["oi"]
    #     max_value = column.max()

    #     cedf1 = ce.loc[ce['oi'] == max_value]
    #     pedf1 = pe.loc[(pe['strike']==cedf1['strike'].iloc[0])]
    #     print(pedf1)    


    #     celtt = cedf1['ltt'].iloc[0]
    #     ceoi1 = cedf1['oi'].iloc[0]
    #     cestrike = cedf1['strike'].iloc[0]
    #     peoi1 = pedf1['oi'].iloc[0]

    #     column = pe["oi"]
    #     max_value = column.max()

    #     pedf2 = pe.loc[pe['oi'] == max_value]
    #     cedf2 = ce.loc[(ce['strike']==pedf2['strike'].iloc[0])]

    #     peltt = pedf2['ltt'].iloc[0]
    #     peoi2 = pedf2['oi'].iloc[0]
    #     pestrike = pedf2['strike'].iloc[0]
    #     ceoi2 = cedf2['oi'].iloc[0]

    #     OITot = {"celtt":celtt,"ceoi1":ceoi1,"cestrike":cestrike,"peoi1":peoi1,"peltt":peltt,"peoi2":peoi2,"pestrike":pestrike,"ceoi2":ceoi2}
        
    #     value2 = LiveOITotal.objects.all()
    #     print(value2)

    #     if len(value2) > 0:

    #         if (value2[0].callstrike != cestrike) or (value2[0].putstrike != pestrike):
    #             # Adding to history table
    #             TotalOIHistory = HistoryOITotal(time=value2[0].time,call1=value2[0].call1,call2=value2[0].call2,put1=value2[0].put1,put2=value2[0].put2,callstrike=value2[0].callstrike,putstrike=value2[0].putstrike,symbol=value2[0].symbol,expiry=value2[0].expiry)
    #             TotalOIHistory.save()

    #             # deleting live table data
    #             value1 = LiveOITotal.objects.all().delete()

    #             # Creating in live data
    #             TotalOICreation = LiveOITotal(time=celtt,call1=ceoi1,call2=ceoi2,put1=peoi1,put2=peoi2,callstrike=cestrike,putstrike=pestrike,symbol=symbol,expiry=new_date)
    #             TotalOICreation.save() 

    #         else:
    #             # deleting live table data
    #             value1 = LiveOITotal.objects.all().delete()

    #             # Creating in live data
    #             TotalOICreation = LiveOITotal(time=celtt,call1=ceoi1,call2=ceoi2,put1=peoi1,put2=peoi2,callstrike=cestrike,putstrike=pestrike,symbol=symbol,expiry=new_date)
    #             TotalOICreation.save()
    #     else:
    #         TotalOICreation = LiveOITotal(time=celtt,call1=ceoi1,call2=ceoi2,put1=peoi1,put2=peoi2,callstrike=cestrike,putstrike=pestrike,symbol=symbol,expiry=new_date)
    #         TotalOICreation.save()
    #     # live Data Creation
    #     # TotalOICreation = LiveOITotal(time=celtt,call1=ceoi1,call2=ceoi2,put1=peoi1,put2=peoi2,callstrike=cestrike,putstrike=pestrike,symbol=symbol,expiry=new_date)
    #     # TotalOICreation.save()

    #     return OITot

    # # Calculation of Change in OI
    # def OIChange():
    #     ce = df.loc[df['type'] == "CE"]
    #     pe = df.loc[df['type'] == "PE"]

    #     column = ce["oi_change"]
    #     max_value = column.max()

    #     cedf1 = ce.loc[ce['oi_change'] == max_value]
    #     pedf1 = pe.loc[(pe['strike']==cedf1['strike'].iloc[0])]

    #     celtt = cedf1['ltt'].iloc[0]
    #     ceoi1 = cedf1['oi_change'].iloc[0]
    #     cestrike = cedf1['strike'].iloc[0]
    #     peoi1 = pedf1['oi_change'].iloc[0]

    #     column = pe["oi_change"]
    #     max_value = column.max()

    #     pedf2 = pe.loc[pe['oi_change'] == max_value]
    #     cedf2 = ce.loc[(ce['strike']==pedf2['strike'].iloc[0])]

    #     peltt = pedf2['ltt'].iloc[0]
    #     peoi2 = pedf2['oi_change'].iloc[0]
    #     pestrike = pedf2['strike'].iloc[0]
    #     ceoi2 = cedf2['oi_change'].iloc[0]

    #     OIChan = {"celtt":celtt,"ceoi1":ceoi1,"cestrike":cestrike,"peoi1":peoi1,"peltt":peltt,"peoi2":peoi2,"pestrike":pestrike,"ceoi2":ceoi2}
        
    #     value1 = LiveOIChange.objects.all()
    #     print(value1)

    #     if len(value1) > 0:

    #         if (value1[0].callstrike != cestrike) or (value1[0].putstrike != pestrike):
    #             # Adding to history table
    #             ChangeOIHistory = HistoryOIChange(time=value1[0].time,call1=value1[0].call1,call2=value1[0].call2,put1=value1[0].put1,put2=value1[0].put2,callstrike=value1[0].callstrike,putstrike=value1[0].putstrike,symbol=value1[0].symbol,expiry=value1[0].expiry)
    #             ChangeOIHistory.save()

    #             # deleting live table data
    #             value1 = LiveOIChange.objects.all().delete()

    #             # Creating in live data
    #             ChangeOICreation = LiveOIChange(time=celtt,call1=ceoi1,call2=ceoi2,put1=peoi1,put2=peoi2,callstrike=cestrike,putstrike=pestrike,symbol=symbol,expiry=new_date)
    #             ChangeOICreation.save() 

    #         else:
    #             # deleting live table data
    #             value1 = LiveOIChange.objects.all().delete()

    #             # Creating in live data
    #             ChangeOICreation = LiveOIChange(time=celtt,call1=ceoi1,call2=ceoi2,put1=peoi1,put2=peoi2,callstrike=cestrike,putstrike=pestrike,symbol=symbol,expiry=new_date)
    #             ChangeOICreation.save() 
    #     else:
    #         ChangeOICreation = LiveOIChange(time=celtt,call1=ceoi1,call2=ceoi2,put1=peoi1,put2=peoi2,callstrike=cestrike,putstrike=pestrike,symbol=symbol,expiry=new_date)
    #         ChangeOICreation.save()

    #     # ChangeOICreation = LiveOIChange(time=celtt,call1=ceoi1,call2=ceoi2,put1=peoi1,put2=peoi2,callstrike=cestrike,putstrike=pestrike,symbol=symbol,expiry=new_date)
    #     # ChangeOICreation.save()

    #     return OIChan

    #     # Calcuation of Total OI - Function Call
    
    # OITotalValue = OITotal()
    # # Calculation of Change in OI - Function Call
    # OIChangeValue = OIChange()

    # # Equity data Calculation - Function Call
    # # callOnePercent,putOnePercent,callCrossed,putCrossed,callHalfPercent,putHalfPercent = equityCheck()
    
    # value1 = HistoryOIChange.objects.filter(symbol=symbol)
    # value2 = HistoryOITotal.objects.filter(symbol=symbol)

    # callOnePercent ={}
    # putOnePercent ={}
    # callCrossed ={}
    # putCrossed ={}
    # callHalfPercent ={}
    # putHalfPercent ={}

    
    
    # return render(request, 'sample.html', {'OITotalValue': OITotalValue,'OIChangeValue': OIChangeValue,'value1':value1,'value2':value2,'strikeGap':strikeGap,'callOnePercent':callOnePercent,'putOnePercent':putOnePercent,'callCrossed':callCrossed,'putCrossed':putCrossed,'putHalfPercent':putHalfPercent,'callHalfPercent':callHalfPercent
    # } )

    return render(request, template_name='new.html')


def ajax_equity(request):

    TrueDatausername = 'tdws127'
    TrueDatapassword = 'saaral@127'

    nse = Nse()
    fnolist = nse.get_fno_lot_sizes()

    symbols = list(fnolist.keys())

    # Default production port is 8082 in the library. Other ports may be given t oyou during trial.
    realtime_port = 8082

    td_app = TD(TrueDatausername, TrueDatapassword, live_port=realtime_port, historical_api=False)

    print('Starting Real Time Feed.... ')
    print(f'Port > {realtime_port}')

    req_ids = td_app.start_live_data(symbols)
    live_data_objs = {}

    time.sleep(1)

    liveData = {}
    for req_id in req_ids:
        liveData[td_app.live_data[req_id].symbol] = [td_app.live_data[req_id].ltp,td_app.live_data[req_id].day_open,td_app.live_data[req_id].day_high,td_app.live_data[req_id].day_low,td_app.live_data[req_id].prev_day_close]

    td_app.disconnect()

    callOnePercent = {}
    putOnePercent = {}
    callHalfPercent = {}
    putHalfPercent = {}
    callCrossed = {}
    putCrossed = {}

    
    LiveEquityResult.objects.all().delete()

    for e in LiveOITotalAllSymbol.objects.all():
        print(e.symbol)
        if e.symbol in liveData:
            # Call
            print(liveData[e.symbol])
            print(liveData[e.symbol][0])
            if liveData[e.symbol][0] > float(e.callstrike):
                print("Call crossed")
                callCrossed[e.symbol] = liveData[e.symbol]
                print(liveData[e.symbol])
                print(liveData[e.symbol][0])
                print(liveData[e.symbol][1])
                print(liveData[e.symbol][2])
                print(liveData[e.symbol][3])
                print(liveData[e.symbol][4])
                callcross = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Call Crossed")
                callcross.save()
                
            elif liveData[e.symbol][0] >= float(e.callone) and liveData[e.symbol][0] <= float(e.callstrike):
                print("Call 1 percent")
                callOnePercent[e.symbol] = liveData[e.symbol]
                callone = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Call 1 percent")
                callone.save()

            elif liveData[e.symbol][0] >= float(e.callhalf) and liveData[e.symbol][0] <= float(e.callstrike):
                print("Call 1/2 percent")
                callHalfPercent[e.symbol] = liveData[e.symbol]
                callhalf = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Call 1/2 percent")
                callhalf.save()

            # Put
            elif liveData[e.symbol][0] < float(e.putstrike):
                print("Put crossed")
                putCrossed[e.symbol] = liveData[e.symbol]
                putcross = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Put crossed")
                putcross.save()

            elif liveData[e.symbol][0] <= float(e.putone) and liveData[e.symbol][0] >= float(e.putstrike):
                print("Put 1 percent")
                putOnePercent[e.symbol] = liveData[e.symbol]
                putone = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Put 1 percent")
                putone.save()

            elif liveData[e.symbol][0] <= float(e.puthalf) and liveData[e.symbol][0] >= float(e.putstrike):
                print("Put 1/2 percent")
                putHalfPercent[e.symbol] = liveData[e.symbol]
                puthalf = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Put 1/2 percent")
                puthalf.save()

    OITotalValue ={}
    OIChangeValue = {}
    value1 = {}
    value2 = {}
    strikeGap = {}

    return render(request,"sample.html",{'OITotalValue': OITotalValue,'OIChangeValue': OIChangeValue,'value1':value1,'value2':value2,'strikeGap':strikeGap,'callOnePercent':callOnePercent,'putOnePercent':putOnePercent,'callCrossed':callCrossed,'putCrossed':putCrossed,'putHalfPercent':putHalfPercent,'callHalfPercent':callHalfPercent})


@csrf_protect
def ajax_optionChain(request):

        def equityCheck():


            def OITotal(df,item,dte):
                print(df)
                ce = df.loc[df['type'] == "CE"]
                pe = df.loc[df['type'] == "PE"]

                column = ce["oi"]
                max_value = column.max()

                cedf1 = ce.loc[ce['oi'] == max_value]
                pedf1 = pe.loc[(pe['strike']==cedf1['strike'].iloc[0])]
                print(pedf1)    


                celtt = cedf1['ltt'].iloc[0]
                ceoi1 = cedf1['oi'].iloc[0]
                cestrike = cedf1['strike'].iloc[0]
                peoi1 = pedf1['oi'].iloc[0]

                column = pe["oi"]
                max_value = column.max()

                pedf2 = pe.loc[pe['oi'] == max_value]
                cedf2 = ce.loc[(ce['strike']==pedf2['strike'].iloc[0])]

                peltt = pedf2['ltt'].iloc[0]
                peoi2 = pedf2['oi'].iloc[0]
                pestrike = pedf2['strike'].iloc[0]
                ceoi2 = cedf2['oi'].iloc[0]

                OITot = {"celtt":celtt,"ceoi1":ceoi1,"cestrike":cestrike,"peoi1":peoi1,"peltt":peltt,"peoi2":peoi2,"pestrike":pestrike,"ceoi2":ceoi2}
                
                value2 = LiveOITotal.objects.all()
                print(value2)

                if len(value2) > 0:

                    if (value2[0].callstrike != cestrike) or (value2[0].putstrike != pestrike):
                        # Adding to history table
                        TotalOIHistory = HistoryOITotal(time=value2[0].time,call1=value2[0].call1,call2=value2[0].call2,put1=value2[0].put1,put2=value2[0].put2,callstrike=value2[0].callstrike,putstrike=value2[0].putstrike,symbol=value2[0].symbol,expiry=value2[0].expiry)
                        TotalOIHistory.save()

                        # deleting live table data
                        value1 = LiveOITotal.objects.all().delete()

                        # Creating in live data
                        TotalOICreation = LiveOITotal(time=celtt,call1=ceoi1,call2=ceoi2,put1=peoi1,put2=peoi2,callstrike=cestrike,putstrike=pestrike,symbol=item,expiry=dte)
                        TotalOICreation.save() 

                    else:
                        # deleting live table data
                        value1 = LiveOITotal.objects.all().delete()

                        # Creating in live data
                        TotalOICreation = LiveOITotal(time=celtt,call1=ceoi1,call2=ceoi2,put1=peoi1,put2=peoi2,callstrike=cestrike,putstrike=pestrike,symbol=item,expiry=dte)
                        TotalOICreation.save()
                else:
                    TotalOICreation = LiveOITotal(time=celtt,call1=ceoi1,call2=ceoi2,put1=peoi1,put2=peoi2,callstrike=cestrike,putstrike=pestrike,symbol=item,expiry=dte)
                    TotalOICreation.save()
                # live Data Creation
                # TotalOICreation = LiveOITotal(time=celtt,call1=ceoi1,call2=ceoi2,put1=peoi1,put2=peoi2,callstrike=cestrike,putstrike=pestrike,symbol=symbol,expiry=new_date)
                # TotalOICreation.save()

                return OITot

            # Calculation of Change in OI
            def OIChange(df,item,dte):
                ce = df.loc[df['type'] == "CE"]
                pe = df.loc[df['type'] == "PE"]

                column = ce["oi_change"]
                max_value = column.max()

                cedf1 = ce.loc[ce['oi_change'] == max_value]
                pedf1 = pe.loc[(pe['strike']==cedf1['strike'].iloc[0])]

                celtt = cedf1['ltt'].iloc[0]
                ceoi1 = cedf1['oi_change'].iloc[0]
                cestrike = cedf1['strike'].iloc[0]
                peoi1 = pedf1['oi_change'].iloc[0]

                column = pe["oi_change"]
                max_value = column.max()

                pedf2 = pe.loc[pe['oi_change'] == max_value]
                cedf2 = ce.loc[(ce['strike']==pedf2['strike'].iloc[0])]

                peltt = pedf2['ltt'].iloc[0]
                peoi2 = pedf2['oi_change'].iloc[0]
                pestrike = pedf2['strike'].iloc[0]
                ceoi2 = cedf2['oi_change'].iloc[0]

                OIChan = {"celtt":celtt,"ceoi1":ceoi1,"cestrike":cestrike,"peoi1":peoi1,"peltt":peltt,"peoi2":peoi2,"pestrike":pestrike,"ceoi2":ceoi2}
                
                value1 = LiveOIChange.objects.all()
                print(value1)

                if len(value1) > 0:

                    if (value1[0].callstrike != cestrike) or (value1[0].putstrike != pestrike):
                        # Adding to history table
                        ChangeOIHistory = HistoryOIChange(time=value1[0].time,call1=value1[0].call1,call2=value1[0].call2,put1=value1[0].put1,put2=value1[0].put2,callstrike=value1[0].callstrike,putstrike=value1[0].putstrike,symbol=value1[0].symbol,expiry=value1[0].expiry)
                        ChangeOIHistory.save()

                        # deleting live table data
                        value1 = LiveOIChange.objects.all().delete()

                        # Creating in live data
                        ChangeOICreation = LiveOIChange(time=celtt,call1=ceoi1,call2=ceoi2,put1=peoi1,put2=peoi2,callstrike=cestrike,putstrike=pestrike,symbol=item,expiry=dte)
                        ChangeOICreation.save() 

                    else:
                        # deleting live table data
                        value1 = LiveOIChange.objects.all().delete()

                        # Creating in live data
                        ChangeOICreation = LiveOIChange(time=celtt,call1=ceoi1,call2=ceoi2,put1=peoi1,put2=peoi2,callstrike=cestrike,putstrike=pestrike,symbol=item,expiry=dte)
                        ChangeOICreation.save() 
                else:
                    ChangeOICreation = LiveOIChange(time=celtt,call1=ceoi1,call2=ceoi2,put1=peoi1,put2=peoi2,callstrike=cestrike,putstrike=pestrike,symbol=item,expiry=dte)
                    ChangeOICreation.save()

                # ChangeOICreation = LiveOIChange(time=celtt,call1=ceoi1,call2=ceoi2,put1=peoi1,put2=peoi2,callstrike=cestrike,putstrike=pestrike,symbol=symbol,expiry=new_date)
                # ChangeOICreation.save()

                return OIChan

            # Fetching the F&NO symbol list
            TrueDatausername = 'tdws127'
            TrueDatapassword = 'saaral@127'

            nse = Nse()
            fnolist = nse.get_fno_lot_sizes()
        
            # Removing 3 symbols from the list as they are not required for equity comparision
            remove_list = ['BANKNIFTY', 'PFC','NIFTY', 'FINNIFTY','BEL','MANAPPURAM','EXIDEIND','PETRONET', 'TATAPOWER', 'ONGC', 'VEDL', 'LALPATHLAB', 'ITC', 'INDHOTEL', 'IDEA','POWERGRID', 'COALINDIA', 'CANBK','HINDPETRO','BANKBARODA','RECLTD','CUB']
            fnolist = [i for i in fnolist if i not in remove_list]

            # Taking the first date from the expiry list.
            ex_list = expiry_list(fnolist[0])
            expiry = ex_list[0]
            dte = datetime.datetime.strptime(expiry, '%d-%b-%Y')

            sampleDict = {}
            count=1

            symlist = [  'PNB'
 ,'TRENT'
 ,'SRTRANSFIN'
 ,'TATACONSUM'
 ,'TORNTPHARM'
 ,'UBL'
 ,'VOLTAS'
 ,'BHARATFORG'
 ,'CONCOR'
 ,'GODREJCP'
 ,'HAVELLS'
 ,'INDUSTOWER'
 ,'KOTAKBANK'
 ,'L&TFH'
 ,'M&M'
]


            fnolist = fnolist[60:130]
            print(fnolist)

            LiveOITotalAllSymbol.objects.all().delete()
            LiveEquityResult.objects.all().delete()

            for item in fnolist:
                
                try:
                    import requests

                    requests.get('https://api.truedata.in/logoutRequest?user=tdws127&password=saaral@127&port=8082') 

                    td_obj = TD('tdws127', 'saaral@127' , log_level= logging.WARNING )
                    nifty_chain = td_obj.start_option_chain(item , dt(dte.year,dte.month,dte.day),chain_length=10,bid_ask=True)
                    time.sleep(3)
                    df = nifty_chain.get_option_chain()

                    nifty_chain.stop_option_chain()
                    td_obj.disconnect()
                    sampleDict[item] = df

                    

                    print(count)
                    print(item)
                    count = count + 1

                    # Total OI Calculation from Option chain
                    FutureData = {}

                    value1 = LiveOIChange.objects.all()
                    value2 = LiveOITotal.objects.all()


                    OIChangeValue = OIChange(df,item,dte)
                    OITotalValue = OITotal(df,item,dte)

                    Fourrows = df.iloc[:4]
                    CEFiltered = Fourrows[Fourrows["type"] == "CE"]
                    strikeGap = float(CEFiltered.iloc[1]["strike"]) - float(CEFiltered.iloc[0]["strike"])
                    FutureData[item] = [OITotalValue['cestrike'],OITotalValue['pestrike'],strikeGap]

                    # Percentage calculation from equity data
                    newDict = {}
                    # for key,value in FutureData.items():
                    # Call 1 percent 
                    callone = float(OITotalValue['cestrike']) - (float(strikeGap))*0.1
                    # Call 1/2 percent 
                    callhalf = float(OITotalValue['cestrike']) - (float(strikeGap))*0.05
                    # Put 1 percent
                    putone = float(OITotalValue['pestrike']) + (float(strikeGap))*0.1

                    # Put 1/2 percent
                    puthalf = float(OITotalValue['pestrike']) + (float(strikeGap))*0.05
                    newDict[item] = [float(OITotalValue['cestrike']),float(OITotalValue['pestrike']),callone,putone,callhalf,puthalf]

                    value1 = LiveOIChange.objects.all()

                    if len(value1) > 0:

                        if (value1[0].callstrike != OIChangeValue['cestrike']) or (value1[0].putstrike != OIChangeValue['pestrike']):
                            # Adding to history table
                            ChangeOIHistory = HistoryOIChange(time=value1[0].time,call1=value1[0].call1,call2=value1[0].call2,put1=value1[0].put1,put2=value1[0].put2,callstrike=value1[0].callstrike,putstrike=value1[0].putstrike,symbol=value1[0].symbol,expiry=value1[0].expiry)
                            ChangeOIHistory.save()

                            # deleting live table data
                            value1 = LiveOIChange.objects.all().delete()

                            # Creating in live data
                            ChangeOICreation = LiveOIChange(time=OIChangeValue['celtt'],call1=OIChangeValue['ceoi1'],call2=OIChangeValue['ceoi2'],put1=OIChangeValue['peoi1'],put2=OIChangeValue['peoi2'],callstrike=OIChangeValue['cestrike'],putstrike=OIChangeValue['pestrike'],symbol=item,expiry=dte)
                            ChangeOICreation.save() 

                        else:
                            # deleting live table data
                            value1 = LiveOIChange.objects.all().delete()

                            # Creating in live data
                            ChangeOICreation = LiveOIChange(time=OIChangeValue['celtt'],call1=OIChangeValue['ceoi1'],call2=OIChangeValue['ceoi2'],put1=OIChangeValue['peoi1'],put2=OIChangeValue['peoi2'],callstrike=OIChangeValue['cestrike'],putstrike=OIChangeValue['pestrike'],symbol=item,expiry=dte)
                            ChangeOICreation.save() 
                    else:
                        ChangeOICreation = LiveOIChange(time=OIChangeValue['celtt'],call1=OIChangeValue['ceoi1'],call2=OIChangeValue['ceoi2'],put1=OIChangeValue['peoi1'],put2=OIChangeValue['peoi2'],callstrike=OIChangeValue['cestrike'],putstrike=OIChangeValue['pestrike'],symbol=item,expiry=dte)
                        ChangeOICreation.save()



                    value2 = LiveOITotal.objects.filter(symbol=item)

                    if len(value2) > 0:

                        if (value2[0].callstrike != OITotalValue['cestrike']) or (value2[0].putstrike != OITotalValue['pestrike']):
                            # Adding to history table
                            TotalOIHistory = HistoryOITotal(time=value2[0].time,call1=value2[0].call1,call2=value2[0].call2,put1=value2[0].put1,put2=value2[0].put2,callstrike=value2[0].callstrike,putstrike=value2[0].putstrike,symbol=value2[0].symbol,expiry=value2[0].expiry)
                            TotalOIHistory.save()

                            # deleting live table data
                            value1 = LiveOITotal.objects.all().delete()

                            # Creating in live data
                            TotalOICreation = LiveOITotal(time=OITotalValue['celtt'],call1=OITotalValue['ceoi1'],call2=OITotalValue['ceoi2'],put1=OITotalValue['peoi1'],put2=OITotalValue['peoi2'],callstrike=OITotalValue['cestrike'],putstrike=OITotalValue['pestrike'],symbol=item,expiry=dte)
                            TotalOICreation.save()

                        else:
                            # deleting live table data
                            value1 = LiveOITotal.objects.all().delete()

                            # Creating in live data
                            TotalOICreation = LiveOITotal(time=OITotalValue['celtt'],call1=OITotalValue['ceoi1'],call2=OITotalValue['ceoi2'],put1=OITotalValue['peoi1'],put2=OITotalValue['peoi2'],callstrike=OITotalValue['cestrike'],putstrike=OITotalValue['pestrike'],symbol=item,expiry=dte)
                            TotalOICreation.save()
                    else:
                        TotalOICreation = LiveOITotal(time=OITotalValue['celtt'],call1=OITotalValue['ceoi1'],call2=OITotalValue['ceoi2'],put1=OITotalValue['peoi1'],put2=OITotalValue['peoi2'],callstrike=OITotalValue['cestrike'],putstrike=OITotalValue['pestrike'],symbol=item,expiry=dte)
                        TotalOICreation.save()

                    # Creating in live data
                    TotalOICreationAll = LiveOITotalAllSymbol(time=OITotalValue['celtt'],call1=OITotalValue['ceoi1'],call2=OITotalValue['ceoi2'],put1=OITotalValue['peoi1'],put2=OITotalValue['peoi2'],callstrike=OITotalValue['cestrike'],putstrike=OITotalValue['pestrike'],symbol=item,expiry=dte,callone=callone,putone=putone,callhalf=callhalf,puthalf=puthalf)
                    TotalOICreationAll.save()



                except websocket.WebSocketConnectionClosedException as e:
                    print('This caught the websocket exception ')
                    td_obj.disconnect()
                    continue
                except IndexError as e:
                    print('This caught the exception')
                    td_obj.disconnect()
                    continue
                except:
                    print("Exception")
                    td_obj.disconnect()
                    continue

            nse = Nse()
            fnolist = nse.get_fno_lot_sizes()

            symbols = list(fnolist.keys())
            print(len(fnolist))

            # Default production port is 8082 in the library. Other ports may be given t oyou during trial.
            realtime_port = 8082

            td_app = TD(TrueDatausername, TrueDatapassword, live_port=realtime_port, historical_api=False)

            print('Starting Real Time Feed.... ')
            print(f'Port > {realtime_port}')

            req_ids = td_app.start_live_data(symbols)
            live_data_objs = {}

            time.sleep(1)

            liveData = {}
            for req_id in req_ids:
                liveData[td_app.live_data[req_id].symbol] = [td_app.live_data[req_id].ltp,td_app.live_data[req_id].day_open,td_app.live_data[req_id].day_high,td_app.live_data[req_id].day_low,td_app.live_data[req_id].prev_day_close]

            td_app.disconnect()

            callOnePercent = {}
            putOnePercent = {}
            callHalfPercent = {}
            putHalfPercent = {}
            callCrossed = {}
            putCrossed = {}

            

            for e in LiveOITotalAllSymbol.objects.all():
                print(e.symbol)
                if e.symbol in liveData:
                    # Call
                    if liveData[e.symbol][0] > float(e.callstrike):
                        print("Call crossed")
                        callCrossed[e.symbol] = liveData[e.symbol]
                        print(liveData[e.symbol])
                        print(liveData[e.symbol][0])
                        print(liveData[e.symbol][1])
                        print(liveData[e.symbol][2])
                        print(liveData[e.symbol][3])
                        print(liveData[e.symbol][4])
                        callcross = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Call Crossed")
                        callcross.save()
                        
                    elif liveData[e.symbol][0] >= float(e.callone) and liveData[e.symbol][0] <= float(e.callstrike):
                        print("Call 1 percent")
                        callOnePercent[e.symbol] = liveData[e.symbol]
                        callone = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Call 1 percent")
                        callone.save()

                    elif liveData[e.symbol][0] >= float(e.callhalf) and liveData[e.symbol][0] <= float(e.callstrike):
                        print("Call 1/2 percent")
                        callHalfPercent[e.symbol] = liveData[e.symbol]
                        callhalf = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Call 1/2 percent")
                        callhalf.save()

                    # Put
                    elif liveData[e.symbol][0] < float(e.putstrike):
                        print("Put crossed")
                        putCrossed[e.symbol] = liveData[e.symbol]
                        putcross = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Put crossed")
                        putcross.save()

                    elif liveData[e.symbol][0] <= float(e.putone) and liveData[e.symbol][0] >= float(e.putstrike):
                        print("Put 1 percent")
                        putOnePercent[e.symbol] = liveData[e.symbol]
                        putone = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Put 1 percent")
                        putone.save()

                    elif liveData[e.symbol][0] <= float(e.puthalf) and liveData[e.symbol][0] >= float(e.putstrike):
                        print("Put 1/2 percent")
                        putHalfPercent[e.symbol] = liveData[e.symbol]
                        puthalf = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Put 1/2 percent")
                        puthalf.save()

            # callOnePercent["ACC"] = [438.35, 432.95, 440.35, 432.1, 435.95]
            # callOnePercent["RAMCOCEM"] = [438.35, 432.95, 440.35, 432.1, 435.95]
            # callOnePercent["PAGEIND"] = [438.35, 432.95, 440.35, 432.1, 435.95]
            # callOnePercent["UPL"] = [438.35, 432.95, 440.35, 432.1, 435.95]
            # callOnePercent["HAL"] = [438.35, 432.95, 440.35, 432.1, 435.95]
            # callOnePercent["IEX"] = [438.35, 432.95, 440.35, 432.1, 435.95]
            # callOnePercent["IPCALAB"] = [438.35, 432.95, 440.35, 432.1, 435.95]
            # callOnePercent["MCX"] = [438.35, 432.95, 440.35, 432.1, 435.95]
            # callOnePercent["POLYCAB"] = [438.35, 432.95, 440.35, 432.1, 435.95]

            # putOnePercent["ACC"] =  [438.35, 432.95, 440.35, 432.1, 435.95]
            # callCrossed["ACC"] = [438.35, 432.95, 440.35, 432.1, 435.95]
            # putCrossed["ACC"] = [438.35, 432.95, 440.35, 432.1, 435.95]
            # callHalfPercent["ACC"] = [438.35, 432.95, 440.35, 432.1, 435.95]
            # putHalfPercent["ACC"] = [438.35, 432.95, 440.35, 432.1, 435.95]

            return callOnePercent,putOnePercent,callCrossed,putCrossed,callHalfPercent,putHalfPercent
        

        # Equity data Calculation - Function Call
        callOnePercent,putOnePercent,callCrossed,putCrossed,callHalfPercent,putHalfPercent = equityCheck()
        OITotalValue ={}
        OIChangeValue = {}
        value1 = {}
        value2 = {}
        strikeGap = {}

        return render(request,"sample.html",{'OITotalValue': OITotalValue,'OIChangeValue': OIChangeValue,'value1':value1,'value2':value2,'strikeGap':strikeGap,'callOnePercent':callOnePercent,'putOnePercent':putOnePercent,'callCrossed':callCrossed,'putCrossed':putCrossed,'putHalfPercent':putHalfPercent,'callHalfPercent':callHalfPercent})

def sample(request):
    
    return render(request,template_name = "sample.html")

#Login View - Login page
@csrf_protect
def login(request):
    
    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']
        print(username)
        if User.objects.filter(username=username).exists():
            user=auth.authenticate(username=username,password=password)
            print(user)
            if user is not None:
                auth.login(request,user)
                # messages.info(request, f"You are now logged in as {username}")
                return redirect('entry')
            else:
                messages.info(request,'incorrect password')
                return redirect('login')
        else:
            messages.error(request,"user doesn't exists")
            return redirect('login')

    else:
        
        return render(request,template_name = "login.html")

#Logout View - User Logout
def logout(request):

    auth.logout(request)
    request.session.flush()
    print("logged out")
    messages.success(request,"Successfully logged out")
    for sesskey in request.session.keys():
        del request.session[sesskey]

    return redirect('login')   


@csrf_protect
@login_required(login_url='login')
def dashboard(request):
    return render(request, 'hello_world.html', {})

@csrf_protect
@login_required(login_url='login')
def entry(request):
    from nsetools import Nse
    nse = Nse()
    fnolist = nse.get_fno_lot_sizes()
    fnolist = nse.get
    print(len(fnolist))
    return render(request, 'entry.html', {'fnolist':fnolist})

def ajax_load_expiry(request):

    print(request.GET)
    entry = request.GET.get('symbol')
    print(entry)
    ex_list = expiry_list(entry)
    print(ex_list)

    return render(request,'expiry_dropdown_list_options.html',{'ex_list':ex_list})

def load_optionChain(request):
    # Getting the Symbol & Expiry selected by user.
    print(request.GET)

    symbol="NIFTY"
    
    if len(request.GET)>0:
        symbol = request.GET["symbol"]
        print("GET")
    else:
        symbol = request.POST['symbol']
        print("POST")
    # expiry = request.POST['expiry_selected']

    liveEqui = LiveEquityResult.objects.filter(symbol=symbol)


    LiveOI = LiveOITotal.objects.filter(symbol=symbol)
    print(LiveOI)

    LiveChangeOI = LiveOIChange.objects.filter(symbol=symbol)
    print(LiveChangeOI)

    HistoryOITot = HistoryOITotal.objects.filter(symbol=symbol).order_by('-time')
    HistoryOIChg = HistoryOIChange.objects.filter(symbol=symbol).order_by('-time')

    if len(LiveOI) > 0:
        return render(request, 'optionChainSingleSymbol.html', {'liveEqui':liveEqui,'symbol':symbol,'OITotalValue':LiveOI,'OIChangeValue':LiveChangeOI,'HistoryOITot':HistoryOITot,'HistoryOIChg':HistoryOIChg})
    else:
        return render(request, 'optionChainNoData.html')

def load_charts(request):

    # Fetching today's date
    dat = dt.today()
    # Deleting past historical data in the database
    HistoryOIChange.objects.filter(time__lte = dt.combine(dat, dt.min.time())).delete()
    HistoryOITotal.objects.filter(time__lte = dt.combine(dat, dt.min.time())).delete()

    # Getting the Symbol & Expiry selected by user.
    symbol = request.POST['symbol']
    expiry = request.POST['expiry_selected']

    # Converting the expiry date format to required format to store in DB  
    new_date=datetime.datetime.strptime(expiry, '%d-%b-%Y').strftime('%Y-%m-%d')

    TrueDatausername = 'wssand020'
    TrueDatapassword = 'vinosa020'
    td_obj = TD(TrueDatausername, TrueDatapassword , log_level= logging.WARNING )

    # Changing the expiry dateformat
    # Fetching the option chain data
    dte = datetime.datetime.strptime(expiry, '%d-%b-%Y')
    nifty_chain = td_obj.start_option_chain( symbol, dt(dte.year,dte.month,dte.day),chain_length = 10,bid_ask=True)
    time.sleep(3)
    print("Getting option chain")
    df = nifty_chain.get_option_chain()

    # calculating the strike gap
    Fourrows = df.iloc[:4]
    CEFiltered = Fourrows[Fourrows["type"] == "CE"]
    strikeGap = int(CEFiltered.iloc[1]["strike"]) - int(CEFiltered.iloc[0]["strike"])

    # Disconnecting user
    td_obj.disconnect()

    #  Calcuation of Total OI
    def OITotal():
        print(df)
        ce = df.loc[df['type'] == "CE"]
        pe = df.loc[df['type'] == "PE"]

        column = ce["oi"]
        max_value = column.max()

        cedf1 = ce.loc[ce['oi'] == max_value]
        pedf1 = pe.loc[(pe['strike']==cedf1['strike'].iloc[0])]
        print(pedf1)    


        celtt = cedf1['ltt'].iloc[0]
        ceoi1 = cedf1['oi'].iloc[0]
        cestrike = cedf1['strike'].iloc[0]
        peoi1 = pedf1['oi'].iloc[0]

        column = pe["oi"]
        max_value = column.max()

        pedf2 = pe.loc[pe['oi'] == max_value]
        cedf2 = ce.loc[(ce['strike']==pedf2['strike'].iloc[0])]

        peltt = pedf2['ltt'].iloc[0]
        peoi2 = pedf2['oi'].iloc[0]
        pestrike = pedf2['strike'].iloc[0]
        ceoi2 = cedf2['oi'].iloc[0]

        OITot = {"celtt":celtt,"ceoi1":ceoi1,"cestrike":cestrike,"peoi1":peoi1,"peltt":peltt,"peoi2":peoi2,"pestrike":pestrike,"ceoi2":ceoi2}
        
        value2 = LiveOITotal.objects.all()
        print(value2)

        if len(value2) > 0:

            if (value2[0].callstrike != cestrike) or (value2[0].putstrike != pestrike):
                # Adding to history table
                TotalOIHistory = HistoryOITotal(time=value2[0].time,call1=value2[0].call1,call2=value2[0].call2,put1=value2[0].put1,put2=value2[0].put2,callstrike=value2[0].callstrike,putstrike=value2[0].putstrike,symbol=value2[0].symbol,expiry=value2[0].expiry)
                TotalOIHistory.save()

                # deleting live table data
                value1 = LiveOITotal.objects.all().delete()

                # Creating in live data
                TotalOICreation = LiveOITotal(time=celtt,call1=ceoi1,call2=ceoi2,put1=peoi1,put2=peoi2,callstrike=cestrike,putstrike=pestrike,symbol=symbol,expiry=new_date)
                TotalOICreation.save() 

            else:
                # deleting live table data
                value1 = LiveOITotal.objects.all().delete()

                # Creating in live data
                TotalOICreation = LiveOITotal(time=celtt,call1=ceoi1,call2=ceoi2,put1=peoi1,put2=peoi2,callstrike=cestrike,putstrike=pestrike,symbol=symbol,expiry=new_date)
                TotalOICreation.save()
        else:
            TotalOICreation = LiveOITotal(time=celtt,call1=ceoi1,call2=ceoi2,put1=peoi1,put2=peoi2,callstrike=cestrike,putstrike=pestrike,symbol=symbol,expiry=new_date)
            TotalOICreation.save()
        # live Data Creation
        # TotalOICreation = LiveOITotal(time=celtt,call1=ceoi1,call2=ceoi2,put1=peoi1,put2=peoi2,callstrike=cestrike,putstrike=pestrike,symbol=symbol,expiry=new_date)
        # TotalOICreation.save()

        return OITot

    # Calculation of Change in OI
    def OIChange():
        ce = df.loc[df['type'] == "CE"]
        pe = df.loc[df['type'] == "PE"]

        column = ce["oi_change"]
        max_value = column.max()

        cedf1 = ce.loc[ce['oi_change'] == max_value]
        pedf1 = pe.loc[(pe['strike']==cedf1['strike'].iloc[0])]

        celtt = cedf1['ltt'].iloc[0]
        ceoi1 = cedf1['oi_change'].iloc[0]
        cestrike = cedf1['strike'].iloc[0]
        peoi1 = pedf1['oi_change'].iloc[0]

        column = pe["oi_change"]
        max_value = column.max()

        pedf2 = pe.loc[pe['oi_change'] == max_value]
        cedf2 = ce.loc[(ce['strike']==pedf2['strike'].iloc[0])]

        peltt = pedf2['ltt'].iloc[0]
        peoi2 = pedf2['oi_change'].iloc[0]
        pestrike = pedf2['strike'].iloc[0]
        ceoi2 = cedf2['oi_change'].iloc[0]

        OIChan = {"celtt":celtt,"ceoi1":ceoi1,"cestrike":cestrike,"peoi1":peoi1,"peltt":peltt,"peoi2":peoi2,"pestrike":pestrike,"ceoi2":ceoi2}
        
        value1 = LiveOIChange.objects.all()
        print(value1)

        if len(value1) > 0:

            if (value1[0].callstrike != cestrike) or (value1[0].putstrike != pestrike):
                # Adding to history table
                ChangeOIHistory = HistoryOIChange(time=value1[0].time,call1=value1[0].call1,call2=value1[0].call2,put1=value1[0].put1,put2=value1[0].put2,callstrike=value1[0].callstrike,putstrike=value1[0].putstrike,symbol=value1[0].symbol,expiry=value1[0].expiry)
                ChangeOIHistory.save()

                # deleting live table data
                value1 = LiveOIChange.objects.all().delete()

                # Creating in live data
                ChangeOICreation = LiveOIChange(time=celtt,call1=ceoi1,call2=ceoi2,put1=peoi1,put2=peoi2,callstrike=cestrike,putstrike=pestrike,symbol=symbol,expiry=new_date)
                ChangeOICreation.save() 

            else:
                # deleting live table data
                value1 = LiveOIChange.objects.all().delete()

                # Creating in live data
                ChangeOICreation = LiveOIChange(time=celtt,call1=ceoi1,call2=ceoi2,put1=peoi1,put2=peoi2,callstrike=cestrike,putstrike=pestrike,symbol=symbol,expiry=new_date)
                ChangeOICreation.save() 
        else:
            ChangeOICreation = LiveOIChange(time=celtt,call1=ceoi1,call2=ceoi2,put1=peoi1,put2=peoi2,callstrike=cestrike,putstrike=pestrike,symbol=symbol,expiry=new_date)
            ChangeOICreation.save()

        # ChangeOICreation = LiveOIChange(time=celtt,call1=ceoi1,call2=ceoi2,put1=peoi1,put2=peoi2,callstrike=cestrike,putstrike=pestrike,symbol=symbol,expiry=new_date)
        # ChangeOICreation.save()

        return OIChan

    # Equity data Calculation
    def equityCheck():
        # Fetching the F&NO symbol list
        nse = Nse()
        fnolist = nse.get_fno_lot_sizes()
    
        # Removing 3 symbols from the list as they are not required for equity comparision
        remove_list = ['BANKNIFTY', 'PFC','NIFTY', 'FINNIFTY', 'EXIDEIND','PETRONET', 'MANAPPURAM','TATAPOWER', 'ONGC', 'VEDL', 'LALPATHLAB', 'ITC', 'INDHOTEL', 'IDEA','POWERGRID', 'COALINDIA', 'CANBK','HINDPETRO','BANKBARODA','RECLTD']
        fnolist = [i for i in fnolist if i not in remove_list]

        # Taking the first date from the expiry list.
        ex_list = expiry_list(fnolist[0])
        expiry = ex_list[0]
        dte = datetime.datetime.strptime(expiry, '%d-%b-%Y')

        sampleDict = {}
        count=1

        symlist = ['NESTLEIND']

        # fnolist = fnolist[0:100]
        print(fnolist)
        LiveOITotalAllSymbol.objects.all().delete()
        for item in fnolist:

            td_obj = TD('tdws127', 'saaral@127' , log_level= logging.WARNING )
            nifty_chain = td_obj.start_option_chain(item , dt(dte.year,dte.month,dte.day),chain_length=20,bid_ask=True)
            time.sleep(2)
            df = nifty_chain.get_option_chain()
            sampleDict[item] = df

            td_obj.disconnect()

            print(count)
            print(item)
            count = count + 1

            # Total OI Calculation from Option chain
            FutureData = {}

            value1 = LiveOIChange.objects.all()
            value2 = LiveOITotal.objects.all()


            OIChangeValue = OIChange()
            OITotalValue = OITotal()

            Fourrows = df.iloc[:4]
            CEFiltered = Fourrows[Fourrows["type"] == "CE"]
            strikeGap = float(CEFiltered.iloc[1]["strike"]) - float(CEFiltered.iloc[0]["strike"])
            FutureData[item] = [OITotalValue['cestrike'],OITotalValue['pestrike'],strikeGap]

            # Percentage calculation from equity data
            newDict = {}
            # for key,value in FutureData.items():
            # Call 1 percent 
            callone = float(OITotalValue['cestrike']) - (float(strikeGap))*0.1
            # Call 1/2 percent 
            callhalf = float(OITotalValue['cestrike']) - (float(strikeGap))*0.05
            # Put 1 percent
            putone = float(OITotalValue['pestrike']) + (float(strikeGap))*0.1

            # Put 1/2 percent
            puthalf = float(OITotalValue['pestrike']) + (float(strikeGap))*0.05
            newDict[item] = [float(OITotalValue['cestrike']),float(OITotalValue['pestrike']),callone,putone,callhalf,puthalf]

            value1 = LiveOIChange.objects.all()

            if len(value1) > 0:

                if (value1[0].callstrike != OIChangeValue['cestrike']) or (value1[0].putstrike != OIChangeValue['pestrike']):
                    # Adding to history table
                    ChangeOIHistory = HistoryOIChange(time=value1[0].time,call1=value1[0].call1,call2=value1[0].call2,put1=value1[0].put1,put2=value1[0].put2,callstrike=value1[0].callstrike,putstrike=value1[0].putstrike,symbol=value1[0].symbol,expiry=value1[0].expiry)
                    ChangeOIHistory.save()

                    # deleting live table data
                    value1 = LiveOIChange.objects.all().delete()

                    # Creating in live data
                    ChangeOICreation = LiveOIChange(time=OITotalValue['celtt'],call1=OITotalValue['ceoi1'],call2=OITotalValue['ceoi2'],put1=OITotalValue['peoi1'],put2=OITotalValue['peoi2'],callstrike=OITotalValue['cestrike'],putstrike=OITotalValue['pestrike'],symbol=item,expiry=dte)
                    ChangeOICreation.save() 

                else:
                    # deleting live table data
                    value1 = LiveOIChange.objects.all().delete()

                    # Creating in live data
                    ChangeOICreation = LiveOIChange(time=OITotalValue['celtt'],call1=OITotalValue['ceoi1'],call2=OITotalValue['ceoi2'],put1=OITotalValue['peoi1'],put2=OITotalValue['peoi2'],callstrike=OITotalValue['cestrike'],putstrike=OITotalValue['pestrike'],symbol=item,expiry=dte)
                    ChangeOICreation.save() 
            else:
                ChangeOICreation = LiveOIChange(time=OITotalValue['celtt'],call1=OITotalValue['ceoi1'],call2=OITotalValue['ceoi2'],put1=OITotalValue['peoi1'],put2=OITotalValue['peoi2'],callstrike=OITotalValue['cestrike'],putstrike=OITotalValue['pestrike'],symbol=item,expiry=dte)
                ChangeOICreation.save()



            value2 = LiveOITotal.objects.filter(symbol=item)

            if len(value2) > 0:

                if (value2[0].callstrike != OITotalValue['cestrike']) or (value2[0].putstrike != OITotalValue['pestrike']):
                    # Adding to history table
                    TotalOIHistory = HistoryOITotal(time=value2[0].time,call1=value2[0].call1,call2=value2[0].call2,put1=value2[0].put1,put2=value2[0].put2,callstrike=value2[0].callstrike,putstrike=value2[0].putstrike,symbol=value2[0].symbol,expiry=value2[0].expiry)
                    TotalOIHistory.save()

                    # deleting live table data
                    value1 = LiveOITotal.objects.all().delete()

                    # Creating in live data
                    TotalOICreation = LiveOITotal(time=OITotalValue['celtt'],call1=OITotalValue['ceoi1'],call2=OITotalValue['ceoi2'],put1=OITotalValue['peoi1'],put2=OITotalValue['peoi2'],callstrike=OITotalValue['cestrike'],putstrike=OITotalValue['pestrike'],symbol=item,expiry=dte)
                    TotalOICreation.save()

                else:
                    # deleting live table data
                    value1 = LiveOITotal.objects.all().delete()

                    # Creating in live data
                    TotalOICreation = LiveOITotal(time=OITotalValue['celtt'],call1=OITotalValue['ceoi1'],call2=OITotalValue['ceoi2'],put1=OITotalValue['peoi1'],put2=OITotalValue['peoi2'],callstrike=OITotalValue['cestrike'],putstrike=OITotalValue['pestrike'],symbol=item,expiry=dte)
                    TotalOICreation.save()
            else:
                TotalOICreation = LiveOITotal(time=OITotalValue['celtt'],call1=OITotalValue['ceoi1'],call2=OITotalValue['ceoi2'],put1=OITotalValue['peoi1'],put2=OITotalValue['peoi2'],callstrike=OITotalValue['cestrike'],putstrike=OITotalValue['pestrike'],symbol=item,expiry=dte)
                TotalOICreation.save()

            # Creating in live data
            TotalOICreationAll = LiveOITotalAllSymbol(time=OITotalValue['celtt'],call1=OITotalValue['ceoi1'],call2=OITotalValue['ceoi2'],put1=OITotalValue['peoi1'],put2=OITotalValue['peoi2'],callstrike=OITotalValue['cestrike'],putstrike=OITotalValue['pestrike'],symbol=item,expiry=dte,callone=callone,putone=putone,callhalf=callhalf,puthalf=puthalf)
            TotalOICreationAll.save() 

        nse = Nse()
        fnolist = nse.get_fno_lot_sizes()

        symbols = list(fnolist.keys())

        # Default production port is 8082 in the library. Other ports may be given t oyou during trial.
        realtime_port = 8082

        td_app = TD(TrueDatausername, TrueDatapassword, live_port=realtime_port, historical_api=False)

        print('Starting Real Time Feed.... ')
        print(f'Port > {realtime_port}')

        req_ids = td_app.start_live_data(symbols)
        live_data_objs = {}

        time.sleep(1)

        liveData = {}
        for req_id in req_ids:
            liveData[td_app.live_data[req_id].symbol] = [td_app.live_data[req_id].ltp,td_app.live_data[req_id].day_open,td_app.live_data[req_id].day_high,td_app.live_data[req_id].day_low,td_app.live_data[req_id].prev_day_close]

        td_app.disconnect()

        callOnePercent = {}
        putOnePercent = {}
        callHalfPercent = {}
        putHalfPercent = {}
        callCrossed = {}
        putCrossed = {}

        LiveEquityResult.objects.all().delete()

        for e in LiveOITotalAllSymbol.objects.all():
            if e.symbol in liveData:
                # Call
                if liveData[e.symbol][0] > float(e.callstrike):
                    print("Call crossed")
                    callCrossed[e.symbol] = liveData[e.symbol]
                    callcross = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=[e.symbol][4],ltp=liveData[e.symbol][0],strike="Call Crossed")
                    callcross.save()
                    
                elif liveData[e.symbol][0] >= float(e.callone) and liveData[e.symbol][0] <= float(e.callstrike):
                    print("Call 1 percent")
                    callOnePercent[e.symbol] = liveData[e.symbol]
                    callone = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=[e.symbol][4],ltp=liveData[e.symbol][0],strike="Call 1 percent")
                    callone.save()

                elif liveData[e.symbol][0] >= float(e.callhalf) and liveData[e.symbol][0] <= float(e.callstrike):
                    print("Call 1/2 percent")
                    callHalfPercent[e.symbol] = liveData[e.symbol]
                    callhalf = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=[e.symbol][4],ltp=liveData[e.symbol][0],strike="Call 1/2 percent")
                    callhalf.save()

                # Put
                elif liveData[e.symbol][0] < float(e.putstrike):
                    print("Put crossed")
                    putCrossed[e.symbol] = liveData[e.symbol]
                    putcross = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=[e.symbol][4],ltp=liveData[e.symbol][0],strike="Put crossed")
                    putcross.save()

                elif liveData[e.symbol][0] <= float(e.putone) and liveData[e.symbol][0] >= float(e.putstrike):
                    print("Put 1 percent")
                    putOnePercent[e.symbol] = liveData[e.symbol]
                    putone = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=[e.symbol][4],ltp=liveData[e.symbol][0],strike="Put 1 percent")
                    putone.save()

                elif liveData[e.symbol][0] <= float(e.puthalf) and liveData[e.symbol][0] >= float(e.putstrike):
                    print("Put 1/2 percent")
                    putHalfPercent[e.symbol] = liveData[e.symbol]
                    puthalf = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=[e.symbol][4],ltp=liveData[e.symbol][0],strike="Put 1/2 percent")
                    puthalf.save()

        # callOnePercent["ACC"] = [438.35, 432.95, 440.35, 432.1, 435.95]
        # callOnePercent["RAMCOCEM"] = [438.35, 432.95, 440.35, 432.1, 435.95]
        # callOnePercent["PAGEIND"] = [438.35, 432.95, 440.35, 432.1, 435.95]
        # callOnePercent["UPL"] = [438.35, 432.95, 440.35, 432.1, 435.95]
        # callOnePercent["HAL"] = [438.35, 432.95, 440.35, 432.1, 435.95]
        # callOnePercent["IEX"] = [438.35, 432.95, 440.35, 432.1, 435.95]
        # callOnePercent["IPCALAB"] = [438.35, 432.95, 440.35, 432.1, 435.95]
        # callOnePercent["MCX"] = [438.35, 432.95, 440.35, 432.1, 435.95]
        # callOnePercent["POLYCAB"] = [438.35, 432.95, 440.35, 432.1, 435.95]

        # putOnePercent["ACC"] =  [438.35, 432.95, 440.35, 432.1, 435.95]
        # callCrossed["ACC"] = [438.35, 432.95, 440.35, 432.1, 435.95]
        # putCrossed["ACC"] = [438.35, 432.95, 440.35, 432.1, 435.95]
        # callHalfPercent["ACC"] = [438.35, 432.95, 440.35, 432.1, 435.95]
        # putHalfPercent["ACC"] = [438.35, 432.95, 440.35, 432.1, 435.95]

        return callOnePercent,putOnePercent,callCrossed,putCrossed,callHalfPercent,putHalfPercent
        
    # Calcuation of Total OI - Function Call
    OITotalValue = OITotal()
    # Calculation of Change in OI - Function Call
    OIChangeValue = OIChange()

    # Equity data Calculation - Function Call
    # callOnePercent,putOnePercent,callCrossed,putCrossed,callHalfPercent,putHalfPercent = equityCheck()
    
    value1 = HistoryOIChange.objects.filter(symbol=symbol)
    value2 = HistoryOITotal.objects.filter(symbol=symbol)

    callOnePercent ={}
    putOnePercent ={}
    callCrossed ={}
    putCrossed ={}
    callHalfPercent ={}
    putHalfPercent ={}

    
    
    return render(request, 'sample.html', {'OITotalValue': OITotalValue,'OIChangeValue': OIChangeValue,'value1':value1,'value2':value2,'strikeGap':strikeGap,'callOnePercent':callOnePercent,'putOnePercent':putOnePercent,'callCrossed':callCrossed,'putCrossed':putCrossed,'putHalfPercent':putHalfPercent,'callHalfPercent':callHalfPercent
    } )

