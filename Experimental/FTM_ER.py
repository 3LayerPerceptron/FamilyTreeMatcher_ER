import json
import argparse
from Levenshtein import ratio
from typing import List, Dict, Tuple
from collections.abc import Callable


FEATURE_LIST = ("_id", "treeId", "name", "middleName" ,"surname", "birthdate", "birthplace")


def genotek_feature_selector(genotek_records: List[Dict], feature_list: tuple) -> List[Dict]:

    """
        Функция обрезает признаки записи до тех, которые включены в feature_list

        Args:
            genotek_records (List[Dict]) : Записи из базы генотека.
            feature_list (tuple)         : Список нужных признаков.

        Returns:
            List[Dict]: Записи из базы генотека только с признаками из feature_list.
    """

    genotek_trimmed = []
    for record in genotek_records:
        d = {}
        for feature in feature_list:
            if feature in record:
                d[feature] = record[feature]
                continue
            d[feature] = None
    
        genotek_trimmed.append(d)
    
    return genotek_trimmed

def reader(path: str, feature_list: tuple) -> List[Dict]:

    """
        Чтение из JSON файла.

        Args:
            path (str)           : Путь до файла, из которого читаем.
            feature_list (tuple) : Список нужных признаков.

        Returns:
            List[Dict]: Считанные записи с признаками из feature_list.
    """

    with open(path) as file:
        data = json.load(file)

    return genotek_feature_selector(data, feature_list)

def writer(data: List[Dict], path: str) -> None:

    """
        Запись в JSON файл.

        Args:
            data (List[Dict]) : Данные, которые сохраняем.
            path (str)        : Путь до файла, в который пишем.

        Returns:
            None
    """

    with open(path, 'w') as file:
        json.dump(data, file)





