let currentResults = [];

let selectedProteins = new Set();

function updateSelectionUI() {
    const count = selectedProteins.size;
    const alignSection = document.getElementById('align-section');
    const selectedCount = document.getElementById('selected-count');
    
    if (count >= 2) {
        alignSection.classList.add('active');
        selectedCount.textContent = `${count} protéine(s) sélectionnée(s): ${Array.from(selectedProteins).join(', ')}`;
    } else if (count === 1) {
        alignSection.classList.add('active');
        selectedCount.textContent = `${count} protéine sélectionnée. Sélectionnez-en au moins une autre pour l'alignement.`;
    } else {
        alignSection.classList.remove('active');
    }
}

function toggleSelectAll() {
    const selectAll = document.getElementById('select-all');
    const checkboxes = document.querySelectorAll('.protein-checkbox');
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = selectAll.checked;
        if (selectAll.checked) {
            selectedProteins.add(checkbox.value);
        } else {
            selectedProteins.delete(checkbox.value);
        }
    });
    
    updateSelectionUI();
}

function toggleProteinSelection(pdbId) {
    if (selectedProteins.has(pdbId)) {
        selectedProteins.delete(pdbId);
    } else {
        selectedProteins.add(pdbId);
    }
    updateSelectionUI();
}

function clearSelection() {
    selectedProteins.clear();
    document.querySelectorAll('.protein-checkbox').forEach(cb => cb.checked = false);
    document.getElementById('select-all').checked = false;
    updateSelectionUI();
}

function generatePyMOLCommands(pdbIds, reference) {
    const colors = ['cyan', 'magenta', 'yellow', 'salmon', 'lime', 'orange', 'purple', 'marine'];
    let commands = '# Charger les structures\n';
    
    pdbIds.forEach(id => {
        commands += `fetch ${id}\n`;
    });
    
    commands += '\n# Afficher et colorer\n';
    pdbIds.forEach((id, i) => {
        const color = colors[i % colors.length];
        commands += `show cartoon, ${id}\ncolor ${color}, ${id}\n`;
    });
    
    commands += `\n# Aligner sur ${reference}\n`;
    pdbIds.forEach(id => {
        if (id !== reference) {
            commands += `align ${id}, ${reference}\n`;
        }
    });
    
    commands += '\n# Paramètres d\'affichage\n';
    commands += 'center\nzoom\nset cartoon_fancy_helices, 1\nset cartoon_fancy_sheets, 1\nbg_color white';
    
    return commands;
}

