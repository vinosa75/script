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


@shared_task
def create_currency():

    # nse = Nse()
    # fnolist = nse.get_fno_lot_sizes()
    # print(len(fnolist))

    nse = Nse()
    fnolist = nse.get_fno_lot_sizes()

    print(len(fnolist))
    symbols = list(fnolist.keys()) 


    TrueDatausername = 'tdws135'
    TrueDatapassword = 'saaral@135'

    # Default production port is 8082 in the library. Other ports may be given t oyou during trial.
    realtime_port = 8082

    td_app = TD(TrueDatausername, TrueDatapassword, live_port=realtime_port, historical_api=False)

    # symbols = 

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
            print(td_app.live_data[req_id])
            liveData[td_app.live_data[req_id].symbol] = [td_app.live_data[req_id].ltp,td_app.live_data[req_id].day_open,td_app.live_data[req_id].day_high,td_app.live_data[req_id].day_low,td_app.live_data[req_id].prev_day_close]


    td_app.stop_live_data(symbols)
    td_app.disconnect()

    top_gainers = {}
    top_losers = {}

    for key,value in liveData.items():
        print(key)
        print(value)
        gainpercent = (value[4] + (value[4]*0.03))
        losspercent = (value[4] - (value[4]*0.03))
        if value[0] > gainpercent:
            top_gainers[key] = value
        elif value[0] < losspercent:
            top_losers[key] = value

    print(top_gainers.keys())
    print(top_losers.keys())
    print(len(top_gainers))
    print(len(top_losers))

    LiveSegment.objects.all().delete()

    for key,value in top_gainers.items():

        gain = LiveSegment(symbol=key,segment="gain")
        gain.save()

    for key,value in top_losers.items():

        loss = LiveSegment(symbol=key,segment="loss")
        loss.save()


    fnolist = list(LiveSegment.objects.values_list('symbol', flat=True))


    # Removing 3 symbols from the list as they are not required for equity comparision
    remove_list = ['HEROMOTOCO','PFC','BEL','MANAPPURAM','EXIDEIND','PETRONET', 'TATAPOWER', 'ONGC', 'VEDL', 'LALPATHLAB', 'ITC', 'INDHOTEL', 'IDEA','POWERGRID', 'COALINDIA', 'CANBK','HINDPETRO','BANKBARODA','RECLTD','CUB']
    # remove_list = []
    fnolist = [i for i in fnolist if i not in remove_list]

    # fnolist = fnolist[0:3]
    print(fnolist)

    def OIPercentChange(df):
        ce = df.loc[df['type'] == "CE"]
        pe = df.loc[df['type'] == "PE"]

        # ce_oipercent_df = ce.sort_values(by=['oi_change_perc'], ascending=False)
        ce_oipercent_df = ce.where(ce['oi_change_perc'] !=0 ).sort_values(by=['oi_change_perc'], ascending=False)

        print(ce_oipercent_df)
        
        minvalue = ce.loc[ce['strike'] != 0].sort_values('strike', ascending=True)
        ceindex = minvalue.iloc[0].name
        peindex = ceindex.replace("CE", "PE")
        pe = pe[peindex:]

        ceoi1 = ce_oipercent_df.iloc[0]['oi_change_perc']
        cestrike = ce_oipercent_df.iloc[0]['strike']
        peoi1 = pe.loc[pe['strike']==ce_oipercent_df.iloc[0]['strike']].iloc[0]['oi_change_perc']

        print(ceoi1)
        print(cestrike)
        print(peoi1)

        pe_oipercent_df = pe.where(pe['oi_change_perc'] !=0 ).sort_values(by=['oi_change_perc'], ascending=False)

        ceoi2 = pe_oipercent_df.iloc[0]['oi_change_perc']
        pestrike = pe_oipercent_df.iloc[0]['strike']
        peoi2 = ce.loc[ce['strike']==pe_oipercent_df.iloc[0]['strike']].iloc[0]['oi_change_perc']

        print(ceoi2)
        print(pestrike)
        print(peoi2)

        celtt = ce_oipercent_df.iloc[0]['ltt']
        peltt = pe_oipercent_df.iloc[0]['ltt']


        OIPercentChange = {"celtt":celtt,"ceoi1":ceoi1,"cestrike":cestrike,"peoi1":peoi1,"peltt":peltt,"peoi2":peoi2,"pestrike":pestrike,"ceoi2":ceoi2}
        
        return OIPercentChange

    def OITotal(df,item,dte):

        ce = df.loc[df['type'] == "CE"]
        pe = df.loc[df['type'] == "PE"]

        print("before final df")

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
        celtt = final_df.iloc[count]['ltt']

        print(ceoi1)
        print(cestrike)
        print(peoi1)

        final_df = pe.loc[pe['oi'] != 0].sort_values('oi', ascending=False)

        ceoi2 = ce.loc[ce['strike']==final_df.iloc[0]['strike']].iloc[0]['oi']
        count = 0

        while ceoi2 == 0:
            count = count + 1
            ceoi2 = ce.loc[ce['strike']==final_df.iloc[count]['strike']].iloc[0]['oi']

        pestrike = final_df.iloc[count]['strike']
        peoi2 = final_df.iloc[count]['oi']
        peltt = final_df.iloc[count]['ltt']

        print(ceoi2)
        print(pestrike)
        print(peoi2)   

        OITot = {"celtt":celtt,"ceoi1":ceoi1,"cestrike":cestrike,"peoi1":peoi1,"peltt":peltt,"peoi2":peoi2,"pestrike":pestrike,"ceoi2":ceoi2}
        
        return OITot

    def OIChange(df,item,dte):

        ce = df.loc[df['type'] == "CE"]
        pe = df.loc[df['type'] == "PE"]

        print("before final df")

        final_df = ce.loc[ce['oi_change'] != 0].sort_values('oi_change', ascending=False)

        minvalue = ce.loc[ce['strike'] != 0].sort_values('strike', ascending=True)

        ceindex = minvalue.iloc[0].name
        peindex = ceindex.replace("CE", "PE")
        pe = pe[peindex:]

        peoi1 = pe.loc[pe['strike']==final_df.iloc[0]['strike']].iloc[0]['oi_change']
        count = 0

        while peoi1 == 0:
            count = count + 1
            peoi1 = pe.loc[pe['strike']==final_df.iloc[count]['strike']].iloc[0]['oi_change']

        cestrike = final_df.iloc[count]['strike']
        ceoi1 = final_df.iloc[count]['oi_change']
        celtt = final_df.iloc[count]['ltt']

        print(ceoi1)
        print(cestrike)
        print(peoi1)

        final_df = pe.loc[pe['oi_change'] != 0].sort_values('oi_change', ascending=False)

        ceoi2 = ce.loc[ce['strike']==final_df.iloc[0]['strike']].iloc[0]['oi_change']
        count = 0

        while ceoi2 == 0:
            count = count + 1
            ceoi2 = ce.loc[ce['strike']==final_df.iloc[count]['strike']].iloc[0]['oi_change']

        pestrike = final_df.iloc[count]['strike']
        peoi2 = final_df.iloc[count]['oi_change']
        peltt = final_df.iloc[count]['ltt']

        print(ceoi2)
        print(pestrike)
        print(peoi2)      

        OIChan = {"celtt":celtt,"ceoi1":ceoi1,"cestrike":cestrike,"peoi1":peoi1,"peltt":peltt,"peoi2":peoi2,"pestrike":pestrike,"ceoi2":ceoi2}
        
        return OIChan

    # Fetching the F&NO symbol list
    TrueDatausername = 'tdws127'
    TrueDatapassword = 'saaral@127'


    import pendulum
    import calendar
    from datetime import date
    import time as te

    sampleDict = {}
    count=1

    exceptionList = ['NIFTY','BANKNIFTY','FINNIFTY']
    # if item not in sym:

    # LiveOITotalAllSymbol.objects.all().delete()
    # LiveEquityResult.objects.all().delete()

    for item in fnolist:
        try:
            print("Before exception list")

            if item in exceptionList:
                    if calendar.day_name[date.today().weekday()] == "Thrusday":
                        expiry = date.today()
                        expiry = "30-Sep-2021"
                        dte = dt.strptime(expiry, '%d-%b-%Y')
                        print("inside thursday")
                    else:
                        expiry = pendulum.now().next(pendulum.THURSDAY).strftime('%d-%b-%Y')
                        expiry = "30-Sep-2021"
                        dte = dt.strptime(expiry, '%d-%b-%Y')
            else:
                print("inside monthend")
                expiry = "30-Sep-2021"
                dte = dt.strptime(expiry, '%d-%b-%Y')

            print("After exception")

            print(dte)
            print(dte.year)
            print(dte.month)
            print(dte.day)

            # td_obj = TD(TrueDatausername, TrueDatapassword, log_level= logging.WARNING )
            td_obj = TD('tdws127', 'saaral@127')
            nifty_chain = td_obj.start_option_chain( item , dt(dte.year , dte.month , dte.day) ,chain_length = 100)
            te.sleep(4)
            df = nifty_chain.get_option_chain()

            nifty_chain.stop_option_chain()
            td_obj.disconnect()
            sampleDict[item] = df

            print(df)
            print(count)
            print(item)
            count = count + 1

            # Total OI Calculation from Option chain
            FutureData = {}

            # value1 = LiveOIChange.objects.all()
            # value2 = LiveOITotal.objects.all()
            print("Before changev")
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

            strikeGap =float(df['strike'].unique()[1]) - float(df['strike'].unique()[0])

            FutureData[item] = [OITotalValue['cestrike'],OITotalValue['pestrike'],strikeGap]

            print(FutureData)

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

            print("before deletiong")

            from datetime import datetime, time
            pastDate = datetime.combine(datetime.today(), time.min)
    
            # LiveEquityResult.objects.all().delete()
            LiveOITotalAllSymbol.objects.filter(time__lte = pastDate).delete()

            # # Deleting past historical data in the database
            HistoryOIChange.objects.filter(time__lte = pastDate).delete()
            HistoryOITotal.objects.filter(time__lte = pastDate).delete()

            # Deleting live data
            LiveOITotal.objects.filter(time__lte = pastDate).delete()
            LiveOIChange.objects.filter(time__lte = pastDate).delete()

            print("After deletion")
            
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


            print("value1 crossed")

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

        except websocket.WebSocketConnectionClosedException as e:
            print('This caught the websocket exception ')
            td_obj.disconnect()
            # return render(request,"testhtml.html",{'symbol':item,'counter':1}) 
        except IndexError as e:
            print('This caught the exception')
            td_obj.disconnect()
            # return render(request,"testhtml.html",{'symbol':item,'counter':1}) 
        except Exception as e:
            print(e)
            td_obj.disconnect()
            # return render(request,"testhtml.html",{'symbol':item,'counter':1}) 

        sleep(5)


while True:
    create_currency()