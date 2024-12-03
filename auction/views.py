from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.utils.timezone import now
from django.utils import timezone

from accounts.models import UserDetails
from auction.forms import TopUpForm, CommentForm
from auction.models import Auction, WatchList, Bid
from django.contrib.auth import get_user_model
from django.views import generic

User = get_user_model()


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        auctions = Auction.objects.filter(end_time__gte=now()).order_by("start_time")
        context["auctions"] = auctions

        if self.request.user.is_authenticated:
            user = self.request.user
            watchlist_items = WatchList.objects.filter(user=user)
            watchlist_ids = [item.auction_id.id for item in watchlist_items]
            watchlist = Auction.objects.filter(id__in=watchlist_ids)

            context["watchlist"] = watchlist
            context["balance"] = user.balance

        return context


class BidPageView(generic.View):
    """
    Returns the bid page for the selected auction.
    """

    def get(self, request, auction_id):
        """
        Handles GET requests to display the bidding page for a specific auction.
        """
        try:
            if "username" in request.session:
                auction = Auction.objects.get(id=auction_id)

                if auction.start_time > timezone.now():
                    return redirect("index")

                user = User.objects.get(username=request.session["username"])
                stats = []

                time_left, expired = auction.remaining_time()
                stats.append(time_left)

                current_cost = 0.20 + (auction.number_of_bids * 0.20)
                current_cost = "%0.2f" % current_cost
                stats.append(current_cost)

                stats.append(False if expired < 0 else True)

                latest_bid = Bid.objects.all().order_by("-bid_time").first()
                if latest_bid:
                    winner = User.objects.get(id=latest_bid.user.id)
                    stats.append(winner.username)
                else:
                    stats.append(None)

                watchlist_items = WatchList.objects.filter(user=user)
                watchlist_ids = [item.auction_id.id for item in watchlist_items]
                watchlist = Auction.objects.filter(id__in=watchlist_ids)

                return render(request, "bid.html", {
                    'auction': auction,
                    'user': user,
                    'stats': stats,
                    'watchlist': watchlist
                })

        except (KeyError, Auction.DoesNotExist):
            return redirect("index")

        return redirect("index")


class RaiseBidView(generic.View):
    """
    Increases the bid of the selected auction and returns to the bidding page.
    """

    def get(self, request, auction_id):
        """
        Handles the GET request to increase the bid for the auction.
        """
        try:
            auction = Auction.objects.get(id=auction_id)
            if auction.end_time < timezone.now():
                return self.redirect_to_bid_page(auction_id)
            elif auction.start_time > timezone.now():
                return redirect("index")

            if "username" in request.session:
                user = User.objects.get(username=request.session["username"])
                user_details = UserDetails.objects.filter(user_id=user.id).first()

                if user_details and user_details.balance > 0.0:
                    latest_bid = Bid.objects.filter(auction_id=auction.id).order_by("-bid_time").first()
                    if not latest_bid or latest_bid.user_id != user:
                        auction.increase_bid(user)

                return self.redirect_to_bid_page(auction_id)
            else:
                return redirect("index")

        except Auction.DoesNotExist:
            return redirect("index")

    def redirect_to_bid_page(self, auction_id):
        """
        Helper method to redirect to the bidding page.
        """
        return redirect("bid_page", auction_id=auction_id)



class CommentView(generic.FormView):
    """
    A view to handle commenting on an auction.
    """

    form_class = CommentForm
    template_name = "bid.html"
    success_url = "/"

    def form_valid(self, form):
        """
        Handle the form when it's valid.
        """
        auction_id = self.kwargs["auction_id"]

        try:
            user = self.request.user
            auction = Auction.objects.get(id=auction_id)

            auction.comment = form.cleaned_data["comment"]
            auction.save()

            return redirect("bid_page", auction_id=auction.id)

        except Auction.DoesNotExist:
            return redirect("index")

    def form_invalid(self, form):
        """
        Handle the form if it's invalid (you can render the form with errors here).
        """
        return redirect("bid_page", auction_id=self.kwargs["auction_id"])

class WatchlistCreateView(generic.CreateView):
    model = WatchList
    fields = []
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        username = self.request.session.get("username")
        user = get_object_or_404(User, username=username)
        auction_id = self.kwargs.get("auction_id")
        auction = get_object_or_404(Auction, id=auction_id)

        form.instance.user_id = user
        form.instance.auction_id = auction
        return super().form_valid(form)

class WatchlistDeleteView(generic.DeleteView):
    model = WatchList
    success_url = reverse_lazy("index")

    def get_object(self, queryset=None):
        username = self.request.session.get("username")
        user = get_object_or_404(User, username=username)
        auction_id = self.kwargs.get("auction_id")
        return get_object_or_404(WatchList, user_id=user, auction_id=auction_id)

class WatchlistPageView(LoginRequiredMixin, generic.ListView):
    """
    Displays a list of auctions that the user has added to the watchlist.
    """
    model = Auction
    template_name = "index.html"
    context_object_name = "auctions"

    def get_queryset(self):
        username = self.request.session.get("username")
        user = get_object_or_404(User, username=username)

        watchlist_items = WatchList.objects.filter(user_id=user)


        return Auction.objects.filter(
            id__in=watchlist_items.values_list("auction_id", flat=True),
            time_ending__gte=timezone.now()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = get_object_or_404(User, username=self.request.session.get("username"))
        context["watchlist"] = context["auctions"]
        return context

class BalanceView(LoginRequiredMixin, generic.DetailView):
    """
    Displays the user's balance page.
    """
    model = User
    template_name = "balance.html"
    context_object_name = "user"

    def get_object(self, queryset=None):
        username = self.request.session.get("username")
        return get_object_or_404(User, username=username)

class TopUpView(LoginRequiredMixin, generic.FormView):
    """
    Handles the top-up functionality for the user's balance.
    """
    template_name = "topup.html"
    form_class = TopUpForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        username = self.request.session.get("username")
        user = get_object_or_404(User, username=username)
        user_details = get_object_or_404(UserDetails, user_id=user.id)
        user_details.balance += form.cleaned_data["amount"]
        user_details.save()

        return super().form_valid(form)
