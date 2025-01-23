import json

from iuliia import BGN_PCGN
from Levenshtein import distance

FB_PATH = "./data/fb-friend-names-hse.txt/hse_fb-friend-names-hse.txt"
VK_PATH = "./data/vk-friend-names-hse.txt/hse_vk-friend-names-hse.txt"
NAME_FREQS_PATH = "./statistics/name_freqs.json"
SURNAME_FREQS_PATH = "./statistics/surname_freqs.json"

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

class Matcher:
    
    def __init__(self, dataset_a, dataset_b, sieve=None, get_similarity=None, get_match=None):
        self.dataset_a = dataset_a
        self.dataset_b = dataset_b
        
        self.sieve = self.sieve if sieve == None else sieve
        
        self.get_similarity = self.get_similarity if get_similarity == None else get_similarity
        
        self.get_match = self.get_match if get_match == None else get_match
        
        self.alpha = 0.8
        self.beta = 0.6
        self.gamma = 3
        self.delta = 5

        self.candidates = {}
    
    def sieve(self):
        candidates = {}
        for profile_a in self.dataset_a:
            
            if len(self.dataset_a[profile_a][0]) != 2:
                continue
            
            name_a, surname_a = self.dataset_a[profile_a][0]

            for profile_b in self.dataset_b:
               
                if len(self.dataset_b[profile_b][0]) != 2:
                    continue
                
                name_b, surname_b = self.dataset_b[profile_b][0]
                
                if name_a[:1].lower() == name_b[:1].lower() and surname_a[:1].lower() == surname_b[:1].lower() and \
                    distance(name_a, name_b) < 2 and distance(surname_a, surname_b) < 2:
                    if profile_a not in candidates:
                        candidates[profile_a] = []
                    candidates[profile_a].append(profile_b)
        
        self.candidates = candidates
        return candidates

    def levenshtein_simmilarity(self, str_a, str_b):
        return 1 - distance(str_a, str_b) / max(len(str_a), len(str_b))

    def compare_friends(self, friends_a, friends_b, nf, sf, n):
        score = 0
        for friend_a in friends_a:
            if len(friend_a) != 2:
                continue
            for friend_b in friends_b:
                if len(friend_b) != 2: # ger rid of wierd data points
                    continue
                if distance(friend_a[1][:2], friend_b[1][:2]) > 1: # first letters of the surname doesn't match
                    continue
                if self.levenshtein_simmilarity(friend_a[0], friend_b[0]) > self.alpha and \
                    self.levenshtein_simmilarity(friend_a[1], friend_b[1]) > self.beta:
                    score += min(1, n / (nf[friend_b[0]] * sf[friend_b[1]]))
        return score


    def get_similarity(self):
        
        with open(NAME_FREQS_PATH) as json_file:
            name_freqs = json.load(json_file)

        with open(SURNAME_FREQS_PATH) as json_file:
            surname_freqs = json.load(json_file)
        
        for candidate_a in self.candidates:

            friends_a = self.dataset_a[candidate_a][1:]
            
            for idx, candidate_b in enumerate(self.candidates[candidate_a]):
                friends_b = self.dataset_b[candidate_b][1:]
                score = self.compare_friends(friends_a, friends_b, \
                                             name_freqs["freqs"], surname_freqs["freqs"], name_freqs["N"])
                self.candidates[candidate_a][idx] = (self.candidates[candidate_a][idx], score)
        return


    def get_match(self):
        matches = {}
        for candidate_a in self.candidates:
            similar_candidates = [candidate_b for candidate_b in self.candidates[candidate_a] if candidate_b[1] > self.gamma]
            if len(similar_candidates) == 0:
                continue
            if len(similar_candidates) > 1:
                similar_candidates.sort(key=lambda x: -x[1])
                if similar_candidates[0][1] / similar_candidates[1][1] < self.delta:
                    continue
                else:
                    similar_candidates = [similar_candidates[0]]

            id, score = similar_candidates[0]
            name_a = " ".join(self.dataset_a[candidate_a][0])
            name_b = " ".join(self.dataset_b[id][0])
            matches[candidate_a] = {"Person" : name_a, "Match" : name_b, "Id" : id, "Score" : score}
        return matches

if __name__ == "__main__":

    fb_dataset = parse_FB_data(FB_PATH, 4429)
    vk_dataset = parse_VK_data(VK_PATH, 21124)


    matcher = Matcher(fb_dataset, vk_dataset)
    matcher.sieve()
    print("Sieve Finished")
    matcher.get_similarity()
    print("Sim Finished")
    matched_profiles = matcher.get_match()
    print("Candidates Matched")

    with open("match.json", "w") as outfile: 
        json.dump(matched_profiles, outfile)

