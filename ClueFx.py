#!/usr/bin/env python3
"""
Detectives today started sifting the evidences at the Tudor Hall, home of the late Dr.Black who was found
murdered last Thursday evening. A number of suspects - guests of Dr.Black - are being questioned. A collection of items
said to be the possible murder weapons have been found too.

The idea of Cluedo is to move from room to room to eliminate people, places, and weapons.
The player who correctly accuses Who, What, and Where wins.
Note: You can only enter in a room when your points are 8 or more than 8.
Author: Kartikay Chiranjeev Gupta
Last Date of modification: 20/6/2021
"""

import socket
import re
import random
import sys
import time
import itertools

from torch import true_divide

players = []
nicknames = []
secret_deck = {}
npc_cards = {}
valid_name_pattern = r'[A-Za-z0-9-_\ ]*'
game_art1 = '''
==================================================================
Welcome to the classic detective game: 
==================================================================
'''
game_art2 = '''
                                                                                            
    ,o888888o.    8 8888      8 8888      88 8 8888888888   8 8888888888 `8.`8888.      ,8' 
   8888     `88.  8 8888      8 8888      88 8 8888         8 8888        `8.`8888.    ,8'  
,8 8888       `8. 8 8888      8 8888      88 8 8888         8 8888         `8.`8888.  ,8'   
88 8888           8 8888      8 8888      88 8 8888         8 8888          `8.`8888.,8'    
88 8888           8 8888      8 8888      88 8 888888888888 8 888888888888   `8.`88888'     
88 8888           8 8888      8 8888      88 8 8888         8 8888           .88.`8888.     
88 8888           8 8888      8 8888      88 8 8888         8 8888          .8'`8.`8888.    
`8 8888       .8' 8 8888      ` 8888     ,8P 8 8888         8 8888         .8'  `8.`8888.   
   8888     ,88'  8 8888        8888   ,d8P  8 8888         8 8888        .8'    `8.`8888.  
    `8888888P'    8 888888888888 `Y88888P'   8 888888888888 8 8888       .8'      `8.`8888. 
 '''
game_art3 = '''
==================================================================
Let the investigation begin...
==================================================================
'''
player_table = """
===========================
||.......Players.........||
||  1.) Prince Azul      ||
||  2.) Lady Lavender    ||
||  3.) Lord Gray        ||
||  4.) Miss Peach       ||
===========================
"""
option_table = """  
===================================================
||........Suspects........||......Weapons........||
||  1.) Colonel Mustard   ||  1.) Horse Shoe     ||
||  2.) Professor Plum    ||  2.) Hammer         ||
||  3.) Mr. Green         ||  3.) Garden Shears  ||
||  4.) Mrs. Peacock      ||  4.) Water Bucket   ||
||  5.) Miss Scarlett     ||  5.) Tennis Racquet ||
||  6.) Mrs. White        ||  6.) Lawn Gnome     ||
||  7.) Rusty             ||                     ||
||  8.) Mrs. Meadow-Brook ||                     ||
===================================================
"""
room_table = """  
========================
||........Rooms.......||
||  1.) Tudor Mansion ||
||  2.) Boat House    ||
||  3.) Gazebo        ||
||  4.) Swimming Pool ||
||  5.) Stable        ||
||  6.) Gate House    ||
||  7.) Garden        ||
||  8.) Tennis Courts ||
||  9.) Garage        ||
========================
"""
suggestion = '''
--------------
| Killer: {} |
| Weapon: {} |
| Place : {} |
-------------- 
'''
cards = [["Colonel Mustard", "Professor Plum", "Mr. Green", "Mrs. Peacock", "Mrs. White", "Miss Scarlett", "Rusty", "Mrs. Meadow-Brook"],
         ["Horse Shoe", "Hammer", "Garden Shears", "Water Bucket", "Tennis Racquet", "Lawn Gnome"],
          ["Tudor Mansion", "Boat House", "Gazebo", "Swimming Pool", "Stable","Gate House","Garden", "Tennis Courts", "Garage"]]
suspects = {1: "Colonel Mustard", 2: "Professor Plum", 3: "Mr. Green", 4: "Mrs. Peacock", 5: "Miss Scarlett",
            6: "Mrs. White", 7:"Rusty", 8:"Mrs. Meadow-Brook"}
weapon = {1: "Horse Shoe", 2: "Hammer", 3: "Garden Shears", 4: "Water Bucket", 5: "Tennis Racquet", 6: "Lawn Gnome"}
rooms = {1: "Tudor Mansion", 2: "Boat House", 3: "Gazebo", 4: "Swimming Pool", 5: "Stable", 6: "Gate House", 7:"Garden", 8:"Tennis Courts", 9:"Garage"}
room_path = [1, 7, 2, 8, 9, 3, 5, 6, 4]
npcs = {}

NUM_CARDS = len(suspects) + len(weapon) + len(rooms)

