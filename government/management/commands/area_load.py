from django.contrib.gis.gdal import DataSource
from django.contrib.gis.utils import LayerMapping
from django.core.management.base import BaseCommand
from openpyxl import load_workbook

from government.models import Area

to_load = [("./government/areas/1countries/Countries_(December_2019)_Boundaries_UK_BUC.shp", Area.COUNTRY, "ctry19nm"),
           ("./government/areas/2regions/Regions_(December_2019)_Boundaries_EN_BUC.shp", Area.REGION, "rgn19nm"),
           ("./government/areas/3counties/Counties_and_Unitary_Authorities_(December_2019)_Boundaries_UK_BUC.shp",
            Area.COUNTY, "ctyua19nm"),
           ("./government/areas/4local_authority_districts/Local_Authority_Districts_(December_2020)_UK_BUC.shp",
            Area.LA, "LAD20NM")]


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
            for (file, t, name_field) in to_load:
                self.stdout.write(" %s, %s, %s" % (file, t, name_field))
                ds = DataSource(file)
                layer = ds[0]
                mapping = {
                    "poly": "POLYGON",
                    "name": name_field,

                }
                lm = CustomLayerMapping(model=Area, data=ds, mapping=mapping, custom={"type": t})
                lm.save(verbose=False, strict=True)

        elif options["pops"]:
            wb = load_workbook(
                filename='/home/max/code/ContactTracing/government/ukmidyearestimates20192020ladcodes.xlsx')
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
