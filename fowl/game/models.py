from django.db import models
from django.contrib.auth.models import User

Q = models.Q

# these things are independent of the game

OUTCOMES = (('no contest', 'no contest'),
            ('normal', 'pinfall/normal'),
            ('dq', 'disqualification'),
            ('submission', 'submission'),
            ('appearance', 'appearance'),
            ('brawl', 'brawl'),
           )

TITLES = (('wwe', 'WWE'),
          ('world', 'World Heavyweight'),
          ('ic', 'Intercontinental'),
          ('us', 'United States'),
          ('tag', 'Tag Team'),
          ('divas', 'Divas'),
         )
TITLE_DICT = dict(TITLES)


class Star(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=200)
    photo_url = models.URLField()
    division = models.CharField(max_length=100)

    @property
    def active(self):
        return self.division != 'other'

    def win_title(self, title, date, tag_partner=None):
        # if they have title on that date (or won it then), don't add anything
        if (self.has_title(date) or
            self.reigns.filter(title=title, begin_date=date).count()):
            return

        # end current title reigns
        TitleReign.objects.filter(title=title).update(end_date=date)
        self.reigns.create(title=title, begin_date=date)
        if tag_partner:
            if title != 'tag':
                raise ValueError("can't have tag partner w/ non-tag belt")
            tag_partner.reigns.create(title=title, begin_date=date)

    def has_title(self, date=None):
        if date:
            current_title = list(self.reigns.filter(
                Q(begin_date__lt=date) & (Q(end_date__gte=date) |
                                          Q(end_date__isnull=True))))
        else:
            current_title = list(self.reigns.filter(end_date__isnull=True))
        if len(current_title) < 1:
            return None
        elif len(current_title) == 1:
            return current_title[0].title
        else:
            return 'multiple' # FIXME

    def titled_name(self, date):
        title = self.has_title(date)
        name = self.name
        if title:
            name = '{0} ({1} Champion)'.format(name, TITLE_DICT[title])
        return name

    def __unicode__(self):
        return self.name

class TitleReign(models.Model):
    star = models.ForeignKey(Star, related_name='reigns')
    title = models.CharField(max_length=20, choices=TITLES)
    begin_date = models.DateField()
    end_date = models.DateField(null=True)

    def __unicode__(self):
        return '{0} champion from {1}-{2}'.format(self.get_title_display(),
                                                  self.begin_date,
                                                  self.end_date or '')

class Event(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()

    def to_dict(self):
        d = {'id': self.id, 'name': self.name, 'date': self.date,
             'matches': [m.to_dict() for m in self.matches.all()]
            }
        return d

    @staticmethod
    def from_dict(d):
        if d.get('id'):
            event = Event.objects.get(pk=d['id'])
            event.name = d['name']
            event.date = d['date']
            event.matches.all().delete()
        else:
            event = Event.objects.create(name=d['name'], date=d['date'])
        for match in d['matches']:
            event.add_match(*match['teams'],
                            winner=match['winner'],
                            outcome=match['outcome'],
                            title_at_stake=match['title_at_stake'],
                            notes=match['notes'])
        return event


    def add_match(self, *teams, **kwargs):
        winner = kwargs.get('winner', None)
        outcome = kwargs.get('outcome', 'no contest')
        title_at_stake = kwargs.get('title_at_stake', None)
        notes = kwargs.get('notes', '')

        match = Match.objects.create(event=self,
                                     title_at_stake=title_at_stake,
                                     notes=notes)
        for team in teams:
            mt = MatchTeam.objects.create(match=match)
            if not isinstance(team, (list, tuple)):
                team = [team]
            for member in team:
                try:
                    member = Star.objects.get(pk=member)
                except Star.DoesNotExist:
                    raise ValueError('invalid star pk {0}'.format(member))
                if not mt.title and member.has_title(self.date):
                    # multiple titles?
                    mt.title = member.has_title(self.date)
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
    outcome = models.CharField(max_length=10, choices=OUTCOMES,
                               default='no contest')
    title_at_stake = models.CharField(max_length=50, choices=TITLES, null=True)
    notes = models.TextField(blank=True, default='')

    def to_dict(self):
        d = {'winner': self.winner_id,
             'outcome': self.outcome,
             'title_at_stake': self.title_at_stake,
             'notes': self.notes}
        d['teams'] = [[m.id for m in team.members.all()]
                      for team in self.teams.all()]
        return d

    def record_win(self, star, outcome):
        team = self.teams.get(members__pk=star)
        team.victorious = True
        team.save()
        self.winner_id = star
        self.outcome = outcome
        self.save()

    def do_title_change(self):
        if self.title_at_stake:
            victors = list(self.teams.get(victorious=True).members.all())
            if len(victors) == 1:
                victors[0].win_title(self.title_at_stake, self.event.date)
            elif len(victors) == 2 and self.title_at_stake == 'tag':
                victors[0].win_title(self.title_at_stake, self.event.date,
                                     victors[1])
            else:
                raise ValueError('invalid number of victors for title change')

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
            if self.outcome == 'dq':
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

                if self.title_at_stake:
                    if winners.title == self.title_at_stake:
                        # title defense
                        if winners.title in ('world', 'wwe'):
                            points[w.id] += 5
                        else:
                            points[w.id] += 3
                    elif self.outcome in ('normal', 'submission'):
                        # title win!
                        if self.title_at_stake in ('world', 'wwe'):
                            points[w.id] += 20
                        else:
                            points[w.id] += 10
                    else:
                        # defense by DQ
                        for star in title_teams[self.title_at_stake
                                               ].members.all():
                            points[star.id] += 1
                else:
                    # look over titles in match, to score a title-nondefense
                    for title, title_team in title_teams.iteritems():
                        # beat someone w/ title in a non-defense
                        if winners.title != title:
                            # beat tag champs in tag match w/o tag belt on line
                            if title == 'tag' and all(c == 2 for c in losers):
                                points[w.id] += 2
                            # beat champ in non-handicap match w/o belt on line
                            elif title != 'tag' and all(c == 1 for c in losers):
                                points[w.id] += 2

            # if multiple people in this match and this person was credited
            # w/ win, give them the bonus points
            if allies:
                points[self.winner_id] += 1
            if self.outcome == 'submission':
                points[self.winner_id] += 1
        return points

    def fancy(self):
        teams = [t.fancy(self.event.date) for t in
                 self.teams.all().order_by('-victorious')
                 .prefetch_related('members')]
        if self.outcome in ('normal', 'dq', 'submission'):
            ret = '{0} defeats {1}'.format(teams[0], ', '.join(teams[1:]))
            ret += {'normal': '', 'dq': ' via disqualification',
                    'submission': ' via submission'}[self.outcome]
        elif self.outcome == 'appearance':
            ret = 'appearance by {0}'.format(', '.join(teams))
        elif self.outcome == 'brawl':
            ret = 'brawl between {0}'.format(', '.join(teams))
        elif self.outcome == 'no contest':
            ret = '{0} - fight to a no contest'.format(' vs. '.join(teams))
        else:
            print self.outcome
        return ret


class MatchTeam(models.Model):
    members = models.ManyToManyField(Star)
    match = models.ForeignKey(Match, related_name='teams')
    victorious = models.BooleanField(default=False)
    title = models.CharField(max_length=50, choices=TITLES, null=True)

    def fancy(self, date):
        return ' & '.join([m.titled_name(date) for m in self.members.all()])


# fantasy stuff

class League(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
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
    color = models.CharField(max_length=50)
    login = models.ForeignKey(User, related_name='teams')
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
