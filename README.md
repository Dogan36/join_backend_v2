
# Join Backend

Das **Join Backend** ist die Server-Seite für die **Join App**, die es Benutzern ermöglicht, Workspaces zu erstellen, Tasks zu verwalten und miteinander zu interagieren. Die API basiert auf **Django** und verwendet **Django Rest Framework (DRF)** zur Bereitstellung von RESTful Endpunkten. Die API verwendet **Token-basierte Authentifizierung** und bietet Funktionen wie Benutzerregistrierung, Passwortänderung und das Verwalten von Kontakten und Workspaces.

## Table of Contents
- [Technologien](#technologien)
- [Installation](#installation)
- [API-Dokumentation](#api-dokumentation)
- [Endpunkte](#endpunkte)
  - [User-Endpunkte](#user-endpunkte)
  - [Workspace-Endpunkte](#workspace-endpunkte)
  - [Task-Endpunkte](#task-endpunkte)
- [Testing](#testing)
- [Deployment](#deployment)

## Technologien


- **Django Rest Framework (DRF)** (API-Framework)
- **drf-spectacular** (API-Dokumentation)
- **PostgreSQL** (Datenbank)
- **Rest Framework Auth Token** (Authentifizierung)


## Installation

### Voraussetzungen

- Python 3.11 oder höher
- PostgreSQL (optional: wenn du die Datenbank lokal verwenden möchtest)

### Schritt 1: Clone das Repository

```bash
git clone https://github.com/Dogan36/join_backend_v2.git
cd join_backend_v2
```

### Schritt 2: Virtuelle Umgebung erstellen und aktivieren

```bash
python -m venv env
source venv/bin/activate  # Für Linux/MacOS
env\Scripts\activate     # Für Windows
```

### Schritt 3: Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### Schritt 5: .env Datei erstellen

Erstelle eine .env-Datei im Stammverzeichnis deines Projekts und füge folgende Variablen hinzu:
  
```bash
SECRET_KEY='dein-geheimer-django-schlüssel'
EMAIL_HOST_USER='deine-email@example.com'
EMAIL_HOST_PASSWORD='dein-email-passwort'
DEBUG=false 
  ```

### Schritt 5: Datenbank erstellen

1. **Datenbank konfigurieren** (Falls PostgreSQL verwendet wird)
   
   Füge `DATABASE_URL`- Variable in -env Datei hinzu um deine Datenbankverbindung zu konfigurieren. 

2. **Migrations durchführen**

   ```bash
   python manage.py migrate
   ```

### Schritt 6: Erstelle ein Superuser-Konto (optional)

```bash
python manage.py createsuperuser
```

### Schritt 7: Entwicklungsserver starten

```bash
python manage.py runserver
```

Die API ist nun unter `http://localhost:8000` verfügbar.

## API-Dokumentation

Die vollständige API-Dokumentation ist unter [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/) verfügbar, wenn du Swagger UI verwendest.
Die Online Dokumentation findest du unter [https://join-backend-v2.onrender.com/api/docs/](https://join-backend-v2.onrender.com/api/docs/)

## Endpunkte

### User-Endpunkte

#### 1. **POST /api/v1/user/register/**
- **Beschreibung**: Registriert einen neuen Benutzer.
- **Body**:
  ```json
  {
    "email": "user@example.com",
    "name": "User Name",
    "password": "securepassword"
  }
  ```

#### 2. **POST /api/v1/user/login/**
- **Beschreibung**: Authentifiziert einen Benutzer und gibt ein Token zurück.
- **Body**:
  ```json
  {
    "username": "user@example.com",
    "password": "securepassword"
  }
  ```

#### 3. **POST /api/v1/user/change-password/**
- **Beschreibung**: Ändert das Passwort des Benutzers.
- **Body**:
  ```json
  {
    "oldPassword": "oldpassword",
    "newPassword": "newpassword"
  }
  ```

#### 4. **POST /api/v1/user/update-profile/**
- **Beschreibung**: Aktualisiert das Benutzerprofil.
- **Body**:
  ```json
  {
    "name": "New Name",
    "email": "newemail@example.com",
    "phone": "1234567890"
  }
  ```

#### 5. **POST /api/v1/user/password-reset-request/**
- **Beschreibung**: Fordert einen Passwort-Rücksetz-Link an.
- **Body**:
  ```json
  {
    "email": "user@example.com"
  }
  ```

#### 6. **POST /api/v1/user/password-reset/{uidb64}/{token}/**
- **Beschreibung**: Setzt das Passwort des Benutzers zurück.
- **Body**:
  ```json
  {
    "password": "newpassword"
  }
  ```

### Workspace-Endpunkte

#### 1. **GET /api/v1/workspaces/**
- **Beschreibung**: Gibt alle Workspaces zurück, bei denen der Benutzer Mitglied ist.

#### 2. **POST /api/v1/workspaces/**
- **Beschreibung**: Erstellt einen neuen Workspace.
- **Body**:
  ```json
  {
    "name": "New Workspace",
    "join_code": "randomcode123"
  }
  ```

#### 3. **POST /api/v1/workspaces/join-by-code/**
- **Beschreibung**: Ermöglicht es einem Benutzer, einem Workspace beizutreten, indem er den Join-Code verwendet.
- **Body**:
  ```json
  {
    "join_code": "randomcode123"
  }
  ```

#### 4. **POST /api/v1/workspaces/leave/**
- **Beschreibung**: Verlässt einen Workspace.
- **Body**:
  ```json
  {
    "workspace_id": 1
  }
  ```

#### 5. **DELETE /api/v1/workspaces/delete-workspace/**
- **Beschreibung**: Löscht einen Workspace, wenn der Benutzer der Eigentümer ist.
- **Body**:
  ```json
  {
    "workspace_id": 1
  }
  ```

### Task-Endpunkte

#### 1. **GET /api/v1/workspaces/{workspace_id}/tasks/**
- **Beschreibung**: Gibt alle Aufgaben eines Workspaces zurück.

#### 2. **POST /api/v1/workspaces/{workspace_id}/tasks/**
- **Beschreibung**: Erstellt eine neue Aufgabe.
- **Body**:
  ```json
  {
    "title": "New Task",
    "description": "Task description",
    "assigned_to": [1, 2],  # IDs der zugewiesenen Kontakte
    "category": 1           # ID der Kategorie
  }
  ```

#### 3. **PUT /api/v1/workspaces/{workspace_id}/tasks/{task_id}/**
- **Beschreibung**: Aktualisiert eine bestehende Aufgabe.

### Testing

Die Tests wurden noch nicht erstellt. Sobald dies geschen ist werden sie sich im **`tests`**-Ordner befinden. Du kannst die Tests dann mit folgendem Befehl ausführen:

```bash
python manage.py test
```

### Deployment

Um das Backend für die Produktion bereitzustellen, kannst du einen WSGI-Server wie **Gunicorn** und einen Reverse-Proxy wie **Nginx** verwenden. Beispiel:

```bash
pip install gunicorn
gunicorn join_backend.wsgi:application --bind 0.0.0.0:8000
```

Für **Datenbanken** in der Produktion, wie z.B. PostgreSQL, stelle sicher, dass die entsprechenden Umgebungsvariablen gesetzt sind und der **Datenbank-Server** erreichbar ist.

## Lizenz

Dieses Projekt steht unter der [MIT-Lizenz]
