import re
from typing import Optional

class RegEx_line:
    """Parse and validate drone simulation file lines."""

    def __init__(self, read_file_dict):
        """
        Initialize with parsed dictionary from Read_file.

        Args:
            read_file_dict: dict from Read_file containing
                            raw parsed lines
        """
        self.drones_number: int = read_file_dict['drones_number']
        self.start_zone: str = read_file_dict['start_zone']
        self.end_zone: str = read_file_dict['end_zone']
        self.hub: list[str] = read_file_dict['hub']
        self.connection: list[str] = read_file_dict['connection']


        self.parsed_alls: list[dict] = []
        
        self.validit_all()

    def  validit_all(self):
        """
        Validate and parse all sections.
        Populates parsed_start, parsed_end,
        parsed_hubs, parsed_connections.

        Raises:
            ValueError: if any line is invalid
        """
        self.drones_number = RegEx_line.validit_drones(self.drones_number)
        self.start_zone[0] = RegEx_line.validit_hub_sd(self.start_zone[0].split(':')[1].strip(), True)
        self.end_zone[0] = RegEx_line.validit_hub_sd(self.end_zone[0].split(':')[1].strip(), True)
        for idx, line in enumerate(self.hub):
            self.hub[idx][0] = RegEx_line.validit_hub_sd(line[0].split(':')[1].strip(), False)
            self.parsed_alls.append(self.hub[idx])
        for idx, line in enumerate(self.connection):
            self.connection[idx][0] = RegEx_line.validate_connection(line[0].split(':')[1].strip())
            self.parsed_alls.append(self.connection[idx])
        self.parsed_alls.append(self.start_zone)
        self.parsed_alls.append(self.end_zone)

        


    
    @staticmethod
    def validit_drones(line: str)->str:
        """
        Parse and validate a hub/start_hub/end_hub line.
        Extracts name, coordinates, and metadata.
        """
        drones = None
        patten = re.match(r"^nb_drones\s*:\s*(\d+)\s*$", line)
        if not patten:
            raise ValueError(f"Invalid line nb_drones : {line}")
        drones = int(patten.group(1))
        if drones < 1:
            raise ValueError("nb_drones must be greater than 0")
        return drones
    

    @staticmethod
    def validit_hub_sd(line: str, ist_special)->list:
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
        meta_pattern = re.compile(
            r"(zone|color|max_drones)=([^\s]+)"
        )
        valid_zones = {'normal', 'blocked', 'restricted', 'priority'}
        valid_keys = {'zone', 'color', 'max_drones'}
        defaults: dict = {
            "zone": "normal",
            "color": None,
            "max_drones": float('inf') if ist_special else 1
        }
        match = pattern.match(line.strip())
        if not match:
            raise ValueError(f"Invalid hub line format: '{line}'")
    
        data = match.groupdict()
        # validate name has no dash
        name = data['name']
        if '-' in name:
            raise ValueError(
                f"Zone name '{name}' cannot contain dashes. "
                f"Dashes are reserved for connection syntax"
            )
        # parse metadata if present
        metadata: dict[str] = data.get("metadata")
        if metadata is not None:
            metadata = metadata.strip()
            key_value_pattern = re.compile(r"(\w+)=([^\s\]]+)")
            for key, value in key_value_pattern.findall(metadata):
                if key not in valid_keys:
                    raise ValueError( f"Invalid metadata key '{key}' in line: '{line}'.")
            for key, value in meta_pattern.findall(metadata):
                if key == 'zone':
                    if value not in valid_zones:
                        raise ValueError(f"Invalid zone type '{value}' in line: '{line}'.")
                    defaults["zone"] = value
                if key == 'color':
                    defaults["color"] = value
                if key == 'max_drones':
                    if ist_special:
                        continue
                    if not value.isdigit() or int(value) <= 0:
                        raise ValueError(f"Invalid max_drones '{value}' in line: '{line}'. Must be positive integer")
                    defaults['max_drones'] = int(value)


        result = {
            "name": data["name"],
            "coordinate": ( int(data["x"]), int(data["y"]) ),
            "zone":       defaults['zone'],
            "color":      defaults['color'],
            "max_drones": defaults['max_drones']
        }
        return result 
    
    @staticmethod
    def validate_connection(line: str) ->dict:
        """
        Parse and validate a connection line.
        Extracts from_hub, to_hub, and max_link_capacity.
        """
        connection_pattern = re.compile(
            r"^(?P<from_hub>[^\s\-]+)" 
            r"-"  
            r"(?P<to_hub>[^\s\[\-]+)"  
            r"(?:\s*\[(?P<metadata>[^\]]*)\])?$" 
        )
        metadata_pattern = re.compile(
            r"max_link_capacity=(?P<capacity>\d+)$"
        )
        defaults = {
            "max_link_capacity": 1
        }
        # Match the connection pattern
        connections = connection_pattern.match(line.strip())
        if not connections:
            raise ValueError(f"Invalid connections line format: '{line}' Expected 'from-to [max_link_capacity=N]'")
        data = connections.groupdict()
        from_hub: str = data['from_hub']
        to_hub: str = data['to_hub']
        metadata = data.get("metadata")

        if not from_hub or not to_hub:
            raise ValueError(f"Empty zone name in connection: '{line}'")
        if from_hub == to_hub:
            raise ValueError(f"Zone cannot connect to itself: '{line}' !?")

        # Parse metadata if present
        if metadata is not None:
            metadata = metadata.strip()
            # Check for max_link_capacity values
            capacity_pattern = re.compile(r"max_link_capacity\s*=\s*(\d+)")
            matches = capacity_pattern.findall(metadata)
            if len(matches) > 1:
                raise ValueError(f"Duplicate max_link_capacity in: '{line}'. Found {len(matches)}")
            # Check for unknown keys
            key_pattern = re.compile(r"(\w+)=")
            keys = key_pattern.findall(metadata)
            for key in keys:
                if key != 'max_link_capacity':
                    raise ValueError(f"Invalid metadata key '{key}' in connection: '{line} Only 'max_link_capacity' is allowed ??")


            # Extract capacity if found
            if matches:
                capacity = int(matches[0])
                if capacity <= 0:
                    raise ValueError(f"max_link_capacity must be positive, got {capacity} in: '{line}'")
                defaults['max_link_capacity'] = int(capacity)
            
            else:
                # Metadata exists but no max_link_capacity
                raise ValueError(f"Invalid metadata format in: '{line}'. Expected 'max_link_capacity=N'")
        
             
        
        result = {
            "from": from_hub,
            "to": to_hub,
            "max_link_capacity": defaults['max_link_capacity']
        }
        return result

     

 
