import json

from iuliia import BGN_PCGN

FB_PATH = "./data/fb-friend-names-hse.txt/hse_fb-friend-names-hse.txt"
VK_PATH = "./data/vk-friend-names-hse.txt/hse_vk-friend-names-hse.txt"

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

def get_freqs(dataset):
    names = {}
    surnames = {}
    cnt = 0
    for friend_list in dataset.values():
        for friend in friend_list:
            
            if len(friend) != 2:
                continue
            name, surname = friend

            if name not in names:
                names[name] = 0
            if surname not in surnames:
                surnames[surname] = 0
            
            names[name] += 1
            surnames[surname] += 1
            cnt += 1
    return names, surnames, cnt

fb_dataset = parse_FB_data(FB_PATH, 4429)
vk_dataset = parse_VK_data(VK_PATH, 21124)

names, surnames, cnt = get_freqs({**vk_dataset, **fb_dataset})

names = {"N" : cnt, "freqs" : names}
surnames = {"N" : cnt, "freqs" : surnames}

with open("./statistics/name_freqs.json", "w") as outfile: 
    json.dump(names, outfile)

with open("./statistics/surname_freqs.json", "w") as outfile: 
    json.dump(surnames, outfile)



        