async function createAlignmentSession() {
    if (selectedProteins.size < 2) {
        alert('⚠️ Veuillez sélectionner au moins 2 protéines pour l\'alignement');
        return;
    }
    
    document.getElementById('message').innerHTML = 
        `<div class="success" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none;">
            <div style="display: flex; align-items: center; gap: 15px;">
                <div class="spinner" style="border-color: rgba(255,255,255,0.3); border-top-color: white;"></div>
                <div>
                    <strong style="font-size: 1.2em;">🧬 Création de la session d'alignement...</strong><br>
                    <span style="font-size: 0.95em; opacity: 0.95; margin-top: 5px; display: block;">Téléchargement et alignement des protéines</span>
                </div>
            </div>
        </div>`;
    
    try {
        const response = await fetch('/create_alignment_session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ pdb_ids: Array.from(selectedProteins) })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const selectedIds = Array.from(selectedProteins).join(', ');
            
            let colorLegend = '';
            if (data.colors) {
                colorLegend = '<div style="margin-top: 15px; padding: 15px; background: #f8f9fa; border-radius: 5px;">';
                colorLegend += '<h4 style="color: #495057; margin-bottom: 10px; font-size: 0.95em;">🎨 Couleurs des protéines :</h4>';
                colorLegend += '<div style="display: flex; flex-wrap: wrap; gap: 10px;">';
                for (const [pdb, color] of Object.entries(data.colors)) {
                    colorLegend += `<div style="display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: white; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                        <div style="width: 20px; height: 20px; background: ${color}; border-radius: 3px; border: 1px solid #ddd;"></div>
                        <span style="font-weight: 600; color: #495057;">${pdb}</span>
                    </div>`;
                }
                colorLegend += '</div></div>';
            }
            
            let alignmentInfo = '';
            if (data.alignment_results && data.alignment_results.length > 0) {
                alignmentInfo = '<div style="margin-top: 15px; padding: 15px; background: #e7f3ff; border-radius: 5px;">';
                alignmentInfo += '<h4 style="color: #004085; margin-bottom: 10px; font-size: 0.95em;">📊 Résultats de l\'alignement (RMSD) :</h4>';
                alignmentInfo += '<ul style="margin-left: 20px; line-height: 1.8; color: #004085;">';
                data.alignment_results.forEach(result => {
                    alignmentInfo += `<li><strong>${result.structure}</strong> vs ${result.reference}: <strong>${result.rmsd} Å</strong> (${result.atoms} atomes)</li>`;
                });
                alignmentInfo += '</ul></div>';
            }
            
            const message = `
                <div style="background: white; padding: 25px; border-radius: 12px; border: 3px solid #28a745; box-shadow: 0 4px 15px rgba(40, 167, 69, 0.2);">
                    <div style="text-align: center; margin-bottom: 20px;">
                        <div style="font-size: 4em; margin-bottom: 10px;">✅</div>
                        <h3 style="color: #28a745; margin-bottom: 10px; font-size: 1.5em;">🎉 Session PyMOL créée avec succès !</h3>
                    </div>
                    
                    <div style="background: #d4edda; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #28a745;">
                        <p style="margin-bottom: 8px; color: #155724;"><strong>✓ ${data.pdb_count} protéines chargées :</strong> ${selectedIds}</p>
                        <p style="margin-bottom: 0; color: #155724;"><strong>✓ Référence :</strong> ${data.reference}</p>
                    </div>
                    
                    ${alignmentInfo}
                    ${colorLegend}
                    
                    <div style="background: #cff4fc; padding: 15px; border-left: 4px solid #0dcaf0; border-radius: 8px; margin-top: 15px;">
                        <h4 style="color: #055160; margin-bottom: 10px; font-size: 1.1em;">💾 Comment ouvrir la session :</h4>
                        <ol style="margin-left: 20px; line-height: 2; color: #055160;">
                            <li>Téléchargez le fichier <strong>.pse</strong> ci-dessous</li>
                            <li>Ouvrez <strong>PyMOL</strong> sur votre ordinateur Windows</li>
                            <li>Dans PyMOL : <strong>File → Open...</strong></li>
                            <li>Sélectionnez le fichier <code>${data.filename}</code></li>
                            <li>Tout est déjà aligné et coloré ! ✨</li>
                        </ol>
                    </div>
                    
                    <div style="margin-top: 20px; text-align: center;">
                        <a href="${data.download_url}" class="btn" style="background: #28a745; color: white; padding: 15px 40px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 1.1em; display: inline-block;">
                            💾 Télécharger la session (.pse)
                        </a>
                    </div>
                </div>
            `;
            document.getElementById('message').innerHTML = message;
            document.getElementById('message').scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            document.getElementById('message').innerHTML = 
                `<div class="error">❌ Erreur : ${data.error}</div>`;
        }
    } catch (error) {
        document.getElementById('message').innerHTML = 
            `<div class="error">❌ Erreur de connexion : ${error.message}</div>`;
    }
}
    if (selectedProteins.size < 2) {
        alert('Veuillez sélectionner au moins 2 protéines pour l\'alignement');
        return;
    }
    
    try {
        const response = await fetch('/align_pymol', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ pdb_ids: Array.from(selectedProteins) })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const selectedIds = Array.from(selectedProteins).join(', ');
            const message = `
                <div style="background: white; padding: 20px; border-radius: 8px; border: 2px solid #6f42c1;">
                    <h3 style="color: #6f42c1; margin-bottom: 15px;">✓ Script d'alignement généré !</h3>
                    <p style="margin-bottom: 10px;"><strong>${data.pdb_count} protéines sélectionnées:</strong> ${selectedIds}</p>
                    <p style="margin-bottom: 10px;"><strong>Référence:</strong> ${data.reference} (les autres seront alignées sur celle-ci)</p>
                    
                    <div style="margin-top: 20px; padding: 15px; background: #f0f8ff; border-left: 4px solid #17a2b8; border-radius: 4px;">
                        <h4 style="color: #17a2b8; margin-bottom: 10px;">📝 Instructions pour ouvrir manuellement :</h4>
                        <ol style="margin-left: 20px; line-height: 1.8;">
                            <li>Cliquez sur le bouton <strong>"💾 Télécharger le script"</strong> ci-dessous</li>
                            <li>Ouvrez <strong>PyMOL</strong> sur votre ordinateur</li>
                            <li>Dans PyMOL, allez dans <strong>File → Run Script...</strong></li>
                            <li>Sélectionnez le fichier <code>${data.filename}</code> que vous venez de télécharger</li>
                            <li>L'alignement se fera automatiquement ! ✨</li>
                        </ol>
                    </div>
                    
                    <div style="margin-top: 20px; padding: 15px; background: #fff3cd; border-left: 4px solid #ffc107; border-radius: 4px;">
                        <h4 style="color: #856404; margin-bottom: 10px;">💡 Alternative : Commandes manuelles</h4>
                        <p style="margin-bottom: 10px;">Vous pouvez aussi copier-coller ces commandes dans la console PyMOL :</p>
                        <pre style="background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 5px; overflow-x: auto; font-family: 'Courier New', monospace; font-size: 0.9em;">${generatePyMOLCommands(Array.from(selectedProteins), data.reference)}</pre>
                    </div>
                    
                    <div style="margin-top: 20px; display: flex; gap: 10px; flex-wrap: wrap;">
                        <a href="${data.download_url}" class="btn btn-small" style="background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: 600;">
                            💾 Télécharger le script
                        </a>
                        <button class="btn btn-small" style="background: #6c757d; color: white; padding: 12px 24px; border-radius: 8px; font-weight: 600;" onclick="document.getElementById('message').innerHTML = ''">
                            ❌ Fermer
                        </button>
                    </div>
                </div>
            `;
            
            document.getElementById('message').innerHTML = 
                `<div class="success" style="background: transparent; border: none; padding: 0;">${message}</div>`;
            
            // Scroll vers le message
            document.getElementById('message').scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            document.getElementById('message').innerHTML = 
                `<div class="error">Erreur: ${data.error}</div>`;
        }
    } catch (error) {
        document.getElementById('message').innerHTML = 
            `<div class="error">Erreur: ${error.message}</div>`;
    }
}

