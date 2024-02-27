# Byte Premium Tool
A tool to calculate scaling needed to achieve cross-lingual training data equity. 

This tool allows you to determine the amount of data (in bytes) for a given language that is equivalent to another amount of data. For more information see the [paper].

To use the tool, 

*  download this repository (what's the technical term)
*  Choose an option/method


## Uses

## Use Case 1: Look up pre-calculated byte premiums

This is the recommended method if the languages you are comparing are both on in our dataset of 1155 languages. This method will calculate the ratio between two languages based on the NLLB, FLORES, or Bible datasets in descending order of priority (refer to paper for details). To use this methods, you only need to provide two language codes. The output will be the ratio of bytes required by the first language with respect to the bytes required for the second language. 

Language codes should be provided in the format ISO639-3 and ISO 15924, separated by an underscore, e.g. eng_latn.

```
python byte_premium_tool.py -l1 'mya_mymr' -l2 'eng_latn'
```

### Required Arguments
*  option/method
*  nllb coefficients
*  output directory
*  l1, l2

## Option 2? Bibles (less reliable?)****


## Option 3: Upload your own parallel texts

If one of your languages is not in the sample, you will need to use this method. This method will calculate the ratio from scratch.
You will need a parallel corpus for the two languages you want to compare. This works better the larger your parallel text corpus is. 

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
