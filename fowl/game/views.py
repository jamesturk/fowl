from itertools import izip_longest
from django.shortcuts import render, get_object_or_404
from fowl.game.models import Team, TeamPoints, Star, Event, League


def events(request, league_id):
    league = get_object_or_404(League, pk = league_id)
    leagues = League.objects.all()
    events = {}
    points = TeamPoints.objects.filter(team__league_id=league_id).order_by(
        'match', 'team').select_related()
    for tp in points:
        event_id = tp.match.event_id
        if event_id not in events:
            events[event_id] = tp.match.event
            events[event_id].scores = {}
            events[event_id].match_list = {}
        events[event_id].match_list.setdefault(tp.match, []
                                               ).append(tp)
        events[event_id].scores.setdefault(tp.team, 0)
        events[event_id].scores[tp.team] += tp.points
    events = sorted(events.values(), key=lambda x: x.date, reverse=True)
    return render(request, "events.html", {'events': events, 'view': 'events', 'league': league, 'leagues':leagues})


def edit_event(request, event_id=None):
    if event_id:
        event = get_object_or_404(Event, pk=event_id)
    else:
        event = None
    if request.method == 'GET':
        return render(request, "edit_event.html", {"event": event})


def league(request, league_id):
    league = get_object_or_404(League, pk = league_id)
    leagues = League.objects.all()
    context = {
        'view': 'league',
        'belts': ['ic', 'us', 'heavyweight', 'wwe'],
        'league': league,
        'leagues': leagues
    }
    teams = list(Team.objects.filter(league__id=league_id)
                 .prefetch_related('stars'))
    context['teams'] = teams
    context['star_sets'] = izip_longest(*(team.stars.all().order_by("division")
                                          for team in teams))
    return render(request, "stables.html", context)


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
