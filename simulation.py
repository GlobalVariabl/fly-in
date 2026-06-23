from step_one import database
{
    'drones_number': 6, 'start_zone': 'start', 'end_zone': 'goal', 
    'hubs': {
        'start': {'coordinate': (0, 0), 'zone': 'normal', 'color': 'green', 'max_drones': "inf", 'state': 'empty', 'holde': 6}, 
        'goal': {'coordinate': (3, 0), 'zone': 'normal', 'color': 'yellow', 'max_drones': 6, 'state': 'empty', 'holde': 0}, 
        'A': {'coordinate': (1, 0), 'zone': 'blocked', 'color': None, 'max_drones': 1, 'state': 'empty', 'holde': 0}, 
        'B': {'coordinate': (1, 1), 'zone': 'priority', 'color': 'blue', 'max_drones': 2, 'state': 'empty', 'holde': 0}, 
        'C': {'coordinate': (2, 0), 'zone': 'blocked', 'color': None, 'max_drones': 1, 'state': 'empty', 'holde': 0}, 
        'D': {'coordinate': (2, 1), 'zone': 'blocked', 'color': None, 'max_drones': 1, 'state': 'empty', 'holde': 0}, 
        'F': {'coordinate': (3, 1), 'zone': 'restricted', 'color': None, 'max_drones': 1, 'state': 'empty', 'holde': 0}}, 
    'graph': {
        'start': [{'to': 'A', 'capacity': 1, 'state': 'empty', 'holde': 0}, {'to': 'B', 'capacity': 1, 'state': 'empty', 'holde': 0}, {'to': 'F', 'capacity': 1, 'state': 'empty', 'holde': 0}], 
        'A': [{'to': 'start', 'capacity': 1, 'state': 'empty', 'holde': 0}, {'to': 'C', 'capacity': 1, 'state': 'empty', 'holde': 0}, {'to': 'D', 'capacity': 1, 'state': 'empty', 'holde': 0}], 
        'B': [{'to': 'start', 'capacity': 1, 'state': 'empty', 'holde': 0}, {'to': 'C', 'capacity': 1, 'state': 'empty', 'holde': 0}, {'to': 'D', 'capacity': 1, 'state': 'empty', 'holde': 0}], 
        'F': [{'to': 'goal', 'capacity': 1, 'state': 'empty', 'holde': 0}, {'to': 'start', 'capacity': 1, 'state': 'empty', 'holde': 0}],
        'C': [{'to': 'A', 'capacity': 1, 'state': 'empty', 'holde': 0}, {'to': 'B', 'capacity': 1, 'state': 'empty', 'holde': 0}, {'to': 'goal', 'capacity': 1, 'state': 'empty', 'holde': 0}], 
        'D': [{'to': 'A', 'capacity': 1, 'state': 'empty', 'holde': 0}, {'to': 'B', 'capacity': 1, 'state': 'empty', 'holde': 0}, {'to': 'goal', 'capacity': 1, 'state': 'empty', 'holde': 0}]}, 
    'distances': {
            'start': [5, 'F'], 'goal': [0, 'goal'], 'A': ["inf", 'A'], 'B': [6, 'start'], 
            'C': ["inf", 'C'], 'D': ["inf", 'D'], 'F': [3, 'goal']}}




