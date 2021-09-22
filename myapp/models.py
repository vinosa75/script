from django.db import models
from django.db.models.base import Model
from datetime import date

# Create your models here.

class HistoryOIChange(models.Model):
    time = models.DateTimeField(auto_now_add=False)
    call1 = models.CharField(max_length=20,default="")
    call2 = models.CharField(max_length=20,default="")
    put1 = models.CharField(max_length=20,default="")
    put2 = models.CharField(max_length=20,default="")
    callstrike = models.CharField(max_length=20)
    putstrike = models.CharField(max_length=20)
    symbol = models.CharField(max_length=20)
    expiry = models.DateField(auto_now_add=False)

    def __str__(self):
        return self.call1+" "+self.callstrike+" "+self.symbol

class HistoryOIPercentChange(models.Model):
    time = models.DateTimeField(auto_now_add=False)
    call1 = models.CharField(max_length=20,default="")
    call2 = models.CharField(max_length=20,default="")
    put1 = models.CharField(max_length=20,default="")
    put2 = models.CharField(max_length=20,default="")
    callstrike = models.CharField(max_length=20)
    putstrike = models.CharField(max_length=20)
    symbol = models.CharField(max_length=20)
    expiry = models.DateField(auto_now_add=False)

    def __str__(self):
        return self.call1+" "+self.callstrike+" "+self.symbol

class LiveOIChange(models.Model):
    time = models.DateTimeField(auto_now_add=False)
    call1 = models.CharField(max_length=20,default="")
    call2 = models.CharField(max_length=20,default="")
    put1 = models.CharField(max_length=20,default="")
    put2 = models.CharField(max_length=20,default="")
    callstrike = models.CharField(max_length=20)
    putstrike = models.CharField(max_length=20)
    symbol = models.CharField(max_length=20)
    expiry = models.DateField(auto_now_add=False)

    def __str__(self):
        return self.call1+" "+self.callstrike+" "+self.symbol

class HistoryOITotal(models.Model):
    time = models.DateTimeField(auto_now_add=False)
    call1 = models.CharField(max_length=20,default="")
    call2 = models.CharField(max_length=20,default="")
    put1 = models.CharField(max_length=20,default="")
    put2 = models.CharField(max_length=20,default="")
    callstrike = models.CharField(max_length=20)
    putstrike = models.CharField(max_length=20)
    symbol = models.CharField(max_length=20)
    expiry = models.DateField(auto_now_add=False)

    def __str__(self):
        return self.call1+" "+self.callstrike+" "+self.symbol
class LiveOITotal(models.Model):
    time = models.DateTimeField(auto_now_add=False)
    call1 = models.CharField(max_length=20,default="")
    call2 = models.CharField(max_length=20,default="")
    put1 = models.CharField(max_length=20,default="")
    put2 = models.CharField(max_length=20,default="")
    callstrike = models.CharField(max_length=20)
    putstrike = models.CharField(max_length=20)
    symbol = models.CharField(max_length=20)
    expiry = models.DateField(auto_now_add=False)
    strikegap = models.CharField(max_length=20,default="")

    def __str__(self):
        return self.call1+" "+self.callstrike+" "+self.symbol

class LiveOIPercentChange(models.Model):
    time = models.DateTimeField(auto_now_add=False)
    call1 = models.CharField(max_length=20,default="")
    call2 = models.CharField(max_length=20,default="")
    put1 = models.CharField(max_length=20,default="")
    put2 = models.CharField(max_length=20,default="")
    callstrike = models.CharField(max_length=20)
    putstrike = models.CharField(max_length=20)
    symbol = models.CharField(max_length=20)
    expiry = models.DateField(auto_now_add=False)
    strikegap = models.CharField(max_length=20,default="")

    def __str__(self):
        return self.call1+" "+self.callstrike+" "+self.symbol


class LiveOITotalAllSymbol(models.Model):
    time = models.DateTimeField(auto_now_add=False)
    call1 = models.CharField(max_length=20,default="")
    call2 = models.CharField(max_length=20,default="")
    put1 = models.CharField(max_length=20,default="")
    put2 = models.CharField(max_length=20,default="")
    callstrike = models.CharField(max_length=20)
    putstrike = models.CharField(max_length=20)
    symbol = models.CharField(max_length=20)
    expiry = models.DateField(auto_now_add=False)
    callone = models.CharField(max_length=20,default="") 
    putone = models.CharField(max_length=20,default="")
    callhalf = models.CharField(max_length=20,default="")
    puthalf = models.CharField(max_length=20,default="")

    def __str__(self):
        return self.call1+" "+self.callstrike+" "+self.symbol


class LiveEquityResult(models.Model):
    time = models.TimeField(auto_now_add=False)
    date = models.DateField()
    symbol = models.CharField(max_length=20,default="")
    open = models.CharField(max_length=20,default="")
    high = models.CharField(max_length=20,default="")
    low = models.CharField(max_length=20,default="")
    prev_day_close = models.CharField(max_length=20,default="")
    ltp = models.CharField(max_length=20)
    strike = models.CharField(max_length=20)
    opencrossed = models.CharField(max_length=20,default="")

    def __str__(self):
        return self.symbol+" "+self.ltp+" "+self.strike