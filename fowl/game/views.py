from itertools import izip_longest
from collections import defaultdict
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from fowl.game.models import (Team, TeamPoints, Star, Event, League,
                              OUTCOMES, TITLES)


@login_required
def events(request, league_id):
    league = get_object_or_404(League, pk = league_id)
    leagues = League.objects.all()
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
    leagues = League.objects.all()
    context = {
        'view': 'league',
        'belts': ['ic', 'us', 'heavyweight', 'wwe'],
        'league': league,
        'leagues': leagues
    }
    teams = list(Team.objects.filter(league__id=league_id))
    context['teams'] = teams
    context['star_sets'] = izip_longest(*(team.stars.all().order_by("division")
                                          for team in teams))
    return render(request, "league.html", context)


def roster(request, league_id):
    league = get_object_or_404(League, pk = league_id)
    leagues = League.objects.all()
    context = {
        'stars': Star.objects.all(),
        'view': 'roster',
        'league': league,
        'leagues': leagues
    }
    return render(request, "roster.html", context)
