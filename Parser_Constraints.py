# with open("01_linear_path.txt", 'r') as file:
#     try:
#         text = file.readline()
#         while not text.startswith("nb_drones: "): 
#             text = file.readline()
#             if not text:
#                 break 
#         print(text)
#         Parser_Constraints.
#     except IOError as e:
#         print(e)

class Get_lines():
    drones_number : str =   0
    start_zone : str = "<name> <x> <y> [metadata]"
    end_zone : str = "<name> <x> <y> [metadata]"
    hub : list[str] = "<name> <x> <y> [metadata] defines a regular zone"
    connection : list[str] = "<name_hub>-<name_hub> [metadata]"

    # def __init__(self, start_zone, end_zone, hub, connection):
    #     self.start_zone = start_zone
    #     self.end_zone = end_zone
    #     self.hub = hub
    #     self.connection = connection
    def __str__(self):
        return (
            f"drones_number  : {self.drones_number}\n"
            f"Start Zone : {self.start_zone}\n"
            f"End Zone   : {self.end_zone}\n"
            f"Hub        : {self.hub}\n"
            f"Connection : {self.connection}\n"
        )
    


def one_line(file_name, string_line):
    text = ""
    try:
        with open(file_name, 'r') as file:        
            while not text.startswith(string_line): 
                text = file.readline()
                if not text:
                    text = 0
                    break
                else:
                    text = text.rstrip("\n")
    except FileNotFoundError:
        print("File not found")
    except Exception as e:
        print(f"Error: {e}")    
    return text

