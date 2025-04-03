# Stockie ML

## Table of Contents
- 🛠 [Project Setup (Local Development)](#project-setup-local-development)
   - ⚙️ [Prerequisites](#prerequisites)
   - 📥 [Installation](#installation)
- 🚀 [Running The Server](#running-the-server)
- 🤝 [Contributing](#contributing)
- 📝 [Resources](#resources)

## Project setup (Local Development)
For first time setup of the project, follow the steps below:

### Local development
### Prerequisites
- python 3.12+
- pip (please upgrade to the latest version)
    ```bash
    python -m pip install --upgrade pip
    ```

### Installation
1. Clone the repo

2. Create a virtual environment
    ```bash
    python -m venv venv
    ```

3. Activate the virtual environment
    ```bash
    source venv/bin/activate
    ```

4. Install the libraries
    ```bash
    pip install -r requirements.txt
    ```
   For any libraries updates, please run the following command
    ```bash
    pip freeze > requirements.txt
    ```

5. Create a `.env` file in the root directory and add the environment variables (please ask for the variables from the team)
    

You're all set! 🚀
To start the development server, follow the next section.


## Running the server

### Local development
1. Activate the virtual environment
   ```bash
   source venv/bin/activate
   ```

2. Run the server
   ```bash
   uvicorn app.main:app --port 8001 --reload
   ```
   or run with the main file (no real-time reload)
   ```bash
   python -m app.main
   ```

3. To access the API documentation, visit
    - 📜 Swagger UI (interactive) → http://127.0.0.1:8001/docs
      - API KEY is needed in order to call any endpoints
      - This server's API KEY allows access to every endpoint
    - 🔥 ReDoc UI (read-only) → http://127.0.0.1:8001/redoc

4. To terminate the server, press `Ctrl + C` in the terminal

5. To deactivate the virtual environment, run
    ```bash
    deactivate
    ```

## Contributing

### Formatting
- please format the all codes in app folder by running command below before committing
    ```bash
    black app/
    isort app/
    flake8 app/
    ```

## Resources

### Logging
- colorlog → https://pypi.org/project/colorlog/
