import geopy.distance


def calculate_distance(user, lat_2, long_2):
    coords_1 = (user.profile.long, user.profile.lat)
    coords_2 = (long_2, lat_2)
    result = int(geopy.distance.geodesic(coords_1, coords_2).km)
    return result
