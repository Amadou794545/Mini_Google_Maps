import osmnx as ox
import networkx as nx
import folium
import numpy as np
from sklearn.linear_model import LinearRegression

# ============================================
# 1. CRÉER UN DATASET D'ENTRAÎNEMENT SIMULÉ
# ============================================
# Heures de la journée (0h à 23h)
heures = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                   12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23])

# Multiplicateur de trafic selon l'heure (1.0 = normal, 2.0 = double du temps)
trafic = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.1, 1.3, 1.8, 2.5, 1.6,
                   1.3, 1.2, 1.4, 1.3, 1.2, 1.3, 1.7, 2.4, 2.2, 1.6,
                   1.4, 1.2, 1.1, 1.0])

# Entraîner le modèle IA
modele = LinearRegression()
modele.fit(heures.reshape(-1, 1), trafic)
print("✅ Modèle IA entraîné !")

# ============================================
# 2. CHARGER LE RÉSEAU ET CALCULER L'ITINÉRAIRE
# ============================================
print("⏳ Chargement du réseau Toulouse...")
G = ox.graph_from_place("Toulouse, France", network_type="drive")

depart = (43.6047, 1.4442)  # Capitole
arrivee = (43.62910, 1.36380)  # Aéroport de Toulouse

noeud_depart = ox.nearest_nodes(G, depart[1], depart[0])
noeud_arrivee = ox.nearest_nodes(G, arrivee[1], arrivee[0])

chemin = nx.shortest_path(G, noeud_depart, noeud_arrivee, weight="length")

# Calculer la distance totale en km
distance_m = nx.shortest_path_length(G, noeud_depart, noeud_arrivee, weight="length")
distance_km = distance_m / 1000
print(f"📏 Distance : {distance_km:.2f} km")

# ============================================
# 3. PRÉDICTION IA SELON L'HEURE
# ============================================
heure_actuelle = 8  # ← Change cette valeur pour tester (0 à 23) !

multiplicateur = modele.predict([[heure_actuelle]])[0]
vitesse_normale = 40  # km/h en ville
vitesse_reelle = vitesse_normale / multiplicateur
temps_minutes = (distance_km / vitesse_reelle) * 60

print(f"\n🕐 Heure choisie       : {heure_actuelle}h")
print(f"🚦 Multiplicateur trafic : x{multiplicateur:.2f}")
print(f"🚗 Vitesse estimée      : {vitesse_reelle:.1f} km/h")
print(f"⏱️  Temps de trajet estimé : {temps_minutes:.1f} minutes")

# ============================================
# 4. AFFICHER LA CARTE AVEC INFOS
# ============================================
carte = folium.Map(location=[43.6047, 1.4442], zoom_start=13)

# Couleur selon le trafic
if multiplicateur < 1.3:
    couleur = "green"
    etat = "🟢 Trafic fluide"
elif multiplicateur < 1.8:
    couleur = "orange"
    etat = "🟠 Trafic modéré"
else:
    couleur = "red"
    etat = "🔴 Trafic dense"

# Tracer l'itinéraire
route_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in chemin]
folium.PolyLine(route_coords, color=couleur, weight=6, opacity=0.9).add_to(carte)

# Marqueurs
folium.Marker(depart, popup=f"🟢 Départ\n{etat}\n⏱️ {temps_minutes:.1f} min",
              icon=folium.Icon(color="green")).add_to(carte)
folium.Marker(arrivee, popup="🔴 Arrivée : Aéroport",
              icon=folium.Icon(color="red")).add_to(carte)

# Légende
legende = f"""
<div style="position:fixed; bottom:30px; left:30px; background:white;
            padding:15px; border-radius:10px; font-size:14px; z-index:1000;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
    <b>🧠 Prédiction IA</b><br>
    🕐 Heure : {heure_actuelle}h<br>
    📏 Distance : {distance_km:.2f} km<br>
    ⏱️ Temps estimé : {temps_minutes:.1f} min<br>
    {etat}
</div>
"""
carte.get_root().html.add_child(folium.Element(legende))
carte.save("toulouse_ia.html")

print(f"\n✅ Carte sauvegardée : toulouse_ia.html")
print("👉 Ouvre ce fichier dans ton navigateur !")
