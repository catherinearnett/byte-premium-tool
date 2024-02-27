import os
import argparse
from torch.nn import functional as F
import torch
import numpy as np
import copy
import statsmodels.formula.api as smf
import pandas as pd
import matplotlib.pyplot as plt


def parse_args():
    parser = argparse.ArgumentParser(description='Retrieves or calculates estimated byte ratio')

    parser.add_argument('--language1', '-l1', type=str, required = True,
                        help='ISO639-3 and ISO 15924 for Language 1, separated by an underscore, e.g. eng_latn')
    parser.add_argument('--language2', '-l2', type=str,required = True,
                        help='ISO639-3 and ISO 15924 for Language 2, separated by an underscore, e.g. eng_latn')
    parser.add_argument('--l1text', '-t1', type=str,
                        help='path to text file for language 1 (if L1 is not in dataset)')
    parser.add_argument('--l2text', '-t2', type=str,
                        help='path to text file for language 2 (if L2 is not in dataset). Should be a parallel text to l1text.')
    parser.add_argument('--l1family', '-f1', type=str,
                        help='language family for Language 1')
    parser.add_argument('--l1writingtype', '-w1', type=str,
                        help='Writing Type for Language 1')
    parser.add_argument('--l1scriptname', '-s1', type=str,
                        help='Script name for Language 1')
    parser.add_argument('--l2family', '-f2', type=str,
                        help='language family for Language 2')
    parser.add_argument('--l2writingtype', '-w2', type=str,
                        help='Writing Type for Language 2')
    parser.add_argument('--l2scriptname', '-s2', type=str,
                        help='Script name for Language 2')
    args = parser.parse_args()
    return args

def process_args(args):
    try:
        language1 = args.language1
    except:
        print("Error: Please specify ISO639-3 and ISO 15924 for Language 1, separated by an underscore, e.g. eng_lat.")

    try:
        language2 = args.language2
    except:
        print("Warning: Default Language 2 is English")
        language2 = None

    if args.l1text:
        try:
            assert os.path.exists(args.l1text)
            with open(args.l1text, "r", encoding = 'utf-8') as f:
                l1text = f.read().splitlines()
        except:
            print("Error: 'l1text' argument does not have a valid path.")
            l1text = None

    if args.l2text:
        try:
            assert os.path.exists(args.l2text)
            with open(args.l2text, "r", encoding = 'utf-8') as f:
                l2text = f.read().splitlines()
        except:
            print("Error: 'l2text' argument does not have a valid path.")
            l2text = None

    if args.l1writingtype:
        try:
            l1writingtype = args.l1writingtype
        except:
            print("Warning: no writing type for Language 1 was provided")
            l1writingtype = None

    if args.l1scriptname:
        try:
            l1scriptname = args.l1scriptname
        except:
            print("Warning: no script name for Language 1 was provided")
            l1scriptname = None

    if args.l1family:
        try:
            l1family = args.l1family
        except:
            print("Warning: no language family for Language 1 was provided")
            l1family = None

    if args.l2writingtype:
        try:
            l2writingtype = args.l2writingtype
        except:
            print("Warning: no writing type for Language 2 was provided")
            l2writingtype = None

    if args.l2scriptname:
        try:
            l2scriptname = args.l2scriptname
        except:
            print("Warning: no script name for Language 1 was provided")
            l2scriptname = None

    if args.l2family:
        try:
            l2family = args.l2family
        except:
            print("Warning: no language family for Language 2 was provided")
            l2family = None

    return args

def retrieve_calculated_ratio(lang, all):
    lang_byte_premium = all[all['lang'] == lang]['byte_coef'].values[0]
    return lang_byte_premium


def calculate_bc_ratio_entropy(content):
    n_chars = len(content)
    n_bytes = len(content.encode('utf-8'))
    list_chars = []
    char_freq = []
    for c in range(len(content)):
        current_char = content[c]
        if current_char not in list_chars:
            list_chars.append(current_char)
            char_freq.append(1)
        else:
            index = list_chars.index(current_char)
            char_freq[index] += 1
    byte_character_ratio = n_bytes/n_chars
    calculated_entropy = scipy.stats.entropy(np.array(char_freq))
    return byte_character_ratio, calculated_entropy

