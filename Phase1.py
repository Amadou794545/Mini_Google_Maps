import osmnx as ox
import folium

# 1. Télécharger le réseau routier de Toulouse
print("⏳ Téléchargement du réseau routier de Toulouse...")
G = ox.graph_from_place("Toulouse, France", network_type="drive")
print("✅ Réseau téléchargé !")

# 2. Afficher quelques infos
print(f"📊 Nombre de nœuds (intersections) : {len(G.nodes)}")
print(f"📊 Nombre d'arêtes (routes) : {len(G.edges)}")

# 3. Convertir en GeoDataFrame
nodes, edges = ox.graph_to_gdfs(G)

# 4. Créer la carte interactive avec Folium
print("🗺️ Création de la carte...")
carte = folium.Map(location=[43.6047, 1.4442], zoom_start=13)

# 5. Ajouter les routes sur la carte
for _, row in edges.iterrows():
    if row.geometry is not None:
        coords = [(lat, lon) for lon, lat in row.geometry.coords]
        folium.PolyLine(coords, color="blue", weight=1, opacity=0.5).add_to(carte)

# 6. Sauvegarder la carte
carte.save("toulouse_map.html")
print("✅ Carte sauvegardée dans toulouse_map.html !")
print("👉 Ouvre ce fichier dans ton navigateur pour voir la carte.")