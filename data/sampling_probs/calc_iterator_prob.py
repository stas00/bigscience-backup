import os
import math
import json
import argparse
import subprocess
from collections import OrderedDict
from new_to_old_format_data_path import output_sampling_probs_new_format

SPLIT = [0, 0.949, 0.999, 1.0]


def calc_multinomial_sampling_prob_with_penalty(dataset_size, alpha=.5):
    """
    Calculate multinomial probability distribution based on https://arxiv.org/pdf/1901.07291.pdf (section 3.1)
    :dataset_size: A dictionary contains the size (value) of each of the language (key).
    """
    tot_size = 0
    probs = OrderedDict()
    for lang, size in dataset_size.items():
        tot_size += size
    for lang, size in dataset_size.items():
        probs[lang] = size / tot_size

    pen_prob = OrderedDict()
    tot_pen_prob = 0.0
    for lang, prob in probs.items():
        tot_pen_prob += (prob ** alpha)
    sum_ = 0.0
    for lang, prob in probs.items():
        pen_prob[lang] = (prob ** alpha) / tot_pen_prob
        sum_ += pen_prob[lang]
    assert math.fabs(1 - sum_) < 1e-6
    return pen_prob


def get_size_stats(args):
    """
    Calculate size for each of the iterator.
    It recusively iterate though a directory to find a specific extension file and report their size in preferred format.
    """
    lang_size_dict = {}
    for (dirpath, dirnames, filenames) in os.walk(args.data_folder_path):
        for filename in filenames:
            if not (filename.startswith(args.name_prefix) and filename.endswith(args.extension_name)):
                continue
            full_file_path = os.path.join(dirpath, filename)
            lang_size = subprocess.check_output("du -s {}".format(full_file_path), shell=True)
            lang_size = int(lang_size.decode("utf-8").split("\t")[0])
            if args.size_format == 'KB':
                _conv = 1
            elif args.size_format == 'MB':
                _conv = 1024
            elif args.size_format == 'GB':
                _conv = 1024 * 1024
            elif args.size_format == 'TB':
                _conv = 1024 * 1024 * 1024
            lang_size_ = round(lang_size / float(_conv), 2)
            lang_size_dict[full_file_path] = lang_size_
    return lang_size_dict


def print_stat(args, lang_size_dict, value_name='size'):
    """
    Print size statistics.
    """
    lang_list = sorted([(k, v) for k, v in lang_size_dict.items()], key=lambda tup: tup[1])
    total_size = 0
    print("\nLanguage : ({})".format(value_name))
    print("-" * 20)
    for lang, size in lang_list:
        print("{} :   {}".format(lang, size))
        total_size += size
    print("-" * 20)
    print("Total size : {}".format(total_size))


def removesuffix(string, suffix):
    if string.endswith(suffix):
        string = string[:-len(suffix)]
    return string


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-folder-path', type=str, required=True,
                        help='Path to the data folder')
    parser.add_argument('--size-format', type=str, required=True,
                        help='Calculation will be done in byte, mega-byte, giga-byte or tera-byte',
                        choices=['KB', 'MB', 'GB', 'TB'])
    parser.add_argument('--alpha', type=float, required=True,
                        help='Sampling penalty.')
    parser.add_argument('--output-dir', type=str, required=True,
                        help='Output directory where sampling prob_dict will be saved.')
    parser.add_argument('--name-prefix', type=str, required=True,
                        help='File name prefix to match. Combination of `--name-prefix` and --extension-name will be used to select file.')
    parser.add_argument('--extension-name', type=str, required=True,
                        help='Extension of the file to match. Combination of `--name-prefix` and --extension-name will be used to select file')
    parser.add_argument('--old-format', action="store_true",
                        help='Legacy option')

    args = parser.parse_args()
    size_dict = get_size_stats(args)
    print_stat(args, size_dict, value_name=args.size_format)
    sampling_probability = calc_multinomial_sampling_prob_with_penalty(
        size_dict, alpha=args.alpha
    )
    print_stat(args, sampling_probability, 'probability')
    total_contrib = 0
    print("\nLanguage : Per epoch contribution in {}".format(args.size_format))
    print("-" * 50)
    for lang, prob in sampling_probability.items():
        sampling_probability[lang] = (prob, size_dict[lang])
        lang_contrib_size = round(size_dict[lang] * prob, 2)
        print("{} :   {}  ({}  ->  {})".format(lang, prob, size_dict[lang], lang_contrib_size))
        total_contrib += lang_contrib_size
    print("-" * 50)
    print("Total size : {}".format(total_contrib))

    open(os.path.join(args.output_dir, 'iterator_selection_prob.{}.json'.format(args.alpha)), "w").write(
        json.dumps(sampling_probability, indent=4)
    )

    if args.old_format:
        with open(os.path.join(args.output_dir, "dataset_probabilities.{}.txt".format(args.alpha)), "w") as fout:
            fout.write(
                " ".join([f"{prob[0]} {removesuffix(path, '.bin')}" for path, prob in sampling_probability.items()]))
        pass
    else:
        output_sampling_probs_new_format(sampling_probability, args.output_dir, args.alpha)

if __name__ == '__main__':
    main()