def calculate_byte_premium(l1text, l2text):
    l1_n_bytes = len(l1text.encode('utf-8'))
    l2_n_bytes = len(l2text.encode('utf-8'))
    byte_premium = l1_n_bytes/l2_n_bytes
    return byte_premium


def fit_linear_models(l1, l1writingtype, l1scriptname, l1family, all, l1text='default.txt'):
    if l1 in list(all['lang']):
    # all[all['lang' == l1]]['bytes_per_char'] and all[all['lang' == l1]]['char_entropy']:
        bytes_per_char_eng_latn = all[all['lang' == 'eng_latn']]['bytes_per_char']
        bytes_per_char_l1= all[all['lang' == l1]]['bytes_per_char']
        l1_df = all[all['lang' == l1]]
        train_df = all[all['lang' != l1]]
    else:
        bytes_per_char_l1, char_entropy = calculate_bc_ratio_entropy(l1text)
        if l1family:
            family = l1family
        elif l1family not in list(all['family']):
            family = 'NA'
        else:
            family = 'NA'
        if l1scriptname:
            script_name = l1scriptname
        elif l1scriptname not in list(all['script_name']):
            family = 'NA'
        else:
            script_name = 'NA'
        l1_df = pd.DataFrame({
                'lang': [l1],
                'bytes_per_char': [bytes_per_char_l1],
                'char_entropy': [char_entropy],
                'writing_type': [l1writingtype],
                'script_name': [script_name],
                'family': [family]
                })
        train_df = all

    #regression 1
    model_i = smf.ols(formula='char_coef ~ char_entropy + writing_type + script_name + family',
                      data=train_df, missing='drop').fit()
    pred = model_i.predict(l1_df).values[0]  # Predicted char premium.
    prediction_i = pred * bytes_per_char_l1 / bytes_per_char_eng_latn  # Predicted byte premium.
    # regression 2
    model_ii = smf.ols(formula='char_coef ~ char_entropy + writing_type + script_name',
                       data=train_df, missing='drop').fit()
    pred = model_ii.predict(l1_df).values[0]  # Predicted char premium.
    prediction_ii = pred * bytes_per_char_l1 / bytes_per_char_eng_latn  # Predicted byte premium.
    # regression 3
    model_iii = smf.ols(formula='char_coef ~ char_entropy + writing_type',
                        data=train_df, missing='drop').fit()
    pred = model_iii.predict(l1_df).values[0]  # Predicted char premium.
    prediction_iii = pred * bytes_per_char_l1 / bytes_per_char_eng_latn  # Predicted byte premium.

    l1_script_ct = len(train_df[train_df['writing_type' == l1writingtype]])
    if l1writingtype is None:
        print('Please enter a valid writing type (abjad, abugida, alphabet, or logography).')
        return np.nan()
    elif l1_script_ct < 5:
        return prediction_iii
    elif l1_df['family'] == 'NA' and l1_df['script_name'] == 'NA':
        return prediction_iii
    elif l1_df['family'] == 'NA':
        return prediction_ii
    else:
        return prediction_i

def main():
    args = parse_args()
    args = process_args(args)
    all_data_df = pd.read_csv("cleaned_data.tsv", sep="\t", header=0)
    if (args.language1 in list(all_data_df['lang'])) and (args.language2 in list(all_data_df['lang'])):
        l1_retrieved = retrieve_calculated_ratio(args.language1, all_data_df)
        l2_retrieved = retrieve_calculated_ratio(args.language2, all_data_df)
        l1_l2_ratio = l1_retrieved/l2_retrieved
        print(l1_l2_ratio)
        return l1_l2_ratio
    elif args.l2text:
        byte_premium = calculate_byte_premium(args.l1text, args.l2text)
        return byte_premium
    else:
        if args.language2 == 'eng_latn':
            l1_predictions = fit_linear_models(args.language1, args.l1writingtype, args.l1scriptname, args.l1family, all_data_df, args.l1text)
            return l1_predictions
        else:
            l1_predictions = fit_linear_models(args.language1, args.l1writingtype, args.l1scriptname, args.l1family, all_data_df, args.l1text)
            l2_predictions = ffit_linear_models(args.language2, args.l2writingtype, args.l2scriptname, args.l2family, all_data_df, args.l2text)
            l1_l2_predicted_ratio = l1_predictions/l2_predictions
            return l1_l2_predicted_ratio


if __name__ == "__main__":
    main()
