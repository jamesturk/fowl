from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

class Star(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=200)
    photo_url = models.URLField()
    division = models.CharField(max_length=100)
    active = models.BooleanField()

    def __unicode__(self):
        return self.name


class StarAdmin(admin.ModelAdmin):
    list_display = ('name', 'division', 'active')
    list_filter = ('division', 'active')
admin.site.register(Star, StarAdmin)


class League(models.Model):
    name = models.CharField(max_length=100)
    raw_picks = models.IntegerField(default=3)
    smackdown_picks = models.IntegerField(default=3)
    diva_picks = models.IntegerField(default=2)
    wildcard_picks = models.IntegerField(default=1)
    oldtimer_picks = models.IntegerField(default=2)

    def __unicode__(self):
        return self.name

admin.site.register(League)


class Team(models.Model):
    name = models.CharField(max_length=100)
    login = models.OneToOneField(User, related_name='team')
    league = models.ForeignKey(League, related_name='teams')
    stars = models.ManyToManyField(Star, related_name='teams')

    def __unicode__(self):
        return self.name

class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'league')
    list_filter = ('league',)

admin.site.register(Team, TeamAdmin)

class Event(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()

    def __unicode__(self):
        return '{0} {1}'.format(self.name, self.date)

admin.site.register(Event)

WIN_TYPES = (('pin', 'pin'),
             ('DQ', 'DQ'),
             ('submission', 'submission'))
class Match(models.Model):
    event = models.ForeignKey(Event, related_name='matches')
    win_type = models.CharField(max_length=10, choices=WIN_TYPES)

    def add_team(self, *members):
        mt = MatchTeam.objects.create(match=self)
        for member in members:
            member = Star.objects.get(pk=member)
            mt.members.add(member)

    def record_win(self, star, win_type):
        self.teams.filter(members__pk=star).update(victorious=True)
        self.win_type = win_type
        self.save()

    def points(self):
        winners = self.teams.filter(victorious=True)
        points = {}
        if winners:
            winners = winners[0]
            allies = winners.members.count() - 1
            opponents = self.teams.filter(victorious=False).aggregate(
                              opponents=models.Count('members'))['opponents']
            for w in winners.members.all():
                points[w.id] = max((opponents - allies)*2, 1)
        return points




    def __unicode__(self):
        return ' vs. '.join(str(t) for t in self.teams.all())

admin.site.register(Match)

class MatchTeam(models.Model):
    members = models.ManyToManyField(Star)
    match = models.ForeignKey(Match, related_name='teams')
    victorious = models.BooleanField(default=False)

    def __unicode__(self):
        ret = ' & '.join([str(m) for m in self.members.all()])
        if self.victorious:
            ret += ' (v)'
        return ret