async function alignInPyMOL() {
    if (selectedProteins.size < 2) {
        alert('⚠️ Veuillez sélectionner au moins 2 protéines pour l\'alignement');
        return;
    }
    
    // Afficher un message de chargement
    document.getElementById('message').innerHTML = 
        `<div class="success" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none;">
            <div style="display: flex; align-items: center; gap: 15px;">
                <div class="spinner" style="border-color: rgba(255,255,255,0.3); border-top-color: white;"></div>
                <div>
                    <strong style="font-size: 1.2em;">🚀 Lancement de PyMOL en cours...</strong><br>
                    <span style="font-size: 0.95em; opacity: 0.95; margin-top: 5px; display: block;">Création du script d'alignement et ouverture de PyMOL</span>
                </div>
            </div>
        </div>`;
    
    try {
        const response = await fetch('/align_and_launch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ pdb_ids: Array.from(selectedProteins) })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const selectedIds = Array.from(selectedProteins).join(', ');
            
            if (data.launched) {
                // PyMOL a été lancé avec succès
                let colorLegend = '';
                if (data.colors) {
                    colorLegend = '<div style="margin-top: 15px; padding: 15px; background: #f8f9fa; border-radius: 5px;">';
                    colorLegend += '<h4 style="color: #495057; margin-bottom: 10px; font-size: 0.95em;">🎨 Légende des couleurs :</h4>';
                    colorLegend += '<div style="display: flex; flex-wrap: wrap; gap: 10px;">';
                    for (const [pdb, color] of Object.entries(data.colors)) {
                        colorLegend += `<div style="display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: white; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                            <div style="width: 20px; height: 20px; background: ${color}; border-radius: 3px; border: 1px solid #ddd;"></div>
                            <span style="font-weight: 600; color: #495057;">${pdb}</span>
                        </div>`;
                    }
                    colorLegend += '</div></div>';
                }
                
                const message = `
                    <div style="background: white; padding: 25px; border-radius: 12px; border: 3px solid #28a745; box-shadow: 0 4px 15px rgba(40, 167, 69, 0.2);">
                        <div style="text-align: center; margin-bottom: 20px;">
                            <div style="font-size: 4em; margin-bottom: 10px; animation: bounceIn 0.6s;">✅</div>
                            <h3 style="color: #28a745; margin-bottom: 10px; font-size: 1.5em;">🎉 PyMOL lancé avec succès !</h3>
                        </div>
                        
                        <div style="background: #d4edda; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #28a745;">
                            <p style="margin-bottom: 8px; color: #155724;"><strong>✓ ${data.pdb_count} protéines chargées :</strong> ${selectedIds}</p>
                            <p style="margin-bottom: 0; color: #155724;"><strong>✓ Référence :</strong> ${data.reference} (les autres sont alignées sur celle-ci)</p>
                        </div>
                        
                        ${colorLegend}
                        
                        <div style="background: #cff4fc; padding: 15px; border-left: 4px solid #0dcaf0; border-radius: 8px; margin-top: 15px;">
                            <h4 style="color: #055160; margin-bottom: 10px; font-size: 1.1em;">👁️ Que voir dans PyMOL ?</h4>
                            <ul style="margin-left: 20px; line-height: 2; color: #055160;">
                                <li>Les structures sont affichées en <strong>cartoon</strong></li>
                                <li>Chaque protéine a une <strong>couleur différente</strong></li>
                                <li>L'<strong>alignement structural</strong> est déjà effectué !</li>
                                <li>Le <strong>RMSD</strong> est affiché dans la console PyMOL</li>
                                <li>Vous pouvez <strong>faire pivoter</strong> la vue avec la souris</li>
                            </ul>
                        </div>
                        
                        <div style="margin-top: 20px; text-align: center;">
                            <button class="btn" style="background: #28a745; color: white; padding: 12px 30px; border-radius: 8px; font-weight: 600; font-size: 1em;" onclick="document.getElementById('message').innerHTML = ''">
                                ✓ Parfait, Compris !
                            </button>
                        </div>
                    </div>
                `;
                document.getElementById('message').innerHTML = message;
            } else {
                // PyMOL n'a pas pu être lancé, afficher les instructions
                const message = `
                    <div style="background: white; padding: 20px; border-radius: 12px; border: 2px solid #ffc107; box-shadow: 0 4px 15px rgba(255, 193, 7, 0.2);">
                        <h3 style="color: #856404; margin-bottom: 15px; font-size: 1.3em;">⚠️ PyMOL non lancé automatiquement</h3>
                        <p style="margin-bottom: 15px; color: #856404; line-height: 1.6;">${data.message}</p>
                        <p style="margin-bottom: 10px; color: #333;"><strong>${data.pdb_count} protéines sélectionnées :</strong> ${selectedIds}</p>
                        
                        <div style="margin-top: 20px; padding: 15px; background: #f0f8ff; border-left: 4px solid #17a2b8; border-radius: 8px;">
                            <h4 style="color: #17a2b8; margin-bottom: 10px;">📝 Ouvrez le script manuellement :</h4>
                            <ol style="margin-left: 20px; line-height: 2;">
                                <li>Téléchargez le script ci-dessous</li>
                                <li>Ouvrez <strong>PyMOL</strong></li>
                                <li>Dans PyMOL : <strong>File → Run Script...</strong></li>
                                <li>Sélectionnez le fichier <code>${data.filename}</code></li>
                                <li>L'alignement se fera automatiquement ! ✨</li>
                            </ol>
                        </div>
                        
                        <div style="background: #fff3cd; padding: 12px; border-left: 4px solid #ffc107; border-radius: 8px; margin-top: 15px;">
                            <p style="margin: 0; color: #856404; font-size: 0.95em;">
                                <strong>💡 Info :</strong> ${data.error_details || 'PyMOL doit être installé et accessible depuis la ligne de commande.'}
                            </p>
                        </div>
                        
                        <div style="margin-top: 20px; display: flex; gap: 10px; flex-wrap: wrap; justify-content: center;">
                            <a href="${data.download_url}" class="btn" style="background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block;">
                                💾 Télécharger le script
                            </a>
                            <button class="btn" style="background: #6c757d; color: white; padding: 12px 24px; border-radius: 8px; font-weight: 600;" onclick="document.getElementById('message').innerHTML = ''">
                                ❌ Fermer
                            </button>
                        </div>
                    </div>
                `;
                document.getElementById('message').innerHTML = message;
            }
            
            // Scroll vers le message
            document.getElementById('message').scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            document.getElementById('message').innerHTML = 
                `<div class="error">❌ Erreur : ${data.error}</div>`;
        }
    } catch (error) {
        document.getElementById('message').innerHTML = 
            `<div class="error">❌ Erreur de connexion : ${error.message}</div>`;
    }
}

