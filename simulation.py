
graph = {
            'drones_number': 3, 
            'start_zone': 'start', 
            'end_zone': 'goal', 
            'hubs': {
                    'start': {'coordinate': (0, 0), 'zone': 'normal', 'color': 'green', 'max_drones': "inf", 'state': 'empty', 'holde': 3}, 
                    'goal': {'coordinate': (3, 0), 'zone': 'normal', 'color': 'yellow', 'max_drones': 3, 'state': 'empty', 'holde': 0}, 
                    'A': {'coordinate': (1, 0), 'zone': 'normal', 'color': None, 'max_drones': 1}, 
                    'B': {'coordinate': (1, 1), 'zone': 'priority', 'color': 'blue', 'max_drones': 1}, 
                    'C': {'coordinate': (2, 0), 'zone': 'normal', 'color': None, 'max_drones': 1}, 
                    'D': {'coordinate': (2, 1), 'zone': 'normal', 'color': None, 'max_drones': 1}}, 
            'graph': {
                'start': [{'to': 'A', 'capacity': 1, 'state': 'empty', 'holde': 0}, {'to': 'B', 'capacity': 1, 'state': 'empty', 'holde': 0}],
                'A': [{'to': 'start', 'capacity': 1, 'state': 'empty', 'holde': 0}, {'to': 'C', 'capacity': 1, 'state': 'empty', 'holde': 0}],
                'B': [{'to': 'start', 'capacity': 1, 'state': 'empty', 'holde': 0}, {'to': 'D', 'capacity': 1, 'state': 'empty', 'holde': 0}],
                'C': [{'to': 'A', 'capacity': 1, 'state': 'empty', 'holde': 0}, {'to': 'goal', 'capacity': 1, 'state': 'empty', 'holde': 0}],
                'D': [{'to': 'B', 'capacity': 1, 'state': 'empty', 'holde': 0}, {'to': 'goal', 'capacity': 1, 'state': 'empty', 'holde': 0}],},
            'distances': {'start': [5, 'B'], 'goal': [0, 'goal'], 'A': [4, 'C'], 'B': [3, 'D'], 'C': [2, 'goal'], 'D': [2, 'goal']},}

class Simulation:
    # Simulation will accept drone next move 
    def __init__(self, graph):
        self.graph = graph
        self.turn = 0
        self.goal = graph['end_zone']

    def run(self):
        goale = graph['end_zone']
        turn = 0
        
        for drone_id in range(0, self.graph['drones_number']):
            self.init_drones(drone_id, self.graph)

        while graph['hubs'][goale]["holde"] != graph['drones_number']:
            ...
            ...
            ...
            ###
            for drone_id in range(0, self.graph['drones_number']):
                self.fly_drones(drone_id, graph)
            ...
            ###
            turn += 1



class Drone:
    def __init__(self, graph, drones_id):
        self.graph = graph
        self.drones_id = drones_id
        self.location = graph["start_zone"]
        self.statue = "WAITING"
    
    @staticmethod
    def fly_drones(self,drones_id, graph):
        # whrer i my in graph
        #(drones_id, zone_name=graph['start_zone'])
        # aske what is bast zone in 1 distances, if if get full lock up fo secand zone and than tchak if it in distances in cost is last than cost zone 

        ...

    def get_state(self,drones_id, graph):
        self.drones_id = drones_id
        self.location = graph["start_zone"]
        self.statue = "WAITING"
        return {"drones_id":self.drones_id,"statue" : self.statue, "location" :self.location}

# 'state': 'empty', 'full', 'Almost'
# 'holde': max_drones - drones

# BEFORE SIMULATION:
#   build gradient field (reverse Dijkstra from goal)
#   each zone knows its distance to goal

# SIMULATION LOOP:
#   while not all drones at goal:
#       turn += 1
#       for each drone → decide move
#       resolve conflicts
#       execute moves
#       print turn output




# DRONE STATE MACHINE:

#           ┌─────────────────┐
#           │    WAITING      │ ← stuck at start or blocked
#           └────────┬────────┘
#                    │ next zone available
#                    ▼
#           ┌─────────────────┐
#           │     MOVING      │ ← normal/priority zone (1 turn)
#           └────────┬────────┘
#                    │ destination is restricted?
#           ┌────────┴────────┐
#           │   IN_TRANSIT    │ ← on connection (turn 1 of 2)
#           └────────┬────────┘
#                    │ must arrive next turn
#                    ▼
#           ┌─────────────────┐
#           │    DELIVERED    │ ← reached goal ✓
#           └─────────────────┘



# start with first indax D1 move to lower zone cost
#  first seiz of next zone > 1 than capacity of link
#  updated zone state and holde drone (max_drones - holde)
#  move to second drones