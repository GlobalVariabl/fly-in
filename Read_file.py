from typing import Optional


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
        Read_file.s_zone = Read_file.valid_special_zone(
            list_lines, "start_hub"
        )
        Read_file.e_zone = Read_file.valid_special_zone(
            list_lines, "end_hub"
        )
        Read_file.hub = Read_file.valid_more_lines(list_lines, "hub")
        Read_file.connection = Read_file.valid_more_lines(
            list_lines, "connection"
        )

    @staticmethod
    def valid_line_dron(list_lines: list[str]) -> str:
        """
        Validates that nb_drones appears exactly once on the first
        non-comment line. Returns the line index where it was found.
        """
        first_non_comment_line_index: Optional[int] = None
        line_dron: Optional[int] = None
        repet_dron: int = 0
        for idx, line in enumerate(list_lines):
            stripped: str = line.strip()
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
        if line_dron is None:
            raise ValueError(f"{line_dron} was not found in file")
        if repet_dron >= 2:
            raise ValueError(
                f"nb_drones was repet {repet_dron} time,"
                f" last at line {line_dron + 1}"
            )
        if first_non_comment_line_index != line_dron:
            raise ValueError(
                f"nb_drones must be on the first non-comment line."
                f"Found at line {line_dron + 1}, but first non-comment"
                f" line is {first_non_comment_line_index + 1}"
            )
        """handl # """
        raw_line: str = list_lines[line_dron].rstrip("\n")
        if "#" in raw_line:
            line_whith_comm: str = raw_line[raw_line.index("#"):]
            line_whith_no_comm: str = raw_line.replace(line_whith_comm, "")
        else:
            line_whith_no_comm = raw_line
        return line_whith_no_comm

    @staticmethod
    def valid_special_zone(
        list_lines: list[str], special_zone: str
    ) -> list[str | int]:
        """
        Validates that start_hub appears exactly once.
        Returns the line index where it was found.
        """
        repet_time: int = 0
        line_idx: Optional[int] = None

        for idx, line in enumerate(list_lines):
            stripped: str = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith(special_zone):
                repet_time += 1
                line_idx = idx

        if repet_time == 0:
            raise ValueError(f"{special_zone} was not found in file")
        if line_idx is None:
            raise ValueError(f"{special_zone} was not found in file")
        if repet_time != 1:
            raise ValueError(
                f"{special_zone} was repet {repet_time} time,"
                f" last at line {line_idx + 1}"
            )

        """handl # """
        raw_line: str = list_lines[line_idx].rstrip("\n")
        if "#" in raw_line:
            line_whith_comm: str = raw_line[raw_line.index("#"):]
            line_whith_no_comm: str = raw_line.replace(line_whith_comm, "")
        else:
            line_whith_no_comm = raw_line

        return [line_whith_no_comm, line_idx]

    @staticmethod
    def valid_more_lines(
        list_lines: list[str], line_word: str
    ) -> list[list[str | int]]:
        """
        Validates that at least one line starts with line_word
        (ignoring comments/empties).
        Returns list of matching lines.
        """
        repet_time: int = 0
        lists_word: list[list[str | int]] = []
        for idx, line in enumerate(list_lines):
            stripped: str = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith(line_word):
                """handl #"""
                raw_line: str = line.rstrip("\n")
                if "#" in raw_line:
                    line_whith_comm: str = raw_line[raw_line.index("#"):]
                    line_whith_no_comm: str = raw_line.replace(
                        line_whith_comm, ""
                    )
                else:
                    line_whith_no_comm = raw_line
                lists_word.append([line_whith_no_comm, idx])
                repet_time += 1
        if repet_time == 0 and line_word != "hub:":
            raise ValueError(f"No '{line_word}' found in file")

        return lists_word

    @staticmethod
    def valid_garbage_line(list_lines: list[str]) -> None:
        """
        Validates that every non-comment, non-empty line starts with a
        valid keyword.
        Valid keywords: nb_drones, start_hub, end_hub, hub, connection
        """
        valid_keywords: set[str] = {
            "nb_drones", "start_hub", "end_hub", "hub", "connection"
        }
        for idx, line in enumerate(list_lines):
            stripped: str = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            if ":" not in stripped:
                raise ValueError(
                    f"Line {idx + 1}: Missing colon ':'."
                    f" Expected format 'keyword: value'"
                )
            parts: list[str] = stripped.split(":")
            keyword: str = parts[0].strip() if parts else ""
            if keyword not in valid_keywords:
                raise ValueError(
                    f"The keyword: {keyword} is Invalid keyword"
                    f" for this file, Line {idx + 1}"
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
