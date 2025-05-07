from flask import Flask, render_template, request, redirect, url_for, session, send_file
import random
import os
import csv
import logging
from datetime import datetime
from flask_app.game_logic import PokerGame, initialiser_deck, tirer_cartes, charger_images_cartes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
participant_info = {"age": "", "niveau": "", "traitement": ""}  # To store player information (e.g., name, age, level)
mise_totale = 0        # Total bet amount during the game
cartes = []  # Player's personal cards
cartes_communes = []  # Community cards
# Store the round number
round_number = 1  # Starts at 1, and will go up to 3
max_rounds = 3  # We'll play 3 rounds

def save_user_data(info, cartes, decision, montant=0):

    round_number = session.get('round_number', 1)
    phase = getattr(game, 'phase', None)  # Safely get the current phase
    
    logger.info("📁 Attempting to save data to CSV...")
    """
    Save the player's data to a CSV file.
    """
    data = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(data):
        os.makedirs(data)
        if not os.path.exists("data"):
            os.makedirs("data")

    timestamp = datetime.now().isoformat()

    row = [
        timestamp,
        info.get("age") if info else "",
        info.get("niveau") if info else "",
        info.get("sexe") if info else "",
        cartes[0] if cartes else "",
        cartes[1] if cartes else "",
        decision,
        montant,
        round_number,
        phase
    ]
    
    file_path = os.path.abspath("data/decisions.csv")
    logger.info("📄 Writing to file:", file_path)

    with open(file_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)
        f.flush()

    logger.info("✅ Data saved:", row)

# Initialize the game instance
game = PokerGame(deck_initializer=initialiser_deck, draw_function=tirer_cartes)

