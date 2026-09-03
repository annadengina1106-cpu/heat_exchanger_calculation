# -*- coding: utf-8 -*-


# Итоговая аттестационная работа
# Программа для расчета кожухотрубчатого теплообменника
# Расчет кожухотрубчатого теплообменника охлаждения бензола
# Тип лицензии: GNU GPL
# Создано: 13.06.2023
# Автор: Деньгина Анна Дмитриевна
# Организация: Уральский Федеральный Университет
# Подразделение: кафедра "Технологии органического синтеза"

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import csv
import math
from PIL import Image


# =============================
# Функция входа в программу
# =============================

def main():
    # Ввод исходных данных
    g1 = float(input('Введите значение производительности бензола, кг/с: '))
    t1_start = float(input('Введите значение начальной температуры бензола, гр.С: '))
    t1_end = float(input('Введите значение конечной температуры бензола, гр.С: '))
    t2_start = float(input('Введите значение начальной температуры воды, гр.С: '))
    t2_end = float(input('Введите значение конечной температуры воды, гр.С: '))
    # Расчет
    dt_max, dt_min, dt_mid, t_mid2, t_mid1 = driving_force(t1_start, t1_end, t2_start, t2_end)
    q = get_heat(t_mid2, g1, t1_start, t1_end, dt_mid)
    g2 = get_expwater(q, t2_end, t2_start)
    dt_mid, t_mid1, t_mid2, s1, s2, d_k, n_z, n = choice(t1_start, t1_end, t2_start, t2_end, dt_max, dt_min, dt_mid,
                                                         t_mid2, t_mid1)
    t_st1, t_st2, alpha1, alpha2, pr1, pr2 = correction_heat(dt_mid, t_mid1, t_mid2, s1, s2, g1, g2)
    f = coeff_heat(q, t_st1, t_st2, alpha1, alpha2, pr1, pr2, dt_mid, t_mid1, t_mid2)
    # Вывод
    output(f, d_k, n_z, n)


# ==================================
# Функция расчета расхода воды
# ==================================

def get_expwater(q, t2_end, t2_start):
    t_list, c_list, ro_list, u_list, la_list, pr_list = file_reader('Исходные данные вода.csv')
    t = (t2_end + t2_start) / 2
    c, ro, u, la, pr = get_data(t, t_list, c_list, ro_list, u_list, la_list, pr_list)
    g2 = q / (c * (t2_end - t2_start))
    return g2


# ==================================================================
# Функция ориентировочного расчета теплообменника и теплового баланса
# ==================================================================

def get_heat(t_mid2, g1, t1_start, t1_end, dt_mid):
    t_list, c_list, ro_list, u_list, la_list, pr_list = file_reader('Исходные данные бензол.csv')
    c, ro, u, la, pr = get_data(t_mid2, t_list, c_list, ro_list, u_list, la_list, pr_list)
    q = g1 * c * (t1_start - t1_end)
    re = 10000
    n_z = int(4 * g1 / (3.14 * 0.016 * re * u * 10 ** (-6)))
    k = 500
    f = q / (k * dt_mid)
    print('Число труб при ориентировочном значении Re = 10000: ', n_z)
    print('Ориентировочная расчетная поверхность теплообмена: ', '%.2f' % f, 'м2')
    return q


# ==================================
# Функция определения движущей силы
# ==================================

def driving_force(t1_start, t1_end, t2_start, t2_end):
    dt_max = t1_start - t2_end
    dt_min = t1_end - t2_start
    dt_mid = (dt_max - dt_min) / (math.log(dt_max / dt_min))
    t_mid2 = 0.5 * (t1_start + t1_end)
    t_mid1 = t_mid2 + dt_mid
    return dt_max, dt_min, dt_mid, t_mid2, t_mid1


# ==================================
# Функция выбора теплообменника
# ==================================

def choice(t1_start, t1_end, t2_start, t2_end, dt_max, dt_min, dt_mid, t_mid2, t_mid1):
    print("Выберите в таблице подходящий теплообменник")
    im = Image.open('Таблица.jpg')
    im.show()
    d_k = float(input('Введите значение диаметра кожуха: '))
    n = float(input('Введите значение числа ходов: '))
    n_z = float(input('Введите значение числа труб на один ход: '))
    s1 = float(input('Введите значение площади сечения потока в вырезе перегородок: '))
    s2 = float(input('Введите значение площади сечения потока между перегородками: '))
    # Уточнение средней движущей силы
    if n > 1:
        a = ((t1_start - t1_end) ** 2 + (t2_end - t2_start) ** 2) ** 0.5
        dt_mid = a / (math.log((dt_max + dt_min + a) / (dt_max + dt_min - a)))
        t_mid2 = 0.5 * (t2_start + t2_end)
        t_mid1 = t_mid2 + dt_mid
    return dt_mid, t_mid1, t_mid2, s1, s2, d_k, n_z, n


# ===================================================
# Функция уточненного расчета теплообменника
# ===================================================

