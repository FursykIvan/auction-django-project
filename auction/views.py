from django.urls import reverse
from django.db.models import Max
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render
from django.views import generic
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.contrib.auth import authenticate, login, logout

from auction.models import Auction, User, Category, Bid, Comment


class IndexView(generic.ListView):
    model = Auction
    template_name = "auctions/index.html"
    context_object_name = "objects"

    def get_queryset(self):
        return Auction.objects.filter(active=True)


class AllListingsView(generic.ListView):
    model = Auction
    template_name = "auctions/index.html"
    context_object_name = "objects"

    def get_queryset(self):
        return Auction.objects.all()

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def createlisting(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        title = request.POST["title"]
        description = request.POST["description"]
        start_bid = request.POST["startBid"]
        category = Category.objects.get(id=request.POST["category"])
        user = request.user
        image = request.POST["url"]
        if image == "":
            image = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/300px-No_image_available.svg.png"
        listing = Auction.objects.create(
            name=title, category=category, date=timezone.now(), startBid=start_bid, description=description, user=user, imageUrl=image, active=True)
        listing.save()
        return HttpResponseRedirect(reverse("index"))
    return render(request, "auctions/createlisting.html", {
        "categories": Category.objects.all()
    })

def details(request: HttpRequest, pk: int) -> HttpResponse:
    item = Auction.objects.get(pk=pk)
    bids = Bid.objects.filter(auctionListing=item)
    comments = Comment.objects.filter(auctionListing=item)
    value = bids.aggregate(Max("bid_value"))["bid_value__max"]
    bid = None
    if value is not None:
        bid = Bid.objects.filter(bidValue=value)[0]
    return render(request, "auctions/details.html", {
        "item": item,
        "bids": bids,
        "comments": comments,
        "bid": bid
    })


def categories(request):
    if request.method == 'POST':
        category = request.POST["category"]
        new_category, created = Category.objects.get_or_create(
            name=category.lower())
        if created:
            new_category.save()
        else:
            messages.warning(request, "Category already Exists!")
        return HttpResponseRedirect(reverse("categories"))
    return render(request, "auctions/categories.html", {
        'categories': Category.objects.all()
    })


def filter_by_category(request: HttpRequest, name: str) -> HttpResponse:
    category = Category.objects.get(name=name)
    obj = Auction.objects.filter(category=category)
    return render(request, "auctions/index.html", {
        "objects": obj
    })

@login_required
def comment(request, pk: int) -> HttpResponse:
    if request.method == 'POST':
        auction = Auction.objects.get(pk=pk)
        user = request.user
        comment_value = request.POST["content"].strip()
        if comment_value != "":
            new_comment = Comment.objects.create(date=timezone.now(
            ), user=user, auction=auction, comment_value=comment_value)
            new_comment.save()
        return HttpResponseRedirect(reverse("details", kwargs={'pk': pk}))
    return HttpResponseRedirect(reverse("index"))


@login_required
def place_bid(request, pk: int) -> HttpResponse:
    if request.method == 'POST':
        auction = Auction.objects.get(pk=pk)
        bid_value = request.POST["bid"]
        args = Bid.objects.filter(auctionListing=auction)
        value = args.aggregate(Max("bidValue"))["bidValue__max"]
        if value is None:
            value = 0
        if float(bid_value) < auction.start_bid or float(bid_value) <= value:
            messages.warning(
                request, f"Bid Higher than: {max(value, auction.start_bid)}!")
            return HttpResponseRedirect(reverse("details", kwargs={'pk': pk}))
        user = request.user
        bid = Bid.objects.create(
            date=timezone.now(), user=user, bidValue=bid_value, auctionListing=auction)
        bid.save()
    return HttpResponseRedirect(reverse("details", kwargs={'pk': pk}))


@login_required
def auction_ending(request, item_id: int) -> HttpResponse:
    auction = Auction.objects.get(id=item_id)
    user = request.user
    if auction.user == user:
        auction.active = False
        auction.save()
        messages.success(
            request, f"Auction for {auction.title} successfully closed!")
    else:
        messages.info(
            request, "You are not authorized to end this listing!")
    return HttpResponseRedirect(reverse("details", kwargs={'id': item_id}))


@login_required
def watchlist(request):
    if request.method == 'POST':
        user = request.user
        auction = Auction.objects.get(id=request.POST["item"])
        if request.POST["status"] == '1':
            user.watchlist.add(auction)
        else:
            user.watchlist.remove(auction)
        user.save()
        return HttpResponseRedirect(
            reverse("details", kwargs={'id': auction.id}))
    return HttpResponseRedirect(reverse("index"))


@login_required
def watch(request):
    user = request.user
    obj = user.watchlist.all()
    return render(request, "auctions/index.html", {
        "objects": obj
    })
