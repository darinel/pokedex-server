import json

class jsonParser:
    def get_json(fname):
        jfile = open(fname)
        rawjson = json.load(jfile)
        jfile.close
        return rawjson

    def get_id(jobject):
        return jobject["id"]

    def get_name(jobject):
        return jobject["name"]

    def get_type(jobject):
        ret = jobject["type"]
        if len(ret) < 2:
            ret.append("None")
        return ret

    def get_base(jobject):
        return jobject["base"]

    def to_list(jobject, keys):
        ret = []
        for key in keys:
            if key in jobject:
                ret.append(jobject[key])
        return ret