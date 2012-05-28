from collections import defaultdict
from django.db import models
from django.contrib.auth.models import User

# these things are independent of the game

OUTCOMES = (
             ('no contest', 'no contest'),
             ('normal', 'normal'),
             ('DQ', 'DQ'),
             ('submission', 'submission'),
             ('appearance', 'appearance'),
             ('brawl', 'brawl'),
            )

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
    title = models.CharField(max_length=20, choices=TITLES, null=True)
    active = models.BooleanField()

    def win_title(self, title, tag_partner=None):
        Star.objects.filter(title=title).update(title=None)
        self.title = title
        self.save()
        if tag_partner:
            if title != 'tag':
                raise ValueError("can't have tag partner w/ non-tag belt")
            tag_partner.title = title
            tag_partner.save()

    def __unicode__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()

    def add_match(self, *teams, **kwargs):
        winner = kwargs.get('winner', None)
        outcome = kwargs.get('outcome', '')
        title_at_stake = kwargs.get('title_at_stake', False)
        notes = kwargs.get('notes', '')

        match = Match.objects.create(event=self,
                                     title_at_stake=title_at_stake,
                                     notes=notes
                                    )
        for team in teams:
            mt = MatchTeam.objects.create(match=match)
            if not isinstance(team, (list, tuple)):
                team = [team]
            for member in team:
                try:
                    member = Star.objects.get(pk=member)
                except Star.DoesNotExist:
                    raise ValueError('invalid star pk {0}'.format(member))
                if not mt.title and member.title:
                    # multiple titles?
                    mt.title = member.title
                    mt.save()
                mt.members.add(member)
        if winner:
            match.record_win(winner, outcome)
        else:
            match.outcome = outcome
            match.save()
        return match

    def __unicode__(self):
        return '{0} {1}'.format(self.name, self.date)


class Match(models.Model):
    event = models.ForeignKey(Event, related_name='matches')
    winner = models.ForeignKey(Star, null=True)
    outcome = models.CharField(max_length=10, choices=OUTCOMES)
    title_at_stake = models.BooleanField(default=False)
    notes = models.TextField(blank=True, default='')

    def record_win(self, star, outcome):
        team = self.teams.get(members__pk=star)
        team.victorious = True
        team.save()
        self.winner_id = star
        self.outcome = outcome
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
                if self.outcome == 'appearance' and not star.active:
                    points[star.id] += 10
                if self.outcome == 'brawl':
                    points[star.id] += 2
            if team.title:
                title_teams[team.title] = team
            if team.victorious:
                winners = team
            else:
                losers.append(team.members.count())
            team_count += 1

        # don't worry about winners of appearances or brawls
        if self.outcome in ('appearance', 'brawl'):
            return points

        if winners:
            winner_count = winners.members.count()
            loser_count = sum(losers)

            # figure out base points for winning
            # DQ wins are worth 1 point no matter what
            if self.outcome == 'DQ':
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
                if w.id == self.winner_id and self.outcome == 'submission':
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
                        if self.title_at_stake and self.outcome != 'DQ':
                            if title in ('heavyweight', 'wwe'):
                                points[w.id] += 20
                            else:
                                points[w.id] += 10
                        # title team gets a point if they defend title by DQ
                        elif self.title_at_stake and self.outcome == 'DQ':
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
        ret = ' vs. '.join(str(t) for t in
                           self.teams.all().prefetch_related('members'))
        if not self.winner_id:
            ret += ' (no contest)'
        return ret

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


# fantasy stuff

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


class Team(models.Model):
    name = models.CharField(max_length=100)
    login = models.OneToOneField(User, related_name='team')
    league = models.ForeignKey(League, related_name='teams')
    stars = models.ManyToManyField(Star, related_name='teams')

    def add_star(self, pk):
        star = Star.objects.get(pk=pk)
        if self.league.teams.filter(stars=star).count() >= 1:
            raise ValueError('cannot add {0}, already drafted in {1}'.format(
                             star, self.league))
        self.stars.add(star)

    def drop_star(self, pk):
        member = Star.objects.get(pk=pk)
        self.stars.remove(member)

    def __unicode__(self):
        return self.name


class TeamPoints(models.Model):
    points = models.IntegerField()
    team = models.ForeignKey(Team, related_name='points')
    star = models.ForeignKey(Star)
    match = models.ForeignKey(Match)

    def __unicode__(self):
        return "{0} received {1} points for {2}'s performance in {3}".format(
                self.team, self.points, self.star, self.match)
