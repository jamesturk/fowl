from collections import defaultdict
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

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

class Star(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=200)
    photo_url = models.URLField()
    division = models.CharField(max_length=100)
    title = models.CharField(max_length=20, choices=TITLES)
    active = models.BooleanField()

    def drafted(self, league):
        return self.teams.filter(league=league).count() >= 1

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

    def score_event(self, event):
        ppv_bonus = 1 if event.name.lower() not in ('raw', 'smackdown') else 0
        TeamPoints.objects.filter(match__event=event).delete()
        for match in event.matches.all():
            for star, points in match.points().iteritems():
                try:
                    team = self.teams.get(stars=star)
                    TeamPoints.objects.create(points=points + ppv_bonus,
                                              team=team,
                                              star_id=star,
                                              match=match)
                except Team.DoesNotExist:
                    pass

    def __unicode__(self):
        return self.name

admin.site.register(League)


class Team(models.Model):
    name = models.CharField(max_length=100)
    login = models.OneToOneField(User, related_name='team')
    league = models.ForeignKey(League, related_name='teams')
    stars = models.ManyToManyField(Star, related_name='teams')

    def add_star(self, **kwargs):
        member = Star.objects.get(**kwargs)
        if member.drafted(self.league):
            raise ValueError('cannot add {0}, already drafted in {1}'.format(
                             member, self.league))
        self.stars.add(member)

    def __unicode__(self):
        return self.name

class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'league')
    list_filter = ('league',)

admin.site.register(Team, TeamAdmin)

class Event(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()

    def add_match(self, *teams, **kwargs):
        winner = kwargs.get('winner', None)
        win_type = kwargs.get('win_type', None)
        title_at_stake = kwargs.get('title_at_stake', False)

        match = Match.objects.create(event=self, title_at_stake=title_at_stake)
        for team in teams:
            if isinstance(team, (list, tuple)):
                match.add_team(*team)
            else:
                match.add_team(team)
        if winner:
            match.record_win(winner, win_type)
        return match

    def __unicode__(self):
        return '{0} {1}'.format(self.name, self.date)

admin.site.register(Event)

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
            if not mt.title and member.title:
                mt.title = member.title
                mt.save()
            mt.members.add(member)

    def record_win(self, star, win_type):
        self.teams.filter(members__pk=star).update(victorious=True)
        self.winner_id = star
        self.win_type = win_type
        self.save()

    def points(self):
        points = {}
        winners = None
        losers = []
        title_teams = {}
        team_count = 0
        for team in self.teams.all():
            for star in team.members.all():
                points[star.id] = 0
            if team.title:
                title_teams[team.title] = team
            if team.victorious:
                winners = team
            else:
                losers.append(team.members.count())
            team_count += 1

        if winners:
            winner_count = winners.members.count()
            loser_count = sum(losers)

            # figure out base points for winning
            # DQ wins are worth 1 point no matter what
            if self.win_type == 'DQ':
                base_points = 1
                allies = 0   # allies don't matter in a DQ
            # rumble is worth participants/2
            elif team_count > 6:
                base_points = team_count / 2
                allies = 0   # no allies in a rumble
            else:
                # normal wins are worth 2
                allies = winner_count - 1
                base_points = max((loser_count - allies) * 2, 1)

            # award points to winners
            for w in winners.members.all():
                points[w.id] = base_points

                # if multiple people in this match and this person was credited
                # w/ win, give them the bonus points
                if allies and w.id == self.winner_id:
                    points[w.id] += 1
                if w.id == self.winner_id and self.win_type == 'submission':
                    points[w.id] += 1

                # look over all titles in this match
                for title, title_team in title_teams.iteritems():
                    # title defense
                    if winners.title == title and self.title_at_stake:
                        if title in ('heavyweight', 'wwe'):
                            points[w.id] += 5
                        else:
                            points[w.id] += 3
                    # beat someone w/ title
                    elif winners.title != title:
                        # title win
                        if self.title_at_stake and self.win_type != 'DQ':
                            if title in ('heavyweight', 'wwe'):
                                points[w.id] += 20
                            else:
                                points[w.id] += 10
                        # title team gets a point if they defend title by DQ
                        elif self.title_at_stake and self.win_type == 'DQ':
                            for star in title_team.members.all():
                                points[star.id] += 1
                        # beat tag champs in tag match w/o tag belt on line
                        elif title == 'tag' and all(c == 2 for c in losers):
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

class TeamPoints(models.Model):
    points = models.IntegerField()
    team = models.ForeignKey(Team, related_name='points')
    star = models.ForeignKey(Star)
    match = models.ForeignKey(Match)

    def __unicode__(self):
        return "{0} recieved {1} points for {2}'s performance in {3}".format(
                self.team, self.points, self.star, self.match)