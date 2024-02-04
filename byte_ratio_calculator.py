import pandas as pd
import numpy as np


* parse arguments
* create error messages about arguments
* load nllb
* check if languages are in nllb
    * for method 1, if they're not both in there, throw an error
    * for method 3, if one is there and one is not, that's good; if both are there, print a warning and then use method 1; what to do if neither language is in datasets?

nllb_coef = pd.read_csv("C:/Users/cathe/tokenizer_typology/parallel_corpus/lang_list_udhr.csv")
