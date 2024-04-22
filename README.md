# Byte Premium Tool

This is a tool to calculate dataset scaling needed to achieve cross-lingual training data equity when dataset size is measured in UTF-8 bytes. For more information see the [paper].

The output of the tool is a single ratio, which represents the number of bytes it takes to encode a parallel text in Language 1 relative to the number of bytes needed to encode the same content in Language 2. 

## Version and Requirements

This tool requires `numpy`, `pandas`, `scipy` and `statsmodels` to be installed. 

Tested in Python 3.9.

### Installation

To use the tool, clone this repository

```
git clone https://github.com/catherinearnett/byte-premium-tool.git
```

## Uses

There are multiple ways to use this tool, depending on whether the languages are in our dataset and whether you have parallel text for the languages. The arguments required to use the tool depend on the use case. 

## Use Case 1: Look up Pre-Calculated Byte Premiums

This is the recommended method if the languages you are comparing are both on in our dataset of 1155 languages. This method will retrieve the byte premium between two languages based on the NLLB, FLORES, or Bible datasets in descending order of priority (refer to paper for details). To use this method, you only need to provide two language codes. The output will be the ratio of bytes required by the first language with respect to the bytes required for the second language. 

Language codes should be provided in the format ISO639-3 and ISO 15924, separated by an underscore, e.g. eng_latn.

```
python3 byte_premium_tool.py --language1=mya_mymr --language2=deu_latn
```

To use in Python code (run from the byte-premium-tool repository directory):

```
from byte_premium_tool import get_pairwise_premium
print(get_pairwise_premium('mya_mymr', 'deu_latn', verbose=False))
```

## Use Case 2: Calculate Byte Premium from Parallel Text

If the languages you want the byte premiums for are not in our dataset, you can calculate the byte premium from a parallel dataset. We recommend a minimum of 100 lines of parallel text for each lanauge, but more data will yield more reliable results. Text should use UTF-8 encoding. 

```
python3 byte_premium_tool.py \
--language1=xx1_xxxx --language2=eng_latn \
--text1=xx1_xxxx.txt --text2=eng_latn.txt --text_type=parallel
```

## Option 3: Predict Byte Premium with Monolingual Text

If the language is not in the dataset and you do not have parallel text, you can predict the byte premium based on a few factors. 

We fit linear regressions to predict the length ratio from langauge family, writing system type, script name, and entropy over characters. We estimate the byte premium by dividing the predicted length ratio by the byte-character ratio.

Entropy over characters and byte-character ratio are calculated by the tool from any texts in the language. **The uploaded texts do not have to be parallel. **

If the script is not in the dataset of 1155 languages, the only feature of the languages that must be provided is script type (alphabet, abugida, abjad, logography). Descriptions of these types can be found in Appendix C of the paper. We recommend finding the script type on the Wikipedia page for the script. You should also provide language family, which can be looked up on [Glottolog](https://glottolog.org/glottolog/language), if possible. 

```
python3 byte_premium_tool.py \
--language1=xx1_xxxx --language2=eng_latn \
--text1=xx1_xxxx.txt --script_type1=alphabet\
```

## How to Cite

```
@article{arnett2024bit,
  title={A Bit of a Problem: Measurement Disparities in Dataset Sizes Across Languages},
  author={Arnett, Catherine and Chang, Tyler A and Bergen, Benjamin K},
  journal={arXiv preprint arXiv:2403.00686},
  url={https://arxiv.org/pdf/2403.00686.pdf},
  year={2024}
}
```
