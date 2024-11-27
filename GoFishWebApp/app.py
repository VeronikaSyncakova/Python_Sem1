from flask import Flask, render_template, session, flash, request, redirect

import DBcm #databse

import cards
import random

app=Flask(__name__)

app.secret_key="dkajnfbghtomndkopmwnckfirh';;;sbdbdhfbfhflqo985#" # seeds the security key

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

@app.get("/")
def login():
    return render_template("login.html")

@app.get("/startgame")
def start():
    reset_state()
    card_images=[card.lower().replace(" ","_") + ".png" for card in session["player"]]
    return render_template(
        "startgame.html",
        title="Welcome to GoFish for web!",
        cards=card_images,   # available in template as {{ cards }}
        n_computer=len(session["computer"]),   #available in the template as {{ n_computer }}
        computerPairs=int(len(session["computer_pairs"])/2),
        playerPairs=int(len(session["player_pairs"])/2)
        )

@app.get("/register") # redirect to registration page
def register():
    return render_template("register.html")
#get user input for registration
@app.post("/input")
def process_the_registration():
    creds = {
    "host": "localhost",
    "user": "gofishuser",
    "password": "gofishpasswd",
    "database": "gofishdb",
    }
    name=request.form['fname']
    handle= request.form['fuser_name']

    SQL="select * from player where handle = (?)" #check if the handle is unique
    username=''
    with DBcm.UseDatabase(creds) as db:
        handleArr=[handle]
        db.execute(SQL,handleArr)
        username=db.fetchall()
        #flash(username)
    if len(username)>0: #username does exist ?
        flash("choose different username")
        return render_template("register.html")
    else:
        SQL="insert into player (name, handle) values (?, ?)"
        with DBcm.UseDatabase(creds) as db: #create user
            db.execute(SQL,(name, handle))
            #results = db.fetchall()
        session["handle"]= request.form['fuser_name']
        return redirect("/startgame")

#get user input log in
@app.post("/username")
def process_the_username():
    creds = {
    "host": "localhost",
    "user": "gofishuser",
    "password": "gofishpasswd",
    "database": "gofishdb",
    }
    handle=request.form['fuser_name']
    username=[]
    if len(handle)<=0:
        flash("Insert username!")
        return redirect("/")
    SQL="select * from player where handle= (?)"
    with DBcm.UseDatabase(creds) as db:
        handleArr=[handle]
        db.execute(SQL,handleArr)
        username=db.fetchall()
    if len(username)>0: #user exists ?
        session["handle"]= request.form['fuser_name']
        flash(f"Welcome {session["handle"]}")
        return redirect("/startgame")
    else: #doesnt exist
        flash("You are not registered! Register to play")
        return redirect("/")

@app.get("/select/<value>")
def process_card_selection(value):
    template="pickCard.html"
    animStyle='style: "animation-name: none;" '
    message=""
    message2=[]
    found_it = False
    for n, card in enumerate(session["computer"]):
        if card.lower().startswith(value):
            found_it = n
            break
    if isinstance(found_it, bool):
        #flash("Go Fish!")
        session["player"].append(session["deck"].pop())
        #flash(f"You drew a {session["player"][-1]}.")
        message+="GoFish!\nYou drew a "+str(session["player"][-1])+"."
        message2.append("Go Fish!")
        message2.append("You drew a "+str(session["player"][-1])+".")
        ## checkEnd()
        ## if len(session["deck"]) == 0:
        ##      break
    else:
        #flash(f"Here is your card from the computer: {session["computer"][n]}.")
        message+="Here is your card: "+str(session["computer"][n])+"."
        message2.append("Here is your card: "+str(session["computer"][n])+".")
        session["player"].append(session["computer"].pop(n))
        template="pickCardNewPair.html"
        
    session["player"], pairs = cards.identify_remove_pairs(session["player"])
    #flash("Player pairs: "+str(pairs))
    if len(pairs)>0:
        message+="\n You have a new pair!"
        message2.append("You have a new pair!")
        animStyle='style: "animation-name: pairsChange;" '
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
            template,
            title="The computer wants to know",
            value=the_value,
            cards=card_images,   # available in template as {{ cards }}
            action_message=message2,
            n_computer=len(session["computer"]),   #available in the template as {{ n_computer }}
            computerPairs=int(len(session["computer_pairs"])/2),
            playerPairs=int(len(session["player_pairs"])/2),
            style=animStyle
            )
    else:
        return checkEnd()


