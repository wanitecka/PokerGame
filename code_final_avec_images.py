import pygame
import csv
import random
import os

# Initialisation de Pygame
pygame.init()

# Constantes
WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
WHITE, BLACK, GREEN, RED, GRAY = (255, 255, 255), (0, 0, 0), (0, 200, 0), (200, 0, 0), (200, 200, 200)
FONT = pygame.font.SysFont("Baskerville", 36)

# Load and scale the background image
try:
    fond = pygame.image.load("fond_poker.png")  # Load the background image
    fond = pygame.transform.scale(fond, (WIDTH, HEIGHT))  # Resize the image to fit the screen
except pygame.error as e:
    print(f"Erreur de chargement de l'image : {e}")
    pygame.quit()
    exit()

# Setup écran
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Expérience Poker Économique")

# Variables globales
participant_info = {"prenom": "", "age": "", "niveau": "", "traitement": ""}
dotation_initiale = 100  # Fixed initial endowment
mise_depart = 0  # Blind amount, updated in attribuer_traitement()
mise_totale = 0  # Total amount bet by the player, starts with mise_depart
cartes = []  # Player's personal cards
cartes_communes = []  # Community cards
mise_suivie = 0  # Amount bet in the current round

# Fonctions utilitaires
def draw_text(text, x, y, color=WHITE, center=False):
    rendered = FONT.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(rendered, rect)

def save_decision(info, cartes, decision, montant=0):
    """
    Save the participant's decision to a CSV file.
    """
    with open("data/decisions.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            info["prenom"], info["age"], info["niveau"], info["traitement"], info["sexe"],
            cartes[0], cartes[1], decision, montant
        ])

def initialiser_deck():
    """
    Initialize a full deck of cards.
    """
    valeurs = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    couleurs = ['D', 'H', 'S', 'C']  # D = Diamond, H = Heart, S = Spade, C = Club
    return [v + c for v in valeurs for c in couleurs]

def tirer_cartes(deck, n):
    """
    Draw n unique cards from the shared deck.
    """
    return [deck.pop(random.randint(0, len(deck) - 1)) for _ in range(n)]

def charger_images_cartes():
    """
    Load card images from the cartes_images folder.
    """
    dossier = "cartes_images"  # Folder containing card images
    images = {}
    for nom_fichier in os.listdir(dossier):
        if nom_fichier.endswith(".png"):
            code = nom_fichier[:-4]  # Remove the ".png" extension
            chemin = os.path.join(dossier, nom_fichier)
            try:
                image = pygame.image.load(chemin)
                image = pygame.transform.scale(image, (100, 145))  # Resize the card images
                images[code] = image
            except pygame.error as e:
                print(f"Error loading image {chemin}: {e}")
    return images

def on_mouse_down(pos):
    global guessed_word, attempts
    for button in buttons:
        if button["rect"].collidepoint(pos):
            letter = button["letter"]
            if letter in word:
                guessed_word = ''.join(
                    letter if word[i] == letter else guessed_word[i]
                    for i in range(len(word))
                )
            else:
                attempts -= 1
            button["clicked"] = True
            turn()  # 👈 This forces an update after the click
            break

def afficher_cartes_communes(images_cartes, phase, y_coordinate):
    """
    Display community cards based on the current phase, aligned in a second row.
    """
    num_cards_to_display = 0
    if phase == 1:  # Flop
        num_cards_to_display = 3
    elif phase == 2:  # Turn
        num_cards_to_display = 4
    elif phase == 3:  # River
        num_cards_to_display = 5

    # Horizontal spacing for community cards
    x_start = 200  # Starting x-coordinate for community cards
    spacing = 120  # Space between cards

    for i, carte in enumerate(cartes_communes[:num_cards_to_display]):
        if carte in images_cartes:
            img = images_cartes[carte]
            screen.blit(img, (x_start + i * spacing, y_coordinate))  # Align cards horizontally

def calcul_chances_de_gagner(cartes, cartes_communes):
    """
    Simulate winning chances based on the number of community cards revealed.
    """
    if len(cartes_communes) == 0:
        return 15  # Pre-flop
    elif len(cartes_communes) == 3:
        return 30  # Flop
    elif len(cartes_communes) == 4:
        return 45  # Turn
    elif len(cartes_communes) == 5:
        return 60  # River

