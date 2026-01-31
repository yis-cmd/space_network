from space_network_lib import *

class NothingCloseEnoughError(Exception):
    pass

def merge_sort(space_entities: list[SpaceEntity])->list[SpaceEntity]:
    if len(space_entities) < 2:
        return space_entities
    half = len(space_entities) // 2
    lower = merge_sort(space_entities[ : half])
    higher = merge_sort(space_entities[half : ])
    sorted_list = []
    lower_p = higher_p = 0
    while len(lower) > lower_p and len(higher) > higher_p:
        if lower[lower_p].distance_from_earth <= higher[higher_p].distance_from_earth:
            sorted_list.append(lower[lower_p])
            lower_p += 1
        else:
            sorted_list.append(higher[higher_p])
            higher_p += 1
    if len(lower) > lower_p:
        sorted_list.extend(lower[lower_p:])
    else:
        sorted_list.extend(higher[higher_p:])
    return sorted_list

def search_farthest_valid(space_entities:list[SpaceEntity], location:int)->SpaceEntity | None:
    upper_range = location + 150
    lower_range = location
    left = 0
    best = None
    right = len(space_entities)-1
    while right >= left:
        middle = (left + right) // 2
        dist = space_entities[middle].distance_from_earth
        if dist > upper_range:
            right = middle - 1
        elif dist <= lower_range:
            left = middle + 1
        else:
            best = space_entities[middle]
            left = middle + 1
    return best

def build_route(space_entities:list[SpaceEntity], start_point:SpaceEntity, end_point:SpaceEntity)->list[SpaceEntity]:
    space_entities = merge_sort(space_entities)
    route = [start_point]
    while route[-1].distance_from_earth + 150 < end_point.distance_from_earth:
        next_entity = search_farthest_valid(space_entities, route[-1].distance_from_earth)
        if next_entity:
            route.append(next_entity)
        else:
            raise NothingCloseEnoughError
    best_route_str = " ".join([ent.name for ent in route])
    print(f"best route found and is {best_route_str}")
    return route