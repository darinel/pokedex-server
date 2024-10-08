import sqlite3
from jsonparse import jsonParser
# Change to be triggered with webhook
# change number 2
# JSON translation and parsing tables
_namefields = ['english', 'japanese', 'chinese', 'french']
_shortnames = ['en', 'jp', 'cn', 'fr']
_basefields = ['HP', 'Attack', 'Defense', 'Sp. Attack', 'Sp. Defense', 'Speed']
_shortbases = ['hp', 'atk', 'def', 'spa', 'spd', 'spe']

# Santizes any dynamic input used in SQL queries
def scrub(input):
    return ''.join(chr for chr in input if chr.isalnum())

# Creates the Pokemon table within the database
def create_tables(dex):
    cur = dex.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS pokemon(id INT NOT NULL, en VARCHAR(255), jp VARCHAR(255), cn VARCHAR(255), fr VARCHAR(255), primtype VARCHAR(255), sectype VARCHAR(255), hp INT, atk INT, def INT, spa INT, spd INT, spe INT, caught BOOL, PRIMARY KEY (id))")
    cur.close()

# Enters raw JSON data into the Pokedex database
def populate_pokedex(dex, json):
    cur = dex.cursor()
    for pokemon in json:
        try:
            cur.execute("INSERT INTO pokemon VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (jsonParser.get_id(pokemon), *jsonParser.to_list(jsonParser.get_name(pokemon), _namefields), *jsonParser.get_type(pokemon), *jsonParser.to_list(jsonParser.get_base(pokemon), _basefields), 0))
        except sqlite3.Error:
            pass
    dex.commit()
    cur.close()

# Converts a single SQL entry to a Python dictionary
def to_dict(raw):
    if raw:
        if len(list(raw)) == 14:
            ret = dict(zip(["id", *_shortnames, "type1", "type2", *_shortbases, "caught"], list(raw)))
            ret["caught"] = bool(ret["caught"])
        else:
            ret = dict(zip(["id", "name", "type1", "type2", *_shortbases, "caught"], list(raw)))
            ret["caught"] = bool(ret["caught"])
    else:
        ret = {}
    return ret

# Converts an SQL query result to an array of Python dictionaries
def to_dicts(cur, limit = 0):
    ret = []
    while True:
        if limit > 0:
            tmp = cur.fetchmany(limit)
        else:
            tmp = cur.fetchall()
        if not tmp:
            break
        page = []
        for mon in tmp:
            page.append(to_dict(mon))
        ret.append(page)
    return ret

# Provides database access functionality
class Pokedex:
    def __init__(self, dexname):
        self.dexname = dexname  # Name of the database
        self.tempflag = False   # Flag used to track the state of the temporary table

    # Creates a connection to the database
    def open_pokedex(self):
        return sqlite3.connect('{}.db'.format(self.dexname))

    # Queries the database for a specific Pokemon
    # lang can be "en", "jp", "cn" or "fr"
    def query_by_id(self, id, lang=""):
        if self.tempflag:
            self.drop_temp_table()
        self.create_temp_table(lang)
        dex = self.open_pokedex()
        cur = dex.cursor()
        res = cur.execute("SELECT * FROM tmp WHERE id=?", [str(id)])
        # res = cur.execute("SELECT * FROM {} WHERE id=?".format(scrub(table)), [str(id)])
        ret = to_dict(res.fetchone())
        cur.close()
        dex.close()
        self.drop_temp_table()
        return ret
    
    # Marks the specified Pokemon as "caught"
    def catch(self, id):
        dex = self.open_pokedex()
        cur = dex.cursor()
        cur.execute("UPDATE pokemon SET caught = 1 WHERE id = ?", [str(id)])
        dex.commit()
        cur.close()
        dex.close()

    # Removes the "caught" marking from the specified Pokemon
    def release(self, id):
        dex = self.open_pokedex()
        cur = dex.cursor()
        # cur.execute("DELETE FROM caught WHERE id = ?", [str(id)])
        cur.execute("UPDATE pokemon SET caught = 0 WHERE id = ?", [str(id)])
        dex.commit()
        cur.close()
        dex.close()

    # Creates a temporary table using only one name localization for query processing
    # lang can be "en", "jp", "cn" or "fr"
    def create_temp_table(self, lang=""):
        dex = self.open_pokedex()
        cur = dex.cursor()

        cur.execute("CREATE TABLE IF NOT EXISTS tmp AS SELECT * FROM pokemon")
        if lang.lower() == "en":
            cur.executescript("""
                BEGIN;
                ALTER TABLE tmp DROP COLUMN jp;
                ALTER TABLE tmp DROP COLUMN cn;
                ALTER TABLE tmp DROP COLUMN fr;
                ALTER TABLE tmp RENAME COLUMN en TO name;
                COMMIT;
            """)
        elif lang.lower() == "jp":
            cur.executescript("""
                BEGIN;
                ALTER TABLE tmp DROP COLUMN en;
                ALTER TABLE tmp DROP COLUMN cn;
                ALTER TABLE tmp DROP COLUMN fr;
                ALTER TABLE tmp RENAME COLUMN jp TO name;
                COMMIT;
            """)
        elif lang.lower() == "cn":
            cur.executescript("""
                BEGIN;
                ALTER TABLE tmp DROP COLUMN en;
                ALTER TABLE tmp DROP COLUMN jp;
                ALTER TABLE tmp DROP COLUMN fr;
                ALTER TABLE tmp RENAME COLUMN cn TO name;
                COMMIT;
            """)
        elif lang.lower() == "fr":
            cur.executescript("""
                BEGIN;
                ALTER TABLE tmp DROP COLUMN en;
                ALTER TABLE tmp DROP COLUMN jp;
                ALTER TABLE tmp DROP COLUMN cn;
                ALTER TABLE tmp RENAME COLUMN fr TO name;
                COMMIT;
            """)
        dex.commit()
        cur.close()
        dex.close()
        self.tempflag = True

    # Deletes the temporary table
    def drop_temp_table(self):
        if self.tempflag:
            dex = self.open_pokedex()
            cur = dex.cursor()
            cur.execute("DROP TABLE tmp")
            dex.commit()
            cur.close()
            dex.close()
            self.tempflag = False

    # Queries the Pokemon database and returns the matching results
    # types must match any present Type value within the database or it is ignored. The primary type is the first value of the tuple, the secondary type is the second
    # caught is 0 if querying for uncaught Pokemon, nonzero if querying for caught Pokemon, or -1 if it is ignored
    # limit will cause the query to be divided into arrays of the specified size. A size less than 0 will not result in pagination
    # lang can be "en", "jp", "cn" or "fr"
    def query_pokemon(self, name="", type=("", ""), caught=-1, limit=0, lang=""):
        types = self.get_all_types()
        if self.tempflag:
            self.drop_temp_table()
        self.create_temp_table(lang)
        dex = self.open_pokedex()
        cur = dex.cursor()

        params = {}
        if name:
            params["name"] = "%" + name + "%"
        else:
            params["name"] = None
        
        if type[0].lower().capitalize() in types:
            params["ptype"] = type[0].lower().capitalize()
        else:
            params["ptype"] = None
        if type[1].lower().capitalize() in types:
            params["stype"] = type[1].lower().capitalize()
        else:
            params["stype"] = None

        if caught == -1:
            params["caught"] = None
        else:
            if caught:
                params["caught"] = 1
            else:
                params["caught"] = 0

        if lang.lower() == "en" or lang.lower() == "cn" or lang.lower() == "jp" or lang.lower() == "fr":
            res = cur.execute("""
                SELECT f.* FROM
                (((SELECT * FROM tmp WHERE name LIKE :name OR :name IS NULL) a
                INNER JOIN
                (SELECT * FROM tmp WHERE primtype = :ptype OR :ptype IS NULL) b
                ON a.id = b.id) c
                INNER JOIN
                (SELECT * FROM tmp WHERE sectype = :stype OR :stype IS NULL) d
                ON c.id = d.id) e
                INNER JOIN
                (SELECT * FROM tmp WHERE caught = :caught OR :caught IS NULL) f
                ON e.id = f.id
            """, params)
        else:
            res = cur.execute("""
                SELECT f.* FROM
                (((SELECT * FROM tmp WHERE (en LIKE :name OR jp LIKE :name OR cn LIKE :name OR fr LIKE :name) OR :name IS NULL) a
                INNER JOIN
                (SELECT * FROM tmp WHERE primtype = :ptype OR :ptype IS NULL) b
                ON a.id = b.id) c
                INNER JOIN
                (SELECT * FROM tmp WHERE sectype = :stype OR :stype IS NULL) d
                ON c.id = d.id) e
                INNER JOIN
                (SELECT * FROM tmp WHERE caught = :caught OR :caught IS NULL) f
                ON e.id = f.id
            """, params)

        ret = to_dicts(res, limit)
        cur.close()
        dex.close()
        self.drop_temp_table()
        return ret

    # Returns all the types present in the database
    def get_all_types(self):
        dex = self.open_pokedex()
        cur = dex.cursor()
        res = cur.execute("SELECT DISTINCT primtype FROM pokemon")
        ret = [t[0] for t in res.fetchall()]
        cur.close()
        dex.close()
        return ret
