#!/usr/bin/env python3


import re


_exception_dict = {
    'Илья': 'male',
    'Никита': 'male',
    'Лёва': 'male',
    'Любовь': 'female'
}


def get_gender(name):
    if name in _exception_dict:
        return _exception_dict[name]
    if (name[-1] == 'а') or (name[-1] == 'я'):
        return 'female'
    return 'male'


_year_pattern = re.compile(r'<h3>(\d{4})</h3></td></tr>')
_name_pattern = re.compile(r'>.+ (.+)</a></td></tr>')


def make_stat(filename, encoding='cp1251'):
    """
    Функция вычисляет статистику по именам за каждый год с учётом пола.
    """
    statistic = {}
    current_year = "0"
    with open(filename, encoding=encoding) as file:
        for line in file:
            year_result = _year_pattern.search(line)
            if year_result:
                current_year = year_result.group(1)
                statistic[current_year] = {"male": {}, "female": {}}
                continue
            name_result = _name_pattern.search(line)
            if name_result:
                name = name_result.group(1)
                gender = get_gender(name)
                if name in statistic[current_year][gender]:
                    statistic[current_year][gender][name] += 1
                else:
                    statistic[current_year][gender][name] = 1
    return statistic


def extract_years(stat: dict):
    """
    Функция принимает на вход вычисленную статистику и выдаёт список годов,
    упорядоченный по возрастанию.
    """
    return sorted(stat.keys())


def _sort_tuples_on_second(input_tuple) -> tuple:
    return input_tuple[1], input_tuple[0]


def extract_on_conditions(
        stat: dict,
        year_cond=lambda year: True,
        gender_cond=lambda gender: True):
    result = {}
    for year in stat:
        if year_cond(year):
            for gender in stat[year]:
                if gender_cond(gender):
                    for name in stat[year][gender]:
                        if name in result:
                            result[name] += stat[year][gender][name]
                        else:
                            result[name] = stat[year][gender][name]
    return sorted(result.items(), key=_sort_tuples_on_second, reverse=True)


def extract_general(stat):
    """
    Функция принимает на вход вычисленную статистику и выдаёт список tuple'ов
    (имя, количество) общей статистики для всех имён.
    Список должен быть отсортирован по убыванию количества.
    """
    return extract_on_conditions(stat)


def extract_general_male(stat):
    """
    Функция принимает на вход вычисленную статистику и выдаёт список tuple'ов
    (имя, количество) общей статистики для имён мальчиков.
    Список должен быть отсортирован по убыванию количества.
    """
    return extract_on_conditions(stat,
                                 gender_cond=lambda gender: gender == "male")


def extract_general_female(stat):
    """
    Функция принимает на вход вычисленную статистику и выдаёт список tuple'ов
    (имя, количество) общей статистики для имён девочек.
    Список должен быть отсортирован по убыванию количества.
    """
    return extract_on_conditions(stat,
                                 gender_cond=lambda gender: gender == "female")


def extract_year(stat, year):
    """
    Функция принимает на вход вычисленную статистику и год.
    Результат — список tuple'ов (имя, количество) общей статистики для всех
    имён в указанном году.
    Список должен быть отсортирован по убыванию количества.
    """
    return extract_on_conditions(stat,
                                 year_cond=lambda y: year == y)


def extract_year_male(stat, year):
    """
    Функция принимает на вход вычисленную статистику и год.
    Результат — список tuple'ов (имя, количество) общей статистики для всех
    имён мальчиков в указанном году.
    Список должен быть отсортирован по убыванию количества.
    """
    return extract_on_conditions(stat,
                                 year_cond=lambda y: year == y,
                                 gender_cond=lambda gender: gender == "male")


def extract_year_female(stat, year):
    """
    Функция принимает на вход вычисленную статистику и год.
    Результат — список tuple'ов (имя, количество) общей статистики для всех
    имён девочек в указанном году.
    Список должен быть отсортирован по убыванию количества.
    """
    return extract_on_conditions(stat,
                                 year_cond=lambda y: year == y,
                                 gender_cond=lambda gender: gender == "female")


if __name__ == '__main__':
    stats = make_stat("home.html")
    print(extract_years(stats))
