from django.db import models

from accounts.models import User


class Goods(models.Model):
    category = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="images/")
    description = models.TextField()
    quantity = models.IntegerField(default=0)
    date_posted = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return f"Id: {self.pk} {self.title}"


class Auction(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    goods_id = models.ForeignKey(Goods, on_delete=models.CASCADE)
    number_of_bids = models.IntegerField(default=0)

    def __str__(self):
        return f"Id: {self.pk} Goods Id:{self.goods_id}"


class Bid(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    auction_id = models.ForeignKey(Auction, on_delete=models.CASCADE)
    bid_time = models.DateTimeField()

    def __str__(self):
        return f"User_id: {self.user_id} Auction_id: {self.auction_id} Bid: {self.bid_time}"


class WatchList(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    auction_id = models.ForeignKey(Auction, on_delete=models.CASCADE)

    def __str__(self):
        return f"User_id: {self.user_id} Auction_id: {self.auction_id}"
