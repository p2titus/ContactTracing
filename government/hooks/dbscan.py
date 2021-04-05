from django.db.models import Min, Max

from shared.models import Contact
from government.models import Cluster
from django.contrib.gis.measure import D
from django.db import connection

import uuid

# TODO: find suitable values
EPS = 500  # metres
MIN_PTS = 4
# Clearly not a UUID, so a cluster can never be generated with a UUID of this.
NOISE = "Noise"


def __get_neighbours(point, excl=[]):
    return Contact.objects.filter(location__point__distance_lte=(point, D(m=EPS))).exclude(id__in=excl)


def __find_cluster(contact, ignore_seen=True):
    contact.refresh_from_db()
    # https://en.wikipedia.org/wiki/DBSCAN#Algorithm
    if contact.cluster is not None and ignore_seen:
        return []
    neighbours = set(__get_neighbours(contact.location.point))
    if len(neighbours) < MIN_PTS:
        contact.cluster = NOISE
        contact.save()
        return []

    contact.cluster = uuid.uuid4()
    changed_clusters = [str(contact.cluster)]

    contact.save()
    seen_ids = [contact.id]
    while len(neighbours) > 0:
        neighbour = neighbours.pop()
        if neighbour.id in seen_ids:
            continue
        seen_ids.append(neighbour.id)
        if neighbour.cluster not in [None, NOISE]:
            changed_clusters.append(neighbour.cluster)

        neighbour.cluster = contact.cluster
        neighbour.save()
        new_neighbours = __get_neighbours(neighbour.location.point)
        if new_neighbours.count() >= MIN_PTS:
            neighbours = neighbours.union(new_neighbours)

    return changed_clusters


def __update_stored_cluster(cluster_id):
    points = Contact.objects.filter(cluster=cluster_id)
    point_count = points.count()
    if point_count == 0:
        c = Cluster.objects.filter(cluster_id=cluster_id)
        if len(c) == 0:
            # I suppose do nothing
            return
        c.delete()
        return

    geos_point_type = connection.ops.select % "area"
    # Kinda naughty cause I'm doing string interpolation, but the cluster IDs are only ever generated by my code.
    new_cluster_data = Cluster.objects.raw("""SELECT sq.cluster_id, sq.area::bytea as area, sq.cluster_size
FROM (select sc.cluster                                                          as cluster_id,
             st_convexhull(st_collect(st_buffer(sa.point, %s, quadsegs := 2))) as area,
             COUNT(sc.id)                                                        as cluster_size
      FROM shared_contact as sc
               join shared_addresses sa on sa.id = sc.location_id
      where sc.cluster = '%s'
      group by sc.cluster) sq
    
        """ % (EPS, cluster_id))
    if len(new_cluster_data) != 1:
        print("Major error, length was actually", len(new_cluster_data))

    dates = points.aggregate(start_date=Min("positive_case__test_date"), end_date=Max("positive_case__test_date"))
    print(dates["start_date"],dates["end_date"])
    Cluster.objects.update_or_create(cluster_id=cluster_id,
                                     defaults={"area": new_cluster_data[0].area,
                                               "cluster_size": new_cluster_data[0].cluster_size,
                                               "indices": list(points.values_list("id", flat=True)),
                                               "start_date": dates["start_date"],
                                               "end_date": dates["end_date"]})


def cluster(contact):
    changed = __find_cluster(contact, True)
    for cluster_id in set(changed):
        # print("updating", cluster_id)
        __update_stored_cluster(cluster_id)


def alternate_find_cluster(contact):
    # https://www.aaai.org/Papers/KDD/1996/KDD96-037.pdf
    if contact.cluster is not None:
        print("Oh no!!!!")
        return
    neighbours = set(__get_neighbours(contact.location.point, []))
    if len(neighbours) < MIN_PTS:
        contact.cluster = NOISE
    else:
        print(len(neighbours))
        neighbours.remove(contact)
        contact.cluster = uuid.uuid4()
        contact.save()
        while len(neighbours) > 0:
            # print("in loop", len(neighbours))
            neighbour = neighbours.pop()
            new_neighbours = __get_neighbours(neighbour.location.point, [])
            if new_neighbours.count() >= MIN_PTS:
                for new_neighbour in new_neighbours:
                    if new_neighbour.cluster in [None, NOISE]:
                        if new_neighbour.cluster is None:
                            # print("Including in neighbours to consider")
                            neighbours.add(new_neighbour)
                        # print("Adding to current cluster")
                        new_neighbour.cluster = contact.cluster
                        new_neighbour.save()
            # neighbours.remove(neighbour)
