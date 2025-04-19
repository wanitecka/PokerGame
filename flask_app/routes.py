from flask import render_template, request, redirect, url_for
import random
import os

participant_info = {"prenom": "", "age": "", "niveau": "", "traitement": "", "sexe": ""}
dotation_initiale = 100
mise_depart = 0
mise_totale = 0
cartes = []
cartes_communes = []
mise_suivie = 0

def register_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/formulaire', methods=['GET', 'POST'])
    def formulaire():
        global participant_info
        if request.method == 'POST':
            participant_info['prenom'] = request.form['prenom']
            participant_info['age'] = request.form['age']
            participant_info['niveau'] = request.form['niveau']
            return redirect(url_for('jeu'))
        return render_template('formulaire.html')

    @app.route('/jeu', methods=['GET', 'POST'])
    def jeu():
        global cartes, cartes_communes, mise_suivie, mise_totale, dotation_initiale, mise_depart
        if request.method == 'POST':
            # Game logic goes here
            pass
        return render_template('game.html', cartes=cartes, cartes_communes=cartes_communes)

    @app.route('/end', methods=['GET', 'POST'])
    def end():
        if request.method == 'POST':
            # Logic to handle end of game
            return redirect(url_for('index'))
        return render_template('end.html')