from django.views.generic import TemplateView
from django.shortcuts import render
from django.utils.timezone import now
from auction.models import Auction, Watchlist
from itertools import chain
from django.contrib.auth import get_user_model

User = get_user_model()


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        auctions = Auction.objects.filter(end_time__gte=now()).order_by('start_time')
        context['auctions'] = auctions

        if self.request.user.is_authenticated:
            user = self.request.user
            watchlist_items = Watchlist.objects.filter(user_id=user)
            watchlist = Auction.objects.none()
            for item in watchlist_items:
                auctions_for_watchlist = Auction.objects.filter(id=item.auction_id.id)
                watchlist = list(chain(watchlist, auctions_for_watchlist))

            context['watchlist'] = watchlist
            context['balance'] = user.balance
        return context
