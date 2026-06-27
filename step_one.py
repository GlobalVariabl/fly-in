from typing import Any
from typing import Optional

import re
import heapq


import re
from typing import Any, Optional


class RegEx_line:
    """Parse and validate drone simulation file lines."""

    hubs: list[dict[str, Any]] = []
    connections: list[dict[str, Any]] = []

    def __init__(self, read_file_dict: dict[str, Any]) -> None:
        """
        Initialize with parsed dictionary from Read_file.

        Args:
            read_file_dict: dict from Read_file containing
                            raw parsed lines
        """
        self.drones_number: Any = read_file_dict["drones_number"]
        self.start_zone: list[Any] = read_file_dict["start_zone"]
        self.end_zone: list[Any] = read_file_dict["end_zone"]
        self.hub: list[Any] = read_file_dict["hub"]
        self.connection: list[Any] = read_file_dict["connection"]
        self.parsed_alls: list[Any] = []
        self.validit_all()

    def validit_all(self) -> None:
        """
        Validate and parse all sections.
        Populates parsed_start, parsed_end,
        parsed_hubs, parsed_connections.

        Raises:
            ValueError: if any line is invalid
        """

        self.drones_number = RegEx_line.validit_drones(self.drones_number)
        self.parsed_alls.append({"drones_number": self.drones_number})

        self.start_zone[0] = RegEx_line.validit_hub_sd(
            self.start_zone[0].split(":", 1)[1].strip(), True
        )
        self.parsed_alls.append(self.start_zone)

        self.end_zone[0] = RegEx_line.validit_hub_sd(
            self.end_zone[0].split(":", 1)[1].strip(), True
        )
        self.parsed_alls.append(self.end_zone)

        if self.start_zone[0]["zone"] == "blocked":
            raise ValueError(
                f"The start zone: {self.start_zone[0]['name']}"
                f" is Inaccessible zone : {self.start_zone[1] + 1}"
            )
        if self.end_zone[0]["zone"] == "blocked":
            raise ValueError(
                f"The End zone: {self.end_zone[0]['name']}"
                f" is Inaccessible zone : {self.start_zone[1] + 1}"
            )
        for idx, line in enumerate(self.hub):
            self.hub[idx][0] = RegEx_line.validit_hub_sd(
                line[0].split(":")[1].strip(), False
            )
            self.parsed_alls.append(self.hub[idx])
            RegEx_line.hubs.append(self.hub[idx][0])
        for idx, line in enumerate(self.connection):
            self.connection[idx][0] = RegEx_line.validate_connection(
                line[0].split(":", 1)[1].strip()
            )
            self.parsed_alls.append(self.connection[idx])
            RegEx_line.connections.append(self.connection[idx][0])

        RegEx_line.validate_connection_link(self.parsed_alls[1:])

    def get_data(self) -> dict[str, Any]:
        """Return parsed data as a dictionary."""
        return {
            "drones_number": self.drones_number,
            "start_zone": self.start_zone[0],
            "end_zone": self.end_zone[0],
            "hub": self.hubs,
            "connection": self.connections,
        }

    @staticmethod
    def validit_drones(line: str) -> int:
        """
        Parse and validate a hub/start_hub/end_hub line.
        Extracts name, coordinates, and metadata.
        """
        drones: Optional[int] = None
        patten = re.match(r"^nb_drones\s*:\s*(\d+)\s*$", line)
        if not patten:
            raise ValueError(f"Invalid line nb_drones : {line}")
        drones = int(patten.group(1))
        if drones < 1:
            raise ValueError("nb_drones must be greater than 0")
        return drones

    @staticmethod
    def validit_hub_sd(line: str, ist_special: bool) -> dict[str, Any]:
        """
        Parse and validate a hub/start_hub/end_hub line.
        Extracts name, coordinates, and metadata.
        """
        pattern = re.compile(
            r"^(?P<name>[^\s\-]+)\s+"
            r"(?P<x>-?\d+)\s+"
            r"(?P<y>-?\d+)"
            r"(?:\s*\[(?P<metadata>[^\]]*)\])?$"
        )
        meta_pattern = re.compile(r"(zone|color|max_drones)=([^\s]+)")
        valid_zones: set[str] = {"normal", "blocked", "restricted", "priority"}
        valid_keys: set[str] = {"zone", "color", "max_drones"}
        defaults: dict[str, Any] = {
            "zone": "normal",
            "color": None,
            "max_drones": float("inf") if ist_special else 1,
        }
        match = pattern.match(line.strip())
        if not match:
            raise ValueError(f"Invalid hub line format: '{line}'")

        data: dict[str, Any] = match.groupdict()
        name: str = data["name"]
        if "-" in name:
            raise ValueError(
                f"Zone name '{name}' cannot contain dashes. "
                f"Dashes are reserved for connection syntax"
            )
        metadata: Optional[str] = data.get("metadata")
        if metadata is not None:

            metadata = metadata.strip()
            key_value_pattern = re.compile(r"(\w+)=([^\s\]]+)")
            all_pairs: list[tuple[str, str]] = key_value_pattern.findall(
                metadata
            )
            valid_key_repet: dict[str, str] = dict()
            cleaned: str = metadata
            for key, value in all_pairs:
                if key not in valid_keys:
                    raise ValueError(
                        f"Invalid metadata key '{key}' in line: '{line}'."
                    )
                if key in valid_key_repet:
                    raise ValueError(
                        f"Duplicate metadata key '{key}' in line: '{line}'."
                    )

                if key == "max_drones":
                    if not re.match(r"^[1-9][0-9]*$", value):
                        raise ValueError(
                            f"Invalid max_drones value '{value}'"
                            f" in line: '{line}'."
                            f" Must be a positive integer"
                        )
                else:
                    if not re.match(r"^[a-zA-Z\-]+$", value):
                        raise ValueError(
                            f"Invalid value '{value}' for key"
                            f" '{key}' in line: '{line}'. "
                        )
                valid_key_repet[key] = value
                cleaned = cleaned.replace(f"{key}={value}", "")

            if cleaned:
                cleaned = " ".join(cleaned.split())
                if cleaned:
                    raise ValueError(
                        f"Invalid metadata format: '{metadata}'"
                        f" in line: '{line}'. "
                        f"Unexpected text: '{cleaned}'"
                    )

            for key, value in meta_pattern.findall(metadata):
                if key == "zone":
                    if value not in valid_zones:
                        raise ValueError(
                            f"Invalid zone type '{value}'"
                            f" in line: '{line}'."
                        )
                    defaults["zone"] = value
                if key == "color":
                    defaults["color"] = value
                if key == "max_drones":
                    if ist_special:
                        continue
                    if not value.isdigit() or int(value) <= 0:
                        raise ValueError(
                            f"Invalid max_drones '{value}' in line:"
                            f" '{line}'. Must be positive integer"
                        )
                    defaults["max_drones"] = int(value)

        result: dict[str, Any] = {
            "name": data["name"],
            "coordinate": (int(data["x"]), int(data["y"])),
            "zone": defaults["zone"],
            "color": defaults["color"],
            "max_drones": defaults["max_drones"],
        }
        return result

    @staticmethod
    def validate_connection(line: str) -> dict[str, Any]:
        """
        Parse and validate a connection line.
        Extracts from_hub, to_hub, and max_link_capacity.
        """
        connection_pattern = re.compile(
            r"^(?P<from_hub>[^\s\-]+)"
            r"-"
            r"(?P<to_hub>[^\s\-]+)"
            r"(?:\s*\[\s*(?:max_link_capacity\s*=\s*"
            r"(?P<capacity>\d+))?\s*\])?\s*$"
        )
        defaults: dict[str, int] = {"max_link_capacity": 1}
        connections = connection_pattern.match(line.strip())
        if not connections:
            raise ValueError(
                f"Invalid connections line format: '{line}'"
                f" Expected 'from-to [max_link_capacity=N]'"
            )
        data: dict[str, Any] = connections.groupdict()
        from_hub: str = data["from_hub"]
        to_hub: str = data["to_hub"]
        capacity: Optional[str] = data["capacity"]

        if not from_hub or not to_hub:
            raise ValueError(f"Empty zone name in connection: '{line}'")
        if from_hub == to_hub:
            raise ValueError(f"Zone cannot connect to itself: '{line}' !?")

        if capacity:
            capacity_int: int = int(capacity)
            if capacity_int <= 0:
                raise ValueError(
                    f"max_link_capacity must be positive,"
                    f" got {capacity_int} in: '{line}'"
                )
            defaults["max_link_capacity"] = capacity_int

        result: dict[str, Any] = {
            "from": from_hub,
            "to": to_hub,
            "max_link_capacity": defaults["max_link_capacity"],
        }
        return result

    @staticmethod
    def validate_connection_link(list_line: list[Any]) -> None:

        goal: str = list_line[1][0]["name"]
        goal_connected: bool = False
        list_line.sort(key=lambda x: x[1])
        set_name: set[str] = set()
        set_coordinate: set[tuple[int, int]] = set()
        set_connection: set[tuple[str, str]] = set()
        for lines in list_line:
            line: dict[str, Any] = lines[0]
            if "name" in line:
                if line["name"] not in set_name:
                    set_name.add(line["name"])
                else:
                    raise ValueError(
                        f"the {line['name']} is repetition"
                        f" in line {lines[1]+1}"
                    )
                if line["coordinate"] not in set_coordinate:
                    set_coordinate.add(line["coordinate"])
                else:
                    raise ValueError(
                        f"the {line['coordinate']} is repetition"
                        f"  in line {lines[1]+1}"
                    )
            elif "from" in line:
                if line["from"] not in set_name:
                    raise ValueError(
                        f"the '{line['from']}' is not defined,"
                        f" Connections must link only previously"
                        f" defined zones  in line {lines[1]+1} ??"
                    )
                if line["to"] not in set_name:
                    raise ValueError(
                        f"the '{line['to']}' is not defined,"
                        f" Connections must link only previously"
                        f" defined zones  in line {lines[1]+1} ??"
                    )
                else:
                    connection: tuple[str, str] = tuple(
                        sorted([line["from"], line["to"]])
                    )
                    if connection not in set_connection:
                        set_connection.add(connection)
                    else:
                        raise ValueError(
                            f"The same connection must not appear"
                            f" more than once {connection} is"
                            f" repetition  in line {lines[1]+1}"
                        )

        for connection in set_connection:
            if goal in connection:
                goal_connected = True
        if not goal_connected:
            raise ValueError(
                f"The is no {goal} in connection so connection"
                f" is not full connect to end zone '{goal}'"
            )