@app.get("/pick/<value>")
def process_picked_card(value):
    message=""
    if value == "0":
        session["computer"].append(session["deck"].pop())
    else:
        for n, card in enumerate(session["player"]):
                if card.startswith(value.title()):
                    break
        #flash(f"DEBUG: The picked card was at location {n}")
        session["computer"].append(session["player"].pop(n))
    
    session["computer"], pairs = cards.identify_remove_pairs(session["computer"])
    #flash("Computer pairs: "+str(pairs))
    if len(pairs)>0:
        message+="and a new pair!"
    session["computer_pairs"].extend(pairs)

    card_images=[card.lower().replace(" ","_") + ".png" for card in session["player"]]
    template="playerPick.html"
    if value=="0":
        template="computerFish.html"

    if (checkEnd() == False):
        return render_template(
            template,
            title="Keep playing!",
            cards=card_images,   # available in template as {{ cards }}
            n_computer=len(session["computer"]),   #available in the template as {{ n_computer }}
            computerPairs=int(len(session["computer_pairs"])/2),
            playerPairs=int(len(session["player_pairs"])/2),
            computer_massage=message
            )
    else:
        return checkEnd()
    
@app.get("/leaderboard")
def showLeaderboard():
    return render_template("leaderboard.html",
        table= getLeaderboard())

def saveScore(score, winner):
    creds = {
    "host": "localhost",
    "user": "gofishuser",
    "password": "gofishpasswd",
    "database": "gofishdb",
    }
    SQL="select id from player where handle = (?)" #check if the handle is unique
    id=''
    with DBcm.UseDatabase(creds) as db:
        handleArr=[winner]
        db.execute(SQL,handleArr)
        id=db.fetchall()
    if len(id)<=0:
        SQL="insert into player (name, handle) values (?, ?)"
        with DBcm.UseDatabase(creds) as db: #create user
            db.execute(SQL,(winner, winner))
            id[0][0]=winner
    SQL="insert into scores (score, player_id) values (?, ?)"
    with DBcm.UseDatabase(creds) as db: #create user
        #flash(id[0][0])
        db.execute(SQL,(score, id[0][0]))

def getLeaderboard():
    creds = {
    "host": "localhost",
    "user": "gofishuser",
    "password": "gofishpasswd",
    "database": "gofishdb",
    }

    SQL="select distinct p.name, p.handle, s.score, s.ts from player as p, scores as s where p.id=s.player_id order by s.score desc limit 10" #check if the handle is unique
    all=''
    with DBcm.UseDatabase(creds) as db:
        db.execute(SQL)
        all=db.fetchall()
    table=[]
    i=1
    for tup in all:
        entry=list(tup)
        entry[3]=entry[3].strftime("%b %d, %Y") #date in a format Month day, year
        entry.append(i)
        table.append(entry)
        i+=1
    #flash(table)
    return table

def checkEnd():
    card_images=[card.lower().replace(" ","_") + ".png" for card in session["player"]]
    computer_images=[card.lower().replace(" ","_") + ".png" for card in session["computer"]]
    if len(session["deck"]) == 0:
        #flash("No cards in the deck! Draw.")
        return render_template(
            "endgame.html",
            title="Game over",
            message="No cards in the deck! Draw.",     # {{ message }}
            messageP="You had",
            messageC="Computer had",
            computerPairs= int(len(session["computer_pairs"])/2),
            playerPairs=int(len(session["player_pairs"])/2),
            cards=card_images,
            computerCards=computer_images
        )
    if len(session["player"]) == 0:
        #flash("The Game is over. The player won.")
        score= len(session["player_pairs"])- round(len(session["computer_pairs"])/4)
        saveScore(score, session["handle"])
        return render_template(
            "endgame.html",
            title="Game over",
            message="Congrats! You won!",     # {{ message }}
            messageP="",     # {{ message }}
            messageC="Computer had",
            computerPairs= int(len(session["computer_pairs"])/2),
            playerPairs=int(len(session["player_pairs"])/2),
            cards=card_images,
            computerCards=computer_images,
        )
    if len(session["computer"]) == 0:
        #flash("The Game is over. The computer won.")
        score= len(session["computer_pairs"])- round(len(session["player_pairs"])/4)
        saveScore(score, "computer")
        return render_template(
            "endgame.html",
            title="Game over",
            message="Good game. The computer won!",     # {{ message }}
            messageP="You had",
            messageC="",     # {{ message }}
            computerPairs= int(len(session["computer_pairs"])/2),
            playerPairs=int(len(session["player_pairs"])/2),
            cards=card_images,
            computerCards=computer_images,
        )
    
    return False




app.run(debug=True)