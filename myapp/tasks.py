from time import sleep
from celery import shared_task
from .models import *
from nsetools import *
from datetime import datetime as dt
from truedata_ws.websocket.TD import TD
import websocket

from celery.schedules import crontab
from celery import Celery
from celery.schedules import crontab
import time
from nsetools import Nse
from myproject.celery import app
from django_celery_beat.models import PeriodicTask, PeriodicTasks
from datetime import timedelta
from celery.exceptions import SoftTimeLimitExceeded
from pytz import timezone
import pendulum
import calendar
from datetime import date
import time as te


@shared_task
def create_currency():

    from datetime import datetime, time,timedelta
    pastDate = datetime.combine(datetime.now(timezone('Asia/Kolkata')), time(9,15)).time()
    nsepadDate = datetime.combine(datetime.now(timezone('Asia/Kolkata')), time(9,15)).date()

    # LiveEquityResult.objects.all().delete()
    LiveSegment.objects.filter(time__lte = pastDate).delete()
    LiveSegment.objects.filter(date__lt = nsepadDate).delete()

    pastDate = datetime.combine(datetime.now(timezone('Asia/Kolkata')), time(9,15))
    segpastDate = datetime.combine(datetime.now(timezone('Asia/Kolkata')), time(9,15)).time()

    # LiveEquityResult.objects.all().delete()
    TestEquityResult.objects.filter(date__lte = pastDate).delete()
    LiveEquityResult.objects.filter(date__lte = pastDate).delete()
    LiveSegment.objects.filter(time__lte = segpastDate).delete()
    LiveSegment.objects.filter(date__lt = nsepadDate).delete()


    def initialEquity():
        try:

            import requests
            url = 'https://www.truedata.in/downloads/symbol_lists/13.NSE_ALL_OPTIONS.txt'
            s = requests.get(url).content
            stringlist=[x.decode('utf-8').split('2')[0] for x in s.splitlines()]

            symbols = list(set(stringlist))

            TrueDatausernamereal = 'tdws135'
            TrueDatapasswordreal = 'saaral@135'

            remove_list = ['BANKNIFTY', 'FINNIFTY', 'NIFTY', 'ASIANPAINT', 'BAJAJFINSV', 'BHARTIARTL', 'BHEL', 'BPCL', 'DEEPAKNTR', 'FEDERALBNK', 'HDFC', 'IOC', 'IRCTC', 'IPCALAB', 'NATIONALUM', 'NTPC', 'PNB', 'SHREECEM', 'VEDL', 'ASTRAL', 'BOSCHLTD', 'EICHERMOT', 'GMRINFRA', 'HDFCLIFE', 'IBULHSGFIN', 'ITC', 'L&TFH', 'BANKBARODA', 'IDFCFIRSTB', 'SAIL', 'IDEA']
            fnolist = [i for i in symbols if i not in remove_list]

            # Default production port is 8082 in the library. Other ports may be given t oyou during trial.
            realtime_port = 8082

            print('Starting Real Time Feed.... ')
            print(f'Port > {realtime_port}')

            td_app = TD(TrueDatausernamereal, TrueDatapasswordreal, live_port=realtime_port, historical_api=False)
            # print(symbols)
            req_ids = td_app.start_live_data(symbols)
            live_data_objs = {}

            te.sleep(3)

            liveData = {}
            for req_id in req_ids:
                # print(td_app.live_data[req_id].day_open)
                if (td_app.live_data[req_id].ltp) == None:
                    continue
                else:
                    liveData[td_app.live_data[req_id].symbol] = [td_app.live_data[req_id].ltp,td_app.live_data[req_id].day_open,td_app.live_data[req_id].day_high,td_app.live_data[req_id].day_low,td_app.live_data[req_id].prev_day_close,dt.now(timezone("Asia/Kolkata")).strftime('%H:%M:%S'),td_app.live_data[req_id].change_perc]


            callcrossedset = LiveEquityResult.objects.filter(strike__contains="Call Crossed")
            callonepercentset = LiveEquityResult.objects.filter(strike="Call 1 percent")
            putcrossedset = LiveEquityResult.objects.filter(strike="Put Crossed")
            putonepercentset = LiveEquityResult.objects.filter(strike="Put 1 percent")
            opencallcross = LiveEquityResult.objects.filter(opencrossed="call")
            openputcross = LiveEquityResult.objects.filter(opencrossed="put")

            callcrossedsetDict = {}
            callonepercentsetDict = {}
            putcrossedsetDict = {}
            putonepercentsetDict = {}
            opencallcrossDict = {}
            openputcrossDict = {}

            for i in callcrossedset:
                callcrossedsetDict[i.symbol] = i.time
            for i in callonepercentset:
                callonepercentsetDict[i.symbol] = i.time
            for i in putcrossedset:
                putcrossedsetDict[i.symbol] = i.time
            for i in putonepercentset:
                putonepercentsetDict[i.symbol] = i.time
            for i in opencallcross:
                opencallcrossDict[i.symbol] = i.time
            for i in openputcross:
                openputcrossDict[i.symbol] = i.time

            # Graceful exit
            td_app.stop_live_data(symbols)
            td_app.disconnect()
            td_app.disconnect()
 
            for key,value in liveData.items():
                if key in fnolist:
                    
                    if float(value[6]) >= 3:
                        # print(key)
                        if LiveSegment.objects.filter(symbol=key,segment="gain").exists():
                            LiveSegment.objects.filter(symbol=key,segment="gain").delete()
                            gain = LiveSegment(symbol=key,segment="gain",change_perc=value[6],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d'),time=dt.now(timezone("Asia/Kolkata")).strftime('%H:%M:%S'),doneToday="Yes")
                            gain.save()

                        else:
                            gain = LiveSegment(symbol=key,segment="gain",change_perc=value[6],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d'),time=dt.now(timezone("Asia/Kolkata")).strftime('%H:%M:%S'),doneToday="Yes")
                            gain.save()

                    elif float(value[6]) <= -3:
                        if LiveSegment.objects.filter(symbol=key,segment="loss").exists():
                            LiveSegment.objects.filter(symbol=key,segment="loss").delete()
                            loss = LiveSegment(symbol=key,segment="loss",change_perc=value[6],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d'),time=dt.now(timezone("Asia/Kolkata")).strftime('%H:%M:%S'),doneToday="Yes")
                            loss.save()
                        else:
                            loss = LiveSegment(symbol=key,segment="loss",change_perc=value[6],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d'),time=dt.now(timezone("Asia/Kolkata")).strftime('%H:%M:%S'),doneToday="Yes")
                            loss.save()

                    elif float(value[6]) <= -0.30:
                        if LiveSegment.objects.filter(symbol=key,segment="below").exists():
                            LiveSegment.objects.filter(symbol=key,segment="below").delete()
                            loss = LiveSegment(symbol=key,segment="below",change_perc=value[6],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d'),time=dt.now(timezone("Asia/Kolkata")).strftime('%H:%M:%S'),doneToday="Yes")
                            loss.save()
                        else:
                            loss = LiveSegment(symbol=key,segment="below",change_perc=value[6],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d'),time=dt.now(timezone("Asia/Kolkata")).strftime('%H:%M:%S'),doneToday="Yes")
                            loss.save()

                    elif float(value[6]) >= 0.30:
                        if LiveSegment.objects.filter(symbol=key,segment="above").exists():
                            LiveSegment.objects.filter(symbol=key,segment="above").delete()
                            loss = LiveSegment(symbol=key,segment="above",change_perc=value[6],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d'),time=dt.now(timezone("Asia/Kolkata")).strftime('%H:%M:%S'),doneToday="Yes")
                            loss.save()
                        else:
                            loss = LiveSegment(symbol=key,segment="above",change_perc=value[6],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d'),time=dt.now(timezone("Asia/Kolkata")).strftime('%H:%M:%S'),doneToday="Yes")
                            loss.save()

            gainList = list(LiveSegment.objects.filter(segment="gain").values_list('symbol', flat=True))
            lossList = list(LiveSegment.objects.filter(segment="loss").values_list('symbol', flat=True))
        
        except websocket.WebSocketConnectionClosedException as e:
            print('This caught the websocket exception ')
            td_app.disconnect()
            # return render(request,"testhtml.html",{'symbol':item,'counter':1}) 
        except IndexError as e:
            print('This caught the exception')
            print(e)
            td_app.disconnect()
            # return render(request,"testhtml.html",{'symbol':item,'counter':1}) 
        except Exception as e:
            print(e)
            td_app.disconnect()
            # return render(request,"testhtml.html",{'symbol':item,'counter':1}) 
  
    equitypastdate = datetime.combine(datetime.now(timezone('Asia/Kolkata')), time(9,15)).strftime('%Y-%m-%d %H:%M:%S')
    timenow = datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S')

    doneToday = LiveSegment.objects.values_list('doneToday', flat=True).distinct()

    if len(doneToday) > 0:
        doneToday = doneToday[0]
    else:
        doneToday = ""

    if timenow > equitypastdate and doneToday != "Yes":
        initialEquity()
   
    fnolist = []

    gainList = list(LiveSegment.objects.filter(segment="gain").values_list('symbol', flat=True))
    lossList = list(LiveSegment.objects.filter(segment="loss").values_list('symbol', flat=True))
    segments = list(LiveSegment.objects.values_list('symbol', flat=True).distinct())
    
    fnolist.extend(gainList)
    fnolist.extend(lossList)
    fnolist.extend(segments)

    fnolist = list(set(fnolist))

    def OIPercentChange(df):
        print("Enter OIper")
        ce = df.loc[df['type'] == "CE"]
        pe = df.loc[df['type'] == "PE"]

        # ce_oipercent_df = ce.sort_values(by=['oi_change_perc'], ascending=False)
        ce_oipercent_df = ce.where(ce['oi_change_perc'] !=0 ).sort_values(by=['oi_change_perc'], ascending=False)

        # print(ce_oipercent_df)
        
        minvalue = ce.loc[ce['strike'] != 0].sort_values('strike', ascending=True)
        ceindex = minvalue.iloc[0].name
        peindex = ceindex.replace("CE", "PE")
        pe = pe[peindex:]

        ceoi1 = ce_oipercent_df.iloc[0]['oi_change_perc']
        cestrike = ce_oipercent_df.iloc[0]['strike']
        peoi1 = pe.loc[pe['strike']==ce_oipercent_df.iloc[0]['strike']].iloc[0]['oi_change_perc']

        # print(ceoi1)
        # print(cestrike)
        # print(peoi1)

        pe_oipercent_df = pe.where(pe['oi_change_perc'] !=0 ).sort_values(by=['oi_change_perc'], ascending=False)

        ceoi2 = pe_oipercent_df.iloc[0]['oi_change_perc']
        pestrike = pe_oipercent_df.iloc[0]['strike']
        peoi2 = ce.loc[ce['strike']==pe_oipercent_df.iloc[0]['strike']].iloc[0]['oi_change_perc']

        # print(ceoi2)
        # print(pestrike)

        # print(peoi2)
        import datetime as det
        # celtt = pe_oipercent_df.iloc[count]['ltt']
        celtt = dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S')
        celtt = dt.strptime(str(celtt), "%Y-%m-%d %H:%M:%S").time()

        my_time_string = "15:30:00"
        my_datetime = det.datetime.strptime(my_time_string, "%H:%M:%S").time()

        if celtt > my_datetime:
            celtt = det.datetime.now().replace(hour=15,minute=30,second=00).strftime("%Y-%m-%d %H:%M:%S")
            peltt = det.datetime.now().replace(hour=15,minute=30,second=00).strftime("%Y-%m-%d %H:%M:%S")
        else:
            celtt = pe_oipercent_df.iloc[0]['ltt']
            peltt = pe_oipercent_df.iloc[0]['ltt']


        OIPercentChange = {"celtt":celtt,"ceoi1":ceoi1,"cestrike":cestrike,"peoi1":peoi1,"peltt":peltt,"peoi2":peoi2,"pestrike":pestrike,"ceoi2":ceoi2}
        print("Exit OIper")
        return OIPercentChange

    def OITotal(df,item,dte):
        print("Enter OITotl")

        ce = df.loc[df['type'] == "CE"]
        pe = df.loc[df['type'] == "PE"]

        # print("before final df")

        final_df = ce.loc[ce['oi'] != 0].sort_values('oi', ascending=False)

        minvalue = ce.loc[ce['strike'] != 0].sort_values('strike', ascending=True)

        ceindex = minvalue.iloc[0].name
        peindex = ceindex.replace("CE", "PE")
        pe = pe[peindex:]

        peoi1 = pe.loc[pe['strike']==final_df.iloc[0]['strike']].iloc[0]['oi']
        count = 0

        while peoi1 == 0:
            count = count + 1
            peoi1 = pe.loc[pe['strike']==final_df.iloc[count]['strike']].iloc[0]['oi']

        cestrike = final_df.iloc[count]['strike']
        ceoi1 = final_df.iloc[count]['oi']
        
        import datetime as det
        celtt = final_df.iloc[count]['ltt']
        celtt = dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S')
        celtt = dt.strptime(str(celtt), "%Y-%m-%d %H:%M:%S").time()

        my_time_string = "15:30:00"
        my_datetime = det.datetime.strptime(my_time_string, "%H:%M:%S").time()

        if celtt > my_datetime:
            celtt = det.datetime.now().replace(hour=15,minute=30,second=00).strftime("%Y-%m-%d %H:%M:%S")
            peltt = det.datetime.now().replace(hour=15,minute=30,second=00).strftime("%Y-%m-%d %H:%M:%S")
        else:
            celtt = final_df.iloc[0]['ltt']
            peltt = final_df.iloc[0]['ltt']

        # print(ceoi1)
        # print(cestrike)
        # print(peoi1)

        final_df = pe.loc[pe['oi'] != 0].sort_values('oi', ascending=False)

        ceoi2 = ce.loc[ce['strike']==final_df.iloc[0]['strike']].iloc[0]['oi']
        count = 0

        while ceoi2 == 0:
            count = count + 1
            ceoi2 = ce.loc[ce['strike']==final_df.iloc[count]['strike']].iloc[0]['oi']

        pestrike = final_df.iloc[count]['strike']
        peoi2 = final_df.iloc[count]['oi']

        # print(ceoi2)
        # print(pestrike)
        # print(peoi2)   

        OITot = {"celtt":celtt,"ceoi1":ceoi1,"cestrike":cestrike,"peoi1":peoi1,"peltt":peltt,"peoi2":peoi2,"pestrike":pestrike,"ceoi2":ceoi2}
        print("Exit OITotl")
        return OITot

    def OIChange(df,item,dte):
        ce = df.loc[df['type'] == "CE"]
        pe = df.loc[df['type'] == "PE"]

        # print("1")

        final_df = ce.loc[ce['oi_change'] != 0].sort_values('oi_change', ascending=False)
        minvalue = ce.loc[ce['strike'] != 0].sort_values('strike', ascending=True)

        # print("2")
        ceindex = minvalue.iloc[0].strike
        # peindex = ceindex.replace("CE", "PE")
        inde = pe[pe['strike']==ceindex].index.values
        pe = pe[inde[0]:]
        print(pe)
        # ce.to_excel("ce.xlsx")
        # print("3")
        print(final_df.iloc[0]['strike'])
        print(pe.loc[pe['strike']==str(final_df.iloc[0]['strike'])])   
        peoi1 = pe.loc[pe['strike']==str(final_df.iloc[0]['strike'])].iloc[0]['oi_change']
        count = 0
        # print("4")
        while peoi1 == 0:
            count = count + 1
            peoi1 = pe.loc[pe['strike']==final_df.iloc[count]['strike']].iloc[0]['oi_change']
        # print("5")
        cestrike = final_df.iloc[count]['strike']
        ceoi1 = final_df.iloc[count]['oi_change']
        import datetime as det
        # print("6")
        celtt = final_df.iloc[count]['ltt']
        celtt = dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S')
        celtt = dt.strptime(str(celtt), "%Y-%m-%d %H:%M:%S").time()

        my_time_string = "15:30:00"
        my_datetime = det.datetime.strptime(my_time_string, "%H:%M:%S").time()

        if celtt > my_datetime:
            celtt = det.datetime.now().replace(hour=15,minute=30,second=00).strftime("%Y-%m-%d %H:%M:%S")
            peltt = det.datetime.now().replace(hour=15,minute=30,second=00).strftime("%Y-%m-%d %H:%M:%S")
        else:
            celtt = final_df.iloc[0]['ltt']
            peltt = final_df.iloc[0]['ltt']

        print(ceoi1)
        print(cestrike)
        print(peoi1)
        # print("7")

        final_df = pe.loc[pe['oi_change'] != 0].sort_values('oi_change', ascending=False)

        ceoi2 = ce.loc[ce['strike']==final_df.iloc[0]['strike']].iloc[0]['oi_change']
        count = 0
        # print("8")

        while ceoi2 == 0:
            count = count + 1
            ceoi2 = ce.loc[ce['strike']==final_df.iloc[count]['strike']].iloc[0]['oi_change']

        pestrike = final_df.iloc[count]['strike']
        peoi2 = final_df.iloc[count]['oi_change']
        peltt = final_df.iloc[count]['ltt']

        # print(ceoi2)
        # print(pestrike)
        # print(peoi2)

        OIChan = {"celtt":celtt,"ceoi1":ceoi1,"cestrike":cestrike,"peoi1":peoi1,"peltt":peltt,"peoi2":peoi2,"pestrike":pestrike,"ceoi2":ceoi2}
        print("Exit OiChnge")
        return OIChan

    def optionChainprocess(df,item,dte):
       
        

        # Total OI Calculation from Option chain
        FutureData = {}

        # value1 = LiveOIChange.objects.all()
        # value2 = LiveOITotal.objects.all()
        # print("Before changev")
        OIChangeValue = OIChange(df,item,dte)
        print("after change")
        
        if OIChangeValue == False:
            print("returning false")
            # return render(request,"testhtml.html",{'symbol':item,'counter':1})

        OITotalValue = OITotal(df,item,dte)

        if OITotalValue == False:
            print("returning false")
            # return render(request,"testhtml.html",{'symbol':item,'counter':1})

        percentChange = OIPercentChange(df)

        # strikeGap =float(df['strike'].unique()[1]) - float(df['strike'].unique()[0])
        midvalue = round(len(df['strike'].unique())/2)
        strikeGap =float(df['strike'].unique()[midvalue]) - float(df['strike'].unique()[midvalue-1])

        FutureData[item] = [OITotalValue['cestrike'],OITotalValue['pestrike'],strikeGap]

        # print(FutureData)

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
        
        # # Fetching today's date
        dat = dt.today()

        # print("before deletiong")

        from datetime import datetime, time
        pastDate = datetime.combine(datetime.now(timezone('Asia/Kolkata')), time(9,15))

        # LiveEquityResult.objects.all().delete()
        LiveOITotalAllSymbol.objects.filter(time__lte = pastDate).delete()

        # # Deleting past historical data in the database
        HistoryOIChange.objects.filter(time__lte = pastDate).delete()
        HistoryOITotal.objects.filter(time__lte = pastDate).delete()
        HistoryOIPercentChange.objects.filter(time__lte = pastDate).delete()

        # Deleting live data
        LiveOITotal.objects.filter(time__lte = pastDate).delete()
        LiveOIChange.objects.filter(time__lte = pastDate).delete()
        LiveOIPercentChange.objects.filter(time__lte = pastDate).delete()

        # print("After deletion")
        
        value1 = LiveOIChange.objects.filter(symbol=item)

        if len(value1) > 0:

            if (value1[0].callstrike != OIChangeValue['cestrike']) or (value1[0].putstrike != OIChangeValue['pestrike']):
                # Adding to history table
                ChangeOIHistory = HistoryOIChange(time=value1[0].time,call1=value1[0].call1,call2=value1[0].call2,put1=value1[0].put1,put2=value1[0].put2,callstrike=value1[0].callstrike,putstrike=value1[0].putstrike,symbol=value1[0].symbol,expiry=value1[0].expiry)
                ChangeOIHistory.save()

                # deleting live table data
                LiveOIChange.objects.filter(symbol=item).delete()

                # Creating in live data
                ChangeOICreation = LiveOIChange(time=OIChangeValue['celtt'],call1=OIChangeValue['ceoi1'],call2=OIChangeValue['ceoi2'],put1=OIChangeValue['peoi1'],put2=OIChangeValue['peoi2'],callstrike=OIChangeValue['cestrike'],putstrike=OIChangeValue['pestrike'],symbol=item,expiry=dte)
                ChangeOICreation.save() 

            else:
                # deleting live table data
                LiveOIChange.objects.filter(symbol=item).delete()

                # Creating in live data
                ChangeOICreation = LiveOIChange(time=OIChangeValue['celtt'],call1=OIChangeValue['ceoi1'],call2=OIChangeValue['ceoi2'],put1=OIChangeValue['peoi1'],put2=OIChangeValue['peoi2'],callstrike=OIChangeValue['cestrike'],putstrike=OIChangeValue['pestrike'],symbol=item,expiry=dte)
                ChangeOICreation.save() 
        else:
            ChangeOICreation = LiveOIChange(time=OIChangeValue['celtt'],call1=OIChangeValue['ceoi1'],call2=OIChangeValue['ceoi2'],put1=OIChangeValue['peoi1'],put2=OIChangeValue['peoi2'],callstrike=OIChangeValue['cestrike'],putstrike=OIChangeValue['pestrike'],symbol=item,expiry=dte)
            ChangeOICreation.save()


        # print("value1 crossed")

        value2 = LiveOITotal.objects.filter(symbol=item)

        if len(value2) > 0:

            if (value2[0].callstrike != OITotalValue['cestrike']) or (value2[0].putstrike != OITotalValue['pestrike']):
                # Adding to history table
                TotalOIHistory = HistoryOITotal(time=value2[0].time,call1=value2[0].call1,call2=value2[0].call2,put1=value2[0].put1,put2=value2[0].put2,callstrike=value2[0].callstrike,putstrike=value2[0].putstrike,symbol=value2[0].symbol,expiry=value2[0].expiry)
                TotalOIHistory.save()

                # deleting live table data
                LiveOITotal.objects.filter(symbol=item).delete()

                # Creating in live data
                TotalOICreation = LiveOITotal(time=OITotalValue['celtt'],call1=OITotalValue['ceoi1'],call2=OITotalValue['ceoi2'],put1=OITotalValue['peoi1'],put2=OITotalValue['peoi2'],callstrike=OITotalValue['cestrike'],putstrike=OITotalValue['pestrike'],symbol=item,expiry=dte,strikegap=strikeGap)
                TotalOICreation.save()

                # Live data for equity
                LiveOITotalAllSymbol.objects.filter(symbol=item).delete()
                TotalOICreationAll = LiveOITotalAllSymbol(time=OITotalValue['celtt'],call1=OITotalValue['ceoi1'],call2=OITotalValue['ceoi2'],put1=OITotalValue['peoi1'],put2=OITotalValue['peoi2'],callstrike=OITotalValue['cestrike'],putstrike=OITotalValue['pestrike'],symbol=item,expiry=dte,callone=callone,putone=putone,callhalf=callhalf,puthalf=puthalf)
                TotalOICreationAll.save()


            else:
                # deleting live table data
                LiveOITotal.objects.filter(symbol=item).delete()

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

        value3 = LiveOIPercentChange.objects.filter(symbol=item)

        if len(value3) > 0:

            if (value3[0].callstrike != percentChange['cestrike']) or (value3[0].putstrike != percentChange['pestrike']):
                # Adding to history table
                ChangeOIPercentHistory = HistoryOIPercentChange(time=value3[0].time,call1=value3[0].call1,call2=value3[0].call2,put1=value3[0].put1,put2=value3[0].put2,callstrike=value3[0].callstrike,putstrike=value3[0].putstrike,symbol=value3[0].symbol,expiry=value3[0].expiry)
                ChangeOIPercentHistory.save()

                # deleting live table data
                LiveOIPercentChange.objects.filter(symbol=item).delete()

                # Creating in live data
                ChangeOIPercentCreation = LiveOIPercentChange(time=percentChange['celtt'],call1=percentChange['ceoi1'],call2=percentChange['ceoi2'],put1=percentChange['peoi1'],put2=percentChange['peoi2'],callstrike=percentChange['cestrike'],putstrike=percentChange['pestrike'],symbol=item,expiry=dte)
                ChangeOIPercentCreation.save() 

            else:
                # deleting live table data
                LiveOIPercentChange.objects.filter(symbol=item).delete()

                # Creating in live data
                ChangeOIPercentCreation = LiveOIPercentChange(time=percentChange['celtt'],call1=percentChange['ceoi1'],call2=percentChange['ceoi2'],put1=percentChange['peoi1'],put2=percentChange['peoi2'],callstrike=percentChange['cestrike'],putstrike=percentChange['pestrike'],symbol=item,expiry=dte)
                ChangeOIPercentCreation.save() 
        else:
            ChangeOIPercentCreation = LiveOIPercentChange(time=percentChange['celtt'],call1=percentChange['ceoi1'],call2=percentChange['ceoi2'],put1=percentChange['peoi1'],put2=percentChange['peoi2'],callstrike=percentChange['cestrike'],putstrike=percentChange['pestrike'],symbol=item,expiry=dte)
            ChangeOIPercentCreation.save()

    # Fetching the F&NO symbol list
    TrueDatausername = 'tdws127'
    TrueDatapassword = 'saaral@127'

    sampleDict = {}
    count=1

    lenthree = (len(fnolist))%3

    for r,g,b in zip(*[iter(fnolist)]*3):

        
            # realtime
            try:

                TrueDatausernamereal = 'tdws135'
                TrueDatapasswordreal = 'saaral@135'


                import requests
                url = 'https://www.truedata.in/downloads/symbol_lists/13.NSE_ALL_OPTIONS.txt'
                s = requests.get(url).content
                stringlist=[x.decode('utf-8').split('2')[0] for x in s.splitlines()]

                symbols = list(set(stringlist))

                remove_list = ['BANKNIFTY', 'FINNIFTY', 'NIFTY', 'ASIANPAINT','BHARTIARTL', 'BHEL', 'BPCL', 'DEEPAKNTR', 'FEDERALBNK', 'HDFC', 'IOC', 'IRCTC', 'IPCALAB', 'MRF', 'NATIONALUM', 'NTPC', 'PNB','VEDL', 'ASTRAL', 'BOSCHLTD', 'EICHERMOT', 'GMRINFRA', 'HDFCLIFE', 'IBULHSGFIN', 'ITC', 'L&TFH', 'PAGEIND', 'BANKBARODA', 'IDFCFIRSTB','IDEA']
                fnolistreal = [i for i in symbols if i not in remove_list]

                # Default production port is 8082 in the library. Other ports may be given t oyou during trial.
                realtime_port = 8082

                print('Starting Real Time Feed.... ')
                print(f'Port > {realtime_port}')

                td_app = TD(TrueDatausernamereal, TrueDatapasswordreal, live_port=realtime_port, historical_api=False)
                # print(symbols)
                req_ids = td_app.start_live_data(symbols)
                live_data_objs = {}

                te.sleep(3)

                liveData = {}
                for req_id in req_ids:
                    # print(td_app.live_data[req_id].day_open)
                    if (td_app.live_data[req_id].ltp) == None:
                        continue
                    else:
                        liveData[td_app.live_data[req_id].symbol] = [td_app.live_data[req_id].ltp,td_app.live_data[req_id].day_open,td_app.live_data[req_id].day_high,td_app.live_data[req_id].day_low,td_app.live_data[req_id].prev_day_close,dt.now(timezone("Asia/Kolkata")).strftime('%H:%M:%S'),td_app.live_data[req_id].change_perc]


                # Finding out the pastdate
                from datetime import datetime, timedelta
                pastDate = datetime.combine(datetime.now(timezone('Asia/Kolkata')), time(9,15))
                segpastDate = datetime.combine(datetime.now(timezone('Asia/Kolkata')), time(9,15)).time()
                nsepadDate = datetime.combine(datetime.now(timezone('Asia/Kolkata')), time(9,15)).date()
                # LiveEquityResult.objects.all().delete()
                LiveEquityResult.objects.filter(date__lte = pastDate).delete()

                removeList = ["NIFTY","BANKNIFTY","FINNIFTY"]

                callcrossedset = LiveEquityResult.objects.filter(strike__contains="Call Crossed")
                callonepercentset = LiveEquityResult.objects.filter(strike="Call 1 percent")
                putcrossedset = LiveEquityResult.objects.filter(strike="Put Crossed")
                putonepercentset = LiveEquityResult.objects.filter(strike="Put 1 percent")
                opencallcross = LiveEquityResult.objects.filter(opencrossed="call")
                openputcross = LiveEquityResult.objects.filter(opencrossed="put")

                callcrossedsetDict = {}
                callonepercentsetDict = {}
                putcrossedsetDict = {}
                putonepercentsetDict = {}
                opencallcrossDict = {}
                openputcrossDict = {}

                for i in callcrossedset:
                    callcrossedsetDict[i.symbol] = i.time
                for i in callonepercentset:
                    callonepercentsetDict[i.symbol] = i.time
                for i in putcrossedset:
                    putcrossedsetDict[i.symbol] = i.time
                for i in putonepercentset:
                    putonepercentsetDict[i.symbol] = i.time
                for i in opencallcross:
                    opencallcrossDict[i.symbol] = i.time
                for i in openputcross:
                    openputcrossDict[i.symbol] = i.time

                # Graceful exit
                td_app.stop_live_data(symbols)
                td_app.disconnect()
                td_app.disconnect()
                # print(liveData)

                # LiveSegment.objects.filter(time__lte = pastDate,date__lte = nsepadDate).delete()
                LiveSegment.objects.filter(time__lte = segpastDate).delete()
                LiveSegment.objects.filter(date__lt = nsepadDate).delete()

                for key,value in liveData.items():
                    if key in fnolistreal:
                        if float(value[6]) >= 3:
                            if len(LiveSegment.objects.filter(symbol=key,segment="gain")) > 0:
                                LiveSegment.objects.filter(symbol=key,segment="gain").delete()
                                gain = LiveSegment(symbol=key,segment="gain",change_perc=value[6],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d'),time=dt.now(timezone("Asia/Kolkata")).strftime('%H:%M:%S'))
                                gain.save()

                            else:
                                gain = LiveSegment(symbol=key,segment="gain",change_perc=value[6],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d'),time=dt.now(timezone("Asia/Kolkata")).strftime('%H:%M:%S'))
                                gain.save()

                        elif float(value[6]) <= -3:
                            if len(LiveSegment.objects.filter(symbol=key,segment="loss")) > 0:
                                LiveSegment.objects.filter(symbol=key,segment="loss").delete()
                                loss = LiveSegment(symbol=key,segment="loss",change_perc=value[6],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d'),time=dt.now(timezone("Asia/Kolkata")).strftime('%H:%M:%S'))
                                loss.save()
                            else:
                                loss = LiveSegment(symbol=key,segment="loss",change_perc=value[6],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d'),time=dt.now(timezone("Asia/Kolkata")).strftime('%H:%M:%S'))
                                loss.save()

                    #     elif float(value[6]) <= -0.30:
                    #         if len(LiveSegment.objects.filter(symbol=key,segment="below")) > 0:
                    #             LiveSegment.objects.filter(symbol=key,segment="below").delete()
                    #             loss = LiveSegment(symbol=key,segment="below",change_perc=value[6],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d'),time=dt.now(timezone("Asia/Kolkata")).strftime('%H:%M:%S'))
                    #             loss.save()
                    #         else:
                    #             loss = LiveSegment(symbol=key,segment="below",change_perc=value[6],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d'),time=dt.now(timezone("Asia/Kolkata")).strftime('%H:%M:%S'))
                    #             loss.save()

                    #     elif float(value[6]) >= 0.30:
                    #         if len(LiveSegment.objects.filter(symbol=key,segment="above")) > 0:
                    #             LiveSegment.objects.filter(symbol=key,segment="above").delete()
                    #             loss = LiveSegment(symbol=key,segment="above",change_perc=value[6],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d'),time=dt.now(timezone("Asia/Kolkata")).strftime('%H:%M:%S'))
                    #             loss.save()
                    #         else:
                    #             loss = LiveSegment(symbol=key,segment="above",change_perc=value[6],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d'),time=dt.now(timezone("Asia/Kolkata")).strftime('%H:%M:%S'))
                    #             loss.save()

                gainList = list(LiveSegment.objects.filter(segment="gain").values_list('symbol', flat=True))
                lossList = list(LiveSegment.objects.filter(segment="loss").values_list('symbol', flat=True))


                # History Check
                for e in LiveOITotalAllSymbol.objects.all():
                    # print(e.symbol)
                    # callcross = TestEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="common",opencrossed="common",time=dt.now(timezone("Asia/Kolkata")).strftime('%H:%M:%S'),date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S'))
                    # callcross.save()

                    # History Check
                    historyLen = HistoryOITotal.objects.filter(symbol=e.symbol)

                    if len(historyLen) > 0:
                        historyStrike = HistoryOITotal.objects.filter(symbol=e.symbol).earliest('time')
                        strikegp = LiveOITotal.objects.filter(symbol=e.symbol)
                        callstrike = historyStrike.callstrike
                        putstrike = historyStrike.putstrike
                        # Call 1 percent 
                        callone = float(callstrike) - (float(strikegp[0].strikegap))*0.1
                        # Put 1 percent
                        putone = float(putstrike) + (float(strikegp[0].strikegap))*0.1

                    else:
                        callstrike = e.callstrike
                        putstrike = e.putstrike
                        callone = e.callone
                        putone = e.putone
                    
                    if e.symbol in liveData and e.symbol not in removeList and e.symbol in gainList:
                        
                        # Call
                        if liveData[e.symbol][1] > float(callstrike):
                            if e.symbol in opencallcrossDict:
                                LiveEquityResult.objects.filter(symbol = e.symbol).delete()
                                callcross = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Call Crossed",opencrossed="call",time=opencallcrossDict[e.symbol],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S'))
                                callcross.save()

                                continue
                            else:
                                callcross = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Call Crossed",opencrossed="call",time=liveData[e.symbol][5],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S'))
                                callcross.save()
                                continue
                        

                        if liveData[e.symbol][0] > float(callstrike) or liveData[e.symbol][1] > float(callstrike):
                            if e.symbol in callcrossedsetDict:
                                # print("Yes")
                                # Deleting the older
                                LiveEquityResult.objects.filter(symbol = e.symbol).delete()
                                # updating latest data
                                # print("Yes")
                                callcross = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Call Crossed",opencrossed="Nil",time=callcrossedsetDict[e.symbol],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S'))
                                callcross.save()

                                continue

                            else:
                                # print("Call crossed")
                                callcross = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Call Crossed",opencrossed="Nil",time=liveData[e.symbol][5],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S'))
                                callcross.save()

                            
                        elif liveData[e.symbol][0] >= float(callone) and liveData[e.symbol][0] <= float(callstrike):

                            if e.symbol in callcrossedsetDict:
                                # print("Already crossed")
                                continue
                            else:
                                if e.symbol in callonepercentsetDict:
                                    # print("Already crossed 1 percent")
                                    LiveEquityResult.objects.filter(symbol = e.symbol).delete()
                                    # updating latest data
                                    callcross = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Call 1 percent",opencrossed="Nil",time=callonepercentsetDict[e.symbol],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S'))
                                    callcross.save()

                                    continue
                                else:
                                    # print("Call 1 percent")

                                    callone = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Call 1 percent",opencrossed="Nil",time=liveData[e.symbol][5],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S'))
                                    callone.save()




                        # Put
                        if e.symbol in liveData and e.symbol not in removeList and e.symbol in lossList:

                            if liveData[e.symbol][1] < float(putstrike):
                                if e.symbol in openputcrossDict:
                                    LiveEquityResult.objects.filter(symbol = e.symbol).delete()
                                    putcross = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Put Crossed",opencrossed="put",time=openputcrossDict[e.symbol],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S'))
                                    putcross.save()

                                    continue
                                else:
                                    putcross = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Put Crossed",opencrossed="put",time=liveData[e.symbol][5],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S'))
                                    putcross.save()

                                    continue

                            if liveData[e.symbol][0] < float(putstrike) or liveData[e.symbol][2] < float(putstrike):
                                if e.symbol in putcrossedsetDict:
                                    # Deleting the older
                                    LiveEquityResult.objects.filter(symbol =e.symbol).delete()
                                    # updating latest data
                                    putcross = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Put Crossed",opencrossed="Nil",time=putcrossedsetDict[e.symbol],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S'))
                                    putcross.save()
                                    # print("put crossed updating only the data")
                                    continue
                                else:
                                    # print("Put crossed")
                                    putcross = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Put Crossed",opencrossed="Nil",time=liveData[e.symbol][5],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S'))
                                    putcross.save()



                            elif liveData[e.symbol][0] <= float(putone) and liveData[e.symbol][0] >= float(putstrike):
                                if e.symbol in putcrossedsetDict:
                                    # print("Already crossed put")
                                    continue
                                else:
                                    if e.symbol in putonepercentsetDict:
                                        # print("Already crossed 1 percent")
                                        LiveEquityResult.objects.filter(symbol =e.symbol).delete()
                                        # updating latest data
                                        putcross = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Put 1 percent",opencrossed="Nil",time=putonepercentsetDict[e.symbol],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S'))
                                        putcross.save()
                                        continue
                                    else:
                                        # print("Put 1 percent")
                                        putone = LiveEquityResult(symbol=e.symbol,open=liveData[e.symbol][1],high=liveData[e.symbol][2],low=liveData[e.symbol][3],prev_day_close=liveData[e.symbol][4],ltp=liveData[e.symbol][0],strike="Put 1 percent",opencrossed="Nil",time=liveData[e.symbol][5],date=dt.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S'))
                                        putone.save()

            except websocket.WebSocketConnectionClosedException as e:
                print('This caught the websocket exception in equity realtime')
                td_app.disconnect()
                td_app.disconnect()
                # return render(request,"testhtml.html",{'symbol':item,'counter':1}) 
            except IndexError as e:
                print('This caught the exception in equity realtime')
                print(e)
                td_app.disconnect()
                td_app.disconnect()
                # return render(request,"testhtml.html",{'symbol':item,'counter':1}) 
            except Exception as e:
                print(e)
                td_app.disconnect()
                td_app.disconnect()
                # return render(request,"testhtml.html",{'symbol':item,'counter':1}) 
            
            # optionchain 3 symbols
            try:
                exceptionList = ['NIFTY','BANKNIFTY','FINNIFTY']
                if r in exceptionList:
                        if calendar.day_name[date.today().weekday()] == "Thrusday":
                            expiry = date.today()
                            expiry = "7-Oct-2021"
                            dte = dt.strptime(expiry, '%d-%b-%Y')
                            # print("inside thursday")
                        else:
                            expiry = pendulum.now().next(pendulum.THURSDAY).strftime('%d-%b-%Y')
                            expiry = "7-Oct-2021"
                            dte = dt.strptime(expiry, '%d-%b-%Y')
                else:
                    # print("inside monthend")
                    expiry = "28-Oct-2021"
                    dte = dt.strptime(expiry, '%d-%b-%Y')

                # print("After exception")

                # td_obj = TD(TrueDatausername, TrueDatapassword, log_level= logging.WARNING )
                symbol1 = r
                symbol2 = g
                symbol3 = b
                td_obj = TD('tdws127', 'saaral@127')
                first_chain = td_obj.start_option_chain( symbol1 , dt(dte.year , dte.month , dte.day) ,chain_length = 74)
                second_chain = td_obj.start_option_chain( symbol2 , dt(dte.year , dte.month , dte.day) ,chain_length = 74)
                third_chain = td_obj.start_option_chain( symbol3 , dt(dte.year , dte.month , dte.day) ,chain_length = 74)

                te.sleep(3)

                df1 = first_chain.get_option_chain()
                df2 = second_chain.get_option_chain()
                df3 = third_chain.get_option_chain()

                first_chain.stop_option_chain()
                second_chain.stop_option_chain()
                third_chain.stop_option_chain()

                td_obj.disconnect()
                td_obj.disconnect()
                # td_app.disconnect()
                sampleDict[symbol1] = df1

                print(df1)
                print(df2)
                print(df3)
                # print(count)
                # print(item)
                count = count + 1

                optionChainprocess(df1,symbol1,dte)
                optionChainprocess(df2,symbol2,dte)
                optionChainprocess(df3,symbol3,dte)

            
            except websocket.WebSocketConnectionClosedException as e:
                print('This caught the websocket exception in optionchain realtime')
                td_obj.disconnect()
                td_obj.disconnect()
            except IndexError as e:
                print('This caught the exception in option chain realtime')
                print(e)
                td_obj.disconnect()
                td_obj.disconnect()
            except Exception as e:
                print(e)
                td_obj.disconnect()
                td_obj.disconnect()


    if lenthree == 2:

        try:
            exceptionList = ['NIFTY','BANKNIFTY','FINNIFTY']
            if fnolist[-1] in exceptionList:
                    if calendar.day_name[date.today().weekday()] == "Thrusday":
                        expiry = date.today()
                        expiry = "7-Oct-2021"
                        dte = dt.strptime(expiry, '%d-%b-%Y')
                        # print("inside thursday")
                    else:
                        expiry = pendulum.now().next(pendulum.THURSDAY).strftime('%d-%b-%Y')
                        expiry = "7-Oct-2021"
                        dte = dt.strptime(expiry, '%d-%b-%Y')
            else:
                # print("inside monthend")
                expiry = "28-Oct-2021"
                dte = dt.strptime(expiry, '%d-%b-%Y')

            # print("After exception")

            # td_obj = TD(TrueDatausername, TrueDatapassword, log_level= logging.WARNING )
            symbol1 = fnolist[-1]
            symbol2 = fnolist[-2]
            td_obj = TD('tdws127', 'saaral@127')
            first_chain = td_obj.start_option_chain( symbol1 , dt(dte.year , dte.month , dte.day) ,chain_length = 75)
            second_chain = td_obj.start_option_chain( symbol2 , dt(dte.year , dte.month , dte.day) ,chain_length = 75)

            te.sleep(3)

            df1 = first_chain.get_option_chain()
            df2 = second_chain.get_option_chain()

            first_chain.stop_option_chain()
            second_chain.stop_option_chain()

            td_obj.disconnect()
            td_obj.disconnect()
            sampleDict[symbol1] = df1

            print(df1)
            print(df2)
            # print(count)
            # print(item)
            count = count + 1

            optionChainprocess(df1,symbol1,dte)
            optionChainprocess(df2,symbol2,dte)

            
        except websocket.WebSocketConnectionClosedException as e:
            print('This caught the websocket exception in optionchain realtime ')
            td_obj.disconnect()
            td_obj.disconnect()
        except IndexError as e:
            print('This caught the exception in optionchain realtime')
            print(e)
            td_obj.disconnect()
            td_obj.disconnect()
        except Exception as e:
            print(e)
            td_obj.disconnect()
            td_obj.disconnect()
        sleep(1)

    elif lenthree == 1:
        try:
            exceptionList = ['NIFTY','BANKNIFTY','FINNIFTY']
            if fnolist[-1] in exceptionList:
                    if calendar.day_name[date.today().weekday()] == "Thrusday":
                        expiry = date.today()
                        expiry = "7-Oct-2021"
                        dte = dt.strptime(expiry, '%d-%b-%Y')
                        # print("inside thursday")
                    else:
                        expiry = pendulum.now().next(pendulum.THURSDAY).strftime('%d-%b-%Y')
                        expiry = "7-Oct-2021"
                        dte = dt.strptime(expiry, '%d-%b-%Y')
            else:
                # print("inside monthend")
                expiry = "28-Oct-2021"
                dte = dt.strptime(expiry, '%d-%b-%Y')

            # print("After exception")

            # td_obj = TD(TrueDatausername, TrueDatapassword, log_level= logging.WARNING )
            symbol1 = fnolist[-1]
            td_obj = TD('tdws127', 'saaral@127')
            first_chain = td_obj.start_option_chain( symbol1 , dt(dte.year , dte.month , dte.day) ,chain_length = 75)

            te.sleep(3)

            df1 = first_chain.get_option_chain()
            first_chain.stop_option_chain()

            td_obj.disconnect()
            td_obj.disconnect()
            sampleDict[symbol1] = df1

            print(df1)
            # print(count)
            # print(item)
            count = count + 1

            optionChainprocess(df1,symbol1,dte)
   
        except websocket.WebSocketConnectionClosedException as e:
            print('This caught the websocket exception in optionchain realtime')
            td_obj.disconnect()
            td_obj.disconnect()

        except IndexError as e:
            print('This caught the exception in optionchain realtime')
            print(e)
            td_obj.disconnect() 
            td_obj.disconnect()
        except Exception as e:
            print(e)
            td_obj.disconnect()
            td_obj.disconnect()
        sleep(1)

while True:
    create_currency()

    