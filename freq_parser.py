import json

FB_DATASET_PATH = "./data/fb_dataset.json"
VK_DATASET_PATH = "./data/vk_dataset.json"

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

if __name__ == "__main__":

    with open(FB_DATASET_PATH) as fb_dataset_file:
        fb_dataset = json.load(fb_dataset_file)
    with open(VK_DATASET_PATH) as vk_dataset_file:
        vk_dataset = json.load(vk_dataset_file)

    names, surnames, cnt = get_freqs({**vk_dataset, **fb_dataset})

    names = {"N" : cnt, "freqs" : names}
    surnames = {"N" : cnt, "freqs" : surnames}

    with open("./statistics/name_freqs.json", "w") as outfile: 
        json.dump(names, outfile)

    with open("./statistics/surname_freqs.json", "w") as outfile: 
        json.dump(surnames, outfile)



        
