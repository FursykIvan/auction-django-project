from django.contrib import admin
from .models import Category, Auction, User, Comment, Bid


admin.site.register(User)
admin.site.register(Category)
admin.site.register(Auction)
admin.site.register(Bid)
admin.site.register(Comment)
