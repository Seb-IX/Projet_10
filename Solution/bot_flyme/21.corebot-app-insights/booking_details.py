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
        n_adult : int = None,
        n_children : int = None,
        seat: str = None,
        unsupported_airports=None,
    ):
        if unsupported_airports is None:
            unsupported_airports = []
        self.destination = destination
        self.origin = origin
        self.budget = budget
        self.start_date = start_date
        self.end_date = end_date
        self.n_adult = n_adult
        self.n_children = n_children
        self.seat = seat
        self.unsupported_airports = unsupported_airports

    def get_details(self):
        return str({
            "destination":self.destination,
            "origin":self.origin,
            "from_date":self.start_date,
            "to_date:":self.end_date,
            "budget:":self.budget,
            "n_adult:":self.n_adult,
            "n_children:":self.n_children,
            "seat":self.seat
        })
