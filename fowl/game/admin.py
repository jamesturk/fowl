from django.contrib import admin

from .models import Star, Match, Event, League, Team


class StarAdmin(admin.ModelAdmin):
    list_display = ('name', 'division')
    list_filter = ('division',)

admin.site.register(Star, StarAdmin)
admin.site.register(Match)
admin.site.register(Event)


class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'league')
    list_filter = ('league',)

admin.site.register(League)
admin.site.register(Team, TeamAdmin)
