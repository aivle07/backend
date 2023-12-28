from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Buy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    commodity = models.CharField('Commodity', max_length=100)
    count = models.IntegerField('Count')
    market_value = models.IntegerField('Market_value')
    create_dt = models.DateTimeField('CREATE DT', auto_now_add=True)
    is_sell = models.BooleanField("Is_sell", default=False)
    
class SellHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    buy = models.ForeignKey(Buy, on_delete=models.CASCADE)
    sell_time_market_value = models.IntegerField('Sell_time_market_value')
    create_dt = models.DateTimeField('CREATE DT', auto_now_add=True)