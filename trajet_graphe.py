import networkx as nx
import folium
from geopy.distance import geodesic 


G = nx.DiGraph()

# les nœuds (sommets) avec les noms d'arrêts spécifiques
arrets_details = {
    'S0': {'nom': 'Rond-Point Victoire (DEPART)', 
           'description': ' Place des Artistes à Kinshasa. Chemin Vert (5 arrêts) ,Chemin Bleu (7 arrêts).', 
           'image_url': 'Rond Point Victoire.png '}, 
    'S4': {'nom': 'Gare Centrale (ARRIVEE)', 
           'description': 'La principale gare ferroviaire de Kinshasa.',
           'image_url': 'gare centrale.png '}, 
    
    # Arrêts du CHEMIN A (Rapide) - 5 arrêts au total
    'S12': {'nom': 'Arrêt Rond point Kimpwaza', 
            'description': 'Nouvel arrêt après le départ, vers Boulevard du 30Juin.',
            'image_url': 'Rond point kimpwaza.png '}, 
    'S15': {'nom': 'Arrêt Huilerie', 
            'description': 'Arrêt central du Chemin A. Boulevard du 30Juin.', 
            'image_url': 'Huielerie.jpg '}, 
    'S13': {'nom': 'Arrêt Regideso', 
            'description': 'Avant-dernier arrêt du Chemin A.',
            'image_url': 'regideso.jpg '}, 
            
    # Arrêts du CHEMIN B (Lent) - 7 arrêts au total
    'S1': {'nom': 'Pont Gaby', 
           'description': 'Premier arrêt du Chemin B (Lent). Le Chemin A le contourne.', 
           'image_url': 'Pond gaby.png '}, 
    'S5': {'nom': 'Arrêt Kabambare', 
           'description': 'Av.Kasa-Vubu contre Av.Kabambare.',
           'image_url': 'lycee kabambare.jpg '}, 
    'S11': {'nom': 'Arrêt Itaga',
            'description': 'Av.Kabambare Contre Av.Itaga.'}, 
    'S6': {'nom': 'Arrêt Pont du canal ', 
           'description': 'Av.Itaga. contre Av.du canal. '}, 
    'S10': {'nom': 'Arrêt Poid Lourd',
            'description': 'Avant-dernier arrêt Av. Kisangani jusqua la gare centrale.',
            'image_url': 'route poid lourd.jpg '}, 
}
arrets = {code: details['nom'] for code, details in arrets_details.items()}
G.add_nodes_from(arrets.keys())


# COORDONNÉES GÉOGRAPHIQUES 
coords = {
    'S0': (-4.340794799500401, 15.313745844582911), # Rond-Point Victoire
    'S4': (-4.30124990118881, 15.317523726760912), 	# Gare Centrale
    
    # Chemin A 
    'S12': (-4.338040623238921, 15.305076006120231), # Rond point Kimpwaza
    'S15': (-4.323440454236438, 15.306183387831855), # Rond point Huilerie
    'S13': (-4.305924247828733, 15.301385286447495), # Boulevard du 30juin Regideso
    
    # Chemin B 
    'S1': (-4.331585879172314, 15.314446591256095), # Pont gaby
    'S5': (-4.321978842774812, 15.31186094157827),  # Kabambare
    'S11': (-4.318020451877732, 15.325904987217928), # Itaga 
    'S6': (-4.310788310982217, 15.323673389325227), # du Canal
    'S10': (-4.305139490389958, 15.326430699968544), # kisagani
}

# les arcs avec 'weight' (temps de trajet en minutes)
trajets_avec_temps = [
    # CHEMIN A : 5 ARRÊTS - RAPIDE (Total 18 min)
    ('S0', 'S12', {'weight': 7}),  
    ('S12', 'S15', {'weight': 6}), 
    ('S15', 'S13', {'weight': 3}), 
    ('S13', 'S4', {'weight': 2}),  
    
    # CHEMIN B : 7 ARRÊTS - LENT (Total 51 min)
    ('S0', 'S1', {'weight': 8}),    
    ('S1', 'S5', {'weight': 10}), 	
    ('S5', 'S11', {'weight': 9}), 	
    ('S11', 'S6', {'weight': 9}), 	
    ('S6', 'S10', {'weight': 8}), 	
    ('S10', 'S4', {'weight': 7}), 	
]
G.add_edges_from(trajets_avec_temps)

# -CALCULS DE CHEMIN ET TEMPS -

etat_initial = 'S0'
etat_final = 'S4'
chemin_rapide = nx.shortest_path(G, source=etat_initial, target=etat_final, weight='weight')
temps_total_rapide = nx.shortest_path_length(G, source=etat_initial, target=etat_final, weight='weight')

# Calcul des temps totaux pour la comparaison à l'arrivée
chemin_A_nodes = ['S0', 'S12', 'S15', 'S13', 'S4']
chemin_B_nodes = ['S0', 'S1', 'S5', 'S11', 'S6', 'S10', 'S4']

time_A = nx.path_weight(G, chemin_A_nodes, weight='weight') # 18 minutes
time_B = nx.path_weight(G, chemin_B_nodes, weight='weight') # 51 minutes

# Calcul du temps cumulé pour les arrêts du Chemin A
temps_cumules_rapide = {'S0': 0}
temps_actuel = 0
for i in range(len(chemin_rapide) - 1):
    u = chemin_rapide[i]
    v = chemin_rapide[i+1]
    temps_segment = G[u][v]['weight']
    temps_actuel += temps_segment
    temps_cumules_rapide[v] = temps_actuel


# - VISUALISATION AVEC FOLIUM -

