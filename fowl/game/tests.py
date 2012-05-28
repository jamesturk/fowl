from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import User
from .models import Match, Event, League, Team, TeamPoints, Star

def _give_belt(star, belt):
    Star.objects.get(pk=star).win_title(belt)

class StarTest(TestCase):
    def test_win_title(self):
        cmpunk = Star.objects.create(pk='cmpunk', name='CM Punk', title='wwe')
        dbry = Star.objects.create(pk='danielbryan', name='Daniel Bryan')
        kofi = Star.objects.create(pk='kofi', name='Kofi Kingston',
                                   title='tag')
        rtruth = Star.objects.create(pk='rtruth', name='R Truth', title='tag')
        swagger = Star.objects.create(pk='swagger', name='Jack Swagger')
        ziggler = Star.objects.create(pk='ziggler', name='Dolph Ziggler')

        # belt win takes it away from original holder
        self.assertEqual(Star.objects.get(pk='cmpunk').title, 'wwe')
        dbry.win_title('wwe')
        self.assertEqual(Star.objects.get(pk='cmpunk').title, None)
        self.assertEqual(Star.objects.get(pk='danielbryan').title, 'wwe')

        # tag belt win
        self.assertEqual(Star.objects.get(pk='kofi').title, 'tag')
        self.assertEqual(Star.objects.get(pk='rtruth').title, 'tag')
        ziggler.win_title('tag', tag_partner=swagger)
        self.assertEqual(Star.objects.get(pk='kofi').title, None)
        self.assertEqual(Star.objects.get(pk='rtruth').title, None)
        self.assertEqual(Star.objects.get(pk='ziggler').title, 'tag')
        self.assertEqual(Star.objects.get(pk='swagger').title, 'tag')


