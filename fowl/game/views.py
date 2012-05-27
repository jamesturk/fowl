from django.shortcuts import render
from fowl.game.models import TeamPoints

def events(request):
    points = TeamPoints.objects.filter().order_by('match',
                                                  'team').select_related()
    totals = TeamPoints.objects.values('match__event',
                                   'team__name').annotate(points=Sum('points'))
    return render(request, "events.html", {'points': points})

def stables(request):
    return render(request, "stables.html")