class Read_file:
    n_drones: str = ""
    s_zone: list[str | int] = []
    e_zone: list[str | int] = []
    hub: list[list[str | int]] = []
    connection: list[list[str | int]] = []

    def __init__(self, file_name: str) -> None:
        self.file_name: str = file_name
        self.read_lines()

    def read_lines(self) -> None:
        list_lines: list[str] = []

        with open(self.file_name, "r") as file:
                list_lines = file.readlines()

        Read_file.valid_garbage_line(list_lines)
        Read_file.valid_line_dron(list_lines)
        Read_file.valid_special_zone(list_lines, "start_hub")
        Read_file.valid_special_zone(list_lines, "end_hub")
        Read_file.valid_more_lines(list_lines, "hub")
        Read_file.valid_more_lines(list_lines, "connection")

        Read_file.n_drones = Read_file.valid_line_dron(list_lines)
        Read_file.s_zone = Read_file.valid_special_zone(list_lines, "start_hub")
        Read_file.e_zone = Read_file.valid_special_zone(list_lines, "end_hub")
        Read_file.hub = Read_file.valid_more_lines(list_lines, "hub")
        Read_file.connection = Read_file.valid_more_lines(list_lines, "connection")
        
    @staticmethod
    def valid_line_dron(list_lines: list[str]) -> str:
        """
        Validates that nb_drones appears exactly once on the first non-comment line.
        Returns the line index where it was found.
        """
        first_non_comment_line_index: Optional[int] = None
        line_dron: Optional[int] = None
        repet_dron: int = 0
        for idx, line in enumerate(list_lines):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            first_non_comment_line_index = idx
            break
        for idx, line in enumerate(list_lines):
            stripped = line.strip()
            if stripped.startswith("nb_drones"):
                repet_dron += 1
                line_dron = idx

        if first_non_comment_line_index is None:
            raise ValueError("File has no non-comment lines")
        if repet_dron == 0:
            raise ValueError("nb_drones was no in file")
        if repet_dron >= 2:
            raise ValueError(
                f"nb_drones was repet {repet_dron} time, last at line {line_dron + 1}"
            )
        if first_non_comment_line_index != line_dron:
            raise ValueError(
                f"nb_drones must be on the first non-comment line."
                f"Found at line {line_dron + 1}, but first non-comment line is {first_non_comment_line_index + 1}"
            )
        """handl # """
        line: str = list_lines[line_dron].rstrip("\n")
        if "#" in line:
            line_whith_comm = line[line.index("#") :]
            line_whith_no_comm = line.replace(line_whith_comm, "")
        else:
            line_whith_no_comm = line
        return line_whith_no_comm

    @staticmethod
    def valid_special_zone(list_lines: list[str], special_zone: str) -> list[str | int]:
        """
        Validates that start_hub appears exactly once.
        Returns the line index where it was found.
        """
        repet_time: int = 0
        line_idx: Optional[int] = None

        for idx, line in enumerate(list_lines):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            if stripped.startswith(special_zone):
                repet_time += 1
                line_idx = idx

        if repet_time == 0:
            raise ValueError(f"{special_zone} was not found in file")
        if repet_time != 1:
            raise ValueError(
                f"{special_zone} was repet {repet_time} time, last at line {line_idx + 1}"
            )

        """handl # """
        line: str = list_lines[line_idx].rstrip("\n")
        if "#" in line:
            line_whith_comm = line[line.index("#") :]
            line_whith_no_comm = line.replace(line_whith_comm, "")
        else:
            line_whith_no_comm = line

        return [line_whith_no_comm, line_idx]

    @staticmethod
    def valid_more_lines(list_lines: list[str], line_word: str) -> list[list[str | int]]:
        """
        Validates that at least one line starts with line_word
        (ignoring comments/empties).
        Returns list of matching lines .
        """
        repet_time: int = 0
        lists_word: list[list[str | int]] = []
        for idx, line in enumerate(list_lines):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith(line_word):
                """handl #"""
                line: str = line.rstrip("\n")
                if "#" in line:
                    line_whith_comm = line[line.index("#") :]
                    line_whith_no_comm = line.replace(line_whith_comm, "")
                else:
                    line_whith_no_comm = line
                lists_word.append([line_whith_no_comm, idx])
                repet_time += 1
        if repet_time == 0 and line_word != "hub:":
            raise ValueError(f"No '{line_word}' found in file")

        return lists_word

    @staticmethod
    def valid_garbage_line(list_lines: list[str]) -> None:
        """
        Validates that every non-comment, non-empty line starts with a valid keyword.
        Valid keywords: nb_drones, start_hub, end_hub, hub, connection
        """
        valid_keywords: set[str] = {"nb_drones", "start_hub", "end_hub", "hub", "connection"}
        for idx, line in enumerate(list_lines):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            if ":" not in stripped:
                raise ValueError(
                    f"Line {idx + 1}: Missing colon ':'. Expected format 'keyword: value'"
                )
            keyword = stripped.split(":")[0].strip() if stripped.split(":") else ""
            if keyword not in valid_keywords:
                raise ValueError(
                    f"The keyword: {keyword} is Invalid keyword for this file, Line {idx + 1}"
                )

    def get_data(self) -> dict[str, object]:
        """Return parsed data as a dictionary."""
        return {
            "drones_number": self.n_drones,
            "start_zone": self.s_zone,
            "end_zone": self.e_zone,
            "hub": self.hub,
            "connection": self.connection,
        }


