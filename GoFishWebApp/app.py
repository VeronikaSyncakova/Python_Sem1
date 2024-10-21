from flask import Flask, render_template, session, flash

import cards
import random

app=Flask(__name__)

app.secret_key="dkajnfbghtomndkopmwnckfirh';;;/sbdbdhfbfhf\lqo985#" # seeds the security key

#PATH="static/cards/"

def reset_state():

    session["deck"] = cards.build_deck()
    session["computer"] = []   #global variable
    session["player"] = []
    session["player_pairs"] = []
    session["computer_pairs"] = []


    for _ in range(7):
        session["computer"].append(session["deck"].pop())
        session["player"].append(session["deck"].pop())

    session["player"], pairs = cards.identify_remove_pairs(session["player"])
    session["player_pairs"].extend(pairs)
    session["computer"], pairs = cards.identify_remove_pairs(session["computer"])
    session["computer_pairs"].extend(pairs)


@app.get("/startgame")
def start():
    reset_state()
    card_images=[card.lower().replace(" ","_") + ".png" for card in session["player"]]
    return render_template(
        "startgame.html",
        title="Welcome to GoFish for web!",
        cards=card_images,   # available in template as {{ cards }}
        n_computer=len(session["computer"]),   #available in the template as {{ n_computer }}
        )

@app.get("/select/<value>")
def process_card_selection(value):
    found_it = False
    for n, card in enumerate(session["computer"]):
        if card.lower().startswith(value):
            found_it = n
            break
    if isinstance(found_it, bool):
        flash("Go Fish!")
        session["player"].append(session["deck"].pop())
        flash(f"You drew a {session["player"][-1]}.")
        ## checkEnd()
        ## if len(session["deck"]) == 0:
        ##      break
    else:
        flash(f"Here is your card from the computer: {session["computer"][n]}.")
        session["player"].append(session["computer"].pop(n))
        
    session["player"], pairs = cards.identify_remove_pairs(session["player"])
    session["player_pairs"].extend(pairs)

    ## What to do when the player or the computer has won?
    ## if len(player) == 0:
    ##    print("The Game is over. The player won.")
    ##    break
    ## if len(computer) == 0:
    ##    print("The Game is over. The computer won.")
    ##    break

    if (checkEnd() == False):
        card = random.choice(session["computer"])
        the_value = card[: card.find(" ")]

        card_images=[card.lower().replace(" ","_") + ".png" for card in session["player"]]

        return render_template(
            "pickCard.html",
            title="The computer wants to know",
            value=the_value,
            cards=card_images,   # available in template as {{ cards }}
            )
    else:
        return checkEnd()


@app.get("/pick/<value>")
def process_picked_card(value):
    if value == "0":
        session["computer"].append(session["deck"].pop())
    else:
        for n, card in enumerate(session["player"]):
                if card.startswith(value.title()):
                    break
        flash(f"DEBUG: The picked card was at location {n}")
        session["computer"].append(session["player"].pop(n))
    
    session["computer"], pairs = cards.identify_remove_pairs(session["computer"])
    session["computer_pairs"].extend(pairs)

    card_images=[card.lower().replace(" ","_") + ".png" for card in session["player"]]

    if (checkEnd() == False):
        return render_template(
            "startgame.html",
            title="Keep playing!",
            cards=card_images,   # available in template as {{ cards }}
            n_computer=len(session["computer"]),   #available in the template as {{ n_computer }}
            )
    else:
        return checkEnd()

def checkEnd():
    card_images=[card.lower().replace(" ","_") + ".png" for card in session["player"]]
    computer_images=[card.lower().replace(" ","_") + ".png" for card in session["computer"]]
    if len(session["deck"]) == 0:
        flash("No cards in the deck! Draw.")
        return render_template(
            "endgame.html",
            title="Game over",
            message="No cards in the deck! Draw.",     # {{ message }}
            messageP="You had",
            messageC="Computer had",
            computerPairs= len(session["computer_pairs"]),
            playerPairs=len(session["player_pairs"]),
            cards=card_images,
            computerCards=computer_images
        )
    if len(session["player"]) == 0:
        flash("The Game is over. The player won.")
        return render_template(
            "endgame.html",
            title="Game over",
            message="Congrats! You won!",     # {{ message }}
            messageP="",     # {{ message }}
            messageC="Computer had",
            computerPairs= len(session["computer_pairs"]),
            playerPairs=len(session["player_pairs"]),
            cards=card_images,
            computerCards=computer_images
        )
    if len(session["computer"]) == 0:
        flash("The Game is over. The computer won.")
        return render_template(
            "endgame.html",
            title="Game over",
            message="Good game. The computer won!",     # {{ message }}
            messageP="You had",
            messageC="",     # {{ message }}
            computerPairs= len(session["computer_pairs"]),
            playerPairs=len(session["player_pairs"]),
            cards=card_images,
            computerCards=computer_images
        )
    
    return False




app.run(debug=True)