class Drone:
    """Represents a single drone."""
    def __init__(self, drones_id: int, graph: dict) -> None:
        """Initialize drone at start zone."""
        self.graph = graph
        self.drones_id = drones_id
        self.location: str = graph["start_zone"]
        self.statue: str = "waiting"
        
        self.can_i_fil: bool = True 
        # self.transit_destination: str | None = None
    
    
    # def fly_drones(self,drones_id, graph):

        # whrer i my in graph
        #(drones_id, zone_name=graph['start_zone'])
        # aske what is bast zone in 1 distances, if if get full lock up fo secand zone and than tchak if it in distances in cost is last than cost zone 

        ...

    def get_next_bast_zone(self) -> str | None:
        """
        Find the best next zone for a drone to move to.
        Returns the zone ID of the best move, or None if no move is available.
        """
        location  = self.location
        best_zone: str | None = None
        all_zones = self.graph["graph"][location]
        location_cost  = self.graph["distances"][location][0]
        best_cost: float = float("inf")
        
        for edge in all_zones:
            next_zone = edge['to']
            next_cost = self.graph["distances"][next_zone][0]
                
            # skip blocked
            if float(next_cost) >= float(location_cost): # or just > !?
                continue
            
            next_zone_data: dict = self.graph['hubs'].get(next_zone, {})
            
            # if zone_data.get('zone') == 'blocked':
            #     continue
            
            # skip full zones
            current: int = next_zone_data.get('holde', 0)
            maximum: float = next_zone_data.get('max_drones', 1)
            if current >= maximum:
                continue

            # pick lowest gradient neighbor
            if next_cost < best_cost:
                best_cost = next_cost
                best_zone = next_zone
        
        return best_zone



    def move_to_next_zone(self, next_zone):
        """Move drone to next zone."""
        self.location = next_zone
        if next_zone == graph['end_zone']:
            self.statue = "DELIVERED"
        print(self.get_state(),"\n")


    def get_state(self):
        """Return current drone state."""
        return {
            "drones_id": self.drones_id, 
            "statue": self.statue, 
            "location": self.location
        }





class Simulation():
    """Manages turn-by-turn simulation. 
    Simulation will accept drone next move"""
    def __init__(self, graph):
        """Initialize simulation."""
        self.graph = graph
        self.turn: int = 0
        self.goal: str = graph['end_zone']
        self.track_drone: list[Drone] = []
        self.run()

    def all_delivered(self) -> bool:
        """Check if all drones delivered."""
        return all(drone.statue == "DELIVERED" for drone in self.track_drone)
                

    def run(self):
        """Run simulation until all drones delivered."""
        # goale = self.graph['end_zone']
        self.turn = 0
        zone_req: list[list[tuple]] = []
        
        for drone_id in range(1, self.graph['drones_number'] + 1):
            drone = Drone(drone_id, self.graph)
            self.track_drone.append(drone)
        buffer_zone = []
        
        while not self.all_delivered():
            
            turn_moves: list[tuple] = []
            move_track = []
            
            for  drone in self.track_drone:

                #__-->{buffer zone} will be post forst
                
                #  
                if drone.statue == "DELIVERED":
                    continue
                
                zone =  drone.get_next_bast_zone()
                if zone is None:
                    continue
                
                zone_data = self.graph['hubs'][zone]
                # print(zone_data)
                if zone_data.get('zone') == 'blocked':
                    continue
                
                # if zone_data.get('zone') == 'restricted':
                    
                # why not just holde 'F' for twe turn => and leaving will be free
                
                
                # restrc 2 turn
                # {all drone will go to here {buffer_zone }if next zone is restrc, in next turn will buffer first }

                
                
                
                current_hold = zone_data.get("hold", 0)
                max_drones = zone_data.get("max_drones", 1)

                if current_hold < max_drones:
                    leaving = drone.location
                    landing = zone

                # if self.graph['hubs'][landing]['holde'] + 1 <= self.graph['hubs'][landing]['max_drones']:
                if leaving != self.graph['start_zone']:
                    self.graph['hubs'][leaving]['holde'] -= 1
                

                # if drone.can_i_fil:
                drone.move_to_next_zone(landing)
                
                
                drone.can_i_fil =  zone_data.get('zone') != 'restricted'
                
                self.graph['hubs'][landing]['holde'] += 1
                    
                if self.graph['hubs'][landing]['holde'] == max_drones:
                    graph['hubs'][landing]['state'] = 'full'
                else:
                    self.graph['hubs'][landing]['state'] = 'empty'
                    
                
                
                move_track.append((drone.drones_id, landing))
            
            zone_req.append(move_track)
            # if move_track:
            #     output = ' '.join(
            #         f"D{did}-{zone}"
            #         for did, zone in move_track
            #     )
            
            print(f"Turn {self.turn + 1}")

            self.turn += 1

        print(f"\nTotal turns: {self.turn}")
        print(zone_req)
        





if __name__ == "__main__":
    try:
        graph = database()
        if graph is None:
            print("Simulation stopped: no valid path found.")
            exit()
        run  = Simulation(graph)
    except Exception as e:
        print(f"Error: {e}")



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