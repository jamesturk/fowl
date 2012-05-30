from itertools import izip_longest
from collections import defaultdict
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from fowl.game.models import (Team, TeamPoints, Star, Event, League,
                              OUTCOMES, TITLES)


@login_required
def events(request, league_id):
    league = get_object_or_404(League, pk = league_id)
    leagues = League.objects.filter(teams__login=request.user)
    events = {}
    points = TeamPoints.objects.filter(team__league_id=league_id).order_by(
        'match__id', 'team').select_related()
    for tp in points:
        event_id = tp.match.event_id
        if event_id not in events:
            events[event_id] = tp.match.event
            events[event_id].scores = {}
            events[event_id].match_list = {}
        events[event_id].match_list.setdefault(tp.match, []).append(tp)
        events[event_id].scores.setdefault(tp.team, 0)
        events[event_id].scores[tp.team] += tp.points
    events = sorted(events.values(), key=lambda x: x.date, reverse=True)
    return render(request, "events.html",
                  {'events': events, 'view': 'events', 'league': league,
                   'leagues':leagues})


@login_required
def edit_event(request, event):
    if event == 'new':
        event = None
    else:
        event = get_object_or_404(Event, pk=event).to_dict()

    if request.method == 'POST':
        edict = {}
        edict['id'] = request.POST.get('id')
        edict['name'] = request.POST.get('name')
        edict['date'] = request.POST.get('date')
        edict['matches'] = []

        outcomes = request.POST.getlist('outcome')
        winners = request.POST.getlist('winner')
        titles = request.POST.getlist('title')
        notes = request.POST.getlist('notes')
        for i, note in enumerate(notes):
            edict['matches'].append({'outcome': outcomes[i],
                                     'winner': winners[i],
                                     'title_at_stake': titles[i],
                                     'notes': notes[i],
                                     'teams': [],
                                    })

        for k, team in request.POST.iterlists():
            if k.startswith('members'):
                _, match, _ = k.split('-')
                # remove empty strings from team
                team = [m for m in team if m]
                if team:
                    edict['matches'][int(match)-1]['teams'].append(team)

        event = Event.from_dict(edict)
        # score the event for all active leagues
        for league in League.objects.filter(active=True):
            league.score_event(event)
        # after event is scored, do title change on all matches
        for match in event.matches.all():
            match.do_title_change()
        # TODO: title changes should take place inline somehow?
        # (would fix for case if title changes twice)
        event = event.to_dict()

    return render(request, "edit_event.html",
                  {'event': event,
                   'OUTCOMES': OUTCOMES,
                   'TITLES': TITLES}
                 )


@login_required
def league(request, league_id):
    league = get_object_or_404(League, pk = league_id)
    leagues = League.objects.filter(teams__login=request.user)
    teams = {team.name: team for team in
             Team.objects.filter(league__id=league_id)}

    # grab the show totals for all shows
    show_totals = TeamPoints.objects.all().values(
        'match__event__id', 'match__event__name', 'team__name').annotate(
            Sum('points'))
    belts = {'us': {'name': None, 'points': 0, 'date': None,
                    'teams': {team: 0 for team in teams}},
             'ic': {'name': None, 'points': 0, 'date': None,
                    'teams': {team: 0 for team in teams}},
             'heavyweight': {'name': None, 'points': 0, 'date': None,
                             'teams': {team: 0 for team in teams}},
             'wwe': {'name': None, 'points': 0, 'date': None,
                     'teams': {team: 0 for team in teams}},
            }
    belt_mapping = {'smackdown': 'ic', 'raw': 'us'}

    # go over all events in order to determine belt holders
    for event in Event.objects.all().order_by('date'):
        # determine which belt is being competed for
        belt_name = belt_mapping.get(event.name.lower(), 'heavyweight')
        # get team scores for this event
        team_points = TeamPoints.objects.filter(match__event=event
                       ).values('team__name').annotate(points=Sum('points'))
        # figure out who won event, also tally wwe belt points
        max_points = 0
        event_winner = []
        for tp in team_points:
            if tp['points'] > max_points:
                max_points = tp['points']
                event_winner = [tp['team__name']]
            elif tp['points'] == max_points:
                event_winner.append(tp['team__name'])
            belts['wwe']['teams'][tp['team__name']] += tp['points']

        # add a point to all event winners
        for ew in event_winner:
            belts[belt_name]['teams'][ew] += 1
        # loop again after adding points to check for new holder
        for ew in event_winner:
            if belts[belt_name]['teams'][ew] > belts[belt_name]['points']:
                belts[belt_name]['points'] = belts[belt_name]['teams'][ew]
                if belts[belt_name]['name'] != ew:
                    belts[belt_name]['name'] = ew
                    belts[belt_name]['date'] = event.date
        # do WWE belt check on PPVs
        if belt_name == 'heavyweight':
            belt_name = 'wwe'
            if belts[belt_name]['teams'][ew] > belts[belt_name]['points']:
                belts[belt_name]['points'] = belts[belt_name]['teams'][ew]
                if belts[belt_name]['name'] != ew:
                    belts[belt_name]['name'] = ew
                    belts[belt_name]['date'] = event.date

    context = {
        'view': 'league',
        'belts': belts,
        'league': league,
        'leagues': leagues
    }
    context['teams'] = teams.values()
    context['star_sets'] = izip_longest(*(team.stars.all().order_by("division")
                                          for team in teams.itervalues()))
    return render(request, "league.html", context)


def roster(request, league_id):
    league = get_object_or_404(League, pk = league_id)
    leagues = League.objects.filter(teams__login=request.user)
    context = {
        'stars': Star.objects.all(),
        'view': 'roster',
        'league': league,
        'leagues': leagues
    }
    return render(request, "roster.html", context)
