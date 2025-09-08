import numpy as np
import click
import logging
import coloredlogs
import os
from dotenv import load_dotenv
from random import shuffle

load_dotenv()
DEBUG = os.getenv("DEBUG") == "true"

logger = logging.getLogger("simple-blackjack")
coloredlogs.install(level="DEBUG" if DEBUG else "INFO", logger=logger)


def winner_print(gid, text, w_cards, l_cards, remaining, money):
    logger.debug(f"[ Game #{gid} ] {text} ({sum(w_cards)} vs. {sum(l_cards)}) | {w_cards} vs. {l_cards} Remaining cards: {remaining} | New balance: {money}")
    if not DEBUG and gid % 100 == 0:
        logger.info(f"[ Game #{gid} ] {text} ({sum(w_cards)} vs. {sum(l_cards)})")


def get_cards(n):
    #     A  2  3  4  5  6  7  8  9  10   J   Q   K
    l = [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10] * n
    shuffle(l)
    return l


def draw_card(deck):
    i = np.random.randint(0, len(deck))
    card_v = deck[i]
    del deck[i]
    return card_v, deck


def cards_init(deck):
    c_bank = []
    c_player = []
    v, new_deck = draw_card(deck)
    c_player.append(v)
    v, new_deck = draw_card(new_deck)
    c_bank.append(v)
    v, new_deck = draw_card(new_deck)
    c_player.append(v)
    v, new_deck = draw_card(new_deck)
    c_bank.append(v)
    return c_bank, c_player, new_deck


def get_value_adjusted_hand(cards, card):
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
        cards = get_cards(num_decks)
        player_won = bank_won = False

        # Deal initial cards for player and bank
        cards_bank, cards_player, cards = cards_init(cards)
        logger.debug("[ Start ] Bank: " + str(cards_bank) + " | Player: " + str(cards_player))
            
        # Deal until the player stands
        while sum(cards_player) < 12 or (sum(cards_player) < bank_min_score and cards_bank[0] > 6):
            new_card, cards = draw_card(cards)
            cards_player = get_value_adjusted_hand(cards_player, new_card)
            logger.debug("[ Card ] Player gets " + str(new_card) + " | Now: " + str(cards_player) + " (" + str(sum(cards_player)) + ")")

        # If the player didn't lose, deal cards for the bank
        if sum(cards_player) > 21:
            bank_won = True
        else:
            while sum(cards_bank) < bank_min_score:
                new_card, cards = draw_card(cards)
                cards_bank = get_value_adjusted_hand(cards_bank, new_card)
                logger.debug("[ Card ] Bank gets " + str(new_card) + " | Now: " + str(cards_bank) + " (" + str(sum(cards_bank)) + ")")
            if sum(cards_bank) > 21:
                player_won = True
            elif sum(cards_bank) > sum(cards_player):
                bank_won = True
            elif sum(cards_player) > sum(cards_bank):
                player_won = True
            elif sum(cards_player) == 21 and sum(cards_bank) == 21:
                if len(cards_player) == 2 or len(cards_bank) == 2:  # Handle BJ vs 21 corner case
                    player_won = len(cards_player) < len(cards_bank)
                    bank_won = len(cards_bank) < len(cards_player)

        if player_won:
            player_wins += 1
            if sum(cards_player) == 21 and len(cards_player) == 2:
                money += bet * 1.5
                winner_print(game_id, 'Player blackjack', cards_player, cards_bank, cards, money)
            else:
                money += bet
                winner_print(game_id, 'Player won', cards_player, cards_bank, cards, money)
        elif bank_won:
            bank_wins += 1
            money -= bet
            winner_print(game_id, 'Bank won', cards_bank, cards_player, cards, money)
        else:
            draws += 1
            winner_print(game_id, 'Draw', cards_bank, cards_player, cards, money)
    logger.info(f"[ Winrate summary ] {player_wins * 100.0 / game_id}% WIN | {bank_wins * 100.0 / game_id}% LOSE | {draws * 100.0 / game_id}% DRAW | Played {game_id} games.")
    logger.info(f"[ Balance summary ] Credit: {credit} | Bet: {initial_bet} | Profit/Losses:  {["", "+"][money > credit]}{money-credit}")


if __name__ == "__main__":
    main()
