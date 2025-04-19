from flask import Flask, render_template, request, redirect, url_for
from flask_app.game_logic import PokerGame
import random
import os
import csv

# Global variables
participant_info = {}  # To store player information (e.g., name, age, level)
mise_depart = 0        # Initial bet amount (randomly assigned as 0 or 50)
mise_totale = 0        # Total bet amount during the game
dotation_initiale = 100  # Initial funds for the player

def save_user_data(data):
    """
    Save the player's data to a CSV file.
    """
    directory = 'data'
    file_path = os.path.join(directory, 'user_data.csv')

    # Ensure the directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_exists = os.path.isfile(file_path)

    with open(file_path, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["prenom", "age", "niveau", "sexe", "mise_totale", "dotation_initiale"])
        if not file_exists:
            writer.writeheader()  # Write the header only if the file doesn't exist
        writer.writerow(data)
        
# Initialize the game instance
game = PokerGame()

def register_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/formulaire', methods=['GET', 'POST'])
    def formulaire():
        global participant_info, mise_depart
        if request.method == 'POST':
            # Collect participant information from the form
            participant_info['prenom'] = request.form['prenom']
            participant_info['age'] = request.form['age']
            participant_info['niveau'] = request.form['niveau']

            # Randomly assign mise_depart as 0 or 50
            mise_depart = random.choice([0, 50])

            # Initialize the game
            game.initialize_game()

            return redirect(url_for('jeu'))  # Redirect to the game page

        # Render the formulaire page
        return render_template('formulaire.html')

    @app.route('/jeu', methods=['GET', 'POST'])
    def jeu():
        global mise_totale, mise_depart

        message = ""
        money_left = game.dotation_initiale - game.mise_totale - mise_depart  # Calculate money left

        # Check if money left is 0
        if money_left <= 0:
            return redirect(url_for('end'))  # Redirect to the end screen

        if request.method == 'POST':
            action = request.form.get('action')  # Get the action from the form
            if action == 'follow':
                return redirect(url_for('bet'))  # Redirect to the betting page
            elif action == 'fold':
                message = "Vous avez décidé de vous coucher. Fin de la partie."
                return redirect(url_for('end'))  # Redirect to the end page

        # Debugging: Print the current phase and community cards
        print(f"Rendering /jeu. Current phase: {game.phase}")
        print(f"Community cards: {game.get_community_cards()}")

        # Render the game page
        return render_template(
            'game.html',
            cartes=game.cartes,
            cartes_communes=game.get_community_cards(),
            mise_depart=mise_depart,
            mise_totale=game.mise_totale,
            money_left=game.dotation_initiale - game.mise_totale - mise_depart,  # Include mise_depart
            chances=game.calculate_chances(),
            phase=game.phase,
            message=message
        )

    @app.route('/bet', methods=['GET', 'POST'])
    def bet():
        global mise_totale

        message = ""
        if request.method == 'POST':
            try:
                # Get the bet amount from the form
                bet = int(request.form.get('bet', 0))
                if bet > 0 and bet <= (game.dotation_initiale - game.mise_totale):
                    game.mise_totale += bet

                    # Check if the game has reached the River phase
                    if game.phase >= 3:  # River is the last phase (phase 3)
                        return redirect(url_for('end'))  # Redirect to the end screen

                    game.next_phase()  # Move to the next phase
                    return redirect(url_for('jeu'))  # Return to the game
                else:
                    message = "Montant invalide. Assurez-vous qu'il est supérieur à 0 et dans vos fonds restants."
            except ValueError:
                message = "Veuillez entrer un montant valide."

        # Render the betting page
        return render_template(
            'bet.html',
            mise_totale=game.mise_totale,
            money_left=game.dotation_initiale - game.mise_totale,
            message=message
        )
    @app.route('/end', methods=['GET', 'POST'])
    def end():
        global participant_info, mise_depart, mise_totale, game

        if request.method == 'POST':
            # Collect the player's sex from the form
            participant_info['sexe'] = request.form.get('sexe')

            # Collect final game data
            final_data = {
                "prenom": participant_info['prenom'],
                "age": participant_info['age'],
                "niveau": participant_info['niveau'],
                "sexe": participant_info['sexe'],
                "mise_totale": game.mise_totale,
                "dotation_initiale": game.dotation_initiale
            }

            # Save the data to a CSV file
            save_user_data(final_data)

            # Reset global variables
            participant_info = {}
            mise_depart = 0
            mise_totale = 0
            game = PokerGame()  # Reinitialize the game instance

            # Thank the player and end the game
            return render_template('thank_you.html', data=final_data)

        # Render the end screen for GET requests
        return render_template('end.html', data=participant_info, mise_totale=game.mise_totale, dotation_initiale=game.dotation_initiale)