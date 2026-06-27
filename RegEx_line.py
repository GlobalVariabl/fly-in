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
                    if not re.match(r"^[0-9][0-9]*$", value):
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
