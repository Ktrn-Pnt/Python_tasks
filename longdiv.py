#!/usr/bin/env python3
def search_dislocation(len_first: int, len_second: int) -> int:
    return len_first - len_second


def search_difference(dividend_: int, digit: int) -> int:
    output = dividend_ - int(str(digit) + '0' * (len(str(dividend_)) - len(str(digit))))
    j = 1
    while output < 0:
        output = dividend_ - int(str(digit) + '0' * (len(str(dividend_)) - len(str(digit)) - j))
        j += 1
    return output


def long_division(dividend: int, divider: int):
    str_dividend = str(dividend)
    quotient = dividend // divider
    str_quotient = str(quotient)
    start_dividend = int(str_quotient[0]) * divider
    start_dislocation = 0

    for j in range(1, len(str_dividend)):
        if int(str_dividend[:j]) >= divider:
            start_dislocation = j - len(str(start_dividend))
            break

    output = f"{dividend}|{divider}\n" + ' ' * start_dislocation + f"{start_dividend}" + (
            len(str_dividend) - len(str(start_dividend)) - start_dislocation) * ' ' + f"|{quotient}\n"

    if quotient == 0:
        start_dividend = dividend
        return f"{dividend}|{divider}\n{start_dividend}" + (
                len(str_dividend) - len(str(start_dividend))) * ' ' + f"|{quotient}\n"

    difference = search_difference(dividend, int(start_dividend))

    if difference < divider:
        dislocation = search_dislocation(len(str_dividend), len(str(difference)))
        if difference != 0:
            return output + ' ' * dislocation + str(difference)
        else:
            return output + ' ' * dislocation + '0'

    j = 1

    while j < len(str_quotient):
        if int(str_quotient[j]) == 0:
            j += 1
            continue

        temp_quotient = divider * int(str_quotient[j])
        temp_rem = str(difference)[:len(str(temp_quotient))]
        dislocation = search_dislocation(len(str_dividend), len(str(difference)))
        output += " " * dislocation + str(temp_rem) + "\n" + " " * (len(str_dividend) - len(str(difference))) + str(
            temp_quotient) + "\n"
        difference = search_difference(difference, int(temp_quotient))

        j += 1

        if j == len(str_quotient):
            dislocation = search_dislocation(len(str_dividend), len(str(int(temp_rem) - temp_quotient)))
            return output + ' ' * dislocation + str(int(temp_rem) - temp_quotient)


def main():
    print(long_division(123, 123))
    print()
    print(long_division(1, 1))
    print()
    print(long_division(15, 3))
    print()
    print(long_division(3, 15))
    print()
    print(long_division(12345, 25))
    print()
    print(long_division(1234, 1423))
    print()
    print(long_division(87654532, 1))
    print()
    print(long_division(24600, 123))
    print()
    print(long_division(4567, 1234567))
    print()
    print(long_division(246001, 123))
    print()
    print(long_division(100000, 50))
    print()
    print(long_division(123456789, 531))
    print()
    print(long_division(425934261694251, 12345678))
    print()
    print(long_division(12345, 25))
    print()
    print(long_division(1234, 1423))
    print()
    print(long_division(24600, 123))
    print()
    print(long_division(246001, 123))
    print()


if __name__ == '__main__':
    main()