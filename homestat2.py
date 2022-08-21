#!/usr/bin/env python3
import collections


def get_years_dict(filename):
    years = collections.defaultdict()
    f = open(filename, 'r', encoding='cp1251')
    for l in f:
        if '<h3>20' in l:
            start_ind = l.find('<h3>20') + 4
            current_key = l[start_ind:start_ind + 4]
            years[current_key] = collections.Counter()

        if '/a' in l:
            href_ind = l.find('href')
            l = l[href_ind:]
            start_index = l.find(' ')
            end_ind = l.find('</a')
            c_name = l[start_index + 1:end_ind]
            years[current_key][c_name] += 1
    f.close()
    return years


def get_gender_dict(names):
    girls_names = collections.Counter()
    boys_names = collections.Counter()

    for key, value in names.items():  # check forein names
        if ((key[-1] == 'а' or key[-1] == 'я' or key == "Любовь") and
                (key != "Лёва" and key != "Никита" and key != "Илья")):
            girls_names[key] = value
        else:
            boys_names[key] = value
    return (girls_names, boys_names)


def make_stat(filename):
    """
    Функция вычисляет статистику по именам за каждый год с учётом пола.
    """
    years_dict = get_years_dict(filename)
    for key, value in years_dict.items():
        years_dict[key] = get_gender_dict(value)
    return years_dict


def extract_years(stat):
    """
    Функция принимает на вход вычисленную статистику и выдаёт список годов,
    упорядоченный по возрастанию.
    """
    return sorted(stat)


def extract_general(stat):
    """
    Функция принимает на вход вычисленную статистику и выдаёт список tuple'ов
    (имя, количество) общей статистики для всех имён.
    Список должен быть отсортирован по убыванию количества.

    """
    general_counter = collections.Counter()
    for year in stat:
        for gender in stat[year]:
            general_counter += gender
    return general_counter.most_common()


def extract_general_male(stat):
    """
    Функция принимает на вход вычисленную статистику и выдаёт список tuple'ов
    (имя, количество) общей статистики для имён мальчиков.
    Список должен быть отсортирован по убыванию количества.
    """
    c = collections.Counter()
    for year in stat:
        c += stat[year][1]
    return c.most_common()


def extract_general_female(stat):
    """
    Функция принимает на вход вычисленную статистику и выдаёт список tuple'ов
    (имя, количество) общей статистики для имён девочек.
    Список должен быть отсортирован по убыванию количества.
    """
    c = collections.Counter()
    for year in stat:
        c += stat[year][0]
    return c.most_common()


def extract_year(stat, year):
    """
    Функция принимает на вход вычисленную статистику и год.
    Результат — список tuple'ов (имя, количество) общей статистики для всех
    имён в указанном году.
    Список должен быть отсортирован по убыванию количества.
    """
    c = collections.Counter()
    for gender in stat[year]:
        c += gender
    return c.most_common()


def extract_year_male(stat, year):
    """
    Функция принимает на вход вычисленную статистику и год.
    Результат — список tuple'ов (имя, количество) общей статистики для всех
    имён мальчиков в указанном году.
    Список должен быть отсортирован по убыванию количества.
    """
    return stat[year][1].most_common()


def extract_year_female(stat, year):
    """
    Функция принимает на вход вычисленную статистику и год.
    Результат — список tuple'ов (имя, количество) общей статистики для всех
    имён девочек в указанном году.
    Список должен быть отсортирован по убыванию количества.
    """
    return stat[year][0].most_common()


if __name__ == '__main__':
    pass
