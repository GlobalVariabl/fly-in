
## The first line defines the number of drones using nb_drones: <number>.

## Zone definition on each line using type prefixes:
◦ start_hub: <name> <x> <y> [metadata] marks the starting zone.
◦ end_hub: <name> <x> <y> [metadata] marks the end zone.
◦ hub: <name> <x> <y> [metadata] defines a regular zone.
◦ The connection syntax forbids dashes in zone names (see below).

## All metadata is optional and enclosed in brackets [...] with default values:
◦ zone=<type> (default: normal)
◦ color=<value> (default: none)
◦ max_drones=<number> (default: 1) - Maximum drones that can occupy this
zone simultaneously
◦ Tags inside brackets can appear in any order.


## Zone types:
Each movement between zones has a cost in turns, based on the zone=type of the
destination:
• normal: 1 turn (default)
• restricted: 2 turns
• priority: 1 turn (but should be preferred in pathfinding algorithms)
• blocked: Inaccessible — cannot be entered

## Colors:
◦ Colors are optional and can be used for visual representation (terminal output
or graphical display).
◦ Accepted values for color are any valid single-word strings (e.g., red, blue,
gray). There is no fixed list of allowed colors.
◦ When colors are specified, the implementation should provide visual feedback
through colored terminal output or graphical representation.

## • Connections are defined using connection: <name1>-<name2> [metadata]:
◦ Define a bidirectional connection (edge) between two zones.
◦ The connection syntax forbids dashes in zone names.
◦ Optional metadata can be specified in brackets [...]:
∗ max_link_capacity=<number> (default: 1) - Maximum drones that can

## traverse this connection simultaneously
• Comments start with ’#’ and are ignored.

## Visual Representation: 
Your implementation must provide visual feedback of the simulation, either through:
◦ Colored terminal output showing drone movements and zone states
◦ A graphical interface displaying the network and drone positions
◦ Both options for enhanced user experience


# VII.4 Parser Constraints
The input file must respect the expected structure and syntax:
• The first line must define the number of drones using nb_drones: <positive_integer>.
• The program must be able to handle any number of drones.
• There must be exactly one start_hub: zone and one end_hub: zone.
• Each zone must have a unique name and valid integer coordinates.
• Zone names can use any valid characters but dashes and spaces.
• Connections must link only previously defined zones using connection: <zone1>-<zone2>
[metadata].
• The same connection must not appear more than once (e.g., a-b and b-a are considered duplicates).
• Any metadata block (e.g., [zone=... color=...] for zones, [max_link_capacity=...]
for connections) must be syntactically valid.
• Zone types must be one of: normal, blocked, restricted, priority. Any invalid
type must raise a parsing error.
• Capacity values (max_drones for zones, max_link_capacity for connections) must
be positive integers.
• Any other parsing error must stop the program and return a clear error message
indicating the line and cause.






Great question — these three are easy to confuse. Here's how they differ:

---

**`zone type`** — controls **movement cost** to enter that zone.
- `normal` → costs 1 turn to enter
- `restricted` → costs 2 turns to enter (drone occupies the connection for 1 turn, then arrives)
- `priority` → costs 1 turn but pathfinding should prefer it
- `blocked` → can't be entered at all

It's about **time**, not space.

---

**`max_drones`** — controls **how many drones can occupy that zone simultaneously**.
- Default is 1 (only one drone can be standing in that zone at a time)
- Exception: start and end zones ignore this rule
- It's about **space inside the zone**

---

**`max_link_capacity`** — controls **how many drones can travel through a connection at the same time**.
- Default is 1
- Two drones can't use the same corridor simultaneously unless capacity > 1
- It's about **space on the path between zones**

---

**A concrete scenario to make it click:**

```
corridorA [zone=restricted, max_drones=2]
connection: hub-corridorA [max_link_capacity=3]
```

- 3 drones can enter the connection toward `corridorA` on the same turn
- But only 2 can actually stand inside `corridorA` at once
- And each one took 2 turns to get there because it's `restricted`

## Does that distinction make sense before we model the classes?


Layer 1 — PATH FINDING (Dijkstra)
    Find all possible paths from start to end
    considering zone type costs
    ↓
Layer 2 — PATH ASSIGNMENT
    Distribute N drones across found paths
    considering capacities
    ↓
Layer 3 — TURN SCHEDULER
    Simulate turn by turn
    resolve conflicts
    decide who moves and who waits