def more_line(file_name, string_line):
    list_data = []
    try:
        with open(file_name, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith(string_line):
                    list_data.append(line.rstrip("\n"))
                    
    except FileNotFoundError:
        print("File not found")
    except Exception as e:
        print(f"Error: {e}")
    return list_data


# s = 'nb_drones: b'
# try:
#     f = int(s.split(':')[1].strip())
# except ValueError as e:
#     print(e)

# print(f , type(f))



# class Validit_var():
#     ...

#metadata = {zone=<type> (default: normal), color=<value> (default: none), max_drones=<number> (default: 1)}
#hub = [<name>, <x>, <y>, [dict(metadata)]]
#connection max_link_capacity=<number> (default: 1) - Maximum drones that can traverse this connection simultaneously

# start == end == max_drones
import re


def validit_hub_lines(lines: str)->list:
    result =[]
    line_pattern = re.compile(r"^(?P<name>[^\s\-]+)\s+(?P<x>-?\d+)\s+(?P<y>-?\d+)(?:\s*\[(?P<metadata>[^\]]*)\])?$",
        re.VERBOSE,
    )

    tag_pattern = re.compile(
        r"(zone|color|max_drones)=([^\s]+)"
    )

    VALID_ZONES = {"normal", "blocked", "restricted", "priority"}

    defaults = {
        "zone": "normal",
        "color": "none",
        "max_drones": 1,
    }
    m = line_pattern.match(lines)
    if m:
        result = [
            m.group("name"),
            tuple([int(m.group("x")), int(m.group("y"))]),
            defaults,
        ]
        metadata = m.group("metadata")
        if metadata:
            for key, value in tag_pattern.findall(metadata):
                result[2][key] = int(value) if key == "max_drones" else value
                if result[2][key] == "zone":
                    if value not in VALID_ZONES:
                        raise ValueError(
                            f"Invalid zone type '{value}'. "
                            f"Expected one of: {', '.join(VALID_ZONES)}"
                        )
        # print(result)
        return result

all_hub = []
drone = Get_lines()
file_name = "01_dead_end_trap.txt"
try:
    drone.drones_number = int(one_line(file_name, 'nb_drones').split(': ')[1])
except  ValueError as e:
    print(e)
drone.start_zone = one_line(file_name, 'start_hub: ')
drone.end_zone = one_line(file_name, 'end_hub: ')
drone.hub = more_line(file_name, 'hub: ')
drone.connection = more_line(file_name, 'connection: ')


all_hub.append(validit_hub_lines(drone.start_zone.split(': ')[1])) 
all_hub.append(validit_hub_lines(drone.end_zone.split(': ')[1])) 

# if all_hub[0][2]['max_drones'] < drone.drones_number:
#     raise ValueError(f"Start Zone should have max_drones of {drone.drones_number}")#ValueError: Start Zone should have max_drones of 2
# if all_hub[1][2]['max_drones'] < drone.drones_number:
#     raise ValueError(f"End Zone should have max_drones of {drone.drones_number}")


for line in drone.hub:
    all_hub.append(validit_hub_lines(line.split(': ')[1])) 


# print('all_hub: ',all_hub)

set_name = set()
set_map = set()
name_map = dict()
list_graph = []
for line in all_hub:
    set_name.add(line[0])
    set_map.add(line[1])
    name_map[line[0]] = line[1]


print("set_name     :",set_name)
# print(len(set_map) == len(all_hub))
# print(len(set_name) == len(all_hub))

# print("name_map",name_map)



# all_hub = ['start', (0,0), {'zone': 'priority', 'color': 'green,', 'max_drones': 1}]
# dict_name_map = {hub: (x,y)}
# ??max_drones vs zone type

# class RegEx_line(Get_lines):
#     all_hub = []
#     def __init__(self, start_zone, end_zone, hub, connection):
#         super().__init__(start_zone, end_zone, hub, connection)

    # for line in hub:
    #     all_hub =




def validit_connection(line: str) -> str:
    result = []
    connection_pattern = re.compile(
        r"""
        ^(?P<from_hub>[^\s-]+)
        -
        (?P<to_hub>[^\[\s]+)
        (?:\s*\[(?P<metadata>[^\]]*)\])?
        $
        """,        re.VERBOSE,
    )
    metadata_pattern = re.compile(
        r"max_link_capacity=(?P<capacity>\d+)"
    )
    defaults = {
        "max_link_capacity": 1
    }
    m = connection_pattern.match(line)
    if m:
        result = [
            m.group("from_hub"),
            m.group("to_hub"),
            defaults
        ]
        metadata = m.group("metadata")
        if metadata:
            cap = metadata_pattern.search(metadata)
            if cap:
                result[2]["max_link_capacity"] = int(cap.group("capacity"))
        return result


dict_name_map = dict() #

# to graph = {'start': ['A', 'B'],
#     'A': ['start', 'goal'],
#     'B': ['start', 'goal'],
#     'goal': ['A', 'B']}    
# 




graphs = dict()
seen = set()
list_name_map = []
for line in drone.connection:
    temp = validit_connection(line.split(': ')[1])
    from_hub = temp[0]
    to_hub = temp[1]
    capacity = temp[2]['max_link_capacity']

    if from_hub not in name_map:
        raise ValueError(f"{from_hub} : is not in zone defain")
    if to_hub not in name_map:
        raise ValueError(f"{to_hub} : is not in zone defain")
    tt = tuple(sorted([from_hub, to_hub]))
    if tt in seen:
        raise ValueError("Duplicate connection")
    seen.add(tt)

    if from_hub not in graphs:
        graphs[from_hub] = []
    if to_hub not in graphs:
        graphs[to_hub] = []
    
    graphs[from_hub].append({'to': to_hub, 'capacity':capacity})
    graphs[to_hub].append({'to': from_hub, 'capacity':capacity})
    list_name_map.append(temp)

print('\ngraphs',graphs)
# print('\nlist_name_map',list_name_map)
# print('\nseen',seen)




json_file = dict()
json_file['nb_drones'] = int(drone.drones_number)
json_file['start'] = all_hub[0][0]
json_file['end'] = all_hub[1][0]
json_file['hub'] = {}
json_file['graph'] = graphs.copy()

for hub in all_hub:
    # {'coordinate': hub[1], 'zone': hub[2]['zone'], 'color': hub[2]['color'], 'max_drones' :hub[2]['max_drones']}
    temp = hub[0]
    json_file['hub'][temp] = {'coordinate': hub[1], 'zone': hub[2]['zone'], 'color': hub[2]['color'], 'max_drones' :hub[2]['max_drones']}



# print('\njson_file' , json_file)



def get_cost(zone_type: str) -> int:
    costs = {
        "normal": 2,
        "priority": 1,
        "restricted": 3,
        "blocked": 15,
    }

    return costs[zone_type]



import heapq


def dijkstra(graph, zones, start, goal):
    distances = {
        node: float("inf")
        for node in graph
    }

    previous = {}

    distances[start] = 0

    heap = [(0, start)]

    while heap:
        current_distance, current_node = heapq.heappop(heap)

        if current_node == goal:
            break

        if current_distance > distances[current_node]:
            continue

        for edge in graph[current_node]:
            neighbor = edge["to"]

            if zones[neighbor]["zone"] == "blocked":
                continue

            move_cost = get_cost(
                zones[neighbor]["zone"]
            )

            new_distance = (
                current_distance
                + move_cost
            )

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance

                previous[neighbor] = current_node

                heapq.heappush(
                    heap,
                    (new_distance, neighbor)
                )

    return distances, previous


def build_path(previous, start, goal):
    path = []

    current = goal

    while current != start:
        path.append(current)

        current = previous[current]

    path.append(start)

    path.reverse()

    return path




# example =[]

# distances = { node: [0, node] if node == json_file['start'] else [float('inf'), node] for node in graphs.keys() }

# print("name_map\n",name_map)
# for current in name_map:
#     print(current)
#     # if zone == json_file['end'] or zone == json_file['start']:
#     #     continue 
#     for edge in graphs[current]:
#         neighbor = edge["to"]

#         cost = get_cost(
#             json_file["hub"][neighbor]["zone"]
#         )

#         new_distance = (
#             distances[current][0]
#             + cost
#         )

#         if new_distance < distances[neighbor][0]:
#             distances[neighbor][0] = new_distance
#             distances[neighbor][1] = current
                

# print(distances)





example =[]

distances = { node: [0, node] if node == json_file['start'] else [float('inf'), node] for node in graphs.keys() }

print("name_map\n",name_map)
for zone in name_map:
    print(distances) 
    for edge in graphs[zone]:
        node = edge['to']
        cost = get_cost(json_file["hub"][node]['zone'])
        new_distance = (distances[zone][0] + cost)

        if new_distance < distances[node][0]:
            distances[node][0] = new_distance
            distances[node][1] = zone
                

print(distances)


the_path = []
the_path.append(json_file["end"])
last_node = distances['goal']
while last_node != distances["start"]:
    temp = last_node[1]
    the_path.append(temp)
    last_node = distances[temp]

the_path.reverse()
print(the_path)