class MatchTest(TestCase):
    fixtures = ['testdata']

    def setUp(self):
        self.event = Event.objects.create(name='Wrestlemania 29', date='2012-04-01')

    def test_basics(self):
        match = self.event.add_match('tripleh', 'undertaker')
        self.assertEqual(unicode(match),
                         'Triple H vs. Undertaker (no contest)')
        match.record_win('undertaker', 'pin')
        self.assertEqual(unicode(match), 'Triple H vs. Undertaker (v)')

        _give_belt('cmpunk', 'wwe')
        match = self.event.add_match('cmpunk', 'reymysterio', winner='cmpunk',
                                     win_type='pin')
        self.assertEqual(unicode(match), 'CM Punk (c) (v) vs. Rey Mysterio')


    def test_scoring(self):
        # one on one : 2 points
        match = self.event.add_match('tripleh', 'undertaker',
                                     winner='undertaker', win_type='pin')
        self.assertEqual(match.points(), {'undertaker': 2, 'tripleh': 0})

        # fatal 4 way: 6 points
        match = self.event.add_match('randyorton', 'sheamus', 'albertodelrio',
                                     'chrisjericho', winner='sheamus',
                                     win_type='pin')
        self.assertEqual(match.points(), {'sheamus': 6, 'randyorton': 0,
                                          'albertodelrio': 0, 'chrisjericho': 0}
                        )

        # win stacked match: 1 point for team (bonuses can apply)
        match = self.event.add_match('santinomarella', ['markhenry', 'kane'],
                                     winner='markhenry', win_type='pin')
        self.assertEqual(match.points(), {'markhenry': 2, 'kane': 1,
                                          'santinomarella': 0})

        # DQ : 1 point
        match = self.event.add_match('kane', 'undertaker', winner='undertaker',
                                     win_type='DQ')
        self.assertEqual(match.points(), {'undertaker': 1, 'kane': 0})

        # submission: +1
        match = self.event.add_match('danielbryan', 'cmpunk',
                                     winner='danielbryan',
                                     win_type='submission')
        self.assertEqual(match.points(), {'danielbryan': 3, 'cmpunk': 0})

        # complicated one, outnumbered + submission
        match = self.event.add_match('cmpunk', ['danielbryan', 'chrisjericho'],
                                     winner='cmpunk', win_type='submission')
        self.assertEqual(match.points(), {'cmpunk': 5, 'chrisjericho': 0,
                                          'danielbryan': 0})

        # tag team: 2 points, +1 for the person who made pin
        match = self.event.add_match(['kofikingston', 'rtruth'],
                                     ['jackswagger', 'dolphziggler'],
                                     winner='dolphziggler', win_type='pin')
        self.assertEqual(match.points(), {'jackswagger': 2,
                                          'dolphziggler': 3,
                                          'kofikingston': 0,
                                          'rtruth': 0})

        # tag team submission: stacks on ziggler
        match = self.event.add_match(['kofikingston', 'rtruth'],
                                     ['jackswagger', 'dolphziggler'],
                                     winner='dolphziggler',
                                     win_type='submission')
        self.assertEqual(match.points(), {'jackswagger': 2,
                                          'dolphziggler': 4,
                                          'kofikingston': 0,
                                          'rtruth': 0})

        # tag team DQ: 1 point each member
        match = self.event.add_match(['kofikingston', 'rtruth'],
                                     ['jackswagger', 'dolphziggler'],
                                     winner='dolphziggler',
                                     win_type='DQ')
        self.assertEqual(match.points(), {'jackswagger': 1,
                                          'dolphziggler': 1,
                                          'kofikingston': 0,
                                          'rtruth': 0})

        # rumble: participants / 2
        match = self.event.add_match('kofikingston', 'rtruth', 'themiz',
                                     'dolphziggler', 'johncena', 'jackswagger',
                                     'kharma', 'kane', 'albertodelrio',
                                     'christian', winner='christian',
                                     win_type='pin')
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
        _give_belt('cmpunk', 'wwe')
        _give_belt('christian', 'ic')
        _give_belt('kofikingston', 'tag')
        _give_belt('rtruth', 'tag')

        # champ doesn't get a bonus just for winning
        match = self.event.add_match('cmpunk', 'reymysterio', winner='cmpunk',
                                     win_type='pin')
        self.assertEqual(match.points(), {'cmpunk': 2, 'reymysterio': 0})

        # +2 bonus for beating a champ in a non-title match
        match = self.event.add_match('cmpunk', 'reymysterio',
                                     winner='reymysterio', win_type='pin')
        self.assertEqual(match.points(), {'cmpunk': 0, 'reymysterio': 4})

        # defending wwe belt is worth +5
        match = self.event.add_match('cmpunk', 'reymysterio', winner='cmpunk',
                                     win_type='pin', title_at_stake=True)
        self.assertEqual(match.points(), {'cmpunk': 7, 'reymysterio': 0})

        # winning wwe belt
        match = self.event.add_match('cmpunk', 'reymysterio',
                                     winner='reymysterio', win_type='pin',
                                     title_at_stake=True)
        self.assertEqual(match.points(), {'reymysterio': 22, 'cmpunk': 0})

        # defending other belt is worth +3
        match = self.event.add_match('christian', 'codyrhodes',
                                     winner='christian', win_type='pin',
                                     title_at_stake=True)
        self.assertEqual(match.points(), {'christian': 5, 'codyrhodes': 0})

        # winning other belt is worth +10
        match = self.event.add_match('christian', 'codyrhodes',
                                     winner='codyrhodes', win_type='pin',
                                     title_at_stake=True)
        self.assertEqual(match.points(), {'codyrhodes': 12, 'christian': 0})

        # title non-defense (DQ/countout)
        match = self.event.add_match('christian', 'codyrhodes',
                                     winner='codyrhodes', win_type='DQ',
                                     title_at_stake=True)
        self.assertEqual(match.points(), {'codyrhodes': 1, 'christian': 1})

        # no bonus in a tag match
        match = self.event.add_match(['cmpunk', 'christian'],
                                     ['reymysterio', 'codyrhodes'],
                                     winner='reymysterio', win_type='pin')
        self.assertEqual(match.points(), {'codyrhodes': 2, 'reymysterio': 3,
                                          'cmpunk': 0, 'christian': 0})

        # ...unless it is the tag title
        match = self.event.add_match(['kofikingston', 'rtruth'],
                                     ['reymysterio', 'sin-cara'],
                                     winner='reymysterio', win_type='pin')
        self.assertEqual(match.points(), {'sin-cara': 4, 'reymysterio': 5,
                                          'kofikingston': 0, 'rtruth': 0})

        # test tag title changing hands
        match = self.event.add_match(['kofikingston', 'rtruth'],
                                     ['reymysterio', 'sin-cara'],
                                     winner='reymysterio', win_type='pin',
                                     title_at_stake=True)
        self.assertEqual(match.points(), {'sin-cara': 12, 'reymysterio': 13,
                                          'kofikingston': 0, 'rtruth': 0})


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
        match1 = event.add_match('reymysterio', 'sin-cara', winner='sin-cara',
                                 win_type='pin')
        match2 = event.add_match('markhenry', ['santinomarella', 'mickfoley'],
                                 winner='mickfoley', win_type='pin')
        _give_belt('codyrhodes', 'ic')
        match3 = event.add_match('sin-cara', 'codyrhodes', title_at_stake=True,
                                 winner='sin-cara', win_type='pin')
        self.league.score_event(event)

        # check TeamPoints objects
        self.assertEqual(TeamPoints.objects.get(team=self.teddy, star__pk='reymysterio').points, 0)
        self.assertEqual(TeamPoints.objects.get(team=self.teddy, star__pk='santinomarella').points, 1)
        self.assertEqual(TeamPoints.objects.get(team=self.johnny, match=match1, star__pk='sin-cara').points, 2)
        self.assertEqual(TeamPoints.objects.get(team=self.johnny, match=match3, star__pk='sin-cara').points, 12)
        self.assertEqual(TeamPoints.objects.get(team=self.johnny, star__pk='markhenry').points, 0)

        # rename the event and rescore
        event.name = 'Wrestlemania'
        event.save()
        # give cody rhodes his belt back for this one
        _give_belt('codyrhodes', 'ic')

        self.league.score_event(event)
        # all should be one higher than before
        self.assertEqual(TeamPoints.objects.get(team=self.teddy, star__pk='reymysterio').points, 1)
        self.assertEqual(TeamPoints.objects.get(team=self.teddy, star__pk='santinomarella').points, 2)
        self.assertEqual(TeamPoints.objects.get(team=self.johnny, match=match1, star__pk='sin-cara').points, 3)
        self.assertEqual(TeamPoints.objects.get(team=self.johnny, match=match3, star__pk='sin-cara').points, 13)
        self.assertEqual(TeamPoints.objects.get(team=self.johnny, star__pk='markhenry').points, 1)
