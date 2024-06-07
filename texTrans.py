#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 28 09:15:18 2018

@author: saschajecklin
"""
import re
import argparse
import time
import deepl
import os, sys

def parse_args(args=None):
    parser = argparse.ArgumentParser(description='Translates LaTeX files with DeepL')
    parser.add_argument("-f", dest="FROM", default="DE", required=True, help="Language of the source document(s) e.g. DE")
    parser.add_argument("-t", dest="TO", default="EN", required=True, help="Language of the target document e.g EN-GB")
    parser.add_argument("-i", dest="INPUT", required=True,  help="Path to the latex input file")
    parser.add_argument("-o", dest="OUTPUT", required=True, help="Path to the latex output file")
    parser.add_argument("-d", dest="DEEPL_AUTH_KEY", required=False, help="Deepl API key")

    return parser.parse_args(args)

def make_xlat(*args, **kwds):
    adict = dict(*args, **kwds)
    rx = re.compile('|'.join(map(re.escape, adict)))
    def one_xlat(match):
        return adict[match.group(0)]
    def xlat(text):
        return rx.sub(one_xlat, text)
    return xlat

def translate(text: str, deepl_auth: str, lang_in="DE", lang_out="EN-US"):
    translated = []
    commands = (r"^@#X\d{18,19}$", # if it starts with @#X followed by 18 to 19 digits its just a hash --> no translation needed
                r"^@#X-\d{18,19}$")
    only_hash_pattern = re.compile("|".join(commands))
    translator = deepl.Translator(deepl_auth)
    for line in text.splitlines():
        #print(line)
        if line in {'', '\n'} or only_hash_pattern.match(line):
            translated.append(line)
#        elif not line.strip():
#            translated.append('')
        else:
            translated.append(translator.translate_text(line, source_lang=lang_in, target_lang=lang_out).text)
    translated = '\n'.join(translated)
    return translated

if __name__ == "__main__":
    args = parse_args()
    DEEPL_AUTH_KEY = os.environ.get("DEEPL_AUTH_KEY")
    if DEEPL_AUTH_KEY == None :
        if args.DEEPL_AUTH_KEY == None:
            print('Specify a Deepl API key.')
            sys.exit(0)
        else:
           DEEPL_AUTH_KEY = args.DEEPL_AUTH_KEY

    print('Translating file {} to {} from {} and saving it to {}'.format(args.INPUT, args.TO, args.FROM, args.OUTPUT))
    fileInputName = args.INPUT
    fileOutName = args.OUTPUT

    with open(fileInputName) as fileIn, open(fileOutName, "w") as fileOut:

        fileStr = fileIn.read()

        print("Starting hashing...")

        #replace commands like \begin{*}, \end{*}, tabs etc. with hashes
        search_pattern = (
            r"\\begin\{\w+\}",
            r"\t",
            "    ",
            "\r",
            r"\\end\{\w+\}",
            r"\\usepackage\{\w+\}",
            r"\\newcommand\{\w+\}",
            r"\\include\{.*\}",
            r"\\input\{\w+\}",
            r"\\\w+\[.*\}",
            r"\%.*",
        )
        search_result_1 = re.findall("|".join(search_pattern), fileStr)
        # random number for every found command + a prefix which hopefully
        # doens't appear in text. Used to skip lines later, which don't need translation
        list1 = ['@#X{}'.format(hash(x)) for x in search_result_1]
        #make a dictionary out of hashes
        d1 = dict(zip(search_result_1, list1))
        hash_dictionary = make_xlat(d1)
        hashedText = hash_dictionary(fileStr)

        #replace all latex commands (starting with a backslash) with hashes
        search_result_2 = re.findall( r"\\\w+", hashedText)
        #random number  + prefix again
        list2 = ['@#X{}'.format(hash(x)) for x in search_result_2]
        #make a dictionary
        d2 = dict(zip(search_result_2, list2))
        hash_dictionary = make_xlat(d2)
        hashedText = hash_dictionary(hashedText)
        #print(hashedText)
        #fileOut.write(translate(hashedText))

        d1.update(d2) # combine dictionaries
        #with open('hash_dict.json', 'w') as f:
        #json.dump(d1, f)

        print("Hashing done. Starting translation...")

        translated = translate(text=hashedText, lang_in = args.FROM, lang_out = args.TO, deepl_auth=DEEPL_AUTH_KEY)

        d1Inv = {val:key for (key, val) in d1.items()} #swap dictionary
        translate2 = make_xlat(d1Inv)
        fileStrOut = translate2(translated)
        #print(fileStrOut)

        fileOut.write(fileStrOut)

        print("Success")