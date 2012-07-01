from django.core.management.base import NoArgsCommand
import scrapelib
import lxml.html

from ...models import Star


class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        url = 'http://www.wwe.com/superstars'
        data = scrapelib.urlopen(url)
        doc = lxml.html.fromstring(data)
        doc.make_links_absolute(url)

        for div in doc.xpath('//div[starts-with(@class, "star ")]'):
            cssclass = div.get('class')
            if 'letter-champion' in cssclass:
                continue
            # get division
            divisions = ('divas', 'raw', 'smackdown')
            for division in divisions:
                if division in cssclass:
                    break
            else:
                division = 'other'
            name = div.xpath('h2')[0].text_content().strip()
            url = div.xpath('a/@href')[0]
            id = url.rsplit('/', 1)[-1]
            photo_url = 'http://wwe.com' + div.xpath('a/img/@data-fullsrc')[0]

            if Star.objects.filter(id=id).count():
                star = Star.objects.get(id=id)
                if star.name != name:
                    print('updating {0} name to {1}'.format(star.name, name))
                    star.name = name
                if star.division != division:
                    print('updating {0} division to {1}'.format(star.name, division))
                    star.division = division
                if star.photo_url != photo_url:
                    print('updating {0} photo to {1}'.format(star.name.encode('utf8'), photo_url))
                    star.photo_url = photo_url
                star.save()
            else:
                print('adding {0}'.format(name))
                Star.objects.create(id=id, name=name, division=division,
                                    photo_url=photo_url)
