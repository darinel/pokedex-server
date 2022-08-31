from flask import Flask, request
from pokedex import Pokedex

app = Flask(__name__)
dex = Pokedex("pokedex")

@app.route("/types", methods=["GET"])
def get_types():
    return {"types": dex.get_all_types()}

@app.route("/pokemon", methods=["GET"])
@app.route("/pokemon/<lang>", methods=["GET"])
def get_pokemon(lang=""):
    args = request.args
    id = args.get("id")
    limit = args.get("limit", default=0, type=int)
    name = args.get("name", default="", type=str)
    type1 = args.get("type1", default="", type=str)
    type2 = args.get("type2", default="", type=str)
    caught = args.get("caught", default=-1, type=int)
    page = args.get("page", default=1, type=int)

    ret = None
    if id:
        ret = {"content": [dex.query_by_id(id, lang)]}
    else:
        tmp = dex.query_pokemon(name, (type1, type2), caught, limit, lang)
        pn = 0
        if tmp:
            if page <= len(tmp):
                pn = page - 1
            elif page > len(tmp):
                pn = len(tmp) - 1
            ret = {"page": pn+1, "total": len(tmp), "content": tmp[pn]}
        else:
            ret = {"content": [tmp]}
    return ret

@app.route("/catch/<int:id>", methods=["GET"])
def catch_pokemon(id=0):
    dex.catch(id)
    return {"content": [dex.query_by_id(id)]}

@app.route("/release/<int:id>", methods=["GET"])
def release_pokemon(id=0):
    dex.release(id)
    return {"content": [dex.query_by_id(id)]}

if __name__ == '__main__':
    app.run(debug=True)