from django.db import models
from django.utils import timezone

from accounts.models import User, UserDetails


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

    def remaining_time(self):
        """
        Calculates the remaining time until the auction ends and checks if the auction has already ended.

        Returns:
        tuple:
            - formatted time (HH:MM:SS) indicating the remaining time
            - total seconds representing how much time is left (negative value if auction has ended)
        """
        if self.end_time < timezone.now():
            return "00:00:00", -1

        time_left = self.end_time - timezone.now()
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        formatted_time = f"{hours:02}:{minutes:02}:{seconds:02}"

        return formatted_time, time_left.total_seconds()

    def increase_bid(self, user):
        """
        Increases the bid for the selected auction by creating a new Bid object.
        """
        user_details = UserDetails.objects.filter(user_id=user.id).first()
        if user_details.balance > 0.0:
            current_bid_amount = 0.20 + (self.number_of_bids * 0.20)
            current_bid_amount = round(current_bid_amount, 2)

            new_bid = Bid(
                auction_id=self,
                user_id=user,
                bid_time=timezone.now()
            )
            new_bid.save()

            self.number_of_bids += 1
            self.save()

            return new_bid
        else:
            return None

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