class Json_file:
    graph = dict()
    distances = dict()

    def __init__(self, clean_data):
        self.drones_number: int = clean_data["drones_number"]
        self.start_zone: str = clean_data["start_zone"]
        self.end_zone: str = clean_data["end_zone"]
        self.hub: list[str] = clean_data["hub"]
        self.connection: list[str] = clean_data["connection"]

    def grouping_in_graph(self):
        Json_file.graph["drones_number"] = self.drones_number
        Json_file.graph["start_zone"] = self.start_zone["name"]
        Json_file.graph["end_zone"] = self.end_zone["name"]
        Json_file.graph["hubs"] = {}
        Json_file.graph["graph"] = {}
        Json_file.graph["distances"] = {}

        Json_file.graph["hubs"][self.start_zone["name"]] = {
            "coordinate": self.start_zone["coordinate"],
            "zone": self.start_zone["zone"],
            "color": self.start_zone["color"],
            "max_drones": self.start_zone["max_drones"],
            "state": "empty",
            "holde": self.drones_number,
        }
        Json_file.graph["hubs"][self.end_zone["name"]] = {
            "coordinate": self.end_zone["coordinate"],
            "zone": self.end_zone["zone"],
            "color": self.end_zone["color"],
            "max_drones": self.drones_number,
            "state": "empty",
            "holde": 0,
        }
        for item in self.hub:
            Json_file.graph["hubs"][item["name"]] = {
                "coordinate": item["coordinate"],
                "zone": item["zone"],
                "color": item["color"],
                "max_drones": item["max_drones"],
                "state": "empty",
                "holde": 0,
            }

        for items in self.connection:
            if items["from"] not in Json_file.graph["graph"]:
                Json_file.graph["graph"][items["from"]] = []
            if items["to"] not in Json_file.graph["graph"]:
                Json_file.graph["graph"][items["to"]] = []

            Json_file.graph["graph"][items["from"]].append(
                {
                    "to": items["to"],
                    "capacity": items["max_link_capacity"],
                    "state": "empty",
                    "holde": 0,
                }
            )
            Json_file.graph["graph"][items["to"]].append(
                {
                    "to": items["from"],
                    "capacity": items["max_link_capacity"],
                    "state": "empty",
                    "holde": 0,
                }
            )

        Json_file.graph["distances"] = Json_file.distances_cost(Json_file.graph)
        return Json_file.graph

    @staticmethod
    def get_cost(zone_name) -> int:
        costs = {
            "normal": 2,
            "priority": 1,
            "restricted": 3,
            "blocked": 151,
        }
        return costs[zone_name]

    @staticmethod
    def distances_cost(graph):
        distances = {
            zone: [float("inf"), zone] if zone != graph["end_zone"] else [0, zone]
            for zone in graph["hubs"]
        }
        goale = graph["end_zone"]
        heap_list = [distances[goale]]
        heapq.heapify(heap_list)
        while heap_list:
            current_cost, current = heapq.heappop(heap_list)
            for edge in graph["graph"][current]:
                neighbor = edge["to"]
                if Json_file.graph["hubs"][neighbor]["zone"] == "blocked":
                    continue
                zone_cost = Json_file.get_cost(
                    Json_file.graph["hubs"][neighbor]["zone"]
                )
                new_cost = zone_cost + current_cost
                if new_cost < distances[neighbor][0]:
                    distances[neighbor][0] = new_cost
                    distances[neighbor][1] = current
                    heapq.heappush(heap_list, (new_cost, neighbor))

        is_valid_path = []
        start = Json_file.graph["start_zone"]
        while start != Json_file.graph["end_zone"]:
            if start != distances[start][1]:
                is_valid_path.append(distances[start][1])
                start = distances[start][1]
            else:
                break
        # print(is_valid_path)
        if Json_file.graph["end_zone"] not in is_valid_path:
            raise ValueError(
                f"No Path Found from {start} to {goale} Check for: All blocked zones cutting all routes"
            )
        return distances


    def get_data(self):
        """Return parsed data as a dictionary."""
        return Json_file.graph


def database():
    try:
        reader = Read_file("test.txt")
        parser = RegEx_line(reader.get_data())
        Json_file(parser.get_data())
        json_file = Json_file(parser.get_data())
        print()
        # print(json_file.grouping_in_graph())
        print()
        return json_file.grouping_in_graph()
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    try:
        reader = Read_file("test.txt")
        parser = RegEx_line(reader.get_data())
        json_file = Json_file(parser.get_data())
        print(f"✓ Successfully parsed!\n")
        print(json_file.grouping_in_graph())

    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
