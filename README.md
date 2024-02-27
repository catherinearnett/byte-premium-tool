# Byte Premium Tool
A tool to calculate scaling needed to achieve cross-lingual training data equity. 

This tool allows you to determine the amount of data (in bytes) for a given language that is equivalent to  another amount of data

link to paper

To use the tool, 

*  download this repository (what's the technical term)
*  Choose an option/method


## Sources

There are multiple options for the source of the byte ratios: `option 1`, `option 2`, `option 3`. 

## Option 1: NLLB method

This is the recommended method if the languages you are comparing are both on the list. See `Appendix` for list of languages. 

This method will calculate the ratio between two languages based on the NLLB dataset (refer to paper). 

```
python byte_ratio_calculator/byte_ratio_calculator.py byte_ratio_calculator/nllb_coef.tsv -m 'option_1' -l1 'eng' -l2 'arb'
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
