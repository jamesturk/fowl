from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import User
from .models import Match, Event, League, Team, TeamPoints

class MatchTest(TestCase):
    fixtures = ['testdata']

    def setUp(self):
        self.wm29 = Event.objects.create(name='Wrestlemania 29', date='2012-04-01')

    def test_display(self):
        match = Match.objects.create(event=self.wm29)
        match.add_team('tripleh')
        match.add_team('undertaker')
        self.assertEqual(unicode(match), 'Triple H vs. Undertaker')
        match.record_win('undertaker', 'pin')
        self.assertEqual(unicode(match), 'Triple H vs. Undertaker (v)')

        match = Match.objects.create(event=self.wm29)
        match.add_team('cmpunk', title='wwe')
        match.add_team('reymysterio')
        self.assertEqual(unicode(match), 'CM Punk (c) vs. Rey Mysterio')
        match.record_win('cmpunk', 'pin')
        self.assertEqual(unicode(match), 'CM Punk (c) (v) vs. Rey Mysterio')


    def test_scoring(self):
        # one on one : 2 points
        match = Match.objects.create(event=self.wm29)
        match.add_team('tripleh')
        match.add_team('undertaker')
        match.record_win('undertaker', 'pin')
        self.assertEqual(match.points(), {'undertaker': 2, 'tripleh': 0})

        # fatal 4 way: 6 points
        match = Match.objects.create(event=self.wm29)
        match.add_team('randyorton')
        match.add_team('albertodelrio')
        match.add_team('sheamus')
        match.add_team('chrisjericho')
        match.record_win('sheamus', 'pin')
        self.assertEqual(match.points(), {'sheamus': 6, 'randyorton': 0,
                                          'albertodelrio': 0, 'chrisjericho': 0}
                                          )

        # win stacked match: 1 point for team (bonuses can apply)
        match = Match.objects.create(event=self.wm29)
        match.add_team('santinomarella')
        match.add_team('markhenry', 'kane')
        match.record_win('markhenry', 'pin')
        self.assertEqual(match.points(), {'markhenry': 2, 'kane': 1,
                                          'santinomarella': 0})

        # DQ : 1 point
        match = Match.objects.create(event=self.wm29)
        match.add_team('kane')
        match.add_team('undertaker')
        match.record_win('undertaker', 'DQ')
        self.assertEqual(match.points(), {'undertaker': 1, 'kane': 0})

        # submission: +1
        match = Match.objects.create(event=self.wm29)
        match.add_team('danielbryan')
        match.add_team('cmpunk')
        match.record_win('danielbryan', 'submission')
        self.assertEqual(match.points(), {'danielbryan': 3, 'cmpunk': 0})

        # complicated one, outnumbered + submission
        match = Match.objects.create(event=self.wm29)
        match.add_team('danielbryan', 'chrisjericho')
        match.add_team('cmpunk')
        match.record_win('cmpunk', 'submission')
        self.assertEqual(match.points(), {'cmpunk': 5, 'chrisjericho': 0,
                                          'danielbryan': 0})

        # tag team: 2 points, +1 for the person who made pin
        match = Match.objects.create(event=self.wm29)
        match.add_team('kofikingston', 'rtruth')
        match.add_team('jackswagger', 'dolphziggler')
        match.record_win('dolphziggler', 'pin')
        self.assertEqual(match.points(), {'jackswagger': 2,
                                          'dolphziggler': 3,
                                          'kofikingston': 0,
                                          'rtruth': 0})

        # tag team submission: stacks on ziggler
        match = Match.objects.create(event=self.wm29)
        match.add_team('kofikingston', 'rtruth')
        match.add_team('jackswagger', 'dolphziggler')
        match.record_win('dolphziggler', 'submission')
        self.assertEqual(match.points(), {'jackswagger': 2,
                                          'dolphziggler': 4,
                                          'kofikingston': 0,
                                          'rtruth': 0})

        # tag team DQ: 1 point each member
        match = Match.objects.create(event=self.wm29)
        match.add_team('kofikingston', 'rtruth')
        match.add_team('jackswagger', 'dolphziggler')
        match.record_win('dolphziggler', 'DQ')
        self.assertEqual(match.points(), {'jackswagger': 1,
                                          'dolphziggler': 1,
                                          'kofikingston': 0,
                                          'rtruth': 0})

        # rumble: participants / 2
        match = Match.objects.create(event=self.wm29)
        match.add_team('kofikingston')
        match.add_team('rtruth')
        match.add_team('themiz')
        match.add_team('dolphziggler')
        match.add_team('johncena')
        match.add_team('jackswagger')
        match.add_team('kharma')
        match.add_team('kane')
        match.add_team('albertodelrio')
        match.add_team('christian')
        match.record_win('christian', 'pin')
        self.assertEqual(match.points(), {'christian': 5,
                                          'kofikingston': 0,
                                          'rtruth': 0,
                                          'themiz': 0,
                                          'dolphziggler': 0,
                                          'johncena': 0,
                                          'jackswagger': 0,
                                          'kharma': 0,
                                          'kane': 0,
                                          'albertodelrio': 0
                         })

    def test_champ_scoring(self):
        # champ doesn't get a bonus just for winning
        match = Match.objects.create(event=self.wm29)
        match.add_team('cmpunk', title='wwe')
        match.add_team('reymysterio')
        match.record_win('cmpunk', 'pin')
        self.assertEqual(match.points(), {'cmpunk': 2, 'reymysterio': 0})

        # defending wwe belt is worth +5
        match = Match.objects.create(event=self.wm29, title_at_stake=True)
        match.add_team('cmpunk', title='wwe')
        match.add_team('reymysterio')
        match.record_win('cmpunk', 'pin')
        self.assertEqual(match.points(), {'cmpunk': 7, 'reymysterio': 0})

        # winning wwe belt
        match = Match.objects.create(event=self.wm29, title_at_stake=True)
        match.add_team('cmpunk', title='wwe')
        match.add_team('reymysterio')
        match.record_win('reymysterio', 'pin')
        self.assertEqual(match.points(), {'reymysterio': 22, 'cmpunk': 0})

        # defending other belt is worth +3
        match = Match.objects.create(event=self.wm29, title_at_stake=True)
        match.add_team('christian', title='ic')
        match.add_team('codyrhodes')
        match.record_win('christian', 'pin')
        self.assertEqual(match.points(), {'christian': 5, 'codyrhodes': 0})

        # winning other belt is worth +3
        match = Match.objects.create(event=self.wm29, title_at_stake=True)
        match.add_team('christian', title='ic')
        match.add_team('codyrhodes')
        match.record_win('codyrhodes', 'pin')
        self.assertEqual(match.points(), {'codyrhodes': 12, 'christian': 0})

        # title non-defense (DQ/countout)
        match = Match.objects.create(event=self.wm29, title_at_stake=True)
        match.add_team('christian', title='ic')
        match.add_team('codyrhodes')
        match.record_win('codyrhodes', 'DQ')
        self.assertEqual(match.points(), {'codyrhodes': 1, 'christian': 1})

        # +2 bonus for beating a champ in a non-title match
        match = Match.objects.create(event=self.wm29)
        match.add_team('cmpunk', title='wwe')
        match.add_team('reymysterio')
        match.record_win('reymysterio', 'pin')
        self.assertEqual(match.points(), {'reymysterio': 4, 'cmpunk': 0})

        # no bonus in a tag match
        match = Match.objects.create(event=self.wm29)
        match.add_team('cmpunk', 'christian', title='wwe')
        match.add_team('reymysterio', 'codyrhodes')
        match.record_win('reymysterio', 'pin')
        self.assertEqual(match.points(), {'codyrhodes': 2, 'reymysterio': 3,
                                          'cmpunk': 0, 'christian': 0})

        # ...unless it is the tag title
        match = Match.objects.create(event=self.wm29)
        match.add_team('cmpunk', 'christian', title='tag')
        match.add_team('reymysterio', 'codyrhodes')
        match.record_win('reymysterio', 'pin')
        self.assertEqual(match.points(), {'codyrhodes': 4, 'reymysterio': 5,
                                          'cmpunk': 0, 'christian': 0})



