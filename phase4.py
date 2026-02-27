import osmnx as ox
import networkx as nx
import folium
import numpy as np
from sklearn.linear_model import LinearRegression
from flask import Flask, render_template_string, request

app = Flask(__name__)

# ============================================
# MODÈLE IA (chargé une seule fois)
# ============================================
heures = np.array(range(24))
trafic = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.1, 1.3, 1.8, 2.5, 1.6,
                   1.3, 1.2, 1.4, 1.3, 1.2, 1.3, 1.7, 2.4, 2.2, 1.6,
                   1.4, 1.2, 1.1, 1.0])
modele = LinearRegression()
modele.fit(heures.reshape(-1, 1), trafic)

print("⏳ Chargement du réseau Toulouse (1-2 min)...")
G = ox.graph_from_place("Toulouse, France", network_type="drive")
print("✅ Réseau chargé !")

LIEUX = {
    "Capitole"         : (43.6047, 1.4442),
    "Aéroport"         : (43.6350, 1.3678),
    "Université Paul Sabatier": (43.5623, 1.4685),
    "Gare Matabiau"    : (43.6108, 1.4536),
    "Cité de l'Espace" : (43.5843, 1.4934),
}

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>🗺️ Mini Google Maps IA</title>
    <style>
        body { font-family: Arial; margin: 0; background: #f0f2f5; }
        .header { background: #4285F4; color: white; padding: 15px 30px; }
        .header h1 { margin: 0; font-size: 22px; }
        .panel { display: flex; gap: 20px; padding: 20px; }
        .controls { background: white; border-radius: 12px; padding: 20px;
                    width: 280px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); height: fit-content; }
        .controls label { font-weight: bold; display: block; margin-top: 12px; color: #333; }
        .controls select, .controls input {
            width: 100%; padding: 8px; margin-top: 5px;
            border: 1px solid #ddd; border-radius: 8px; font-size: 14px; }
        .btn { background: #4285F4; color: white; border: none; padding: 12px;
               width: 100%; border-radius: 8px; font-size: 16px; cursor: pointer; margin-top: 15px; }
        .btn:hover { background: #3367d6; }
        .result { background: #f8f9fa; border-radius: 8px; padding: 12px; margin-top: 15px; font-size: 14px; }
        iframe { border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); flex: 1; }
    </style>
</head>
<body>
    <div class="header"><h1>🗺️ Mini Google Maps avec IA — Toulouse</h1></div>
    <div class="panel">
        <div class="controls">
            <form method="POST">
                <label>📍 Départ</label>
                <select name="depart">
                    {% for lieu in lieux %}<option {% if lieu == depart_sel %}selected{% endif %}>{{ lieu }}</option>{% endfor %}
                </select>

                <label>🏁 Arrivée</label>
                <select name="arrivee">
                    {% for lieu in lieux %}<option {% if lieu == arrivee_sel %}selected{% endif %}>{{ lieu }}</option>{% endfor %}
                </select>

                <label>🕐 Heure de départ : {{ heure }}h</label>
                <input type="range" name="heure" min="0" max="23" value="{{ heure }}"
                       oninput="this.previousElementSibling.textContent='🕐 Heure de départ : '+this.value+'h'">

                <button class="btn" type="submit">🔍 Calculer l'itinéraire</button>
            </form>

            {% if result %}
            <div class="result">
                <b>🧠 Résultat IA</b><br><br>
                📏 Distance : <b>{{ result.distance }} km</b><br>
                ⏱️ Temps estimé : <b>{{ result.temps }} min</b><br>
                🚗 Vitesse : <b>{{ result.vitesse }} km/h</b><br>
                {{ result.etat }}
            </div>
            {% endif %}
        </div>

        <iframe src="/map" width="100%" height="600px"></iframe>
    </div>
</body>
</html>
"""

carte_html = ""

@app.route("/map")
def map_view():
    return carte_html if carte_html else "<p>Lance un calcul d'abord !</p>"

@app.route("/", methods=["GET", "POST"])
def index():
    global carte_html
    lieux = list(LIEUX.keys())
    result = None
    depart_sel  = lieux[0]
    arrivee_sel = lieux[1]
    heure = 8

    if request.method == "POST":
        depart_sel  = request.form.get("depart")
        arrivee_sel = request.form.get("arrivee")
        heure = int(request.form.get("heure", 8))

        depart_coords  = LIEUX[depart_sel]
        arrivee_coords = LIEUX[arrivee_sel]

        n1 = ox.nearest_nodes(G, depart_coords[1],  depart_coords[0])
        n2 = ox.nearest_nodes(G, arrivee_coords[1], arrivee_coords[0])

        chemin = nx.shortest_path(G, n1, n2, weight="length")
        distance_m  = nx.shortest_path_length(G, n1, n2, weight="length")
        distance_km = round(distance_m / 1000, 2)

        mult           = modele.predict([[heure]])[0]
        vitesse_reelle = round(40 / mult, 1)
        temps          = round((distance_km / vitesse_reelle) * 60, 1)

        if mult < 1.3:
            couleur, etat = "green",  "🟢 Trafic fluide"
        elif mult < 1.8:
            couleur, etat = "orange", "🟠 Trafic modéré"
        else:
            couleur, etat = "red",    "🔴 Trafic dense"

        result = {"distance": distance_km, "temps": temps,
                  "vitesse": vitesse_reelle, "etat": etat}

        carte = folium.Map(location=[43.6047, 1.4442], zoom_start=13)
        coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in chemin]
        folium.PolyLine(coords, color=couleur, weight=6).add_to(carte)
        folium.Marker(depart_coords,  popup=depart_sel,  icon=folium.Icon(color="green")).add_to(carte)
        folium.Marker(arrivee_coords, popup=arrivee_sel, icon=folium.Icon(color="red")).add_to(carte)
        carte_html = carte._repr_html_()

    return render_template_string(HTML, lieux=lieux, result=result,
                                  depart_sel=depart_sel, arrivee_sel=arrivee_sel, heure=heure)

if __name__ == "__main__":
    print("\n🚀 Serveur lancé ! Ouvre : http://127.0.0.1:5000\n")
    app.run(debug=False)