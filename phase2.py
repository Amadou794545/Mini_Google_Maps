import osmnx as ox
import networkx as nx
import folium

# 1. Télécharger le réseau de Toulouse
print("⏳ Chargement du réseau...")
G = ox.graph_from_place("Toulouse, France", network_type="drive")
print("✅ Réseau chargé !")

# 2. Définir un point de départ et d'arrivée (lat, lon)
depart  = (43.6047, 1.4442)   # Place du Capitole
arrivee = (43.62910, 1.36380)   # Aéroport de Toulouse

# 3. Trouver les nœuds les plus proches sur le réseau
noeud_depart  = ox.nearest_nodes(G, depart[1],  depart[0])
noeud_arrivee = ox.nearest_nodes(G, arrivee[1], arrivee[0])

# 4. Calculer le chemin le plus court
print("🔍 Calcul de l'itinéraire...")
chemin = nx.shortest_path(G, noeud_depart, noeud_arrivee, weight="length")
print(f"✅ Itinéraire trouvé ! ({len(chemin)} étapes)")

# 5. Créer la carte
carte = folium.Map(location=[43.6047, 1.4442], zoom_start=13)

# 6. Tracer l'itinéraire en rouge
route_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in chemin]
folium.PolyLine(route_coords, color="red", weight=5, opacity=0.8).add_to(carte)

# 7. Ajouter les marqueurs départ / arrivée
folium.Marker(depart,  popup="🟢 Départ : Capitole",          icon=folium.Icon(color="green")).add_to(carte)
folium.Marker(arrivee, popup="🔴 Arrivée : Aéroport Toulouse", icon=folium.Icon(color="red")).add_to(carte)

# 8. Sauvegarder
carte.save("toulouse_itineraire.html")
print("✅ Carte sauvegardée : toulouse_itineraire.html")
print("👉 Ouvre ce fichier dans ton navigateur !")