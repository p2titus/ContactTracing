from django.contrib.gis.gdal import DataSource
from django.contrib.gis.utils import LayerMapping
from django.core.management.base import BaseCommand
from openpyxl import load_workbook
from ContactTracing.settings import POPULATION_XLSX_FILE, AREA_FILES_AND_CODES

from government.models import Area



class CustomLayerMapping(LayerMapping):
    def __init__(self, *args, **kwargs):
        self.custom = kwargs.pop('custom', {})
        super(CustomLayerMapping, self).__init__(*args, **kwargs)

    def feature_kwargs(self, feature):
        kwargs = super(CustomLayerMapping, self).feature_kwargs(feature)
        kwargs.update(self.custom)
        return kwargs


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--shps', action='store_true')
        parser.add_argument("--pops", action="store_true")

    def handle(self, *args, **options):

        if options["shps"]:
            # ignores all options/args
            for (t, file, name_field) in AREA_FILES_AND_CODES:

                ds = DataSource(file)
                layer = ds[0]
                mapping = {
                    "poly": "POLYGON",
                    "name": name_field,

                }
                types = {
                    "country": Area.COUNTRY,
                    "region": Area.REGION,
                    "county": Area.COUNTY,
                    "la": Area.LA
                }
                lm = CustomLayerMapping(model=Area, data=ds, mapping=mapping, custom={"type":  types[t]})
                lm.save(verbose=False, strict=True)

        elif options["pops"]:
            wb = load_workbook(filename=POPULATION_XLSX_FILE)
            sheet = wb["MYE2 - Persons"]
            data = sheet["B6": "D431"]

            for n, _, p in data:
                name = n.value
                pop = p.value
                poss = Area.objects.filter(name__iexact=name.strip())
                if len(poss) > 0:
                    for area in poss:
                        area.population = int(pop)
                        area.save()
                    print(name, pop)
                else:
                    print("Not found", name, pop, poss)

        else:
            print("Please provide a valid argument.")
