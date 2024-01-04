import numpy as np
from random import shuffle
import click

DEBUG = True

def debugPrint(msg):
    if DEBUG:
        print(msg)

def winnerPrint(gid, text, w_cards, l_cards, remaining, money):
    debugPrint("[ Game #" + str(gid) + " ] " + text + " (" + str(sum(w_cards)) + " vs. " + str(sum(l_cards)) + ") | " + str(w_cards) + " vs. " + str(l_cards) + " | Remaining cards: " + str(remaining) + " | New balance: " + str(money))
    if not DEBUG and gid % 100 == 0:
        print("[ Game #" + str(gid) + " ] " + text + " (" + str(sum(w_cards)) + " vs. " + str(sum(l_cards)) + ")")

def getCards(n):
    #     A  2  3  4  5  6  7  8  9  10   J   Q   K
    l = [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10] * n
    shuffle(l)
    return l

def drawCard(deck):
    i = np.random.randint(0, len(deck))
    card_v = deck[i]
    del deck[i]
    return card_v, deck

def cardsInit(deck):
    c_bank = []
    c_player = []
    v, new_deck = drawCard(deck)
    c_player.append(v)
    v, new_deck = drawCard(new_deck)
    c_bank.append(v)
    v, new_deck = drawCard(new_deck)
    c_player.append(v)
    v, new_deck = drawCard(new_deck)
    c_bank.append(v)
    return c_bank, c_player, new_deck

def getValueAdjustedHand(cards, card):
    cards.append(card)
    if sum(cards) > 21:
        for idx, v in enumerate(cards):
            if cards[idx] == 11:
                cards[idx] = 1
                break
    return cards

@click.command()
@click.argument("num_games", default=1000000)
@click.argument("num_decks", default=4)
@click.argument("credit", default=10000)
@click.argument("initial_bet", default=50)
def main(num_games, num_decks, credit, initial_bet):
    bank_min_score = 17
    game_id = player_wins = bank_wins = draws = 0
    bet = initial_bet
    money = credit
    while game_id < num_games and money >= bet:
        game_id += 1
        cards = getCards(num_decks)
        player_won = bank_won = False

        # Deal initial cards for player and bank
        cards_bank, cards_player, cards = cardsInit(cards)
        debugPrint("[ Start ] Bank: " + str(cards_bank) + " | Player: " + str(cards_player))
            
        # Deal until the player stands
        while sum(cards_player) < 12 or (sum(cards_player) < bank_min_score and cards_bank[0] > 6):
            new_card, cards = drawCard(cards)
            cards_player = getValueAdjustedHand(cards_player, new_card)
            debugPrint("[ Card ] Player gets " + str(new_card) + " | Now: " + str(cards_player) + " (" + str(sum(cards_player)) + ")")

        # If the player didn't lose, deal cards for the bank
        if sum(cards_player) > 21:
            bank_won = True
        else:
            while sum(cards_bank) < bank_min_score:
                new_card, cards = drawCard(cards)
                cards_bank = getValueAdjustedHand(cards_bank, new_card)
                debugPrint("[ Card ] Bank gets " + str(new_card) + " | Now: " + str(cards_bank) + " (" + str(sum(cards_bank)) + ")")
            if sum(cards_bank) > 21:
                player_won = True
            elif sum(cards_bank) > sum(cards_player):
                bank_won = True
            elif sum(cards_player) > sum(cards_bank):
                player_won = True

        if player_won:
            player_wins += 1
            if sum(cards_player) == 21 and len(cards_player) == 2:
                money += bet * 1.5
                winnerPrint(game_id, 'Player blackjack', cards_player, cards_bank, cards, money)
            else:
                money += bet
                winnerPrint(game_id, 'Player won', cards_player, cards_bank, cards, money)
        elif bank_won:
            bank_wins += 1
            money -= bet
            winnerPrint(game_id, 'Bank won', cards_bank, cards_player, cards, money)
        else:
            draws += 1
            winnerPrint(game_id, 'Draw', cards_bank, cards_player, cards, money)
    print("[ Winrate summary ] " + str(float(player_wins * 100.0 / game_id)) + "% WIN | " + str(float(bank_wins * 100.0 / game_id)) + "% LOSE | " + str(float(draws * 100.0 / game_id)) + "% DRAW | Played " + str(game_id) + " games.")
    print("[ Balance summary ] Credit: " + str(credit) + " | Bet: " + str(initial_bet) + " | Profit/Losses: " + ["", "+"][money-credit > 0] + str(money-credit))

if __name__ == "__main__":
    main()
