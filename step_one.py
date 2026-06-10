import re


class RegEx_line:
    
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
            print(result)
            return result


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




class Read_file(RegEx_line):
    drones_number : int =   0
    start_zone : str = ""
    end_zone : str = ""
    hub : list[str] = []
    connection : list[str] = []
    
    def __init__(self, file_name):
        self.file_name = file_name
        self.drones_number = int(Read_file.one_line(self.file_name, 'nb_drones').split(': ')[1])
        self.start_zone = Read_file.one_line(self.file_name, 'start_hub: ').split(': ')[1]
        self.end_zone = Read_file.one_line(self.file_name, 'end_hub: ').split(': ')[1]
        self.hub = Read_file.more_line(file_name, 'hub: ').split(': ')[1]
        self.connection = Read_file.more_line(file_name, 'connection: ').split(': ')[1]

    @classmethod
    def one_line(cls, file_name, string_line):
        text = ""
        try:
            with open(file_name, 'r') as file:        
                while not text.startswith(string_line): 
                    text = file.readline()
                    if not text:
                        text = ""
                        break
                    else:
                        text = text.rstrip("\n")
        except FileNotFoundError:
            print("File not found")
        except Exception as e:
            print(f"Error: {e}")    
        return text

    @classmethod
    def more_line(cls, file_name, string_line):
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

    def get_line(self):
        return [self.drones_number, self.start_zone,
                self.end_zone, self.hub,
                self.connection]
    
