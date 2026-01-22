"""



Application web Flask pour la recherche de protéines dans RCSB PDB
Avec système d'authentification
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session, flash
import requests
import json
import pandas as pd
from typing import List, Dict, Optional
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from functools import wraps
import subprocess
import tempfile
import time

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_super_securisee_changez_moi'  # CHANGEZ CETTE CLÉ EN PRODUCTION !

# Configuration de la base de données
DATABASE = 'users.db'

def init_db():
    """Initialiser la base de données des utilisateurs"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialiser la base de données au démarrage
init_db()

def get_db_connection():
    """Obtenir une connexion à la base de données"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    """Décorateur pour protéger les routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

class RCSBPDBSearch:
    """Classe pour interagir avec l'API RCSB PDB"""
    
    def __init__(self):
        self.search_url = "https://search.rcsb.org/rcsbsearch/v2/query"
        self.data_url = "https://data.rcsb.org/rest/v1/core/entry"
        
    def search_by_id(self, pdb_id: str) -> Optional[Dict]:
        """Récupère les informations détaillées d'une protéine par son ID PDB."""
        url = f"{self.data_url}/{pdb_id.upper()}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la récupération de {pdb_id}: {e}")
            return None
    
    def search_by_name(self, protein_name: str, max_results: int = 10) -> List[str]:
        """Recherche des protéines par nom."""
        query = {
            "query": {
                "type": "terminal",
                "service": "text",
                "parameters": {
                    "attribute": "struct.title",
                    "operator": "contains_phrase",
                    "value": protein_name
                }
            },
            "return_type": "entry",
            "request_options": {
                "return_all_hits": False,
                "results_verbosity": "compact",
                "sort": [{"sort_by": "score", "direction": "desc"}],
                "scoring_strategy": "combined"
            }
        }
        
        return self._execute_query(query, max_results)
    
    def search_by_organism(self, organism: str, max_results: int = 10) -> List[str]:
        """Recherche des protéines par organisme source."""
        query = {
            "query": {
                "type": "terminal",
                "service": "text",
                "parameters": {
                    "attribute": "rcsb_entity_source_organism.scientific_name",
                    "operator": "exact_match",
                    "value": organism
                }
            },
            "return_type": "entry",
            "request_options": {
                "return_all_hits": False,
                "results_verbosity": "compact",
                "sort": [{"sort_by": "score", "direction": "desc"}]
            }
        }
        
        return self._execute_query(query, max_results)
    
    def search_by_keyword(self, keyword: str, max_results: int = 10) -> List[str]:
        """Recherche générale par mot-clé."""
        query = {
            "query": {
                "type": "terminal",
                "service": "full_text",
                "parameters": {
                    "value": keyword
                }
            },
            "return_type": "entry",
            "request_options": {
                "return_all_hits": False,
                "results_verbosity": "compact"
            }
        }
        
        return self._execute_query(query, max_results)
    
    def search_by_resolution(self, max_resolution: float, max_results: int = 10) -> List[str]:
        """Recherche des structures avec une résolution maximale donnée."""
        query = {
            "query": {
                "type": "terminal",
                "service": "text",
                "parameters": {
                    "attribute": "rcsb_entry_info.resolution_combined",
                    "operator": "less_or_equal",
                    "value": max_resolution
                }
            },
            "return_type": "entry",
            "request_options": {
                "return_all_hits": False,
                "results_verbosity": "compact",
                "sort": [{"sort_by": "rcsb_entry_info.resolution_combined", "direction": "asc"}]
            }
        }
        
        return self._execute_query(query, max_results)
    
    def advanced_search(self, protein_name: str, organism: str = None, 
                       max_resolution: float = None, max_results: int = 10) -> List[str]:
        """Recherche avancée combinant plusieurs critères."""
        queries = [
            {
                "type": "terminal",
                "service": "text",
                "parameters": {
                    "attribute": "struct.title",
                    "operator": "contains_phrase",
                    "value": protein_name
                }
            }
        ]
        
        if organism:
            queries.append({
                "type": "terminal",
                "service": "text",
                "parameters": {
                    "attribute": "rcsb_entity_source_organism.scientific_name",
                    "operator": "exact_match",
                    "value": organism
                }
            })
        
        if max_resolution:
            queries.append({
                "type": "terminal",
                "service": "text",
                "parameters": {
                    "attribute": "rcsb_entry_info.resolution_combined",
                    "operator": "less_or_equal",
                    "value": max_resolution
                }
            })
        
        query = {
            "query": {
                "type": "group",
                "logical_operator": "and",
                "nodes": queries
            },
            "return_type": "entry",
            "request_options": {
                "return_all_hits": False,
                "results_verbosity": "compact",
                "sort": [{"sort_by": "score", "direction": "desc"}]
            }
        }
        
        return self._execute_query(query, max_results)
    
    def _execute_query(self, query: Dict, max_results: int = 10) -> List[str]:
        """Exécute une requête sur l'API RCSB."""
        try:
            response = requests.post(
                self.search_url,
                json=query,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            data = response.json()
            
            if not isinstance(data, dict):
                return []
            
            if "result_set" in data and data["result_set"]:
                if not isinstance(data["result_set"], list):
                    return []
                
                results = []
                for item in data["result_set"][:max_results]:
                    if isinstance(item, dict) and "identifier" in item:
                        results.append(item["identifier"])
                    elif isinstance(item, str):
                        results.append(item)
                
                return results
            else:
                return []
                
        except Exception as e:
            print(f"Erreur lors de la requête: {e}")
            return []
    
    def get_protein_details(self, pdb_ids: List[str]) -> List[Dict]:
        """Récupère les détails de plusieurs protéines."""
        proteins_data = []
        
        for pdb_id in pdb_ids:
            if not isinstance(pdb_id, str):
                continue
                
            data = self.search_by_id(pdb_id)
            
            if data and isinstance(data, dict):
                try:
                    protein_info = {
                        'PDB_ID': pdb_id,
                        'Title': 'N/A',
                        'Resolution': 'N/A',
                        'Experimental_Method': 'N/A',
                        'Release_Date': 'N/A',
                        'Organism': 'N/A'
                    }
                    
                    if 'struct' in data and isinstance(data['struct'], dict):
                        protein_info['Title'] = data['struct'].get('title', 'N/A')
                    
                    if 'rcsb_entry_info' in data and isinstance(data['rcsb_entry_info'], dict):
                        res = data['rcsb_entry_info'].get('resolution_combined')
                        if res:
                            if isinstance(res, list) and len(res) > 0:
                                protein_info['Resolution'] = res[0]
                            elif isinstance(res, (int, float)):
                                protein_info['Resolution'] = res
                    
                    if 'exptl' in data and isinstance(data['exptl'], list) and len(data['exptl']) > 0:
                        if isinstance(data['exptl'][0], dict):
                            protein_info['Experimental_Method'] = data['exptl'][0].get('method', 'N/A')
                    
                    if 'rcsb_accession_info' in data and isinstance(data['rcsb_accession_info'], dict):
                        protein_info['Release_Date'] = data['rcsb_accession_info'].get('initial_release_date', 'N/A')
                    
                    if 'rcsb_entity_source_organism' in data:
                        organisms = data['rcsb_entity_source_organism']
                        if isinstance(organisms, list) and len(organisms) > 0:
                            if isinstance(organisms[0], dict):
                                protein_info['Organism'] = organisms[0].get('scientific_name', 'N/A')
                    
                    proteins_data.append(protein_info)
                    
                except Exception as e:
                    print(f"Erreur lors de l'extraction des données pour {pdb_id}: {e}")
        
        return proteins_data


# Initialiser le searcher
pdb_search = RCSBPDBSearch()

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Connexion réussie !', 'success')
            return redirect(url_for('index'))
        else:
            flash('Identifiant ou mot de passe incorrect', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Page d'inscription"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username or not email or not password:
            flash('Tous les champs sont requis', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Le mot de passe doit contenir au moins 6 caractères', 'error')
            return render_template('register.html')
        
        # Vérifier si l'utilisateur existe déjà
        conn = get_db_connection()
        existing_user = conn.execute('SELECT * FROM users WHERE username = ? OR email = ?', 
                                    (username, email)).fetchone()
        
        if existing_user:
            conn.close()
            flash('Cet identifiant ou email est déjà utilisé', 'error')
            return render_template('register.html')
        
        # Créer l'utilisateur
        hashed_password = generate_password_hash(password)
        conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                    (username, email, hashed_password))
        conn.commit()
        conn.close()
        
        flash('Compte créé avec succès ! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Déconnexion"""
    session.clear()
    flash('Vous avez été déconnecté', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Page d'accueil"""
    return render_template('index.html', username=session.get('username'))

@app.route('/search', methods=['POST'])
@login_required
def search():
    """Endpoint de recherche"""
    try:
        data = request.get_json()
        search_type = data.get('search_type')
        max_results = int(data.get('max_results', 10))
        
        results_ids = []
        
        if search_type == 'keyword':
            keyword = data.get('keyword', '')
            results_ids = pdb_search.search_by_keyword(keyword, max_results)
            
        elif search_type == 'name':
            protein_name = data.get('protein_name', '')
            results_ids = pdb_search.search_by_name(protein_name, max_results)
            
        elif search_type == 'organism':
            organism = data.get('organism', '')
            results_ids = pdb_search.search_by_organism(organism, max_results)
            
        elif search_type == 'id':
            pdb_id = data.get('pdb_id', '')
            results_ids = [pdb_id.upper()]
            
        elif search_type == 'resolution':
            resolution = float(data.get('resolution', 2.0))
            results_ids = pdb_search.search_by_resolution(resolution, max_results)
            
        elif search_type == 'advanced':
            protein_name = data.get('protein_name', '')
            organism = data.get('organism', '') or None
            resolution = data.get('resolution', '') 
            resolution = float(resolution) if resolution else None
            results_ids = pdb_search.advanced_search(protein_name, organism, resolution, max_results)
        
        # Récupérer les détails
        proteins = pdb_search.get_protein_details(results_ids)
        
        return jsonify({
            'success': True,
            'count': len(proteins),
            'results': proteins
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/export', methods=['POST'])
def export():
    """Exporter les résultats en CSV"""
    try:
        data = request.get_json()
        results = data.get('results', [])
        
        if not results:
            return jsonify({'success': False, 'error': 'Aucun résultat à exporter'}), 400
        
        # Créer le DataFrame
        df = pd.DataFrame(results)
        
        # Sauvegarder dans un fichier temporaire
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'pdb_search_results_{timestamp}.csv'
        filepath = os.path.join('static', filename)
        
        # Créer le dossier static s'il n'existe pas
        os.makedirs('static', exist_ok=True)
        
        df.to_csv(filepath, index=False)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'download_url': f'/download/{filename}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/download/<filename>')
def download(filename):
    """Télécharger un fichier CSV"""
    filepath = os.path.join('static', filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return "Fichier non trouvé", 404

@app.route('/download_pdb/<pdb_id>')
def download_pdb(pdb_id):
    """Télécharger un fichier PDB"""
    try:
        pdb_id = pdb_id.upper()
        
        # URL du fichier PDB sur RCSB
        pdb_url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
        
        # Télécharger le fichier PDB
        response = requests.get(pdb_url)
        response.raise_for_status()
        
        # Sauvegarder dans le dossier static
        os.makedirs('static/pdb_files', exist_ok=True)
        filepath = os.path.join('static', 'pdb_files', f'{pdb_id}.pdb')
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return send_file(filepath, as_attachment=True, download_name=f'{pdb_id}.pdb')
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/pymol_script/<pdb_id>')
def pymol_script(pdb_id):
    """Générer un script PyMOL pour ouvrir la structure"""
    try:
        pdb_id = pdb_id.upper()
        
        # Créer un script PyMOL
        script_content = f"""# Script PyMOL pour {pdb_id}
fetch {pdb_id}, async=0
center {pdb_id}
zoom {pdb_id}
show cartoon
color spectrum
set cartoon_fancy_helices, 1
set cartoon_fancy_sheets, 1
bg_color white
"""
        
        # Sauvegarder le script
        os.makedirs('static/pymol_scripts', exist_ok=True)
        script_path = os.path.join('static', 'pymol_scripts', f'{pdb_id}.pml')
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        return send_file(script_path, as_attachment=True, download_name=f'{pdb_id}.pml')
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/open_pymol/<pdb_id>')
def open_pymol(pdb_id):
    """Lancer PyMOL avec la structure (nécessite PyMOL installé)"""
    try:
        pdb_id = pdb_id.upper()
        
        # Créer un script temporaire
        script_content = f"""import pymol
from pymol import cmd

pymol.finish_launching(['pymol', '-q'])

cmd.fetch('{pdb_id}')
cmd.center('{pdb_id}')
cmd.zoom('{pdb_id}')
cmd.show('cartoon')
cmd.color('spectrum')
cmd.set('cartoon_fancy_helices', 1)
cmd.set('cartoon_fancy_sheets', 1)
cmd.bg_color('white')
"""
        
        os.makedirs('static/pymol_scripts', exist_ok=True)
        script_path = os.path.join('static', 'pymol_scripts', f'open_{pdb_id}.py')
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Essayer de lancer PyMOL (fonctionnera seulement si PyMOL est installé)
        import subprocess
        import sys
        
        # Différentes commandes selon l'OS
        if sys.platform == 'win32':
            cmd = ['pymol', script_path]
        elif sys.platform == 'darwin':  # macOS
            cmd = ['/Applications/PyMOL.app/Contents/MacOS/PyMOL', script_path]
        else:  # Linux
            cmd = ['pymol', script_path]
        
        subprocess.Popen(cmd)
        
        return jsonify({
            'success': True,
            'message': f'PyMOL lancé avec {pdb_id}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Impossible de lancer PyMOL: {str(e)}. Veuillez télécharger le fichier PDB manuellement.'
        }), 400

@app.route('/align_pymol', methods=['POST'])
def align_pymol():
    """Générer un script PyMOL pour aligner plusieurs structures"""
    try:
        data = request.get_json()
        pdb_ids = data.get('pdb_ids', [])
        
        if len(pdb_ids) < 2:
            return jsonify({
                'success': False,
                'error': 'Veuillez sélectionner au moins 2 protéines pour l\'alignement'
            }), 400
        
        # Convertir en majuscules
        pdb_ids = [pdb_id.upper() for pdb_id in pdb_ids]
        
        # Créer un script PyMOL pour l'alignement
        script_content = f"""# Script PyMOL - Alignement de structures
# Protéines: {', '.join(pdb_ids)}
# Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Charger toutes les structures
"""
        
        colors = ['cyan', 'magenta', 'yellow', 'salmon', 'lime', 'orange', 'purple', 'marine']
        
        for pdb_id in pdb_ids:
            script_content += f"fetch {pdb_id}, async=0\n"
        
        script_content += "\n# Afficher en cartoon\n"
        for i, pdb_id in enumerate(pdb_ids):
            color = colors[i % len(colors)]
            script_content += f"show cartoon, {pdb_id}\n"
            script_content += f"color {color}, {pdb_id}\n"
        
        # Utiliser la première structure comme référence
        reference = pdb_ids[0]
        script_content += f"\n# Alignement structural sur {reference} (référence)\n"
        
        for pdb_id in pdb_ids[1:]:
            script_content += f"align {pdb_id}, {reference}\n"
        
        script_content += f"\n# Centrer et zoomer\n"
        script_content += f"center\n"
        script_content += f"zoom\n"
        
        script_content += "\n# Paramètres d'affichage\n"
        script_content += "set cartoon_fancy_helices, 1\n"
        script_content += "set cartoon_fancy_sheets, 1\n"
        script_content += "bg_color white\n"
        script_content += "set seq_view, on\n"
        
        script_content += "\n# Afficher le RMSD dans la console\n"
        for pdb_id in pdb_ids[1:]:
            script_content += f"print('RMSD {reference} vs {pdb_id}:')\n"
        
        script_content += "\n# Légende des couleurs\n"
        for i, pdb_id in enumerate(pdb_ids):
            color = colors[i % len(colors)]
            script_content += f"# {pdb_id}: {color}\n"
        
        # Sauvegarder le script
        os.makedirs('static/pymol_scripts', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'align_{"-".join(pdb_ids[:3])}_{timestamp}.pml'
        script_path = os.path.join('static', 'pymol_scripts', filename)
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'download_url': f'/download_pymol_script/{filename}',
            'pdb_count': len(pdb_ids),
            'reference': reference,
            'pdb_ids': pdb_ids,
            'colors': {pdb_ids[i]: colors[i % len(colors)] for i in range(len(pdb_ids))}
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/download_pymol_script/<filename>')
def download_pymol_script(filename):
    """Télécharger un script PyMOL"""
    filepath = os.path.join('static', 'pymol_scripts', filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return "Fichier non trouvé", 404

@app.route('/create_alignment_session', methods=['POST'])
@login_required
def create_alignment_session():
    """Créer une session PyMOL avec alignement des protéines sélectionnées"""
    try:
        data = request.get_json()
        pdb_ids = data.get('pdb_ids', [])
        
        if len(pdb_ids) < 2:
            return jsonify({
                'success': False,
                'error': 'Veuillez sélectionner au moins 2 protéines pour l\'alignement'
            }), 400
        
        pdb_ids = [pdb_id.upper() for pdb_id in pdb_ids]
        
        # Créer le dossier pour les sessions
        os.makedirs('static/pymol_sessions', exist_ok=True)
        
        # Nom du fichier de session
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        session_filename = f'alignment_{"_".join(pdb_ids[:3])}_{timestamp}.pse'
        session_path = os.path.abspath(os.path.join('static', 'pymol_sessions', session_filename))
        
        # Couleurs pour chaque protéine
        colors = ['cyan', 'magenta', 'yellow', 'salmon', 'lime', 'orange', 'purple', 'marine']
        
        # Créer un script Python temporaire pour PyMOL
        pymol_script = f"""#!/usr/bin/env python3
# Script PyMOL pour alignement de structures
import pymol
from pymol import cmd
import json
import sys

try:
    # Lancer PyMOL en mode headless
    pymol.finish_launching(['pymol', '-c'])
    
    # Liste des PDB IDs
    pdb_ids = {pdb_ids}
    colors = {colors}
    
    # Charger toutes les structures
    print('Chargement des structures...')
    for pdb_id in pdb_ids:
        cmd.fetch(pdb_id, type='pdb', async_=0)
        print(f'Chargé: {{pdb_id}}')
    
    # Appliquer les couleurs et afficher en cartoon
    print('Application des couleurs...')
    for i, pdb_id in enumerate(pdb_ids):
        color = colors[i % len(colors)]
        cmd.show('cartoon', pdb_id)
        cmd.color(color, pdb_id)
        print(f'{{pdb_id}}: {{color}}')
    
    # Faire l'alignement (première protéine = référence)
    reference = pdb_ids[0]
    alignment_results = []
    
    print(f'Alignement sur référence: {{reference}}')
    for pdb_id in pdb_ids[1:]:
        result = cmd.align(pdb_id, reference)
        rmsd = result[0]
        aligned_atoms = result[1]
        alignment_results.append({{
            'structure': pdb_id,
            'reference': reference,
            'rmsd': round(rmsd, 3),
            'atoms': aligned_atoms
        }})
        print(f'RMSD {{pdb_id}} vs {{reference}}: {{rmsd:.3f}} Å ({{aligned_atoms}} atomes)')
    
    # Paramètres d'affichage
    cmd.center()
    cmd.zoom()
    cmd.set('cartoon_fancy_helices', 1)
    cmd.set('cartoon_fancy_sheets', 1)
    cmd.bg_color('white')
    cmd.set('seq_view', 1)
    
    # Sauvegarder la session
    print(f'Sauvegarde de la session: {session_path}')
    cmd.save('{session_path}')
    
    # Écrire les résultats dans un fichier JSON
    results_file = '{session_path}.json'
    with open(results_file, 'w') as f:
        json.dump({{
            'success': True,
            'alignment_results': alignment_results,
            'pdb_ids': pdb_ids,
            'reference': reference
        }}, f)
    
    print('Session créée avec succès!')
    cmd.quit()
    sys.exit(0)
    
except Exception as e:
    print(f'Erreur: {{e}}', file=sys.stderr)
    # Écrire l'erreur dans le fichier JSON
    results_file = '{session_path}.json'
    with open(results_file, 'w') as f:
        json.dump({{
            'success': False,
            'error': str(e)
        }}, f)
    sys.exit(1)
"""
        
        # Créer un fichier temporaire pour le script
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(pymol_script)
            temp_script_path = temp_file.name
        
        try:
            # Exécuter PyMOL dans un subprocess isolé avec timeout
            print(f'Exécution du script PyMOL: {temp_script_path}')
            result = subprocess.run(
                ['python3', temp_script_path],
                capture_output=True,
                text=True,
                timeout=60  # Timeout de 60 secondes
            )
            
            # Afficher la sortie pour debug
            if result.stdout:
                print('PyMOL stdout:', result.stdout)
            if result.stderr:
                print('PyMOL stderr:', result.stderr)
            
            # Lire les résultats du fichier JSON
            results_json_path = f'{session_path}.json'
            time.sleep(0.5)  # Petit délai pour s'assurer que le fichier est écrit
            
            if os.path.exists(results_json_path):
                with open(results_json_path, 'r') as f:
                    pymol_results = json.load(f)
                
                # Nettoyer le fichier JSON temporaire
                os.remove(results_json_path)
                
                if not pymol_results.get('success', False):
                    return jsonify({
                        'success': False,
                        'error': pymol_results.get('error', 'Erreur inconnue lors de la création de la session')
                    }), 400
                
                # Vérifier que le fichier .pse a été créé
                if not os.path.exists(session_path):
                    return jsonify({
                        'success': False,
                        'error': 'Le fichier de session n\'a pas été créé'
                    }), 400
                
                alignment_results = pymol_results.get('alignment_results', [])
            else:
                # Fichier JSON non trouvé, vérifier si le fichier .pse existe
                if os.path.exists(session_path):
                    alignment_results = []
                    print('Session créée mais pas de résultats d\'alignement disponibles')
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Échec de la création de la session PyMOL'
                    }), 400
            
            return jsonify({
                'success': True,
                'filename': session_filename,
                'download_url': f'/download_session/{session_filename}',
                'pdb_count': len(pdb_ids),
                'reference': pdb_ids[0],
                'pdb_ids': pdb_ids,
                'colors': {pdb_ids[i]: colors[i % len(colors)] for i in range(len(pdb_ids))},
                'alignment_results': alignment_results,
                'rmsd_results': alignment_results  # Alias pour compatibilité frontend
            })
            
        finally:
            # Nettoyer le script temporaire
            try:
                if os.path.exists(temp_script_path):
                    os.remove(temp_script_path)
            except:
                pass
        
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Timeout: La création de la session PyMOL a pris trop de temps (>60s)'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur: {str(e)}'
        }), 400

@app.route('/download_session/<filename>')
@login_required
def download_session(filename):
    """Télécharger un fichier de session PyMOL"""
    filepath = os.path.join('static', 'pymol_sessions', filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True, download_name=filename)
    else:
        return "Fichier non trouvé", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