def page_accueil():
    accueil_active = True
    while accueil_active:
        screen.blit(fond, (0, 0))  # Draw the background image

        # Display welcome text and rules
        draw_text("Bienvenue au Casino !", WIDTH // 2, 50, center=True)
        draw_text("Vous allez jouer au poker.", WIDTH // 2, 100, center=True)
        draw_text("Vous démarrez avec 100€ pour miser.", WIDTH // 2, 150, center=True)

        draw_text("Rappel des règles :", WIDTH // 2, 220, center=True)
        draw_text("- Vous recevez 2 cartes privées, visibles uniquement par vous.", WIDTH // 2, 260, center=True)
        draw_text("- 5 cartes communes seront révélées progressivement.", WIDTH // 2, 300, center=True)
        draw_text("- Le but : faire la meilleure combinaison possible.", WIDTH // 2, 340, center=True)
        draw_text("- Mais attention, les autres joueurs peuvent avoir mieux !", WIDTH // 2, 380, center=True)

        draw_text("Appuyez sur Entrée pour valider", WIDTH // 2, 550, center=True)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Check if the Enter key is pressed
                    accueil_active = False  # Exit the welcome screen and proceed to the form

def entrer_montant():
    """
    Ask the player to enter a bet amount. The amount must be greater than 0 and less than or equal to the remaining funds.
    """
    global mise_suivie, dotation_initiale, mise_depart
    montant = ""
    input_box_active = True
    error_message = ""  # To display error messages

    while input_box_active:
        screen.blit(fond, (0, 0))  # Draw the background image
        draw_text("Entrez le montant à miser (en €) :", WIDTH // 2, 100, center=True)
        draw_text(f"{montant}€", WIDTH // 2, 150, center=True)
        draw_text("Appuyez sur Entrée pour confirmer", WIDTH // 2, 300, center=True)

        # Display error message if any
        if error_message:
            draw_text(error_message, WIDTH // 2, 400, color=RED, center=True)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                input_box_active = False
                return 0
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Validate the input
                    if montant.isdigit():
                        montant_int = int(montant)
                        if montant_int > 0 and montant_int <= dotation_initiale - mise_depart:
                            mise_suivie = montant_int
                            return mise_suivie
                        elif montant_int <= 0:
                            error_message = "Le montant doit être supérieur à 0"
                        else:
                            error_message = "Montant invalide, dépasse la dotation"
                    else:
                        error_message = "Veuillez entrer un nombre valide"
                elif event.key == pygame.K_BACKSPACE:
                    montant = montant[:-1]
                else:
                    montant += event.unicode

def formulaire():
    """
    Display a form to collect participant information, including a selection for "Niveau".
    """
    input_boxes = [
        {"label": "Prénom", "key": "prenom", "text": ""},
        {"label": "Âge", "key": "age", "text": ""},
    ]
    niveau_options = ["Oui, débutant", "Oui, intermédiaire", "Oui, avancé", "Non"]
    selected_niveau = 0  # Index of the selected option
    current_box = 0
    running = True
    error_message = ""  # To display validation errors

    while running:
        screen.blit(fond, (0, 0))  # Draw the background image
        draw_text("Veuillez remplir les informations :", WIDTH // 2, 40, center=True)

        # Display text input boxes
        for i, box in enumerate(input_boxes):
            color = GRAY if i != current_box else GREEN
            pygame.draw.rect(screen, color, (200, 100 + i * 80, 400, 50))
    
            # Draw text slightly above the vertical center of the box
            draw_text(f"{box['label']}: {box['text']}", 210, 100 + i * 80 + 5, center=False)

        # Display "Niveau" selection
        niveau_start_y = 300  # Adjust this value to move the whole block lower
        if current_box == len(input_boxes):  # If on the "Niveau" selection
            draw_text("Niveau :", WIDTH // 2, niveau_start_y - 40, center=True)
            for i, option in enumerate(niveau_options):
                box_y = niveau_start_y + i * 50
                box_rect = pygame.Rect(200, box_y, 400, 40)
                color = GREEN if i == selected_niveau else GRAY
                pygame.draw.rect(screen, color, box_rect)

                # Render the text and center it inside the box
                text_surface = FONT.render(option, True, WHITE)
                text_rect = text_surface.get_rect(center=box_rect.center)
                screen.blit(text_surface, text_rect)

        # Display error message if any
        if error_message:
            draw_text(error_message, WIDTH // 2, 500, color=RED, center=True)

        draw_text("Appuyez sur Entrée pour valider", WIDTH // 2, 630, center=True)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if current_box < len(input_boxes):  # Validate current input box
                        if current_box == 0:  # Validate "Prénom"
                            if not input_boxes[current_box]["text"].isalpha():
                                error_message = "Prénom invalide. Utilisez uniquement des lettres."
                            else:
                                error_message = ""
                                current_box += 1
                        elif current_box == 1:  # Validate "Âge"
                            if not input_boxes[current_box]["text"].isdigit() or len(input_boxes[current_box]["text"]) != 2:
                                error_message = "Âge invalide. Entrez un nombre à 2 chiffres."
                            else:
                                error_message = ""
                                current_box += 1
                    elif current_box == len(input_boxes):  # Finalize "Niveau" selection
                        for box in input_boxes:
                            participant_info[box["key"]] = box["text"]
                        participant_info["niveau"] = niveau_options[selected_niveau]
                        return True
                elif event.key == pygame.K_BACKSPACE and current_box < len(input_boxes):
                    input_boxes[current_box]["text"] = input_boxes[current_box]["text"][:-1]
                elif event.key == pygame.K_DOWN and current_box == len(input_boxes):
                    selected_niveau = (selected_niveau + 1) % len(niveau_options)
                elif event.key == pygame.K_UP and current_box == len(input_boxes):
                    selected_niveau = (selected_niveau - 1) % len(niveau_options)
                elif current_box < len(input_boxes):
                    input_boxes[current_box]["text"] += event.unicode

def attribuer_traitement():
    """
    Randomly assign a treatment to the participant and set the initial blind amount (mise_depart).
    """
    global mise_depart, mise_totale
    traitement = random.choice(["avec_mise", "sans_mise"])
    if traitement == "avec_mise":
        mise_depart = 50  # 50% of the initial endowment
    else:
        mise_depart = 0

    # Initialize mise_totale with the value of mise_depart
    mise_totale = mise_depart

    participant_info["traitement"] = traitement

def game_over_screen():
    """
    Display the Game Over screen when the player has no money left.
    """
    screen.fill(WHITE)
    draw_text("GAME OVER", WIDTH // 2, HEIGHT // 2 - 50, color=RED, center=True)
    draw_text("No money left", WIDTH // 2, HEIGHT // 2, color=BLACK, center=True)
    draw_text("Appuyez sur une touche pour quitter", WIDTH // 2, HEIGHT // 2 + 50, color=GRAY, center=True)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False

def end():
    """
    Display the end screen after all phases are completed.
    """
    global participant_info, mise_totale
    running = True
    selected_sex = "female"  # Default selection

    while running:
        screen.blit(fond, (0, 0))  # Draw the background image
        
        # Display buttons
        button_width = 200
        button_height = 60
        button_spacing = 50  # Space between buttons

        # Calculate total width of both buttons + spacing
        total_buttons_width = (2 * button_width) + button_spacing

        # Starting x position to center buttons
        start_x = (WIDTH - total_buttons_width) // 2
        y_button = 300

        draw_text("Fin de l'expérience", WIDTH // 2, 100, color=WHITE, center=True)
        draw_text(f"Total misé : {mise_totale}€", WIDTH // 2, 150, color=WHITE, center=True)
        draw_text("Quel est votre sexe ?", WIDTH // 2, 250, color=WHITE, center=True)

        # Draw buttons
        female_btn = pygame.draw.rect(screen, GREEN if selected_sex == "female" else GRAY, (start_x, y_button, button_width, button_height))
        male_btn = pygame.draw.rect(screen, GREEN if selected_sex == "male" else GRAY, (start_x + button_width + button_spacing, y_button, button_width, button_height))

        # Draw button labels centered inside the buttons
        draw_text("Femme", female_btn.centerx, female_btn.centery, color=WHITE, center=True)
        draw_text("Homme", male_btn.centerx, male_btn.centery, color=WHITE, center=True)

        draw_text("Appuyez sur Entrée pour finir la partie", WIDTH // 2, 400, color=WHITE, center=True)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if female_btn.collidepoint(event.pos):
                    selected_sex = "female"
                elif male_btn.collidepoint(event.pos):
                    selected_sex = "male"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    participant_info["sexe"] = selected_sex  # Save the selected sex
                    running = False

def jeu():
    global cartes, cartes_communes, mise_suivie, mise_totale, dotation_initiale, mise_depart
    images_cartes = charger_images_cartes()  # Load card images
    deck = initialiser_deck()  # Initialize the deck
    cartes = tirer_cartes(deck, 2)  # Draw personal cards
    cartes_communes = tirer_cartes(deck, 5)  # Draw 5 community cards
    running = True
    phase = 0  # Game phases: 0 = Pre-flop, 1 = Flop, 2 = Turn, 3 = River

    while running:
        screen.blit(fond, (0, 0))  # Draw the background image

        # Display fixed text at the top
        draw_text(f"Mise de départ (blind) : {mise_depart}€", 50, 30, color=WHITE)
        draw_text(f"Total misé : {mise_totale}€", 50, 60, color=WHITE)
        money_left = dotation_initiale - mise_totale
        draw_text(f"Money left : {money_left}€", 50, 90, color=WHITE)

        # Check if the player has no money left
        if money_left <= 0:
            game_over_screen()
            return  # Exit the game loop

        # Display personal cards
        x_start_personal = 200  # Starting x-coordinate for personal cards
        spacing_personal = 120  # Space between personal cards
        y_coordinate_personal = 200  # First row for personal cards
        if cartes[0] in images_cartes:
            screen.blit(images_cartes[cartes[0]], (x_start_personal, y_coordinate_personal))
        if cartes[1] in images_cartes:
            screen.blit(images_cartes[cartes[1]], (x_start_personal + spacing_personal, y_coordinate_personal))

        # Dynamically position "Chance de gagner" and buttons below the cards
        y_offset = y_coordinate_personal + 145 + 50  # Start below the community cards
        if phase > 0:
            y_offset += 145 + 50  # Add height and spacing for community cards if displayed

        # Display community cards based on the current phase
        if phase > 0:
            y_coordinate_community = y_coordinate_personal + 145 + 50  # Personal cards' height + spacing
            afficher_cartes_communes(images_cartes, phase, y_coordinate_community)

        # Dynamically position "Chance de gagner" and buttons below the cards
        y_offset = y_coordinate_personal + 145 + 50  # Start below the community cards
        if phase > 0:
            y_offset += 145 + 50  # Add height and spacing for community cards if displayed

        # Display "Chance de gagner"
        chances = calcul_chances_de_gagner(cartes, cartes_communes[:phase + 2])
        draw_text(f"Chance de gagner : {chances}%", WIDTH // 2, y_offset, color=WHITE, center=True)

        # Display decision buttons
        draw_text("Que décidez-vous ?", WIDTH // 2, y_offset + 50, color=WHITE, center=True)
        suivre_btn = pygame.draw.rect(screen, GREEN, (WIDTH // 4 - 100, y_offset + 100, 200, 60))
        coucher_btn = pygame.draw.rect(screen, RED, (3 * WIDTH // 4 - 100, y_offset + 100, 200, 60))
        draw_text("Suivre", suivre_btn.centerx, suivre_btn.centery, color=WHITE, center=True)
        draw_text("Se coucher", coucher_btn.centerx, coucher_btn.centery, color=WHITE, center=True)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if suivre_btn.collidepoint(event.pos):
                    if phase == 0:  # Pre-flop: No bet required, just move to the next phase
                        phase += 1
                    else:  # For Flop, Turn, and River phases
                        mise_suivie = entrer_montant()  # Ask for bet amount
                        if mise_suivie > 0:  # Only proceed if a valid bet is made
                            mise_totale += mise_suivie  # Update total money bet
                            phase += 1
                elif coucher_btn.collidepoint(event.pos):
                    running = False

        # End the game after the river phase
        if phase > 3:  # River phase is the last phase
            running = False

# Exécution
page_accueil()  # Show the welcome screen

if formulaire():  # Show the form to collect participant information
    attribuer_traitement()  # Assign treatment
    jeu()  # Start the game
    
    end()

pygame.quit()