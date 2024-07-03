# xerparser
# udftype.py

from datetime import datetime
from enum import Enum
from typing import Any


class UDFTYPE:
    """
    A class to represent a User Defined Field.
    """

    class FieldType(Enum):
        """
        An enum class to represent the data type stored
        in a User Defined Field.
        """

        FT_END_DATE = "End Date"
        FT_FLOAT_2_DECIMALS = "Float"
        FT_INT = "Integer"
        FT_MONEY = "Cost"
        FT_START_DATE = "Start Date"
        FT_STATICTYPE = "Indicator"
        FT_TEXT = "Text"

    class Indicators(Enum):
        """
        An enum class to store the indicator icons that may be
        assigned to a UDF of type `FT_STATICTYPE` ("Indicator").
        """

        # Emoji's don't match perfectly with icons used by P6 but are close.
        UDF_G1 = "🛑"
        UDF_G2 = "⚠️"
        UDF_G3 = "✅"
        UDF_G4 = "⭐"

    def __init__(self, **data) -> None:
        self.uid: str = data["udf_type_id"]
        self.table: str = data["table_name"]
        self.label: str = data["udf_type_label"]
        self.udf_type_name: str = data["udf_type_name"]
        self.type: UDFTYPE.FieldType = UDFTYPE.FieldType[data["logical_data_type"]]

    @staticmethod
    def get_udf_value(udf_type: "UDFTYPE", **data: str) -> Any:
        if udf_type.type in (
            UDFTYPE.FieldType.FT_END_DATE,
            UDFTYPE.FieldType.FT_START_DATE,
        ):
            return datetime.strptime(data["udf_date"], "%Y-%m-%d %H:%M")

        if udf_type.type in (
            UDFTYPE.FieldType.FT_FLOAT_2_DECIMALS,
            UDFTYPE.FieldType.FT_MONEY,
        ):
            return float(data["udf_number"].replace(",", "."))

        if udf_type.type is UDFTYPE.FieldType.FT_INT:
            return int(data["udf_number"])

        if udf_type.type is UDFTYPE.FieldType.FT_STATICTYPE:
            return UDFTYPE.Indicators[data["udf_text"]].value

        return data["udf_text"]
