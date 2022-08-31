from jsonparse import jsonParser
import pokedex

j = jsonParser.get_json("pokemon.json")
dex = pokedex.Pokedex("pokedex")
db = dex.open_pokedex()
pokedex.create_tables(db)
pokedex.populate_pokedex(db, j)