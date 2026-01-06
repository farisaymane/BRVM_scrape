# 📊 BRVM Data Extractor

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Selenium](https://img.shields.io/badge/Selenium-4.0+-43B02A?style=for-the-badge&logo=selenium&logoColor=white)](https://selenium.dev)
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![Tkinter](https://img.shields.io/badge/Tkinter-GUI-blue?style=for-the-badge)](https://docs.python.org/3/library/tkinter.html)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

**Application desktop complète pour l'extraction et l'analyse des données historiques de la BRVM**

[Fonctionnalités](#-fonctionnalités) • [Installation](#-installation) • [Utilisation](#-utilisation) • [Documentation](#-documentation)

<img src="https://img.shields.io/badge/BRVM-Bourse_Régionale-orange?style=for-the-badge" alt="BRVM"/>

</div>

---

## 🎯 À propos

**BRVM Data Extractor** est une application desktop Python avec interface graphique permettant d'extraire automatiquement les données historiques des actions cotées sur la **Bourse Régionale des Valeurs Mobilières (BRVM)**, la bourse commune aux 8 pays de l'UEMOA (Union Économique et Monétaire Ouest Africaine).

L'application utilise Selenium pour simuler l'interaction utilisateur sur [Sika Finance](https://www.sikafinance.com) et extraire des données complètes incluant les prix OHLC, volumes et variations.

### 🏦 Pays membres de la BRVM
Bénin 🇧🇯 • Burkina Faso 🇧🇫 • Côte d'Ivoire 🇨🇮 • Guinée-Bissau 🇬🇼 • Mali 🇲🇱 • Niger 🇳🇪 • Sénégal 🇸🇳 • Togo 🇹🇬

---

## ✨ Fonctionnalités

### 🖥️ Interface Graphique Moderne
| Fonctionnalité | Description |
|----------------|-------------|
| 📋 **Sélection intuitive** | Liste déroulante de tous les tickers BRVM disponibles |
| 📅 **Sélection de période** | Champs de dates personnalisables (début/fin) |
| 📊 **Visualisation temps réel** | Tableau de données avec défilement |
| 📈 **Barre de progression** | Suivi de l'avancement de l'extraction |
| 🎨 **Design moderne** | Interface stylisée avec thème professionnel |

### 📊 Extraction de Données
| Donnée | Description |
|--------|-------------|
| **Date** | Date de cotation |
| **Open** | Prix d'ouverture (FCFA) |
| **High** | Prix le plus haut (FCFA) |
| **Low** | Prix le plus bas (FCFA) |
| **Close** | Prix de clôture (FCFA) |
| **Volume_Titres** | Nombre de titres échangés |
| **Volume_FCFA** | Valeur totale des transactions |
| **Variation_Pct** | Variation en pourcentage |

### 📈 Analyse Technique Intégrée
- **Moyennes mobiles** (MM5, MM20)
- **RSI** (Relative Strength Index - 14 périodes)
- **Volatilité** sur 20 jours
- **Niveaux de support/résistance**
- **Statistiques descriptives** (min, max, moyenne, écart-type)

### 💾 Export Multi-formats
- **Excel (.xlsx)** avec mise en forme et statistiques
- **CSV** pour l'analyse dans d'autres outils
- **Nommage automatique** avec ticker et dates

---

## 🛠️ Technologies

```
Python 3.8+
├── tkinter              # Interface graphique native
├── selenium             # Automatisation navigateur web
├── pandas               # Manipulation de données
├── openpyxl             # Export Excel
├── python-dateutil      # Gestion des dates
└── Chrome/ChromeDriver  # Navigateur pour le scraping
```

---

## 📦 Installation

### Prérequis

- **Python 3.8+** ([Télécharger](https://www.python.org/downloads/))
- **Google Chrome** ([Télécharger](https://www.google.com/chrome/))
- **ChromeDriver** (correspondant à votre version de Chrome)

### Étapes d'installation

#### 1. Cloner le repository

```bash
git clone https://github.com/farisaymane/BRVM_scrape.git
cd BRVM_scrape
```

#### 2. Créer un environnement virtuel (recommandé)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

Ou manuellement :
```bash
pip install selenium pandas openpyxl python-dateutil
```

#### 4. Configurer ChromeDriver

**Option A - Installation automatique :**
```bash
pip install chromedriver-autoinstaller
```

**Option B - Installation manuelle :**
1. Vérifier votre version de Chrome : `chrome://version`
2. Télécharger ChromeDriver correspondant : [chromedriver.chromium.org](https://chromedriver.chromium.org/downloads)
3. Ajouter au PATH système ou placer dans le dossier du projet

---

## 🚀 Utilisation

### Méthode 1 : Interface Graphique (Recommandée)

**Windows :**
```bash
# Double-cliquez sur le fichier
BRVM Scraper.bat
```

**Ou via Python :**
```bash
python app1.py
```

### Méthode 2 : Ligne de commande

```bash
python sika2_selenium.py
```

### Méthode 3 : Import dans votre code

```python
from sika2_selenium import SikaSeleniumExtractor

# Créer l'extracteur (headless=False pour voir le navigateur)
extractor = SikaSeleniumExtractor(headless=True)

# Extraire les données
df = extractor.extract_data(
    ticker="SNTS.sn",           # Sonatel Sénégal
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# Afficher les résultats
print(f"Données extraites: {len(df)} lignes")
print(df.head())

# Sauvegarder
extractor.save_to_excel(df, "SNTS.sn")

# Fermer le navigateur
extractor.close_driver()
```

### Extraction de plusieurs tickers

```python
from sika2_selenium import SikaSeleniumExtractor

tickers = ["SNTS.sn", "BOAB.bj", "SGBC.ci", "ONTBF.bf"]
extractor = SikaSeleniumExtractor(headless=True)

for ticker in tickers:
    df = extractor.extract_data(ticker, "2024-01-01", "2024-12-31")
    if not df.empty:
        extractor.save_to_excel(df, ticker)
        print(f"✅ {ticker}: {len(df)} lignes")

extractor.close_driver()
```

---

## 📂 Structure du projet

```
BRVM_scrape/
│
├── 📜 app1.py                    # Application GUI principale
├── 📜 sika2_selenium.py          # Module d'extraction Selenium
├── 📜 BRVM Scraper.bat           # Lanceur Windows
├── 📜 requirements.txt           # Dépendances Python
├── 📜 README.md                  # Documentation
├── 📜 LICENSE                    # Licence MIT
│
├── 📁 BRVM_Downloads/            # Données exportées
│   ├── SNTS_sn_historique_*.xlsx
│   ├── BOABF_bf_historique_*.csv
│   └── ...
│
└── 📜 .gitignore                 # Fichiers ignorés
```

---

## 📊 Exemples de données extraites

### Format CSV/Excel

| Date | Open | High | Low | Close | Volume_Titres | Volume_FCFA | Variation_Pct |
|------|------|------|-----|-------|---------------|-------------|---------------|
| 2025-01-15 | 4855 | 4885 | 4855 | 4885 | 3911 | 19,046,570 | +0.72% |
| 2025-01-16 | 4885 | 4885 | 4885 | 4885 | 1170 | 5,715,450 | 0.00% |
| 2025-01-17 | 4855 | 4885 | 4885 | 4855 | 1276 | 6,214,120 | -0.61% |

### Statistiques générées

```
📊 STATISTIQUES - BOAC.ci (6 mois)
═══════════════════════════════════
Prix moyen      : 4,725.50 FCFA
Prix minimum    : 4,600.00 FCFA
Prix maximum    : 4,885.00 FCFA
Volume FCFA total: 245,890,000 FCFA
Variation moyenne: +0.15%
Plus forte hausse: +2.67%
Plus forte baisse: -2.67%
```

---

## 🔧 Configuration avancée

### Mode visible (débogage)

Dans l'interface GUI, cochez **"Mode visible (pour développeurs)"** pour voir le navigateur en action.

Ou en code :
```python
extractor = SikaSeleniumExtractor(headless=False)
```

### Personnaliser le chemin ChromeDriver

```python
extractor = SikaSeleniumExtractor(
    headless=True,
    chromedriver_path="C:/chemin/vers/chromedriver.exe"
)
```

---

## 📋 Tickers disponibles

L'application supporte **tous les titres cotés sur la BRVM**, incluant :

| Pays | Exemples de tickers |
|------|---------------------|
| 🇸🇳 Sénégal | SNTS.sn (Sonatel), TTLS.sn |
| 🇨🇮 Côte d'Ivoire | SGBC.ci, BOAC.ci, SICC.ci |
| 🇧🇯 Bénin | BOAB.bj |
| 🇧🇫 Burkina Faso | BOABF.bf, ONTBF.bf |
| 🇲🇱 Mali | BOAM.ml |
| 🇳🇪 Niger | BOAN.ne |
| 🇹🇬 Togo | ETIT.tg |

---

## ⚠️ Avertissements

- **Usage personnel** : Ce projet est destiné à des fins éducatives et d'analyse personnelle
- **Respect du serveur** : L'application inclut des délais entre les requêtes pour ne pas surcharger le serveur
- **Données** : Les données sont extraites de Sika Finance et peuvent être sujettes à des erreurs ou retards
- **Conformité** : Assurez-vous de respecter les conditions d'utilisation de Sika Finance

---

## 🐛 Dépannage

### Erreur "ChromeDriver not found"
```bash
pip install chromedriver-autoinstaller
```

### Erreur "Chrome version mismatch"
Mettez à jour ChromeDriver pour correspondre à votre version de Chrome.

### Les données ne s'affichent pas
- Vérifiez votre connexion internet
- Essayez le mode visible pour voir ce qui se passe
- Vérifiez que le ticker est valide

---

## 🤝 Contribution

Les contributions sont les bienvenues !

1. **Fork** le projet
2. **Créez** une branche (`git checkout -b feature/NouvelleFonctionnalité`)
3. **Committez** vos changements (`git commit -m 'Ajout: NouvelleFonctionnalité'`)
4. **Pushez** (`git push origin feature/NouvelleFonctionnalité`)
5. **Ouvrez** une Pull Request

---

## 📝 Roadmap

- [ ] Support multi-navigateurs (Firefox, Edge)
- [ ] API REST pour intégration externe
- [ ] Graphiques interactifs intégrés
- [ ] Extraction automatique programmée (scheduler)
- [ ] Base de données locale (SQLite)
- [ ] Alertes de prix personnalisées
- [ ] Export vers Google Sheets

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 👤 Auteur

<div align="center">

**Faris TOGUYENI**

 Étudiant en Génie Mécanique – Concentration Mécatronique  
 Université du Québec à Trois-Rivières (UQTR)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/faris-toguyeni-54b26a34a/)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/farisaymane)
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:toguyenifaris@gmail.com)

</div>

---