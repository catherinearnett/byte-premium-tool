# Byte Premium Tool
A tool to calculate scaling needed to achieve cross-lingual training data equity. 

This tool allows you to determine the amount of data (in bytes) for a given language that is equivalent to another amount of data. For more information see the [paper].

To use the tool, 

*  download this repository (what's the technical term)
*  Choose an option/method


## Uses

There are multiple ways to use this tool, depending on whether the languages are in our dataset and whether you have parallel text for the languages. 

## Use Case 1: Look up Pre-Calculated Byte Premiums

This is the recommended method if the languages you are comparing are both on in our dataset of 1155 languages. This method will calculate the ratio between two languages based on the NLLB, FLORES, or Bible datasets in descending order of priority (refer to paper for details). To use this methods, you only need to provide two language codes. The output will be the ratio of bytes required by the first language with respect to the bytes required for the second language. 

Language codes should be provided in the format ISO639-3 and ISO 15924, separated by an underscore, e.g. eng_latn.

```
python byte_premium_tool.py -l1 mya_mymr -l2 eng_latn
```


## Use Case 2: Calculate Byte Premium from Parallel Text

If the languages you want the byte premiums for are not in our dataset, you can calculate the byte premium from a parallel dataset. 

*  recommendation about minimum length
*  formatting requirements for text
*  Language codes should be provided in the format ISO639-3 and ISO 15924, separated by an underscore, e.g. eng_latn.

```
python byte_premium_tool.py -l1 mya_mymr -t1 mya.txt -l2 eng_latn -t2 eng.txt
```


## Option 3: Predict Byte Premium

If the language is not in the dataset and you do not have parallel text, you can predict the byte premium based on a few factors. 

We fit linear regressions to predict the length ratio from:
*  language family
*  writing system type
*  script name
*  entropy over characters

We estimate the byte premium by dividing the predicted length ratio by the byte-character ratio.

Entropy over characters and byte-character ratio are calculated with the tool. 

```
python byte_ratio_calculator.py -m 'option_3' -l1 'eng' -l1t 'eng.txt' -l2 'arb' -l2t 'arb.txt'
```

### Required Arguments
*  option/method
*  output directory
*  l1, l2
*  paralell corpus

## Output Format(s)

## Version and Requirements

## How to Cite

## References

## Appendix

### NLLB languages list
