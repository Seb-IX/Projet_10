
from luis_utility import LuisApp
from booking_details import BookingDetails

def predict_to_book_details(luis_recognizer : LuisApp, text: str, Intent):
    result = None
    intent = None
    try:
        prediction, intent = luis_recognizer.predict(text,get_intent=True)
        ## LuisApp => predict => result, intent
    
        if intent == Intent.BOOK_FLIGHT.value:
            result = BookingDetails()
            for k,v in prediction.items():
                if k == "dst_city":
                    result.destination = v
                elif k == "or_city":
                    result.origin = v
                elif k == "str_date":
                    if result.check_date(v):
                        result.start_date = v
                elif k == "end_date":
                    if result.check_date(v):
                        result.end_date = v
                elif k == "n_adult":
                    if result.check_n_adult_or_children(v):
                        result.n_adult = v
                elif k == "n_children":
                    if result.check_n_adult_or_children(v):
                        result.n_children = v
                elif k == "budget":
                    if result.check_budget(v):
                        result.budget = v
                elif k == "seat":
                    result.seat = v

    except Exception as exception:
        print(exception)

    return intent, result