async function launchAlignment(scriptFilename) {
    try {
        const response = await fetch('/launch_alignment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ script_filename: scriptFilename })
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('message').innerHTML = 
                `<div class="success">✓ ${data.message}</div>`;
        } else {
            document.getElementById('message').innerHTML = 
                `<div class="error">Erreur: ${data.error}</div>`;
        }
    } catch (error) {
        document.getElementById('message').innerHTML = 
            `<div class="error">Erreur: ${error.message}</div>`;
    }
}

function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    document.getElementById(tabName + '-tab').classList.add('active');
    event.target.classList.add('active');
}

async function search(searchType) {
    let searchData = {
        search_type: searchType,
        max_results: 10
    };
    
    if (searchType === 'keyword') {
        searchData.keyword = document.getElementById('keyword-input').value;
        searchData.max_results = document.getElementById('keyword-max').value;
    } else if (searchType === 'name') {
        searchData.protein_name = document.getElementById('name-input').value;
        searchData.max_results = document.getElementById('name-max').value;
    } else if (searchType === 'organism') {
        searchData.organism = document.getElementById('organism-input').value;
        searchData.max_results = document.getElementById('organism-max').value;
    } else if (searchType === 'id') {
        searchData.pdb_id = document.getElementById('id-input').value;
    } else if (searchType === 'resolution') {
        searchData.resolution = document.getElementById('resolution-input').value;
        searchData.max_results = document.getElementById('resolution-max').value;
    } else if (searchType === 'advanced') {
        searchData.protein_name = document.getElementById('advanced-name').value;
        searchData.organism = document.getElementById('advanced-organism').value;
        searchData.resolution = document.getElementById('advanced-resolution').value;
        searchData.max_results = document.getElementById('advanced-max').value;
    }
    
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').style.display = 'none';
    document.getElementById('message').innerHTML = '';
    
    // Réinitialiser la sélection
    clearSelection();
    
    try {
        const response = await fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(searchData)
        });
        
        const data = await response.json();
        
        document.getElementById('loading').style.display = 'none';
        
        if (data.success) {
            currentResults = data.results;
            displayResults(data.results);
            document.getElementById('message').innerHTML = 
                `<div class="success">✓ ${data.count} résultat(s) trouvé(s)</div>`;
        } else {
            document.getElementById('message').innerHTML = 
                `<div class="error">Erreur: ${data.error}</div>`;
        }
    } catch (error) {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('message').innerHTML = 
            `<div class="error">Erreur de connexion: ${error.message}</div>`;
    }
}

