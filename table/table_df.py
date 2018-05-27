from turing_machine.dtm import DTM
from turing_machine.ntm import NTM
from turing_machine.xdtm import XDTM
import pandas as pd
from importlib import import_module
from ast import literal_eval


def table(name,druh):
    input_s = "{"
    if druh == "dtm":
        df, input_symbols = dtm_table(name)
    elif druh == "ntm":
        df, input_symbols = ntm_table(name)
    elif druh == "xtm":
        df, input_symbols = xtm_table(name)
    for i in input_symbols:
        input_s += i + ", "
    input_s = input_s[:-2]
    input_s +="}"
    return df, input_s, input_symbols

    
def dtm_table(name):
    file = import_module(name)
    dc = file.dtm.transitions
    df = pd.DataFrame.from_dict(data=dc,orient='index')
    df.fillna("( -, -, - )",inplace=True)
    rows, columns = df.shape
    reject_state = "( "+file.dtm.reject_state+", -, - )"
    final_state = "( "+file.dtm.final_states+", -, - )"
    z1=[]
    z2=[]
    for i in file.dtm.tape_symbols:
         z2.append(reject_state)
         z1.append(final_state)
    df1 = pd.DataFrame([z1], index = [file.dtm.final_states], columns=list(df.columns.values))
    df2 = pd.DataFrame([z2], index = [file.dtm.reject_state], columns=list(df.columns.values))
    df = df.append(df1)
    df = df.append(df2)
    input_symbols = file.dtm.input_symbols
    return df, input_symbols     

def change_ntm(x):
    word1 = ""
    if x == "( -, -, - )":
        return x
    else:
        counter = 1
        for i in x:
            word = ', '.join(i)
            if counter == len(x):
                word1 += '(' +word+')'
            else:
                word1 += '(' +word+'), '
            counter +=1
        return word1

def ntm_table(name):
    file = import_module(name)
    dc = file.ntm.transitions
    df = pd.DataFrame.from_dict(data=dc,orient='index')   
    df.fillna("( -, -, - )",inplace=True)
    df = df.applymap(lambda x: change_ntm(x))
    rows, columns = df.shape
    reject_state = "( "+file.ntm.reject_state+", -, - )"
    final_state = "( "+file.ntm.final_states+", -, - )"
    z1=[]
    z2=[]
    for i in file.ntm.tape_symbols:
         z2.append(reject_state)
         z1.append(final_state)
    df1 = pd.DataFrame([z1], index = [file.ntm.final_states], columns=list(df.columns.values))
    df2 = pd.DataFrame([z2], index = [file.ntm.reject_state], columns=list(df.columns.values))
    df = df.append(df1)
    df = df.append(df2)

    input_symbols = file.ntm.input_symbols
    return df, input_symbols  

def xtm_table(name):
    file = import_module(name)
    dc = file.xdtm.transitions
    first = dc.keys()
    second = []
    for i in first:
        for j in dc[i].keys():
            second.append(j)
    list(set(second))
    
    df = pd.DataFrame(data=dc,index=second)
    df = df.T
    
    df.fillna("( -, -, - )",inplace=True)
    rows, columns = df.shape
    reject_state = "( "+file.xdtm.reject_state+", -, - )"
    final_state = "( "+file.xdtm.final_states+", -, - )"
    z1=[]
    z2=[]
    for i in range(columns):
         z2.append(reject_state)
         z1.append(final_state)
    df1 = pd.DataFrame([z1], index = [file.xdtm.final_states], columns=list(df.columns.values))
    df2 = pd.DataFrame([z2], index = [file.xdtm.reject_state], columns=list(df.columns.values))
    df = df.append(df1)
    df = df.append(df2)

    input_symbols = file.xdtm.input_symbols
    return df, input_symbols

    




