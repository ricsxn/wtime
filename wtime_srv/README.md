# wtime_srv

WTime Server project, offer a web based front-end capable to manage working time entries in a multi-user based web platform.

## Setting up the service
Requirements: `python3, pip3, npm`

* Clone this project: `git clone <wtime project> && cd <wtime project dir>/wtime_srv`

* Prepare the python virtual environment: `python3 -m venv venv`

* Access the virtual environment: `source venv/bin/activate`

* Load all required packages: pip install -r requirements.txt

* Install other required stuff: 
```bash
cd static
npm init -y 
npm install @popperjs/core bootstrap@5 jquery
npm install --save @fortawesome/fontawesome-free
```

* Launch a standalone instance (debug only): `./wtime_srv.sh`

* Initial DB setup: `curl localhost:8889/create_db`

* Finally, open a browser and connect to: `localhost:8889/`