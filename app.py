from math import ceil
import os
import sys
import json
import random
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

                if messaging_event.get("message"):  
                    # someone sent us a message
                    # the facebook ID of the person sending you the message
                    sender_id = messaging_event["sender"]["id"]
                    # the recipient's ID, which should be your
                    # page's facebook ID
                    recipient_id = messaging_event["recipient"]["id"]
                    # the message's text
                    message_text = messaging_event["message"]["text"]
                    try:
                        function, inputs = message_text.split(None, 1)
                    except ValueError:
                        function = "error"
                        continue
                    response = "Sorry, I do not recognize the input"
                    # does the 'flip' option
                    # to use, first number determines how many flips,
                    # all of the other items
                    # after will be the items we sample from
                    if function == "flip" and check_valid_flip(inputs):
                        num_flips, possibilities = inputs.split(None, 1)
                        possibilities = possibilities.split()
                        response = "I flipped {0} time(s), and got:\n".format(num_flips)
                        distribution = do_flips(num_flips, possibilities)
                        for option, count in distribution.iteritems():
                            response += "{0}: {1}\n".format(option, count)
                    # does the tip calculations
                    elif function == "tip" and check_valid_tip(inputs):
                        tip_values = do_tip(inputs)
                        response = "Here are some percentages for price [{0}]:\n".format(inputs)
                        for value in tip_values:
                            response += "{0}\n".format(value)
                    # does the bill split option how wird
                    # to use, first number is how much to tip in $XX.XX form
                    # second number is how much the tax.
                    elif function == "split" and check_valid_split(inputs):
                        inputs = inputs.split()
                        tip_value = inputs[0]
                        tax_value = inputs[1]
                        prices = inputs[2:]
                        log("tip = {0}, tax = {1} prices = {2}".format(tip_value, tax_value, prices))
                        prices = do_split(tip_value, tax_value, prices)
                        response = ""
                        for idx, price in enumerate(prices):
                            response += "person {0} owes: {1}\n".format(idx + 1, price)
                            
                        
                    
                    send_message(sender_id, response)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def check_valid_flip(inputs):
    # we need at least 3, number of sample, and at least two possibilities
    if len(inputs) > 2 and inputs[0].isdigit():
        return True

    return False


def do_flips(num_flips, possibilities):
    """
    takes number num_flips, and list of possibilities(list of strings)
    returns a hash of possibility => frequency
    """
    num_flips = int(num_flips)
    count_dict = {}
    for times in range(num_flips):
        flip_value = random.choice(possibilities)
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
        costs = float(inputs)
        if costs == float("nan"):
            raise ValueError
    except ValueError:
        return False
    else:
        return True


def do_tip(price):
    price = float(price)
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
    inputs = inputs.split()
    try:
        log("we got inputs {0}".format(inputs))
        log("type = {0}".format(type(inputs)))
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
    tip = float(tip)
    tax = float(tax)
    prices = map(float, prices)
    log("do_split type {0}".format(type(prices)))
    log("do_split price {0}".format(prices))
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


def valid_request(function):
    """
    checks if the text given by user is a valid input.
    At this time, we can only handle 'flip' 'tip', and 'split'
    """
    valid_inputs = ["flip", "tip", "split"]
    if function in valid_inputs:
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