class NPC:
    def __init__(self, name):
        self.name = name
        self.hidden = False
        if random.randint(1,100) <= 25:
            self.hide()

    def set_card(self, card):
        self.card = card

    def show_card(self):
        return self.card

    def hide(self):
        self.hidden = True

    def find(self):
        self.hidden = False

    def location(self):
        return self.room_no

    def move_to(self, room_no):
        self.room_no = room_no

    def __str__(self):
        if self.hidden:
            status = 'hidden'
        else:
            status = 'located'
        return f"{self.name} is {status} in the {rooms[self.room_no]} and holds {self.card}"
    
class Player:
    def __init__(self, conn):
        self.room_no = 1 # All players tart at Tudor Mansion
        self.cards = []
        self.connection = conn
        self.name = None
    
    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_connection(self, conn):
        self.connection = conn

    def send_message(self, message):
        self.connection.send(message.encode("utf-8"))

    def recv_message(self):
        msg = self.connection.recv(1024).decode("utf-8")
        return msg

    def move_to(self, room_no):
        self.room_no = room_no
        # TODO: Check what NPCs are present

    def location(self):
        return self.room_no

    def add_card(self, card):
        self.cards.append(card)

    def get_cards(self):
        return self.cards

    def __str__(self):
        return f"{self.name} currently in {rooms[self.room_no]} holding {self.cards}"


print("________________Setting up the Game Server__________________")
server_type = input("Choose the type of server...\n1.)Offline Server\n2.)Online Server\n")
if server_type == "1":
    server_type = "127.0.0.1"  # .................................................................Local host IP address.
elif server_type == "2":
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.connect(("8.8.8.8", 80))  # ..................................Using Google DNS -To get your IPV4 Address.
        server_type = server.getsockname()[0]
        print(f"Players can connect using: {server_type} address.")
        server.close()
    except Exception as online_error:
        print(f"{online_error}: Check your internet connection.")
        sys.exit(1)
else:
    print("Invalid option !")
    sys.exit(1)

n_players = int(input("Enter the number of players (2-6)\n(Least 3 players are recommended)\n"))
if type(n_players) == int and 6 >= n_players >= 2:
    print("Waiting for players to join....")
else:
    print("Invalid character entered.")
    sys.exit(1)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((server_type, 55555))
server.listen(n_players)


def send_all(message, ex_id=""):
    """ Sends message to all players in the game. """
    for player in players:
        if player == ex_id:
            continue
        player.send_message(message)

def shuffle_cards(t_cards):
    """ Shuffle cards and distribute among players.
    Returns two dictionaries: 1.) nickname-their cards 2.) Murder Envelope cards. """
    # TODO: Rebalance this to allow 2-6? players - if off by a card or two
    # have some NPCs not hold a card and just "not know anything"
    x = 0
    y = int((NUM_CARDS - len(suspects) - 3) / len(players))
    count = y
    excess_cards = (NUM_CARDS - len(suspects)) % len(players)
    temp_decs = []
    p_cards = []

    # Start by shuffling each grouping and picking a card for the Murder Envelope
    params = ["Killer", "Weapon", "Place"]  # Keys to access Murder Envelope cards.
    for i in range(0, 3):
        random.shuffle(t_cards[i])
        secret_deck.update({params[i]: t_cards[i][i]})

    # Remove Murder Envelope cards from the decks, and add to one big deck
    for i in range(0, 3):
        t_cards[i].remove(secret_deck[params[i]])
        p_cards.extend(t_cards[i])
    random.shuffle(p_cards)

    # Put a card in each NPC's hands and place them around the locations
    for i in range(1, len(suspects) + 1):
        npc = NPC(suspects[i])
        npc.set_card(p_cards.pop())
        npc_location = random.randint(1,len(rooms))
        npc.move_to(npc_location)
        npcs[suspects[i]] = npc
        print(npc)

    # Dole out cards to players
    decks = {}
    for i in range(0, len(players)):
        plr = players[i]
        for j in range(x, count):
            plr.add_card(p_cards[j])
        decks.update({plr.get_name(): plr.get_cards()})
        x = count
        count += y

    print(decks, "\n", secret_deck)
    return decks, secret_deck

def get_player_name(player):
    player.send_message("Please choose a nickname: ")
    nickname = player.recv_message()
    while True:
        if re.fullmatch(valid_name_pattern, nickname):
            break
        else:
            player.send_message('Invalid character used !')
            player.send_message("Choose a valid nickname: ")
            nickname = player.recv_message()
    while nickname in nicknames:
        player.send_message("This name is not available!\nPlease choose another nickname: ")
        nickname = player.recv_message()
    nicknames.append(nickname)
    player.set_name(nickname)

def accept_requests():
    """Accepts new connection until selected number of people join."""
    global players, players_deck, secret_deck
    while len(players) < n_players:
        send_all("Waiting for other players to join...")
        conn, address = server.accept()
        player = Player(conn)
        players.append(player)
        player.send_message("Hey there!\n")
        get_player_name(player)
        send_all(f"{player.get_name()} has joined the Game.\n")
    players_deck, secret_deck = shuffle_cards(cards)
    time.sleep(2)
    send_all("\nShuffling Cards...")
    time.sleep(2)
    send_all("...")
    time.sleep(2)
    send_all("...")
    time.sleep(2)
    send_all(game_art1)
    time.sleep(2)
    send_all(game_art2)
    time.sleep(2)
    send_all(game_art3)
    time.sleep(2)
    nicknames.sort()
    main_game()
    return None

