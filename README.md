# Pokedex Backend

This is a simple backend and API for creating a Pokedex database and serving queries via HTTP.

## Tech Stack

- Python: The application parses JSON info containing Pokemon data and uses it to create a database.
- SQLite: A Python-native database management framework used to create and query the database.
- Flask: An open-source Python web framework used to configure the API routes

## Usage

Pokemon data can be served via HTTP requests to the server.

- ``/types``: Returns of a list of all Pokemon types found in the database

- ``/catch/<id>``: Updates a specified Pokemon entry to indicate it was caught. If the database was updated, the entry for the updated pokemon will be returned.

- ``/release/<id>``: Updates a specified Pokemon entry to indicate it was released. If the database was updated, the entry for the updated pokemon will be returned.

- ``/pokemon/[lang = en, jp, cn, fr]``: Returns a list of all Pokemon in the database. An optional language (English - "en", Japanese - "jp", Chinese - "cn" or French - "fr") to display the Pokemon name in can be specified after the route. The returned Pokemon data can be further filtered using query parameters:

    - ``id (int)``: Returns the Pokemon with the specified ID number. This will override any other parameters to return the chosen Pokemon.
    - ``name (string)``: Returns Pokemon whose name contains the specified string. If the language is specified, it will search based on the names in the chosen language. If no language is specified, all languages will be searched for matches.
    - ``type1, type2 (string)``: Returns Pokemon with the specified primary ("type1") and secondary ("type2") types. If one of the specified types is invalid it will be ignored by the server.
    - ``caught (0 or not 0)``: If a value greater than zero is entered, it will return all caught Pokemon. If zero is entered, it will return all Pokemon not yet caught.
    - ``limit (int)``: Limits the amount of Pokemon returned by a query to the specified value. The results can be iterated over using the "page" parameter.
    - ``page (int)``: Selects the page of Pokemon results to be viewed when the "limit" parameter is used.

Example usage:
- ``pokedex.io/types``: Returns a list of all Pokemon types
- ``pokedex.io/pokemon``: Returns all Pokemon
- ``pokedex.io/catch/400``: Updates Pokemon No. 400's Caught status
- ``pokedex.io/pokemon/fr``: Returns all Pokemon using their French name
- ``pokedex.io/pokemon?name=ard``: Returns all Pokemon with "ard" in any of their localized names.
- ``pokedex.io/pokemon/fr?name=rre&type1=grass&type2=poison&caught=1``: Returns all Pokemon of Grass/Poison typing whose French name contains "rre" and have already been caught

## Setup

Note: make sure Python is installed and up-to-date on your system. [Download Python here.](https://www.python.org/)

1. Create the virtual environment for the server:
- Mac:

``python3 -m venv venv``

``source venv/bin/activate``

``pip3 install Flask``

- Windows: 

``py -m venv venv``

``.\venv\Scripts\activate``

``pip install Flask``

2. While running in the virtual environment, create the Pokemon database:
- Mac: ``python3 makedb.py``
- Windows: ``python makedb.py``

3. Start the server:
- Mac: ``python3 pokedex-app.py``
- Windows: ``python pokedex-app.py``

The server will be running at localhost:5000 by default. Enter the URL in your browser or use the curl command line tool to make a request:
``curl 'http://127.0.0.1:5000/pokemon'``

## Further Considerations/Future Work

Due to limited time during this week due to professional obligations and personal matters, I was not able to fully realize my goals in this project. Listed below are several aspects that I wish to fulfill with this project over time.

- Front-end UI: A client application that will provide access to the functions of the API.
- Production WSGI: An interface that would allow this project to serve remote clients via a hosted web server.
- Security: All SQL queries in this application are function-based and use parameters rather than string interpoliation, so it is fairly protected from typical SQL injection attacks. However, I would like to thoroughly pen test it to secure any vulnerabilities.
- Authentication: A PKI implementation that would allow for only authenticated requests to be processed by the application.
- Advanced error testing and handling: Fully pushing the logical limits of the server with a more robust testing strategy.