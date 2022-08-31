import sys
import pokedex
from jsonparse import jsonParser

j = jsonParser.get_json("pokemon.json")     # Read the JSON file that specifies the Pokemon
dex = pokedex.Pokedex("pokedex")            # Create a Pokedex object for database access
db = dex.open_pokedex()                     # Create a new database
pokedex.create_tables(db)                   # Create the Pokemon table within the database
pokedex.populate_pokedex(db, j)             # Populate the Pokemon database
db.close()                                  # Close the database after creation
