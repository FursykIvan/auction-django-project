from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField("Auction", null=True, blank=True, related_name="watchlist")


class Auction(models.Model):
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    start_bid = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.URLField(blank=True)
    active = models.BooleanField()

    def __str__(self):
        return (f"{self.id} : {self.title} in {self.category.title}\n"
                f"Posted at : {self.date}\n"
                f"Value : {self.start_bid}\n"
                f"Description : {self.description}\n"
                f"Posted By : {self.user.username} Active Status: {self.active}")

class Category(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.id}: {self.title}"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    bid_value = models.DecimalField(max_digits=10, decimal_places=2)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id} : {self.user.username} bid {self.bid_value} on {self.auction.title} at {self.date}"



class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    comment_value = models.CharField(max_length=100)

    def __str__(self):
        return (f"{self.id} : {self.user.username} "
                f"commented on {self.auction.title} posted by {self.auction.user.username} "
                f"at {self.date} : {self.comment_value}")
