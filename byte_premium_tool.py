"""
Compute the pairwise byte premium between two languages.

For details, see documentation above the get_pairwise_premium() function.
Sample usage:
python3 byte_premium_tool.py \
--language1=mya_mymr --language2=deu_latn

If using parallel text:
python3 byte_premium_tool.py \
--language1=xx1_xxxx --language2=eng_latn \
--text1=xx1_xxxx.txt --text2=eng_latn.txt --text_type=parallel

If predicting byte premium from monolingual text with a common script:
python3 byte_premium_tool.py \
--language1=xx1_latn --language2=eng_latn \
--text1=xx1_latn.txt --family1="Indo-European"

If predicting byte premium from monolingual text with an unknown script:
python3 byte_premium_tool.py \
--language1=xx1_xxxx --language2=eng_latn \
--text1=xx1_xxxx.txt --script_type1=alphabet

To use in Python code (run from the byte-premium-tool repository directory):
from byte_premium_tool import get_pairwise_premium
print(get_pairwise_premium('mya_mymr', 'deu_latn', verbose=False))

"""

import argparse
import codecs
from collections import Counter
import numpy as np
import os
import pandas as pd
import scipy
import statsmodels.formula.api as smf


DATA_PATH = 'all_merged_20240223.tsv'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--language1', '-l1', type=str, required=True,
                        help='ISO 639-3 and ISO 15924 for language 1, separated by an underscore, e.g. eng_latn.')
    parser.add_argument('--language2', '-l2', type=str, required=True,
                        help='ISO 639-3 and ISO 15924 for language 2, separated by an underscore, e.g. eng_latn.')
    parser.add_argument('--text1', '-t1', type=str,
                        help='Path to text file for language 1 (if languages are not in dataset).')
    parser.add_argument('--text2', '-t2', type=str,
                        help='Path to text file for language 2 (if languages are not in dataset).')
    parser.add_argument('--text_type', type=str, default='monolingual',
                        help='Whether the input texts are monolingual or parallel.')
    parser.add_argument('--script_type1', '-w1', type=str,
                        help='Script (writing) type for language 1.')
    parser.add_argument('--script_type2', '-w2', type=str,
                        help='Script (writing) type for language 2.')
    parser.add_argument('--family1', '-f1', type=str,
                        help='Language family for language 1.')
    parser.add_argument('--family2', '-f2', type=str,
                        help='Language family for language 2.')
    args = parser.parse_args()
    return args


def retrieve_calculated_premium(lang, all_data_df):
    available_langs = set(all_data_df['lang'])
    if lang in available_langs:
        return all_data_df[all_data_df['lang'] == lang]['byte_coef'].values[0]
    else:
        return None


def calculate_pairwise_premium_from_parallel(text1, text2):
    with codecs.open(text1, 'rb', encoding='utf-8') as f:
        raw_text1 = f.read()
    with codecs.open(text2, 'rb', encoding='utf-8') as f:
        raw_text2 = f.read()
    if (len(raw_text1.split('\n')) < 100) or (len(raw_text2.split('\n')) < 100):
        print('WARNING: parallel text <100 lines; byte premium estimate may be inaccurate.')
    return len(raw_text1.encode('utf-8')) / len(raw_text2.encode('utf-8'))


def get_premium_from_regression(language, all_data_df, text, script_type, family, verbose=True):
    assert text is not None, f'text path must be provided to predict byte premium for novel language: {language}'
    script = language.strip().split('_')[-1]
    script_counts = all_data_df['script_name'].value_counts()
    this_script_count = script_counts[script] if script in script_counts else 0
    # Choose regression to use.
    if this_script_count >= 5:
        known_families = set(all_data_df['family'])
        known_families.remove(np.nan)
        known_families.remove('other')
        if (family is not None) and (family in known_families):
            if verbose: print(f'Using regression I because script is common and language family is known.')
            regression_to_use = 'I'
        else:
            if family is not None:
                print(f'WARNING: family {family} is not in the set of known families: {known_families}')
            if verbose: print(f'Using regression II because script is common but language family is unknown.')
            regression_to_use = 'II'
    else:
        if verbose: print(f'Using regression III due to uncommon script: {script}')
        regression_to_use = 'III'
    # Compute character entropy and bytes-per-character ratio.
    with codecs.open(text, 'rb', encoding='utf-8') as f:
        raw_text = f.read()
    if len(raw_text.split('\n')) < 20:
        print('WARNING: monolingual text <20 lines; character entropy and bytes-per-character ratio may be inaccurate.')
    n_chars = len(raw_text)
    n_bytes = len(raw_text.encode('utf-8'))
    char_counter = Counter()
    for char in raw_text:
        char_counter[char] += 1
    char_counts = np.array(list(char_counter.values()))
    char_entropy = scipy.stats.entropy(char_counts, base=2)  # Automatically normalizes counts to sum to one.
    bytes_per_char = n_bytes / n_chars
    if verbose: print(f'Computed character entropy: {char_entropy}')
    if verbose: print(f'Computed bytes-per-character ratio: {bytes_per_char}')
    # Get script_type.
    inferred_script_type = None
    if script in set(all_data_df['script_name']):
        inferred_script_type = all_data_df[all_data_df['script_name'] == script]['writing_type'].values[0]
    if inferred_script_type is None:
        assert script_type is not None, 'script_type must be set for unknown script'
        assert script_type in ['abjad', 'abugida', 'alphabet', 'logography'], f'script_type {script_type} invalid'
    else:
        if verbose: print(f'Using inferred script type: {inferred_script_type}')
        script_type = inferred_script_type
    # Create language dataframe (regression predictors for the novel language).
    language_df = pd.DataFrame({'char_entropy': [char_entropy],
            'writing_type': [script_type],
            'script_name': [script],
            'family': [family]})
    # Run regression.
    if regression_to_use == 'I':
        linear_reg = smf.ols(formula='char_coef ~ char_entropy + writing_type + script_name + family',
                             data=all_data_df, missing='drop').fit()
    elif regression_to_use == 'II':
        linear_reg = smf.ols(formula='char_coef ~ char_entropy + writing_type + script_name',
                             data=all_data_df, missing='drop').fit()
    else:
        linear_reg = smf.ols(formula='char_coef ~ char_entropy + writing_type',
                             data=all_data_df, missing='drop').fit()
    char_ratio_pred = linear_reg.predict(language_df).values[0]  # Predicted char ratio.
    bytes_per_char_eng_latn = all_data_df[all_data_df['lang'] == 'eng_latn']['bytes_per_char'].values[0]
    byte_premium = char_ratio_pred * bytes_per_char / bytes_per_char_eng_latn  # Predicted byte premium.
    return byte_premium


