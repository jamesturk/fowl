from collections import defaultdict
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
TITLES = (('wwe', 'WWE'),
          ('heavyweight', 'Heavyweight'),
          ('ic', 'Intercontinental'),
          ('us', 'United States'),
          ('tag', 'Tag Team'),
          ('diva', 'Divas'),
         )
class Match(models.Model):
    event = models.ForeignKey(Event, related_name='matches')
    winner = models.ForeignKey(Star, null=True)
    win_type = models.CharField(max_length=10, choices=WIN_TYPES)
    title_at_stake = models.BooleanField(default=False)

    def add_team(self, *members, **kwargs):
        title = kwargs.get('title', None)
        mt = MatchTeam.objects.create(match=self, title=title)
        for member in members:
            member = Star.objects.get(pk=member)
            mt.members.add(member)

    def record_win(self, star, win_type):
        self.teams.filter(members__pk=star).update(victorious=True)
        self.win_type = win_type
        self.winner__pk = star
        self.save()


    def points(self):
        points = defaultdict(int)
        winners = self.teams.filter(victorious=True)

        if winners:
            winners = winners[0]
            winner_count = winners.members.count()
            losers = [x.mcount for x in self.teams.all().annotate(mcount=models.Count('members'))]
            loser_count = sum(losers)

            # figure out base points for winning
            # DQ wins are worth 1 point no matter what
            if self.win_type == 'DQ':
                base_points = 1
                allies = 0   # allies don't matter in a DQ
            # rumble is worth participants/2
            elif self.teams.count() > 6:
                base_points = self.teams.count() / 2
                allies = 0   # no allies in a rumble
            else:
                # normal wins are worth 2
                allies = winner_count - 1
                opponents = self.teams.filter(victorious=False).aggregate(
                                  opponents=models.Count('members'))['opponents']
                base_points = max((opponents - allies) * 2, 1)

            # award points to winners
            for w in winners.members.all():
                points[w.id] = base_points

                # if multiple people in this match and this person was credited
                # w/ win, give them the bonus points
                if allies and w.id == self.winner__pk:
                    points[w.id] += 1
                if w.id == self.winner__pk and self.win_type == 'submission':
                    points[w.id] += 1

                # look over all titles in this match
                for t in self.teams.values_list('title', flat=True):
                    # skip titles we hold or people without titles
                    if t is None:
                        continue
                    # title defense
                    elif winners.title == t and self.title_at_stake:
                        if t in ('heavyweight', 'wwe'):
                            points[w.id] += 5
                        else:
                            points[w.id] += 3
                    # beat someone w/ title
                    elif winners.title != t:
                        # title win
                        if self.title_at_stake and self.win_type != 'DQ':
                            if t in ('heavyweight', 'wwe'):
                                points[w.id] += 20
                            else:
                                points[w.id] += 10
                        elif self.title_at_stake and self.win_type == 'DQ':
                            for star in self.teams.get(title=t).members.all():
                                points[star.id] += 1
                        # beat tag champs in tag match w/o tag belt on line
                        elif t == 'tag' and all(c == 2 for c in losers):
                            points[w.id] += 2
                        # beat champ in non-handicap match w/o belt on line
                        elif all(c == 1 for c in losers):
                            points[w.id] += 2
        return points

    def __unicode__(self):
        return ' vs. '.join(str(t) for t in self.teams.all())

admin.site.register(Match)

class MatchTeam(models.Model):
    members = models.ManyToManyField(Star)
    match = models.ForeignKey(Match, related_name='teams')
    victorious = models.BooleanField(default=False)
    title = models.CharField(max_length=50, choices=TITLES, null=True)

    def __unicode__(self):
        ret = ' & '.join([str(m) for m in self.members.all()])
        if self.title:
            ret += ' (c)'
        if self.victorious:
            ret += ' (v)'
        return ret