def register_routes(app):
    @app.route('/')
    def index():
        global game
        # Reset the game phase and initialize the session round number
        game.reset_for_new_round()  # Reset the game state for a new round
        session['round_number'] = 1  # Reset round number at game start
        return render_template('index.html')

    @app.route('/jeu', methods=['GET', 'POST'])
    def jeu():
        global game, mise_totale, max_rounds, round_number, total_money_bet, mise_depart

        logger.info(f"Current phase: {game.phase}, Round: {session.get('round_number', 1)}")

        round_number = session.get('round_number', 1)
       
    # Initialize/reset game at the start of a new round
        if request.method == 'GET':
            if game.phase == 0:  # Only reset for new round when game.phase == 0
                game.reset_for_new_round()  # Ensures phase is reset to 0
                mise_depart = 50 if round_number == 3 else 0  # Assign a value to mise_depart
                game.mise_totale = mise_depart
                
        # Calculate money left
        money_left = game.dotation_initiale - game.mise_totale
        # Load card image paths
        image_paths = charger_images_cartes()

        # Check if money left is 0
        if money_left <= 0:
            logger.info(f"Redirecting to final_form — money_left: {money_left}, round: {round_number}, phase: {game.phase}")
            return redirect(url_for('final_form'))  # Redirect to the end screen

        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'follow':
                return redirect(url_for('bet'))  # Always go to bet on follow
            elif action == 'fold':
                return redirect(url_for('final_form'))
            
        # Determine which template to render based on the phase
        if game.phase == 0:
            template = 'preflop.html'
        elif game.phase == 1:
            template = 'flop.html'
        elif game.phase == 2:
            template = 'turn.html'
        elif game.phase == 3:
            logger.info("We are in Phase 3!")
            template = 'river.html'
            
        # Calculate chances (placeholder logic)
        chances = random.randint(0, 100)

        # Render the game page
        return render_template(
            template,
            cartes=game.cartes,
            cartes_communes=game.get_community_cards(),
            image_paths=image_paths,
            mise_depart=mise_depart,
            mise_totale=game.mise_totale,
            money_left=money_left,  # Pass money_left to the template
            chances=game.calculate_chances(),
            phase=game.phase,
            round_number=session['round_number'],
            message=None
        )
    
    @app.route('/round_summary')
    def round_summary():
        global round_number, game

        # Ensure round_number is tracked in session
        round_number = session.get('round_number', 1)
        logger.info(f"Round number at summary: {round_number}")

        # Check if game has reached max rounds, then redirect to final form
        if round_number > max_rounds:
            return redirect(url_for('final_form'))
        
        show_final_button = False  # Valeur par défaut

        # Define the message for each round
        if round_number == 1:
            message = "Fin de la première partie. Vous allez commencer la partie 2."
        elif round_number == 2:
            message = "Fin de la deuxième partie. Vous allez commencer la dernière partie avec une mise de départ de 50."
        elif round_number == 3:
            show_final_button = True
            return redirect(url_for('end_summary'))
        
        show_final_button = (round_number == max_rounds)

        # Render the round summary page with the current round message
        return render_template('round_summary.html', round_number=round_number, message=message, show_final_button=show_final_button)


    @app.route('/bet', methods=['GET', 'POST'])
    def bet():
        global game, mise_totale, mise_depart, total_money_bet

        round_number = session.get('round_number', 1)
        starting_bet = session.get('starting_bet', 0)
      
        if round_number > 3:
            return redirect(url_for('final_form'))  # or 'end'
        
        # Calculate money left
        money_left = game.dotation_initiale - game.mise_totale
        message = ""
       
        if request.method == 'POST':
            bet_str = request.form.get('bet', '').strip()
            logger.info("Raw bet input:", repr(bet_str))  # Debugging info
           
            if not bet_str.isdigit():
                message = "Veuillez entrer un montant valide."
            else:
                bet = int(bet_str)
                max_bet = game.dotation_initiale - game.mise_totale
                logger.info(f"Bet entered: {bet}, Max allowed: {max_bet}")  # More debugging info
                
                if bet > 0 and bet <= (game.dotation_initiale - game.mise_totale):
                    game.mise_totale += bet

                    # ✅ SAVE the data immediately
                    save_user_data(
                        info=None,  # No participant info yet
                        cartes=game.cartes,
                        decision=f"phase_{game.phase}_bet",
                        montant=bet,
                    )

                    if game.phase < 3:
                        game.next_phase()
                        return redirect(url_for('jeu'))
                    else:
                        return redirect(url_for('round_summary'))
                else:
                    message = "Montant invalide."
            
        # Render the betting page
        return render_template(
            'bet.html',
            mise_totale=game.mise_totale,
            money_left=money_left,
            message=message
        )
    
    @app.route('/final_form', methods=['GET', 'POST'])
    def final_form():
        global participant_info, mise_depart
        if request.method == 'POST':
            # 1. Collect participant information from the form
            participant_info = {
                'age': request.form['age'],
                'niveau': request.form['niveau'],
                "sexe": request.form['sexe']
            }

            # 2. Log final decision and cards
            save_user_data(
                info=participant_info,
                cartes=game.cartes,
                decision="final",
                montant=game.mise_totale,
            )
            
            return redirect(url_for('end'))  # Now redirect to final results

        return render_template('formulaire.html')  # Reuse the form template


    @app.route('/end', methods=['GET', 'POST'])
    def end():
        global participant_info, mise_depart, mise_totale, game

        if request.method == 'POST':

            # Collect final game data
            final_data = {
                "age": participant_info['age'],
                "niveau": participant_info['niveau'],
                "sexe": participant_info['sexe'],
                "mise_totale": game.mise_totale
            }

            # Save the data to a CSV file
            save_user_data(
                info=participant_info,
                cartes=game.cartes,
                decision="final",
                montant=game.mise_totale,
            )

        # Thank the player and show final screen
            response = render_template('thank_you.html', data=final_data, round_number=round_number)
        else:
            # Show regular end screen
            response = render_template('end.html', data=participant_info, mise_totale=game.mise_totale, dotation_initiale=game.dotation_initiale)

        # Reset global variables
        participant_info = {}
        mise_depart = 0
        mise_totale = 0
        game = PokerGame(deck_initializer=initialiser_deck, draw_function=tirer_cartes)

        return response
    
    @app.route('/next_round', methods=['POST'])
    def next_round():
        global game, round_number
        max_rounds = 3

        round_number = session.get('round_number', 1)

        if round_number < max_rounds:
            round_number += 1
            session['round_number'] = round_number

            if round_number == 3:
                session['starting_bet'] = 50  # Apply special rule
            else:
                session['starting_bet'] = 0  # Default starting bet

            game.reset_for_new_round()
            return redirect(url_for('jeu'))  # <-- Go to preflop setup
        else:
            return redirect(url_for('final_form'))
        
    @app.route('/end_summary')
    def end_summary():
        message = "Fin de la troisième partie. Le jeu se termine maintenant."
        return render_template('round_summary.html', round_number=3, message=message, show_button=True)
    
    @app.route('/download_csv')
    def download_csv():
        try:
            return send_file('data/decisions.csv', as_attachment=True)
        except FileNotFoundError:
            return "Aucun fichier trouvé.", 404

