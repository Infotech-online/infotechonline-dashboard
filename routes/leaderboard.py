from flask import Blueprint, request, render_template, current_app
import json
import os

# Blueprint
leaderboard_blueprint = Blueprint('leaderboard_blueprint', __name__)

# Ruta principal
@leaderboard_blueprint.route('/leaderboard_dia_2')
def second_leaderboard():

    # Se retorna el template del leaderboard
    return render_template("leaderboard_2.html")

# Ruta principal
@leaderboard_blueprint.route('/leaderboard_dia_3')
def third_leaderboard():

    # Se retorna el template del leaderboard
    return render_template("leaderboard_3.html")

# Ruta principal
@leaderboard_blueprint.route('/leaderboard_dia_4')
def last_leaderboard():

    # Se retorna el template del leaderboard
    return render_template("leaderboard_4.html")