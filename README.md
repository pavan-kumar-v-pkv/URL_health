# URL Health Monitor

A simple web application to monitor the health status of multiple URLs by checking if they are UP or DOWN, along with the response times. Build using Flask, SQLite database and Dockerized for easy deployment.

## Features

- Input multiple URLs via a user-friendly GUI.
- Check each URL's availabilty (UP/DOWN status).
- Measures and displays reponse times in milliseconds.
- Stores historical check results for reference.
- Displays current and past URL health check data in a clean table.
- Dockerized for easy setup and deployment.

## Tech Stack
- Backend: Flask
- Database: SQLite
- Frontend: HTML/CSS (Flask templates)
- Containerization: Docker

## How to Run

### Prerequisites

- Docker and Docker Compose installed on your system.
- Python 3.12 or higher installed on your system.
- Git installed on your system.

### Steps to Run

1. Clone the repository:
```bash
$ git clone https://github.com/pavan-kumar-v-pkv/URL_health.git
$ cd URL_health
```

2. Build and run the Docker container:
```bash
$ docker-compose up --build
```

3. Access the application:
Open your web browser and navigate to http://localhost:5001 to access the application.

4. Use the web interface to enter URLs and check their health status.

## Project Structure

- app.py: The main application file.
- templates/: The templates directory.
- requirements.txt: The list of dependencies.
- docker-compose.yml: The Docker Compose file.
- Dockerfile: The Dockerfile.

## Screenshots

### Main Page
![](screenshots/homepage.png.png)

### Results Page
![](screenshots/results.png.png)

### History Page
![](screenshots/history.png.png)


Author
Pavan Kumar V
Email: pavankumarvpkv@gmail.com
GitHub: pavan-kumar-v-pkv