def cluefx_turn(player):
    # Character moves
    temp_win = True
    player.send_message(room_table)
    player.send_message("\nChoose a location to move to: ")
    room_no = 0
    while room_no > len(rooms) or room_no < 1 or type(room_no) != int:  #check if entered option is valid.
        try:
            room_no = int(player.recv_message())
        except Exception as e:
            player.send_message("Invalid room selected!\n")
            print(f"Invalid Character Entered by user: {e}")
            room_no = 0

    # Search or make accusation
    player.send_message("\n(S)earch or make (A)ccusation")
    time.sleep(0.5)

    choice = ''
    while choice not in ['S','s','A','a']:
        try:
            choice = player.recv_message()
            if choice not in ['S','s','A','a']:
                print(f"Invalid choice, please enter S or A")
                player.send_message("Invalid choice")
                choice = ''
        except Exception as e:
            print(f"Invalid choice, please enter S or A")
            player.send_message("Invalid choice")
            choice = ''

    if choice in ['A', 'a']:
        player.send_message("\nChoose Suspect and Weapon. (separated by space)")
        time.sleep(0.5)
        player.send_message(option_table)
        sus_wea = [0, 0]
        while sus_wea[0] > len(suspects) or sus_wea[0] < 1 or type(sus_wea[0]) != int or len(sus_wea) != 2:
            # ..................................................................To check if entered option is valid.
            try:
                sus_wea = list(map(int, player.recv_message().split(" ")))
            except Exception as er:
                print(f"Invalid Character Entered: {er}")
                player.send_message("Invalid Character selected!")
                sus_wea = [0, 0]
        while sus_wea[1] > len(weapon) or sus_wea[1] < 1 or type(sus_wea[1]) != int or len(sus_wea) != 2:
            # ..................................................................To check if entered option is valid.
            try:
                sus_wea = list(map(int, player.recv_message().split(" ")))
            except Exception as er:
                print(f"Invalid Weapon Entered: {er}")
                player.send_message("Invalid Character selected!")
                sus_wea = [0, 0]
        send_all(f"\n{player.get_name()}'s suggestion:")
        send_all(suggestion.format((suspects[sus_wea[0]]), weapon[sus_wea[1]], rooms[room_no]))
        accused = [suspects[sus_wea[0]], weapon[sus_wea[1]], rooms[room_no]]
        time.sleep(2)
        for name in nicknames:
            for accuse in accused:
                if accuse in players_deck[name] and name != player.get_name():
                    send_all(f"{name} has disapproved {player.get_name()}'s suggestion.", player)
                    player.send_message(f"{name} has {accuse}.")
                    temp_win = False
                    break
            if not temp_win:
                break
        if temp_win:
            send_all(f"No proof against {player.get_name()}'s suggestion.")
    else:
        print(f"Do search in the {rooms[room_no]}")
    
    # (optional) make final guess
    player.send_message("Do you want to reveal cards ?(y/n)")
    choice_r = player.recv_message()
    if choice_r == 'y':
        if secret_deck["Killer"] == suspects[sus_wea[0]] and secret_deck["Weapon"] == weapon[sus_wea[1]] and \
            secret_deck["Place"] == rooms[room_no]:
            send_all(f"{player.get_name()} WON !")
            player.send_message(f"\nCongrats {player.get_name()} you have solved the case !")
            return True
        else:
            send_all(f"Wrong accusation !\n{player.get_name()} will no longer make accusations.")
            nicknames.remove(player.get_name())

    # Move NPCs
    print(f"Move the NPCs")
    for name in npcs:
        npc = npcs[name]
        current_room = npc.location()
        index = room_path.index(current_room)
        delta = random.choice([-1, 1])
        index += delta
        if index < 0:
            index = len(room_path) - 1
        elif index >= len(room_path):
            index = 0
        print(f"was in {current_room} ({index}) ")
        print(f"moving to {room_path[index]}")
        npc.move_to(room_path[index])
        if random.randint(1,100) <= 25:
            npc.hide()
        else:
            npc.find()
        print(npc)
        npcs[name] = npc

    return

def show_player_detail():
    """Display each player their cards and points."""
    for player in players:
        deck = players_deck[player.get_name()]
        player.send_message("\n=============================================\n")
        player.send_message(f"Your Cards: {deck}\n\n")


def main_game():
    """Passes player name to 'player_turn' function turn-by-turn until one player wins."""
    iter_players = itertools.cycle(players)
    player = next(iter_players)
    win = False
    while not win:
        time.sleep(1)
        show_player_detail()
        time.sleep(1)
        win = cluefx_turn(player)
        player = next(iter_players)
    send_all("\nThanks for playing.")

    for player in players:
        try:
            player.recv_message()
        except Exception as e:
            print(e)
    server.close()


accept_requests()
