import csv  # https://docs.python.org/3/library/csv.html

# https://django-extensions.readthedocs.io/en/latest/runscript.html

# python3 manage.py runscript many_load

from unesco.models import Category, State, Iso, Region, Site

def get_value(value, type_cast = None):
    try:
        return type_cast(value) if type_cast != None else value
    except:
        return None

def run():
    fhand = open('unesco/whc-sites-2018-clean.csv')
    reader = csv.reader(fhand)
    next(reader)  # Advance past the header

    Category.objects.all().delete()
    State.objects.all().delete()
    Iso.objects.all().delete()
    Region.objects.all().delete()
    Site.objects.all().delete()


    # Format
    # email,role,course
    # jane@tsugi.org,I,Python
    # ed@tsugi.org,L,Python

    for row in reader:
        cate, _ = Category.objects.get_or_create(name=row[7])
        state, _ = State.objects.get_or_create(name=row[8])
        iso, _ = Iso.objects.get_or_create(name=row[10])
        region, _ = Region.objects.get_or_create(name=row[9])

        name = get_value(row[0][:300])
        description = get_value(row[1])
        justification = get_value(row[2])
        year = get_value(row[3], int)
        longitude = get_value(row[4], float)
        latitude = get_value(row[5], float)
        area_hectares = get_value(row[6], float)

        # site, _ = Site.objects.get_or_create()
        site = Site(name = name,
                    description=description,
                    justification=justification,
                    year =year,
                    longitude=longitude,
                    latitude=latitude,
                    area_hectares=area_hectares,
                    category=cate,
                    state=state,
                    region=region,
                    iso=iso)

        site.save()
