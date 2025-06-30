from typing import Optional, Tuple, Dict, Literal


class FilterBuilder:
    def __init__(self, value: str, field_id: int, mode: Literal["a", "b", "c"]):
        self.value = value.strip().lower()
        self.field_id = field_id
        self.mode = mode

    def build(self) -> Tuple[Optional[str], str]:
        """
        Returns (FROM-clause or None, WHERE-clause string)
        """
        prefix = "vals" if self.mode == "a" else f"f{self.field_id}"
        col = "val"
        where = ""
        from_ = None

        if "%" in self.value:
            if self.value.startswith("%"):
                where = f"AND lower({prefix}.{col}) LIKE :filter_{self.field_id}"
            else:
                where = f"AND lower(left({prefix}.{col}, 127)) LIKE :filter_{self.field_id}"
        else:
            where = f"AND lower(left({prefix}.{col}, 127)) = :filter_{self.field_id}"

        if self.mode == "b":
            from_ = f"LEFT JOIN ru {prefix} ON {prefix}.up=vals.id AND {prefix}.t={self.field_id}"

        return from_, where

    def get_params(self) -> Dict[str, str]:
        return {f"filter_{self.field_id}": self.value}