def decade_hasher(record: Dict, n_buckets: int, start_year: int = 1700) -> int:

    """
        Функция, которая выичсляет бакет, в котором находится записи из той же декады, что и record.

        Args:
            record (Dict)   : Запись, для которой необходимо определить бакет.
            n_buckets (int) : Количество бакетов.
            start_year (int): Начальное значение, от которого отсчитываются декады.

        Returns:
            int : -2 Если поле year не заполнено.
                -1 Если формат года не соответсвует входит во временной промежуток бакетировния.
                0 ... n_buckets Если получилось определить индекс бакета.
    """

    # Check if there is any data in "birthdate" field

    if record["birthdate"] == None or record["birthdate"][0]["year"] == None:
        return -2
        

    year = record["birthdate"][0]["year"]
    
    if year < start_year or year > start_year + 10 * n_buckets:
        return -1
    
    return (year // 100 - (start_year // 100)) * 10 + (year % 100) // 10




class Matcher:

    """
        Класс для мэтчинга записей.

        Attributes:
            needles_  (List[Dict]) : Список записей, для которых мы ищем мэтчи.
            haystack_ (List[Dict]) : Список запискй, среди которых мы ищем мэтчи.
    """

    def __init__(self, needles: List[Dict], haystack: List[Dict]) -> None:

        """
            Инициализация класса мэтчера.

            Parameters:
                needles_  (List[Dict]) : Список записей, для которых мы ищем мэтчи.
                haystack_ (List[Dict]) : Список запискй, среди которых мы ищем мэтчи.
        """
        
        self.needles_ = needles
        self.haystack_ = haystack


    def get_name_score(self, this_record: Dict, other_record: Dict) -> float:

        """
            Функция для рассчета схожести по имени.

            Note: Функция вынесна отдельно для более простой замены и расширения функциональности.
                Скорее всего, в более поздней версии она будет заменена.

            Args:
                this_record     (Dict) : Запись, в которой будут сравниваться, соответсвующие поля.
                other_record    (Dict) : Запись, в которой будут сравниваться, соответсвующие поля.

            Returns:
                float : схожесть поля от 0 до 1
        """

        if this_record['name'] == None or other_record['name'] == None\
            or len(this_record['name']) == 0 or len(other_record['name']) == 0:
            return 0

        return ratio(this_record["name"][0].lower(), other_record["name"][0].lower())
    
    def get_middlename_score(self, this_record: Dict, other_record: Dict) -> float:

        """
            Функция для рассчета схожести по отчеству.

            Note: Функция вынесна отдельно для более простой замены и расширения функциональности.
                Скорее всего, в более поздней версии она будет заменена.

            Args:
                this_record     (Dict) : Запись, в которой будут сравниваться, соответсвующие поля.
                other_record    (Dict) : Запись, в которой будут сравниваться, соответсвующие поля.

            Returns:
                float : схожесть поля от 0 до 1
        """

        if this_record['middleName'] == None or other_record['middleName'] == None\
            or len(this_record['middleName']) == 0 or len(other_record['middleName']) == 0:
            return 0

        return ratio(this_record["middleName"][0].lower(), other_record["middleName"][0].lower())

    def get_surname_score(self, this_record: Dict, other_record: Dict) -> float:

        """
            Функция для рассчета схожести по фамилии.

            Note: Функция вынесна отдельно для более простой замены и расширения функциональности.
                Скорее всего, в более поздней версии она будет заменена.

            Args:
                this_record     (Dict) : Запись, в которой будут сравниваться, соответсвующие поля.
                other_record    (Dict) : Запись, в которой будут сравниваться, соответсвующие поля.

            Returns:
                float : схожесть поля от 0 до 1
        """
        
        if this_record['surname'] == None or other_record['surname'] == None\
            or len(this_record['surname']) == 0 or len(other_record['surname']) == 0:
            return 0

        return ratio(this_record["surname"][0].lower(), other_record["surname"][0].lower())

    def get_address_score(self, this_record: Dict, other_record: Dict) -> float:

        """
            Функция для рассчета схожести по фдресу.

            Note: Функция вынесна отдельно для более простой замены и расширения функциональности.
                Скорее всего, в более поздней версии она будет заменена.

            Args:
                this_record     (Dict) : Запись, в которой будут сравниваться, соответсвующие поля.
                other_record    (Dict) : Запись, в которой будут сравниваться, соответсвующие поля.

            Returns:
                float : схожесть поля от 0 до 1
        """

        if this_record['birthplace'] == None or other_record['birthplace'] == None\
            or len(this_record['birthplace']) == 0 or len(other_record['birthplace']) == 0:
            return 0

        return ratio(this_record["birthplace"][0].lower(), other_record["birthplace"][0].lower())


    def get_score(self, this_record: Dict, other_record: Dict) -> float:

        """
            Функция для рассчета схожести по всем признакам.

            Args:
                genotek_records (List[Dict]) : Записи из базы генотека.
                feature_list (tuple)         : Список нужных признаков.

            Returns:
                float : схожесть записи (чем больше score, тем более схожи записи)
        """

        # coefficients will be determined experimentally. For now each feature has equal weights

        coef_1, coef_2, coef_3, coef_4 = 1, 1, 1, 1

        # code in get_<feature>_score pretty much the same, but in future modifications feature score implementations may be different.

        name_score       = coef_1 * self.get_name_score(this_record, other_record)
        surname_score    = coef_2 * self.get_surname_score(this_record, other_record)
        address_score    = coef_3 * self.get_address_score(this_record, other_record)
        middlename_score = coef_4 * self.get_middlename_score(this_record, other_record)

        return name_score + surname_score + address_score + middlename_score

    def bucketizer(self, haystack: List[Dict], hasher: Callable[[Dict, int], int], n_buckets: int) -> List[List[Dict]]:

        """
            Функция разбивает список записей на список бакетов с помощью hasher

            Args:
                haystack  (List[Dict])                 : Записи, которые необходимо разбить на бакеты.
                hasher    (Callable[[Dict, int], int]) : Функция, вычисляющая индекс бакета.
                n_buckets (int)                        : Количество бакетов.

            Returns:
                List[Dict]: Список бакетов. Последний бакет содержит значения, на которых не удалось вычислить хеш.
        """
        
        buckets = []
        
        for i in range(n_buckets):
            buckets.append([])
        buckets.append([]) # idx: -1 bucket for unbucketed data

        for element in haystack:
            buckets[hasher(element, n_buckets)].append(element)
        
        return buckets
    
    def linear_search(self, needle: Dict, haystack: List[Dict], in_score: float, in_match: Dict) -> Tuple[float, Dict]:

        """
            Линейный поиск записи needle в списке записей haystack.

            Args:
                needle (Dict)         : Запись, для которой мы ищем мэтч.
                haystack (List[Dict]) : Список записей среди, котрых мы ищем мэтч.
                in_score (tuple)      : Значение схожести, которое мы пытаемся превзойти
                in_match (Dict)       : Наиболее схожий объект

            Returns:
                Tuple[float, Dict] Наиболее подходящий мэтч, среди всего haystack.
        """

        best_score = in_score
        best_match = in_match

        for element in haystack:
            
            if needle["treeId"] == element["treeId"]:
                continue
            
            score = self.get_score(needle, element)
            
            if score > best_score:
                best_score = score
                best_match = element
        
        return best_score, best_match


    def get_matches_bucketized(self, hasher: Callable[[Dict, int], int], n_buckets: int) -> List[Tuple[float, Dict, Dict]]:

        """
            Функция для поиска мэтчей для needles_ по бакетированному haystack_

            Args:
                hasher: Callable[[Dict, int], int] : Хешер для определения индекса бакета.
                n_buckets                          : Количество бакетов.

            Returns:
                List[Tuple[float, Dict, Dict]]     : Список мэтчей.
        """
        
        matches = []


        haystack_bucketized = self.bucketizer(self.haystack_, hasher, n_buckets)

        for needle in self.needles_:

            hash_out = hasher(needle, n_buckets)
            
            if hash_out == -1: # record has a year, but it is outside main buckets interval

                best_score, best_match = self.linear_search(needle, haystack_bucketized[-1], float("-inf"), None)

            if hash_out != -2: # year field is invalid

                best_score, best_match = self.linear_search(needle, self.haystack_, float("-inf"), None)
                    
            else: # valid year field let's check corresponding bucket and "unbucketed" bucket

                best_score, best_match = self.linear_search(needle, haystack_bucketized[hasher(needle, n_buckets)], float("-inf"), None)
                best_score, best_match = self.linear_search(needle, haystack_bucketized[-1], best_score, best_match)
                

            matches.append([best_score, {"record_id" : needle["_id"]}, {"match_id" : best_match["_id"]}])

        return matches






def main(needles_path: str, haystack_path: str, save_path: str) -> None:

    """
       Основная функция для контроля программы.

        Args:
            needles_path (List[Dict]) : Путь до файла, для записей которого нужно найти мэтчи
            haystack_path (str)       : Путь до файла, где нужно искть мэтчи
            save_path                 : Путь до файла, куда сохраняем

        Returns:
            None
    """
    
    # read data

    needles = reader(needles_path, FEATURE_LIST)
    haystack = reader(haystack_path, FEATURE_LIST)

    # get matches

    matcher = Matcher(needles, haystack)
    matches = matcher.get_matches_bucketized(decade_hasher, n_buckets=25)

    # save matches

    writer(matches, save_path)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('needles_path')
    parser.add_argument('haystack_path')
    parser.add_argument('save_path')
    
    args = parser.parse_args()
    main(args.needles_path, args.haystack_path, args.save_path)
