# TP DevOps - Ansible — Déploiement d'une API FastAPI

Projet du TP DevOps S8 : déploiement complet automatisé d'une application web minimaliste
(**FastAPI** en Python) sur une infrastructure Ubuntu 24.04, pilotée par Ansible et testée
avec Molecule + Vagrant/VirtualBox.

## Application déployée : FastAPI

API HTTP minimaliste exposant une ressource `items` (voir [`app/main.py`](app/main.py)).

| Méthode | Route | Description |
|---|---|---|
| GET | `/` | Métadonnées de l'appli (name, env) |
| GET | `/health` | Healthcheck (utilisé par nginx) |
| GET | `/items` | Liste des items |
| GET | `/items/{id}` | Détail d'un item |
| POST | `/items` | Création d'un item |
| DELETE | `/items/{id}` | Suppression |
| GET | `/docs` | Swagger UI auto-généré |

### Stack

- **FastAPI + Uvicorn** (Python 3.12)
- **Nginx** en reverse proxy (port 80 → 8000 interne)
- **MySQL** comme base de données (prêt à être branché à l'appli)

### Lancer manuellement (hors Ansible)

```bash
python3 -m venv .venv-local
source .venv-local/bin/activate
pip install -r app/requirements.txt
cd app && uvicorn main:app --reload
# → http://127.0.0.1:8000/docs
```

## Auteur

- Hugo Leyx-Valade *(travail individuel)*

## Bonus implémentés

- [x] **Ansible Vault** : fichier de passphrase `.devops_vault_pass.txt` référencé dans
      `ansible.cfg`. Les secrets sensibles (`mysql_root_password`, `database_app_password`)
      peuvent être chiffrés via `ansible-vault encrypt_string`.
- [ ] Multi-environnements (staging / production)
- [ ] Certbot (TLS Let's Encrypt)
- [ ] Maildev (serveur SMTP de développement)
- [ ] Postfix
- [ ] Backup automatisé

---

## Documentation technique

## Prérequis

Avant de commencer, assurez-vous d'avoir installé les outils suivants sur votre machine :

- [Python 3.12](https://www.python.org/download/)
  ```bash
  sudo apt-get install python3 python3-pip
  sudo pip3 install virtualenv
  ```
- [VirtualBox](https://www.virtualbox.org/)
- [Vagrant](https://www.vagrantup.com/)

## Mise en place de l'environnement local

Ce projet utilise un environnement virtuel Python pour isoler les dépendances. Pour l'initialiser, exécutez depuis la racine du projet :

```bash
source venv.sh
```

Cette commande crée l'environnement virtuel, l'active et installe toutes les dépendances Python nécessaires (Ansible, Molecule, etc.).

Des fonctions utilitaires sont ensuite disponibles dans le terminal :
- `download_galaxy` — télécharge les rôles Ansible déclarés dans `roles/requirements.yml`
- `rebuild_env` — recrée l'environnement virtuel from scratch
- `deactivate` — quitte l'environnement virtuel

## Développement et tests avec Molecule

Ce projet intègre [Molecule](https://molecule.readthedocs.io/en/stable/) pour tester les rôles Ansible dans des machines virtuelles éphémères.

| Commande | Description |
|---|---|
| `molecule converge` | Crée la VM de test et applique les playbooks |
| `molecule login` | Se connecte en SSH à la machine de test |
| `molecule verify` | Exécute les tests de vérification |
| `molecule test` | Lance le cycle de test complet (create → converge → verify → destroy) |

> Avant tout commit, vérifiez que tous les tests passent avec `molecule test`.

## Structure du projet

```
.
├── hosts/              # Inventaires (machines cibles)
│   └── hosts_dev       # Inventaire de développement (utilisé par Molecule)
├── group_vars/         # Variables par groupe d'hôtes
│   ├── all.yml
│   ├── api.yml
│   └── database.yml
├── roles/              # Rôles Ansible locaux
│   └── requirements.yml
├── molecule/           # Configuration des tests Molecule
├── playbook_install.yml # Playbook principal de déploiement
└── venv.sh             # Script d'initialisation de l'environnement
```

## Déploiement

### 1. Activer l'environnement virtuel

```bash
source venv.sh
```

### 2. Télécharger les rôles Galaxy

```bash
download_galaxy
```

### 3. Configurer le vault Ansible

Certaines variables sont chiffrées avec [Ansible Vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html).
Créez un fichier `.devops_vault_pass.txt` à la racine du projet contenant le mot de passe du vault.

Pour ce projet d'exemple, le mot de passe est : `password`

> **Attention :** Ne poussez jamais ce fichier sur un dépôt distant. Ajoutez-le à votre `.gitignore`.

### 4. Lancer le playbook

Voici la commande pour lancer le playbook si une vrai machine est configuré (ce qui n'est pas le cas pour ce TP).
```bash
ansible-playbook -i hosts/hosts_dev -u devops playbook_install.yml
```

## Gestion des vaults

```bash
# Créer un nouveau vault
ansible-vault create group_vars/devops_dev/vault.yml

# Editer un vault existant
ansible-vault edit group_vars/devops_dev/vault.yml

# Consulter un vault
ansible-vault view group_vars/devops_dev/vault.yml
```
