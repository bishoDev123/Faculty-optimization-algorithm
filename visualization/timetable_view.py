# 	Displays the generated weekly timetable
from core.models import Timetable, Problem
import pandas as pd


def timetable_to_dataframe(
    timetable: Timetable,
    problem: Problem
) -> pd.DataFrame:
    pass