"""
Returns the pairwise byte premium between two languages.
Note: not optimized for repeated use, e.g. loads the dataframe each time this
function is called.

In order of priority, compute premium using:
(1) Our existing dataset of byte premiums (both languages must be in our set).
(2) A parallel text; text1 and text2 must be paths to content-matched text.
Then, text_type should be set to 'parallel'.

(3) Regression for one or both languages. For any language (of the two) that is
not in our set, provide a path to monolingual text in the language (text1 or
text2). If the script is in our set of known scripts (e.g. 'latn'), then the
scripttype is optional (inferred from our dataset). Otherwise, scripttype
should be provided. If the script is in our set of common scripts, then language
family can also optionally be provided.
"""
def get_pairwise_premium(language1, language2,
        text1=None, text2=None, text_type='monolingual',
        script_type1=None, script_type2=None, family1=None, family2=None,
        verbose=True):
    # Validate language codes.
    language1 = language1.lower()
    language2 = language2.lower()
    for lang in [language1, language2]:
        if len(lang.strip().split('_')) != 2:
            print(f'Invalid language code: {lang}; '
                  'language code should be ISO 639-3 and ISO 15924 separated by an underscore, e.g. eng_latn.')
            return None
    # Read byte premium data.
    if verbose: print('Reading existing byte premium dataset.')
    global DATA_PATH
    all_data_df = pd.read_csv(DATA_PATH, sep='\t', header=0)
    all_data_df = all_data_df[all_data_df['byte_coef'].notnull()]
    # Compute from existing premiums. If not in our set, these are None.
    premium1 = retrieve_calculated_premium(language1, all_data_df)
    premium2 = retrieve_calculated_premium(language2, all_data_df)
    if premium1 and premium2:
        if verbose: print('Retrieved both premiums from existing dataset.')
        return premium1 / premium2
    # Compute from parallel text.
    if (text_type == 'parallel') and text1 and text2:
        if verbose: print(f'Calculating premium from parallel text (assuming {language1} to {language2}).')
        return calculate_pairwise_premium_from_parallel(text1, text2)
    # Compute from linear regressions.
    if not premium1:  # language1 was not in our set.
        if verbose: print(f'Predicting {language1} premium from regression.')
        premium1 = get_premium_from_regression(language1, all_data_df, text1, script_type1, family1, verbose=verbose)
    if not premium2:  # language2 was not in our set.
        if verbose: print(f'Predicting {language2} premium from regression.')
        premium2 = get_premium_from_regression(language2, all_data_df, text2, script_type2, family2, verbose=verbose)
    # By this point, both premium1 and premium2 should be computed.
    return premium1 / premium2


def main():
    args = parse_args()

    # Check for byte premium data file.
    global DATA_PATH
    if not os.path.isfile(DATA_PATH): DATA_PATH = os.path.join('byte-premium-tool', DATA_PATH)
    if not os.path.isfile(DATA_PATH):
        print('ERROR: cannot find byte premium data file; '
              'DATA_PATH should point to all_merged_20240223.tsv, which can be downloaded '
              'from our github repository: https://github.com/catherinearnett/byte-premium-tool')
        return

    byte_premium = get_pairwise_premium(args.language1, args.language2,
            text1=args.text1, text2=args.text2, text_type=args.text_type,
            script_type1=args.script_type1, script_type2=args.script_type2,
            family1=args.family1, family2=args.family2, verbose=True)
    print('Returned byte premium:')
    print(byte_premium)


if __name__ == "__main__":
    main()
