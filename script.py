import json
import time
import itertools
import multiprocessing as mp
from Levenshtein import distance

FB_DATASET_PATH = "./data/fb_dataset.json"
VK_DATASET_PATH = "./data/vk_dataset.json"
NAME_FREQS_PATH = "./statistics/name_freqs.json"
SURNAME_FREQS_PATH = "./statistics/surname_freqs.json"

class Matcher:
    
    def __init__(self, dataset_a, dataset_b, sieve=None, get_similarity=None, get_match=None):
        
        self.mp_flag = False
        
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

    def sieve(self, data):
        candidates = {}
        for profile_a in data:
            
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
            if(self.mp_flag == False):
                self.candidates = candidates
        return candidates

    
    def sieve_mp(self, n_proc):
        self.mp_flag = True
        a_size = len(self.dataset_a.values())
        
        chunks = [ dict(itertools.islice(self.dataset_a.items(), i, i + a_size // n_proc))
            for i in range(0, a_size, a_size // n_proc)]

        pool = mp.Pool(processes=n_proc)
        results = pool.map(self.sieve, chunks)
        pool.close()
        pool.join()
        candidates = {key : value for element in results for key, value in element.items()}
        self.candidates = candidates
        self.mp_flag = False
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
    
    start_time = time.time()
    
    with open(FB_DATASET_PATH) as fb_dataset_file:
        fb_dataset = json.load(fb_dataset_file)
    with open(VK_DATASET_PATH) as vk_dataset_file:
        vk_dataset = json.load(vk_dataset_file)

    end_time = time.time()
    print(f"data loading was finished in: {(end_time - start_time):.2f} seconds")

    start_time = time.time()
    matcher = Matcher(vk_dataset, fb_dataset)
    end_time = time.time()
    print(f"matcher construction was finished in: {(end_time - start_time):.2f} seconds")

    start_time = time.time()
    matcher.sieve_mp(n_proc=4)
    end_time = time.time()
    print(f"sieving was finished in: {(end_time - start_time):.2f} seconds with n_proc= 4")
    
    start_time = time.time()
    matcher.get_similarity()
    end_time = time.time()
    print(f"similarity calculation was finished in: {(end_time - start_time):.2f} seconds")
    
    start_time = time.time()
    matched_profiles = matcher.get_match()
    end_time = time.time()
    print(f"profile matching was finished in: {(end_time - start_time):.2f} seconds")

    with open("match.json", "w") as outfile: 
        json.dump(matched_profiles, outfile)

