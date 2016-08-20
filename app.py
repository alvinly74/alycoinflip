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

                if messaging_event.get("message"):  # someone sent us a message
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    response = "HAH GAYYYY"
                    
                    # does the 'flip' option
                    # to use, first number determines how many flips, all of the other items
                    # after will be the items we sample from
                    if message_text.startswith("flip"):
                        num_flips = int(message_text.split()[1:2][0])
                        possibilites = message_text.split()[2:-1]
                        response = "we flipped {0} number of coins and got: ".format(num_flips)
                        flips = []
                        for times in range(num_flips):
                            flips.append(random.choice(possibilites))
                        
                        response += ", ".join(flips)
                        
                    # does the bill split option
                    # to use, first number is how much to tip(in decimal form)
                    # second number is how much the tax total is, all numbers afterwards will add tip
                    if message_text.startswith("split"):
                        tip_percentage = float(message_text.split()[1:2][0])
                        tax_value = float(message_text.split()[2:3][0])
                        total = sum(costs)
                        costs = message_text.split()[3:-1]
                        costs = map(float, costs)
                        tax_percentages = map(lambda price: price/total)
                        grand_totals = []
                        for idx in range(len(costs)):
                            total = costs[idx] * (1 + tax_percentages[idx])
                            totals.append(append)
                        response = ", ".join(totals)
                    send_message(sender_id, response)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

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
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
