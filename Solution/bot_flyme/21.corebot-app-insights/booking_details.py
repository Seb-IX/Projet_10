# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.


class BookingDetails:
    def __init__(
        self,
        destination: str = None,
        origin: str = None,
        budget: int = None,
        start_date: str = None,
        end_date: str = None,
        seat: str = None
    ):
        self.destination = destination
        self.origin = origin
        self.budget = budget
        self.start_date = start_date
        self.end_date = end_date
        self.seat = seat

    def get_details(self):
        return str({
            "destination":self.destination,
            "origin":self.origin,
            "from_date":self.start_date,
            "to_date:":self.end_date,
            "budget:":self.budget,
            "seat":self.seat
        })