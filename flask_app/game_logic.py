import random 
import os

class PokerGame:
    def __init__(self):
        self.full_deck = [
            "2S", "2H", "2D", "2C",
            "3S", "3H", "3D", "3C",
            "4S", "4H", "4D", "4C",
            "5S", "5H", "5D", "5C",
            "6S", "6H", "6D", "6C",
            "7S", "7H", "7D", "7C",
            "8S", "8H", "8D", "8C",
            "9S", "9H", "9D", "9C",
            "10S", "10H", "10D", "10C",
            "JS", "JH", "JD", "JC",
            "QS", "QH", "QD", "QC",
            "KS", "KH", "KD", "KC",
            "AS", "AH", "AD", "AC"
        ]
        self.cartes = []  # Player's cards
        self.cartes_communes = []  # Community cards
        self.phase = 0  # Start at the Pre-flop phase (as an integer)
        self.mise_totale = 0
        self.dotation_initiale = 100

    def initialize_game(self):
        """Shuffle the deck and deal initial cards."""
        shuffled_deck = random.sample(self.full_deck, len(self.full_deck))
        self.cartes = shuffled_deck[:2]  # First 2 cards for the player
        self.cartes_communes = shuffled_deck[2:7]  # Next 5 cards as community cards
        self.phase = 0  # Start at the Pre-flop phase

    def next_phase(self):
        """Move to the next phase of the game."""
        if self.phase < 3:  # River is the last phase (phase 3)
            self.phase += 1

    def get_phase_name(self):
        """Return the name of the current phase."""
        phase_names = ["Pre-flop", "Flop", "Turn", "River"]
        return phase_names[self.phase]

    def get_community_cards(self):
        """Return the community cards based on the current phase."""
        if self.phase == 0:  # Pre-flop
            return []  # No community cards in Pre-flop
        elif self.phase == 1:  # Flop
            return self.cartes_communes[:3]  # First 3 community cards
        elif self.phase == 2:  # Turn
            return self.cartes_communes[:4]  # First 4 community cards
        elif self.phase == 3:  # River
            return self.cartes_communes[:5]  # All 5 community cards
        return []  # Default case if phase is invalid
    
    def calculate_chances(self):
        """Simulate winning chances based on the current phase."""
        if self.phase == 0:  # Pre-flop
            return 15  # Example chance percentage
        elif self.phase == 1:  # Flop
            return 30
        elif self.phase == 2:  # Turn
            return 45
        elif self.phase == 3:  # River
            return 60
        return 0  # Default case if phase is invalid