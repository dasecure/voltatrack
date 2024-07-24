import json

def dict_diff(d1, d2, path=""):
    for k in d1.keys():
        if k not in d2:
            print(f"{path}: Key {k} not in second json")
        else:
            if type(d1[k]) is dict:
                if type(d2[k]) is dict:
                    dict_diff(d1[k], d2[k], path=f"{path}.{k}")
                else:
                    print(f"{path}: Type mismatch on key {k}")
            else:
                if d1[k] != d2[k]:
                    print(f"{path}: Value mismatch on key {k}")

def compare_json_files(file1, file2):
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        d1 = json.load(f1)
        d2 = json.load(f2)
        dict_diff(d1, d2)

compare_json_files('allStations.json', 'sunnyvale.json')