from pydantic import BaseModel
from enum import Enum



class Ticketbase(BaseModel):
  ticket_available: int


class TicketType(str, Enum):
    regular = "regular"  
    plus_one = "Plus 1"
    plus_two = "plus 2"
    plus_three = "plus 3"
    plus_four = "plus 4"


class Remind(str, Enum):
    none = "..."
    Two_weeks  = "Two_weeks"
    one_weeks = "one_week"
    Two_days = "Two_days"
    one_day = "one_day"