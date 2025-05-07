import random 
import os

def initialiser_deck():
    # Fallback deck if no initializer is passed in
    valeurs = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    couleurs = ['S', 'H', 'D', 'C']
    return [v + c for v in valeurs for c in couleurs]
    
def tirer_cartes(deck, n):
    random.shuffle(deck)
    return [deck.pop() for _ in range(n)]

def charger_images_cartes():
    """
    Generate a mapping of card codes to their image file paths (relative to /static).
    """
    dossier = os.path.join("flask_app", "static", "cartes_images")
    images = {}
    for nom_fichier in os.listdir(dossier):
        if nom_fichier.endswith(".png"):
            code = nom_fichier[:-4]  # Remove ".png"
            images[code] = f"cartes_images/{nom_fichier}"
    return images

class PokerGame: 
    def __init__(self, deck_initializer=None, draw_function=None):
        """
        Initialize the game, allow for custom deck and draw functions.
        """
        # Use the passed deck_initializer function or fallback to the default
        self.phase = 0  # Start from phase 0
        self.round = 1  # Start from round 1
        self.max_rounds = 3
        self.deck_initializer = deck_initializer or initialiser_deck
        self.draw_function = draw_function
        self.full_deck = self.deck_initializer()  # Initialize deck on game start
        self.cartes = []  # Player's cards
        self.cartes_communes = []  # Community cards
        self.phase = 0  # Start at the Pre-flop phase
        self.mise_totale = 0
        self.dotation_initiale = 100
   
    def initialize_game(self):
        self.full_deck = self.deck_initializer()
        deck = self.full_deck.copy()

        if self.draw_function:
            self.cartes = self.draw_function(deck, 2)
        else:
            deck = random.sample(deck, len(deck))
            self.cartes = deck[:2]
            deck = deck[2:]

        self.cartes_communes = []
        self.phase = 0
    
    def reset_for_new_round(self):
        self.initialize_game()  # Reinitialize the deck and cards
        self.mise_totale = 0  # Reset the total bet amount

        if self.phase == 3:
            # If you're on the last phase (River), don't reset to Phase 0 (Pre-flop).
            # Let the phase continue from the last state.
            pass
        else:
            # Reset the phase only if you're not at Phase 3.
            self.phase = 0  # This will start the round at Pre-flop again.


    def draw_personal_cards(self):
        """Draw 2 personal cards for the player."""
        if self.draw_function:
            self.cartes = self.draw_function(self.full_deck, 2)
        else:
            self.cartes = random.sample(self.full_deck, 2)
            
    def next_phase(self):
        """Move to the next phase of the game."""
        if self.phase == 0:  # Move from Pre-flop to Flop
            # Draw 3 cards for the flop
            self.cartes_communes.extend(self.draw_function(self.full_deck, 3))
            self.phase += 1
        elif self.phase == 1:  # Move from Flop to Turn
            self.cartes_communes.extend(self.draw_function(self.full_deck, 1))
            self.phase += 1
        elif self.phase == 2:  # Move from Turn to River
            self.cartes_communes.extend(self.draw_function(self.full_deck, 1))
            self.phase += 1
        elif self.phase == 3:
            print("Already in Phase 3: The River has been dealt.")
        
    def get_phase_name(self):
        return ["Pre-flop", "Flop", "Turn", "River"][self.phase]

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