class Read_file():
    n_drones : str = ""
    s_zone : str = ""
    e_zone : str = ""
    hub : list[str] = []
    connection : list[str] = []

    def __init__(self, file_name):
        self.file_name = file_name
        self.read_lines()

    def read_lines(self):
        list_lines : list[str] = []

        try:
            with open(self.file_name, 'r') as file:
                list_lines = file.readlines()
            # print(list_lines)
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
        except FileNotFoundError:
            print("File not found")
        except Exception as e:
            print(f"Error:\n   {e}")
    
    @staticmethod
    def valid_line_dron(list_lines):
        """
        Validates that nb_drones appears exactly once on the first non-comment line.
        Returns the line index where it was found.
        """
        first_non_comment_line_index = None
        line_dron = None
        repet_dron = 0
        for idx, line in enumerate(list_lines):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
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
            raise ValueError ("nb_drones was no in file")
        if repet_dron >= 2:
            raise ValueError (
                f"nb_drones was repet {repet_dron} time, last at line {line_dron + 1}")
        if first_non_comment_line_index != line_dron:
            raise ValueError (
                f"nb_drones must be on the first non-comment line."
                f"Found at line {line_dron + 1}, but first non-comment line is {first_non_comment_line_index + 1}"
                            )
        
        return list_lines[line_dron].rstrip("\n")
    
    @staticmethod
    def valid_special_zone(list_lines, special_zone):
        """
        Validates that start_hub appears exactly once.
        Returns the line index where it was found.
        """
        repet_time = 0
        line_idx = None

        for idx ,line in enumerate(list_lines):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            if stripped.startswith(special_zone):
                repet_time += 1
                line_idx = idx

        if repet_time == 0:
            raise ValueError (f"{special_zone} was not found in file")
        if repet_time != 1:
            raise ValueError (f"{special_zone} was repet {repet_time} time, last at line {line_idx + 1}")
         
        return [list_lines[line_idx].rstrip("\n"), line_idx]
    
    @staticmethod
    def valid_more_lines(list_lines, line_word):
        """
        Validates that at least one line starts with line_word (ignoring comments/empties).
        Returns list of matching lines .
        """
        repet_time = 0
        lists_word = []
        for idx ,line in enumerate(list_lines):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith(line_word):
                lists_word.append([line.rstrip("\n"), idx])
                repet_time += 1
        if repet_time == 0 and line_word != 'hub:':
            raise ValueError (f"No '{line_word}' found in file")
        return lists_word
    
    @staticmethod
    def valid_garbage_line(list_lines):
        """
        Validates that every non-comment, non-empty line starts with a valid keyword.
        Valid keywords: nb_drones, start_hub, end_hub, hub, connection
        """
        valid_keywords = {'nb_drones', 'start_hub', 'end_hub', 'hub', 'connection'}
        minimal_line = 0
        for idx ,line in enumerate(list_lines):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            
            if ':' not in  stripped:
                raise ValueError(
                    f"Line {idx + 1}: Missing colon ':'. Expected format 'keyword: value'"
                )
            keyword = stripped.split(':')[0].strip() if stripped.split(":") else ""
            if keyword not in valid_keywords:
                raise ValueError(f"The keyword: {keyword} is Invalid keyword for this file, Line {idx + 1}")
            
            minimal_line += 1
        # if minimal_line < 5:
        #     raise ValueError(
        #             f"Incomplete map file ({minimal_line} data lines found you need all {valid_keywords})"
        #         )

    def get_data(self):
        """Return parsed data as a dictionary."""
        return {
            'drones_number': self.n_drones,
            'start_zone': self.s_zone,
            'end_zone': self.e_zone,
            'hub': self.hub,
            'connection': self.connection
        }

        
if __name__ == "__main__":
    try:
        reader = Read_file("01_dead_end_trap.txt")
        parser = RegEx_line(reader.get_data())
        # print(f"Drones:{reader.n_drones}\n")
        # print(f"Start zone: {reader.s_zone}\n")
        # print(f"End zone: {reader.e_zone}\n")
        # print(f"Hubs: {reader.hub}\n")
        # print(f"Connections: {reader.connection}\n")

        print(f"✓ Successfully parsed!")
        print(f"\n  Drones: {parser.drones_number}")
        print(f"\n  Start zone: {parser.start_zone}")
        print(f"\n  End zone: {parser.end_zone}")
        print(f"\n  Hubs: {parser.hub}")
        print(f"\n  Connections: {parser.connection}")
        print(f"\n  parsed_all: {parser.parsed_alls}")

    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")


