import os
import sys
import json

import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must
    # return the 'hub.challenge' value in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message
                                    # the facebook ID of the person sending you the message
                                    sender_id = messaging_event["sender"]["id"]
                                    # the recipient's ID, which should be your
                                    # page's facebook ID
                                    recipient_id = messaging_event["recipient"]["id"]
                                    # the message's text
                                    message_text = messaging_event["message"]["text"]
                                    request, inputs = message_text.split(None, 1)
                                    inputs = inputs.split()
                                    if not valid_request(inputs):
                                        response = "Sorry, we do not recognize the input"
                                    # does the 'flip' option
                                    # to use, first number determines how many flips,
                                    # all of the other items
                                    # after will be the items we sample from
                                    elif request == "flip" and check_valid_flip(inputs):
                                        response = "flipping"
                
                                    # does the tip calculations
                                    elif request == "tip" and chec_valid_tip(inputs):
                                        response = "tip"
                                    # does the bill split option how wird
                                    # to use, first number is how much to tip in $XX.XX form
                                    # second number is how much the tax.
                                    elif request == "split" and check_valid_split(inputs):
                                        response = "split"
                                    send_message(sender_id, response)

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    send_message(sender_id, "got it, thanks!")

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


# def send_message(recipient_id, message_text):
# 
#     log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))
# 
#     params = {
#         "access_token": os.environ["PAGE_ACCESS_TOKEN"]
#     }
#     headers = {
#         "Content-Type": "application/json"
#     }
#     data = json.dumps({
#         "recipient": {
#             "id": recipient_id
#         },
#         "message": {
#             "text": message_text
#         }
#     })
#     r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
#     if r.status_code != 200:
#         log(r.status_code)
#         log(r.text)
# 
# 
# def log(message):  # simple wrapper for logging to stdout on heroku
#     print str(message)
#     sys.stdout.flush()
# 
# 
# if __name__ == '__main__':
    # app.run(debug=True)

# import os
# import sys
# import json
# import random
# import requests
# from math import ceil
# from flask import Flask, request
# 
# app = Flask(__name__)
# 
# 
# @app.route('/', methods=['GET'])
# def verify():
#     # when the endpoint is registered as a webhook, it must
#     # return the 'hub.challenge' value in the query arguments
#     hub_mode = request.args.get("hub.mode")
#     if hub_mode == "subscribe" and request.args.get("hub.challenge"):
#         verify_token = request.args.get("hub.verify_token")
#         if not verify_token == os.environ["VERIFY_TOKEN"]:
#             return "Verification token mismatch", 403
#         return request.args["hub.challenge"], 200
# 
#     return "Hello world", 200
# 
# 
# @app.route('/', methods=['POST'])
# def webook():
# 
#     # endpoint for processing incoming messaging events
# 
#     data = requests.get_json()
#     # you may not want to log every incoming message in production,
#     # but it's good for testing
#     log(data)
# 
#     if data["object"] == "page":
#         for entry in data["entry"]:
#             for messaging_event in entry["messaging"]:
#                 log("what am I doing!?")
#                 # someone sent us a message
#                 if messaging_event.get("message"):
#                     # the facebook ID of the person sending you the message
#                     sender_id = messaging_event["sender"]["id"]
#                     # the recipient's ID, which should be your
#                     # page's facebook ID
#                     recipient_id = messaging_event["recipient"]["id"]
#                     # the message's text
#                     message_text = messaging_event["message"]["text"]
#                     request, inputs = message_text.split(None, 1)
#                     inputs = inputs.split()
#                     if not valid_request(inputs):
#                         response = "Sorry, we do not recognize the input"
#                     # does the 'flip' option
#                     # to use, first number determines how many flips,
#                     # all of the other items
#                     # after will be the items we sample from
#                     elif request == "flip" and check_valid_flip(inputs):
#                         response = "flipping"
# 
#                     # does the tip calculations
#                     elif request == "tip" and chec_valid_tip(inputs):
#                         response = "tip"
#                     # does the bill split option how wird
#                     # to use, first number is how much to tip in $XX.XX form
#                     # second number is how much the tax.
#                     elif request == "split" and check_valid_split(inputs):
#                         response = "split"
#                     send_message(sender_id, response)
#                 if messaging_event.get("delivery"):  # delivery confirmation
#                     pass
# 
#                 if messaging_event.get("optin"):  # optin confirmation
#                     pass
# 
#                 # user clicked/tapped "postback" button in earlier message
#                 if messaging_event.get("postback"):
#                     pass
# 
#     return "ok", 200
# 
# 
def check_valid_flip(inputs):
    # we need at least 3, number of sample, and at least two possibilities
    if len(inputs) > 3 and inputs[0].isdigit():
        return True

    return False


def do_flip(num_flips, possibilites):
    """
    takes number num_flips, and list of possibilities(list of strings)
    returns a hash of possibility => frequency
    """
    count_dict = {}
    for times in range(num_flips):
        flip_value = random.choice(possibilites)
        if count_dict.get(flip_value):
            count_dict[flip_value] += 1
        else:
            count_dict[flip_value] = 1

    return count_dict


def check_valid_tip(inputs):
    """
    inputs is a list, attempt to float all of inputs
    as long as contents is a number and not "NaN" or "not a number",
    this is good.
    """
    try:
        costs = map(float, inputs)
        if any(price == float("nan") for price in costs):
            raise ValueError
    except ValueError:
        return False
    else:
        return True


def do_tip(price):
    tip_amounts = []
    tip_percentages = [0.10, 0.15, 0.2, 0.25, 0.3]
    for percentage in tip_percentages:
        percent_string = str(percentage * 100) + "%"
        value = ceil(price * percentage * 100)/100
        res_string = "{0}: {1}".format(percent_string,
                                       value)
        tip_amounts.append(res_string)
    return tip_amounts


def check_valid_split(inputs):
    """
    tries to check if all inputs we have are valid numbers(floats)
    """
    try:
        numbers = map(float, inputs)
    # something in inputs isn't 'float' able
    except ValueError:
        return False
    else:
        return True


def do_split(tip, tax, prices):
    """
    takes floats tax and tip, and list of floats prices.
    returns an array of adjusted prices with proprotioned tax and tip added
    to each price.
    """
    total = sum(prices)
    portions = []
    for idx, price in enumerate(prices):
        portion = price/total
        price_portion = ceil(price * portion * 100) / 100
        tip_portion = ceil(tip * portion * 100) / 100
        tax_portion = ceil(tax * portion * 100) / 100
        grand_total = (price + tip_portion + tax_portion)
        portions.append(grand_total)
    return portions


def valid_request(inputs):
    """
    checks if the text given by user is a valid input.
    At this time, we can only handle 'flip' 'tip', and 'split'
    """
    valid_inputs = ["flip", "tip", "split"]
    if request in valid_inputs:
        return True
    return False


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id,
                                                        text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