function displayResults(results) {
    const tbody = document.getElementById('results-body');
    tbody.innerHTML = '';
    
    if (results.length === 0) {
        document.getElementById('results').style.display = 'block';
        tbody.innerHTML = '<tr><td colspan="8" class="no-results">Aucun résultat trouvé</td></tr>';
        return;
    }
    
    document.getElementById('results-count').textContent = `${results.length} résultat(s) trouvé(s)`;
    
    results.forEach(protein => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><input type="checkbox" class="protein-checkbox" value="${protein.PDB_ID}" onchange="toggleProteinSelection('${protein.PDB_ID}')"></td>
            <td><a href="https://www.rcsb.org/structure/${protein.PDB_ID}" target="_blank" class="pdb-link">${protein.PDB_ID}</a></td>
            <td>${protein.Title}</td>
            <td>${protein.Resolution}</td>
            <td>${protein.Experimental_Method}</td>
            <td>${protein.Release_Date}</td>
            <td>${protein.Organism}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn-small btn-pymol" onclick="openInPyMOL('${protein.PDB_ID}')" title="Ouvrir dans PyMOL">
                        🔬 PyMOL
                    </button>
                    <a href="/download_pdb/${protein.PDB_ID}" class="btn-small btn-download" title="Télécharger PDB">
                        💾 PDB
                    </a>
                    <a href="/pymol_script/${protein.PDB_ID}" class="btn-small btn-script" title="Script PyMOL">
                        📜 Script
                    </a>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
    
    document.getElementById('results').style.display = 'block';
}

async function exportResults() {
    if (currentResults.length === 0) {
        alert('Aucun résultat à exporter');
        return;
    }
    
    try {
        const response = await fetch('/export', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ results: currentResults })
        });
        
        const data = await response.json();
        
        if (data.success) {
            window.location.href = data.download_url;
            document.getElementById('message').innerHTML = 
                `<div class="success">✓ Export réussi! Le téléchargement va commencer...</div>`;
        } else {
            document.getElementById('message').innerHTML = 
                `<div class="error">Erreur lors de l'export: ${data.error}</div>`;
        }
    } catch (error) {
        document.getElementById('message').innerHTML = 
            `<div class="error">Erreur de connexion: ${error.message}</div>`;
    }
}

async function openInPyMOL(pdbId) {
    try {
        const response = await fetch(`/open_pymol/${pdbId}`);
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('message').innerHTML = 
                `<div class="success">✓ ${data.message}</div>`;
        } else {
            if (confirm(`Impossible de lancer PyMOL automatiquement.\n\nVoulez-vous télécharger le fichier PDB pour l'ouvrir manuellement dans PyMOL ?`)) {
                window.location.href = `/download_pdb/${pdbId}`;
            }
        }
    } catch (error) {
        if (confirm(`Erreur: ${error.message}\n\nVoulez-vous télécharger le fichier PDB pour l'ouvrir manuellement dans PyMOL ?`)) {
            window.location.href = `/download_pdb/${pdbId}`;
        }
    }
}

// Recherche en appuyant sur Entrée
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !this.classList.contains('protein-checkbox')) {
                const tabId = this.closest('.tab-content').id.replace('-tab', '');
                search(tabId);
            }
        });
    });
});
