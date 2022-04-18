# Import Required Libraries
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Functionality Helper Functions


def parse_int(n):
    """
    Securely converts a non-integer value to integer.
    """
    try:
        return int(n)
    except ValueError:
        return float("nan")


def build_validation_result(is_valid, violated_slot, message_content):
    """
    Define a result message structured as Lex response.
    """
    if message_content is None:
        return {"isValid": is_valid, "violatedSlot": violated_slot}

    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }

    # Dialog Actions Helper Functions


def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response

# Intents Handlers


def recommendPortfolio(intent_request):
    """
    Performs dialog management and fulfillment for recommending a portfolio.
    """
    print("Calling recommend portfolio")

    # Get slots values
    first_name = get_slots(intent_request)["firstName"]
    age = get_slots(intent_request)["age"]
    investment_amount = get_slots(intent_request)["investmentAmount"]
    risk_level = get_slots(intent_request)["riskLevel"]
    source = intent_request["invocationSource"]

    if source == "DialogCodeHook":
        # This part of the code performs basic validation on the supplied input slots.

        # Get all slots
        slots = get_slots(intent_request)

    # Validation users input using the validate_data function
        validation_result = validate_data(
            first_name, age, investment_amount, risk_level)

        # if the data provided is not valid. the elicit dialog action is used to re-prompt for the first violation encountered.
        if not validation_result["isValid"]:
            slots[validation_result["violatedSlot"]
                  ] = None  # Cleans invalid slot
            return elicit_slot(
                intent_request["sessionAttributes"],
                intent_request["currentIntent"]["name"],
                slots,
                validation_result["violatedSlot"],
                validation_result["message"],
            )

        # Fetch current session attributes
        output_session_attributes = intent_request["sessionAttributes"]

        # Once all slots are valid, a delegate dialog is returned to Lex bot to prompt the next course of action.
        return delegate(output_session_attributes, get_slots(intent_request))

    # Return a message with convserion results
    return close(
        intent_request["sessionAttributes"],
        'Fulfilled',
        {
            "contentType": "PlainText",
            "content": f"Thank you for the previous information. This is the recommended portfolio allocation: {recommendation(risk_level)}"
        },
    )

# Data Validation


def validate_data(first_name, age, investment_amount, risk_level):
    """
    Validates the data provided by the user.
    """

    print(
        f"First Name: {first_name}, \n Age: {age}, \n Investment Amount: {investment_amount}, \n Risk Level: {risk_level}")

    if age is not None:
        if parse_int(age) <= 0 or parse_int(age) >= 65:
            return build_validation_result(False, "age", "Age should be between 0 and 65."
                                           )
    if investment_amount is not None:
        if parse_int(investment_amount) < 5000:
            return build_validation_result(False, "investmentAmount", "Investment amount should be greater than 5000."
                                           )
    if risk_level is not None:
        risk_level = risk_level.lower()

        if risk_level != "none" and risk_level != "low" and risk_level != "medium" and risk_level != "high":
            return build_validation_result(False, "riskLevel", "Risk level should be none, low, medium, or high."
                                           )
    return build_validation_result(True, None, None)

# Equities Allocation Recommendation


def recommendation(risk_level):
    """
    Function to return the recommended asset allocations
    """

    risk_level = risk_level.lower()

    if risk_level == "none":
        return "100% bonds (AGG), 0% equities (SPY)"
    elif risk_level == "low":
        return "60% bonds (AGG), 40% equities (SPY)"
    elif risk_level == "medium":
        return "40% bonds (AGG), 60% equities (SPY)"
    elif risk_level == "high":
        return "20% bonds (AGG), 80% equities (SPY)"
    else:
        return "Invalid Input Please enter either none, low, medium, or high"

# Intents Dispatcher


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot
    """
    print(f"Calling dispatch(intent_request = {intent_request})")
    intent_name = intent_request["currentIntent"]["name"]

    # dispatch to the bots intent handlers
    if intent_name == "recommendPortfolio":
        return recommendPortfolio(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")
# Main Handler


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    print(f"Calling lambda_handler(event = {event}, context = {context})")

    return dispatch(event)
