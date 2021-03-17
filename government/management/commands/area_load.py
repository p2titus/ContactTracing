from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.utils import LayerMapping
from government.models import Area

to_load = [("./government/areas/1countries/Countries_(December_2019)_Boundaries_UK_BUC.shp", Area.COUNTRY, "ctry19nm"),
           ("./government/areas/2regions/Regions_(December_2019)_Boundaries_EN_BUC.shp", Area.REGION, "rgn19nm"),
           ("./government/areas/3counties/Counties_and_Unitary_Authorities_(December_2019)_Boundaries_UK_BUC.shp", Area.COUNTY, "ctyua19nm"),
           ("./government/areas/4local_authority_districts/Local_Authority_Districts_(December_2020)_UK_BUC.shp", Area.LA, "LAD20NM")]
class CustomLayerMapping(LayerMapping):
    def __init__(self, *args, **kwargs):
        self.custom = kwargs.pop('custom', {})
        super(CustomLayerMapping, self).__init__(*args, **kwargs)

    def feature_kwargs(self, feature):
        kwargs = super(CustomLayerMapping, self).feature_kwargs(feature)
        kwargs.update(self.custom)
        return kwargs

class Command(BaseCommand):
    def handle(self, *args, **options):
        # ignores all options/args
        for (file, t, name_field ) in to_load:
            self.stdout.write(" %s, %s, %s" % (file, t, name_field))
            ds = DataSource(file)
            layer = ds[0]
            mapping = {
                "poly": "POLYGON",
                "name": name_field,

            }
            lm = CustomLayerMapping(model=Area,data= ds,mapping= mapping, custom= {"type": t})
            lm.save(verbose=False, strict=True)