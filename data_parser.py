FB_PATH = "./data/fb-friend-names-hse.txt/hse_fb-friend-names-hse.txt"
VK_PATH = "./data/vk-friend-names-hse.txt/hse_vk-friend-names-hse.txt"

import json
from iuliia import BGN_PCGN

def parse_VK_data(path, n_lines):
    dataset = {}

    with open(path) as input_file:
        data = [json.loads(next(input_file)) for _ in range(n_lines)]
    
    for i in range(len(data)):
        main_profile = data[i]["info"]
        key = str((data[i]["_id"])).strip()

        record = [[BGN_PCGN.translate(main_profile["name"]), BGN_PCGN.translate(main_profile["secName"])]] + \
            [[BGN_PCGN.translate(person["name"]), BGN_PCGN.translate(person["secName"])] for person in data[i]["friends"]]
        
        if record != ["", ""]:
            dataset[key] = record

    return dataset

def parse_FB_data(path, n_lines):
    dataset = {}

    with open(path) as input_file:
        data = [next(input_file) for _ in range(n_lines)]
    
    for line in data:
        splitted_line = line.split("|")
        splitted_data = [BGN_PCGN.translate(entity).split()[1:] for entity in splitted_line]
        dataset[splitted_line[0].split()[0]] = splitted_data
    
    return dataset

if __name__ == "__main__":
    fb_dataset = parse_FB_data(FB_PATH, 4_429) # total users: 4_429
    vk_dataset = parse_VK_data(VK_PATH, 21_124) # total users: 21_124

    with open("./data/fb_dataset.json", "w") as outfile: 
        json.dump(fb_dataset, outfile)

    with open("./data/vk_dataset.json", "w") as outfile: 
        json.dump(vk_dataset, outfile)