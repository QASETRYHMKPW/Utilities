import argparse
import math
import os
import sys

import yaml
from multiprocessing import Pool
from typing import List
from argparse import RawTextHelpFormatter

CONFIG_KEY_DELIMITER = "group-delimiter"

CONFIG_KEY_INFLATE_BY_CASE = 'inflate-by-case'

CONFIG_KEY_GROUPS = 'groups'

BATCH_SIZE = 2000


def inflate_word(word: str):
    """
    Generate all cases combination using given word
    :param word:
    :return:
    """
    temp = []
    for ch in word.lower():
        if ch.isalpha():
            temp.append([ch.upper(), ch.lower()])
        else:
            temp.append([ch])

    count = math.prod([len(x) for x in temp])
    joined = []
    for idx, e in enumerate(temp):
        item_repeat = int(math.ceil(count / pow(2, idx + 1)))
        list_repeat = pow(2, idx)
        new = [item for item in e for _ in range(item_repeat)] * list_repeat
        joined.append(new)

    transposed = list(map(list, zip(*joined)))
    return [''.join(x) for x in transposed]


def enumerate_keyword_cases(group_seeds: List) -> List:
    keywords = []
    for seeds in group_seeds:
        keyword_group = []
        for seed in seeds:
            keyword_group.append(inflate_word(seed))

        keywords.append([x for sub_list in keyword_group for x in sub_list])
    return keywords


def dec_to_variant_base(dec_number, variant_base: []) -> List:
    ret = []
    number = dec_number
    for b in variant_base:
        if b == 0:
            ret.append(0)
            continue
        i, n = divmod(number, b)
        ret.append(i)
        number = n
    return ret


def generate(index_range: range, keywords: List[List[str]], group_delimiter: str) -> List[str]:
    print(f"Processing range: {index_range}")
    all_pwd = []
    keywords_len = [len(x) for x in keywords]
    variant_base = [1]

    first = keywords_len[0]
    variant_base.append(first)
    for second in keywords_len[1::]:
        y = first * second
        variant_base.append(y if second != 1 else 0)
        first = y
    variant_base.reverse()

    for overall_index in index_range:
        pwd = []
        indices = dec_to_variant_base(overall_index, variant_base)
        indices.reverse()
        for i, words in enumerate(keywords):
            pwd.append(words[indices[i]])
        all_pwd.append(group_delimiter.join(pwd))
        overall_index += 1
    return all_pwd


def split(a, n):
    k, m = divmod(a, n)
    return [range(i * k + min(i, m), (i + 1) * k + min(i + 1, m)) for i in range(n)]


def main():
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument('-c', '--config', nargs='?', required=True, dest='config_file',
                        help="configuration file in yaml format, example:\n"
                             "\tgroup-delimiter: \"-\"\n"
                             "\tinflate-by-case: true\n"
                             "\tgroups: [\n"
                             "\t  [ "
                             "\t    ['jan', 'john'],\n"
                             "\t    ['doe'],\n"
                             "\t    ['877867']\n"
                             "\t  ]\n"
                             "\t]\n")
    parser.add_argument('-o', '--output', nargs='?', required=True, dest="output_file",
                        help="output file path")

    args = parser.parse_args()
    config_file = args.config_file
    output_file = args.output_file

    if not os.path.exists(config_file):
        print("ERROR: config file does not exists", file=sys.stderr)
        exit(1)

    with open(config_file) as file:
        configs = yaml.load(file, yaml.FullLoader)

    try:
        output = open(output_file, 'w')
    except Exception as ex:
        print(f"ERROR: Failed to create output file:\n{ex}")
        exit(1)
    else:
        with output:
            groups = configs[CONFIG_KEY_GROUPS]
            for group in groups:
                if configs[CONFIG_KEY_INFLATE_BY_CASE]:
                    keywords = enumerate_keyword_cases(group)
                else:
                    keywords = group

                gen_count = math.prod([len(x) for x in keywords])
                delimiter = configs[CONFIG_KEY_DELIMITER]

                if gen_count < BATCH_SIZE:
                    result = generate(split(gen_count, 1)[0], keywords, delimiter)
                    save_to_file(result, output)
                else:
                    ranges = split(gen_count, gen_count // BATCH_SIZE)
                    with Pool(min(os.cpu_count(), len(ranges))) as p:
                        results = p.starmap(generate, [(r, keywords, delimiter) for r in ranges])
                    for r in results:
                        save_to_file(r, output)


def save_to_file(pwd_list: List[str], output) -> None:
    for p in pwd_list:
        output.write(p + '\n')


if __name__ == "__main__":
    main()