def correction_heat(dt_mid, t_mid1, t_mid2, s1, s2, g1, g2):
    t_list, c_list, ro_list, u_list, la_list, pr_list = file_reader('Исходные данные бензол.csv')
    c, ro, u, la, pr = get_data(t_mid1, t_list, c_list, ro_list, u_list, la_list, pr_list)
    # средняя скорость движения бензола
    w1 = g1 / (s1 * ro)
    # критерий Рейнольдса для бензола
    re1 = w1 * ro * 0.016 / (u * 10 ** (-6))
    if re1 < 10000:
        nu1 = 27 * pr ** 0.43
    else:
        nu1 = 0.023 * re1 ** 0.8 * pr ** 0.4
    # коэффициент теплоотдачи
    alpha1 = nu1 * la / 0.016
    pr1 = pr
    t_list, c_list, ro_list, u_list, la_list, pr_list = file_reader('Исходные данные вода.csv')
    c, ro, u, la, pr = get_data(t_mid2, t_list, c_list, ro_list, u_list, la_list, pr_list)
    # средняя скорость движения воды
    w2 = g2 / (s2 * ro)
    # критерий Рейнольдса для воды
    re2 = w2 * ro * 0.016 / (u * 10 ** (-6))
    nu2 = 0.24 * re2 ** 0.6 * pr ** 0.36
    # коэффициент теплоотдачи
    alpha2 = nu2 * la / 0.02
    pr2 = pr
    # температура стенок труб со стороны бензола
    k = 1 / (1 / alpha1 + 5.77 * 10 ** (-4) + 1 / alpha2)
    t_st1 = t_mid1 - k * dt_mid / alpha1
    t_st2 = t_mid2 + k * dt_mid / alpha2
    return t_st1, t_st2, alpha1, alpha2, pr1, pr2


# ======================================================================
# Функция уточнения коэффициента теплопередачи и площади поверхности
# ======================================================================

def coeff_heat(q, t_st1, t_st2, alpha1, alpha2, pr1, pr2, dt_mid, t_mid1, t_mid2):
    t_list, c_list, ro_list, u_list, la_list, pr_list = file_reader('Исходные данные бензол.csv')
    c, ro, u, la, pr = get_data(t_st1, t_list, c_list, ro_list, u_list, la_list, pr_list)
    pr1_st = pr
    t_list, c_list, ro_list, u_list, la_list, pr_list = file_reader('Исходные данные вода.csv')
    c, ro, u, la, pr = get_data(t_st2, t_list, c_list, ro_list, u_list, la_list, pr_list)
    pr2_st = pr
    alpha_1 = alpha1 * (pr1 / pr1_st) ** 0.25
    alpha_2 = alpha2 * (pr2 / pr2_st) ** 0.25
    k = 1 / (1 / alpha_1 + 5.77 * 10 ** (-4) + 1 / alpha_2)
    t_st_1 = t_mid1 - k * dt_mid / alpha_1
    t_st_2 = t_mid2 + k * dt_mid / alpha_2
    delta1 = (t_st1 - t_st_1) * 100 / t_st1
    delta2 = (t_st2 - t_st_2) * 100 / t_st2
    if delta1 < 5 and delta2 < 5:
        print('Отклонения температур стенок не превышают 5%, уточнений коэффициента передачи не требуется')
    f = q / (k * dt_mid)
    return f


def output(f, d_k, n_z, n):
    print('Выбираем ближайший теплообменник с поверхностью, большей, чем расчетная - ', '%.2f' % f, 'м2')
    f1 = float(input('Введите значение площади поверхности выбранного теплообменника, м2: '))
    print('Для охлаждения бензола был выбран теплообменник со следующими параметрами:\n'
          'Диаметр кожуха - ', d_k, ', число ходов - ', n, ', число труб на один ход - ', n_z,
          ', площадь поверхности - ', f1)
    d = (f1 - f) * 100 / f
    print('Запас составит: ', '%.2f' % d, '%')


# =============================
# Функция работы с csv файлом
# =============================

def file_reader(fileName):
    t_list = []
    c_list = []
    ro_list = []
    u_list = []
    la_list = []
    pr_list = []
    # Прочитать файл и вывести на печать
    with open(fileName, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            t_list.append(float(row['T']))
            c_list.append(float(row['C']))
            ro_list.append(float(row['Ro']))
            u_list.append(float(row['U']))
            la_list.append(float(row['La']))
            pr_list.append(float(row['Pr']))
    return t_list, c_list, ro_list, u_list, la_list, pr_list


# =========================================================================
# Функция интерполяции теплофизических свойств при заданной температуре
# =========================================================================

def get_data(t, t_list, c_list, ro_list, u_list, la_list, pr_list):
    c = c_list[0]
    ro = ro_list[0]
    u = u_list[0]
    la = la_list[0]
    pr = pr_list[0]
    if (t < t_list[0]) or (t > t_list[7]):
        print('Заданное значение температуры', t, 'гр.С находится за пределами интерполяции!')
    # расчет теплофизических свойств теплоносителей при их средних температурах
    else:
        for i in range(0, (len(t_list)) - 1):
            if t == t_list[i]:
                c = c_list[i]
                ro = ro_list[i]
                u = u_list[i]
                la = la_list[i]
                pr = pr_list[i]
            else:
                if (t > t_list[i]) and (t < t_list[i + 1]):
                    c = c_list[i] + ((c_list[i + 1] - c_list[i]) / (t_list[i + 1] - t_list[i])) * (t - t_list[i])
                    ro = ro_list[i] + ((ro_list[i + 1] - ro_list[i]) / (t_list[i + 1] - t_list[i])) * (t - t_list[i])
                    u = u_list[i] + ((u_list[i + 1] - u_list[i]) / (t_list[i + 1] - t_list[i])) * (t - t_list[i])
                    la = la_list[i] + ((la_list[i + 1] - la_list[i]) / (t_list[i + 1] - t_list[i])) * (t - t_list[i])
                    pr = pr_list[i] + ((pr_list[i + 1] - pr_list[i]) / (t_list[i + 1] - t_list[i])) * (t - t_list[i])
    return c, ro, u, la, pr


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