class LeagueTest(TestCase):
    fixtures = ['testdata']

    def setUp(self):
        self.user = User.objects.create_user('me', 'test@example.com',
                                              'password')
        self.user2 = User.objects.create_user('me2', 'test@example.com',
                                              'password')
        self.league = League.objects.create(name='FOWL')
        self.teddy = Team.objects.create(name='Team Teddy', login=self.user,
                                   league=self.league)
        self.johnny = Team.objects.create(name='Team Johnny', login=self.user2,
                                    league=self.league)

    def test_team_add_star(self):
        self.teddy.add_star(pk='reymysterio')
        self.johnny.add_star(pk='sin-cara')
        with self.assertRaises(ValueError):
            self.teddy.add_star(pk='reymysterio')
        with self.assertRaises(ValueError):
            self.johnny.add_star(pk='sin-cara')

    def test_score_event(self):
        self.teddy.add_star(pk='reymysterio')
        self.teddy.add_star(pk='santinomarella')
        self.johnny.add_star(pk='sin-cara')
        self.johnny.add_star(pk='markhenry')
        event = Event.objects.create(name='smackdown', date='2012-01-01')
        match1 = Match.objects.create(event=event)
        match1.add_team('reymysterio')
        match1.add_team('sin-cara')
        match1.record_win('sin-cara', 'pin')
        match2 = Match.objects.create(event=event)
        match2.add_team('santinomarella', 'mickfoley')
        match2.add_team('markhenry')
        match2.record_win('mickfoley', 'pin')
        match3 = Match.objects.create(event=event, title_at_stake=True)
        match3.add_team('codyrhodes', title='ic')
        match3.add_team('sin-cara')
        match3.record_win('sin-cara', 'pin')
        self.league.score_event(event)

        # check TeamPoints objects
        self.assertEqual(TeamPoints.objects.get(team=self.teddy, star__pk='reymysterio').points, 0)
        self.assertEqual(TeamPoints.objects.get(team=self.teddy, star__pk='santinomarella').points, 1)
        self.assertEqual(TeamPoints.objects.get(team=self.johnny, match=match1, star__pk='sin-cara').points, 2)
        self.assertEqual(TeamPoints.objects.get(team=self.johnny, match=match3, star__pk='sin-cara').points, 12)
        self.assertEqual(TeamPoints.objects.get(team=self.johnny, star__pk='markhenry').points, 0)
        for obj in TeamPoints.objects.all():
            print obj

        # rename the event and rescore
        event.name = 'Wrestlemania'
        event.save()
        self.league.score_event(event)
        # all should be one higher than before
        self.assertEqual(TeamPoints.objects.get(team=self.teddy, star__pk='reymysterio').points, 1)
        self.assertEqual(TeamPoints.objects.get(team=self.teddy, star__pk='santinomarella').points, 2)
        self.assertEqual(TeamPoints.objects.get(team=self.johnny, match=match1, star__pk='sin-cara').points, 3)
        self.assertEqual(TeamPoints.objects.get(team=self.johnny, match=match3, star__pk='sin-cara').points, 13)
        self.assertEqual(TeamPoints.objects.get(team=self.johnny, star__pk='markhenry').points, 1)