centre_lat, centre_lon = coords['S0']
m = folium.Map(location=[centre_lat, centre_lon], zoom_start=13, tiles='OpenStreetMap')

# Tous les nœuds (arrêts) AVEC POP-UP DÉTAILLÉ
for node_code, details in arrets_details.items():
    lat, lon = coords[node_code]
    
    temps_cumule = temps_cumules_rapide.get(node_code)
    distance_ecoule = None
    
    # Calcul de la distance géodésique pour le Chemin A
    if node_code != 'S0' and node_code in chemin_rapide:
        lat_start, lon_start = coords['S0']
        distance_ecoule = geodesic((lat_start, lon_start), (lat, lon)).kilometers
    
    # Construction du Pop-up HTML 
    popup_content = f"""
    <div style="width: 220px; font-family: Arial, sans-serif; text-align: center; line-height: 1.4;">
    """
    
    # Image
    image_url = details.get('image_url', '').strip() # Suppression des espaces blancs
    if image_url and not image_url.endswith(('.png', '.jpg', )): 
        pass 
    else:
        # Affichage d'une image d'exemple pour la démonstration (sinon commenter cette section)
        popup_content += f"""
        <div style="height: 120px; overflow: hidden; margin: -10px -10px 5px -10px; border-radius: 4px 4px 0 0;">
            <img src="{image_url}" alt="{details["nom"]}" style="width:100%; height:auto;">
        </div>
        """
    
    # Nom et Description
    popup_content += f"""
        <h5 style="margin: 0; padding-bottom: 5px; color: #333;">{details['nom']} ({node_code})</h5>
        <p style="margin: 0 0 10px 0; font-size: 11px; color: #666;">{details['description']}</p>
        <hr style="border: 0; border-top: 1px solid #eee;">
    """
    
    # Détails du Trajet (Temps et Distance)
    
    # CAS SPÉCIAL : ARRIVÉE (S4) - Affichage de la comparaison
    if node_code == etat_final:
        popup_content += f"""
        <div style="padding: 5px 0;">
            <h5 style="color: darkgreen; margin: 5px 0 0; font-weight: bold;">Chemin Rapide (Vert): {time_A:.0f} min 🚀</h5>
            <h5 style="color: blue; margin: 5px 0 0;">Chemin Lent (Bleu): {time_B:.0f} min 🔵</h5>
            <p style="color: #CC0000; font-size: 11px; margin: 5px 0 0;">Économie de temps : {time_B - time_A:.0f} min </p>
        </div>
        """
    # CAS ARRÊT INTERMÉDIAIRE du Chemin A (Rapide)
    elif temps_cumule is not None and node_code != 'S0':
        popup_content += f"""
        <div style="display: flex; justify-content: space-around; align-items: center; padding: 5px 0;">
            
            <div style="text-align: left; font-size: 12px;">
                <p style="margin: 0; color: #666;">Distance:</p>
                <strong style="color: #444;">{distance_ecoule:.2f} km</strong>
            </div>
            
            <i class="fa fa-car" style="font-size: 28px; color: #333;"></i> 
            
            <div style="text-align: right; font-size: 12px;">
                <p style="margin: 0; color: #666;">Temps estimé:</p>
                <strong style="color: #444;">{temps_cumule:.2f} min</strong>
            </div>
        </div>
        """
    # CAS ARRÊT du Chemin B (Lent)
    elif node_code != 'S0':
        popup_content += f"""<p style="color: blue; font-size: 12px; margin: 5px 0; font-weight: bold;">Arrêt du Chemin B (Lent)</p>"""
    # CAS DÉPART (S0)
    else:
         popup_content += f"""<p style="color: #666; font-size: 12px; margin: 5px 0;">{arrets_details[node_code]['nom']}</p>"""
         
    popup_content += "</div>" # Fin du Pop-up
    
    # Ajout du marqueur à la carte
    color = 'green' if node_code == etat_final else ('red' if node_code == etat_initial else 'blue')
    
    folium.Marker(
        [lat, lon],
        popup=folium.Popup(folium.Html(popup_content, script=True), max_width=350), 
        icon=folium.Icon(color=color, icon='info-sign')
    ).add_to(m)

# Ajouter les arcs (TOUS les trajets)
for u, v, data in G.edges(data=True): 
    
    is_in_fastest_path = any((u == chemin_rapide[i] and v == chemin_rapide[i+1]) for i in range(len(chemin_rapide) - 1))
    
    line_color = 'darkgreen' if is_in_fastest_path else 'blue' 
    line_weight = 5 if is_in_fastest_path else 2
    
    tooltip_text = f"{arrets_details[u]['nom']} à {arrets_details[v]['nom']}<br>Temps estimé: {data['weight']} min"
    
    # Tooltip affichant le temps total du chemin
    if is_in_fastest_path:
        tooltip_text = f"CHEMIN A (5 ARRÊTS) - RAPIDE ! ({time_A:.0f} min total)<br>" + tooltip_text
    else:
        tooltip_text = f"CHEMIN B (7 ARRÊTS) - LENT ({time_B:.0f} min total)<br>" + tooltip_text

    folium.PolyLine(
        locations=[coords[u], coords[v]],
        color=line_color,
        weight=line_weight,
        tooltip=folium.Tooltip(tooltip_text)
    ).add_to(m)


# Sauvegarder la carte en fichier HTML
output_file = 'trajet_victoire_gare_comparaison_finale.html' 
m.save(output_file)

print(f"\n✅ Carte OSM interactive sauvegardée sous : {output_file}")
print(f"🚀 Temps Chemin Rapide (A) : {temps_total_rapide} minutes")
print(f"🐌 Temps Chemin Lent (B) : {time_B} minutes")