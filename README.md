# texTrans
Translates LaTex Files with DeepL

This project is currently in its alpha state. It works but is still a mess. Sadly DeepL has a problem accepting longer texts with many hashes (used e.g. for newline and tabs). Therefor the translation is carried out line by line, which obviously takes some time.

Prerequisites
------------

    pip install deepl
    pip install tqdm
    
Usage
------------

    python textTrans.py -f <FROM> -t <TO> -i <input File>
    
    Example:
    python texTrans.py -f DE -t EN-GB - myfile.tex
Output will be created as input_trans.tex


Disclaimer
----------
Using this script could violate the ToS of DeepL. Therefore the purpose of this script is purely educational. Furthermore, the translation API can easily be switched to another API.
    
    
