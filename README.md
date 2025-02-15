# Log to OCEL2 Converter

This project is a Flask web application that converts log data from JSON format into an OCEL2 (Object-centric Event Log) format. It provides a web interface for mapping, previewing, and exporting log data. This tool is developed as part of a Master's thesis in **Business Informatics and Data Science** at the **University of Camerino**.

## Features

- **Web Interface:** A modern single-page web application built with Flask.
- **File Mapping:** Import log data in JSON format and map it into the OCEL2 format.
- **Dynamic Mapping and Preview:** Configure parameters interactively, including normalization of nested columns and dynamic selection of attributes.
- **Relationship Qualifier:** Define custom relationship qualifiers for OCEL relations.
- **Dockerized Deployment:** Easily deploy the entire application using Docker.

## Setup & Deployment

The project is containerized using Docker. To build and run the project, ensure you have Docker and Docker Compose installed, then follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/menga28/log-to-ocel.git
   ```

2. **Navigate to the project directory:**

   ```bash
   cd log-to-ocel
   ```

3. **Build and run the project with Docker Compose:**

   ```bash
   docker-compose up --build
   ```

   This command builds the Docker image (using the provided Dockerfile) and starts the Flask web application on the configured port (typically port 5001).

## Usage

1. **Open the Web Interface:**  
   Once the application is running, open your web browser and navigate to `http://localhost:5001` (or the configured host and port).

2. **Upload a Log File or Use a Sample:**  
   - You can drag and drop or select a JSON log file.
   - Alternatively, click "Use Sample File" to load a predefined sample.

3. **Mapping Process:**  
   - **Mapping Page (Columns to Normalize):**  
     Select nested columns to normalize. Click "continue" to invoke normalization.
   - **Select Attributes:**  
     Configure OCEL parameters such as the activity column, timestamp column, object types, and additional event attributes. Then click "Finalize" to set OCEL parameters.
   - **Relationship Qualifier:**  
     After the OCEL is created, proceed to the Relationship Qualifier page to define custom qualifiers for your relationships. You can add as many qualifier mappings as needed.

4. **Export:**  
   Once mapping is complete, you can export the OCEL2 data in your desired format.

## Requirements

- Docker & Docker Compose
- Python 3.8+ (for local development)
- PM4Py (used for OCEL conversion)

## Project Structure

- **app/**  
  Contains the Flask application code, templates, and static assets.
- **Dockerfile & docker-compose.yml:**  
  Used for containerizing and deploying the application.
- **requirements.txt:**  
  Lists all Python dependencies.

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
