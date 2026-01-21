import pandas as pd
import matplotlib.pyplot as plt

# Charger les séquences d'acides aminés depuis le CSV
df = pd.read_csv('aa_sequences_varlen.csv')

# Afficher les premières lignes
print(df.head())
print(f"\nNombre de séquences: {len(df)}\n")

# Compter le nombre d'acides aminés pour chaque séquence
df['amino_acids_count'] = df['sequence'].str.len()

# Afficher les statistiques
print(df[['id', 'amino_acids_count']].head(10))
print(f"\nMoyenne d'acides aminés par séquence: {df['amino_acids_count'].mean():.2f}")
print(f"Min: {df['amino_acids_count'].min()}, Max: {df['amino_acids_count'].max()}")

# Créer le graphique en barres
plt.figure(figsize=(14, 6))
plt.bar(df['id'], df['amino_acids_count'], color='steelblue', alpha=0.8)
plt.xlabel('ID de la séquence', fontsize=12)
plt.ylabel('Nombre d\'acides aminés', fontsize=12)
plt.title('Nombre d\'acides aminés par séquence', fontsize=14, fontweight='bold')
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.show()
