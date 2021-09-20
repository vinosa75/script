
Entry = 15135
StrikePrice	= 14950

outputValue = (Entry-StrikePrice)/4
count = 0

sampleList = []

for i in range(0,10):
    
    print(outputValue)
    NewValue = outputValue*(i+1)

    OneFourth = round(outputValue*(count+0.25),2)
    Half = round(outputValue*(count+0.50),2)
    ThreeFourth = round(outputValue*(count+0.75),2)

    count = count+1

    sampleList.append((i,NewValue,OneFourth,Half,ThreeFourth))
    
