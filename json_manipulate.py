import json

def read(file):
    with open(file,"r") as f:
        return json.load(f)
def write(obj, file):
    with open(file, "w") as f:
        return json.dump(obj,f, sort_keys=True, indent=4)