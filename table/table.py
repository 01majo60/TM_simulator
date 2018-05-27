from turing_machine.dtm import DTM
from turing_machine.ntm import NTM
from turing_machine.xdtm import XDTM
import pandas as pd
from importlib import import_module
from ast import literal_eval

def table(name,vstup,druh):
    if druh == "dtm":
        df, list_of_table, stroj, list_of_tape = dtm_table(name,vstup)
        return df,list_of_table,stroj, list_of_tape 
    elif druh == "ntm":
        df, list_of_table, stroj, list_of_tape, final = ntm_table(name,vstup)
        return df,list_of_table,stroj, list_of_tape , final
    elif druh == "xtm":
        df, list_of_table, stroj, list_of_tape, length = xtm_table(name,vstup)
        return df,list_of_table,stroj, list_of_tape , length
    
def change_dtm(x):
    if x != "( -, -, - )":
        word = ', '.join(x)
        word1 = '('+word+')'
        return word1
    else:
        return x
    
def dtm_table(name,vstup):
    file = import_module(name)
    dc = file.dtm.transitions
    df = pd.DataFrame.from_dict(data=dc,orient='index')
    
    df.fillna("( -, -, - )",inplace=True)
    df = df.applymap(lambda x: change_dtm(x))
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
    generator = file.dtm.validate_input1(vstup, step=True)
    
    list_of_table = []
    list_of_tape = []

    tape_index = []
    tape_table = []
    tape_index.append(file.dtm.left_end)
    tape_table.append("")
    for i in vstup:
        tape_index.append(i)    
        tape_table.append("")
    tape_index.append(file.dtm.blank_symbol)    
    tape_table.append("")
    tape_table[0] = "^"
    dl = pd.DataFrame(data=tape_table,index=tape_index)
    dl.columns=[""]
    dl = dl.T
    list_of_tape.append(dl)
    
    stroj = False
    counter = 0
    for current_state,tape_symbol,tape,direction in generator:
        if file.dtm.final_states == current_state:
            stroj = True
        list_of_table.append(df.style.applymap(color_red,subset=pd.IndexSlice[current_state,[tape_symbol]]))
        tape_index = []
        tape_table = []
        if direction == 'R':  
            counter +=1
        if direction == 'L':
            counter -=1
        for i in tape:
            tape_index.append(i)
            tape_table.append("")
        tape_index.append(file.dtm.blank_symbol)
        tape_table.append("")
        if len(tape)-1 < counter:
            tape_index.append(file.dtm.blank_symbol)
            tape_table.append("")
        tape_table[counter] = "^"
        dl = pd.DataFrame(data=tape_table,index=tape_index)
        dl.columns=[""]
        dl = dl.T
        list_of_tape.append(dl)

       
    return df,list_of_table,stroj, list_of_tape

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

def ntm_table(name,vstup):
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

    generator = file.ntm.validate_input(vstup, step=True)
    
    list_of_table = []
    list_of_tape = []

    tape_index = []
    tape_table = []
    tape_index.append(file.ntm.left_end)
    tape_table.append("")
    for i in vstup:
        tape_index.append(i)    
        tape_table.append("")
    tape_table[0] = "^"
    dl = pd.DataFrame(data=tape_table,index=tape_index)
    dl.columns=[""]
    dl = dl.T
    list_of_tape.append(dl)
    
    stroj = False
    counter = 1
    for s,t,c,tape_symbol, current_state,tape,final in generator:

        if file.ntm.final_states == current_state:
            stroj = True
        list_of_table.append(df.style.applymap(color_red,subset=pd.IndexSlice[current_state,[tape_symbol]]))
        
        tape_index = []
        tape_table = []
       
        for i in tape:
            tape_index.append(i)
            tape_table.append("")
        tape_index.append(file.ntm.blank_symbol)
        tape_table.append("")
        if len(tape)-1 < counter:
            tape_index.append(file.ntm.blank_symbol)
            tape_table.append("")
        tape_table[counter] = "^"
        dl = pd.DataFrame(data=tape_table,index=tape_index)
        dl.columns=[""]
        dl = dl.T
        list_of_tape.append(dl)
        if c == 'R':  
            counter +=1
        if c == 'L':  
            counter -=1
        final = final
    return df,list_of_table,stroj, list_of_tape, final

def xtm_table(name,vstup):
    file = import_module(name)
    dc = file.xdtm.transitions
    first = dc.keys()
    second = []
    for i in first:
        for j in dc[i].keys():
            second.append(j)
    list(set(second))
    
    df = pd.DataFrame(data=dc,index=second)
    df.fillna("( -, -, - )",inplace=True)
    df = df.T
    

    rows, columns = df.shape
    df = df.applymap(lambda x: change_dtm(x))
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
    
    generator = file.xdtm.validate_input1(vstup, step=True)
    
    list_of_table = []
    list_of_tape = []
    
    
    stroj = False
    counter = []
    for current_state,tape_symbol, tapes ,directions in generator:
        if file.xdtm.final_states == current_state:
            stroj = True
        list_of_table.append(df.style.applymap(color_red,subset=pd.IndexSlice[current_state,[tape_symbol]]))
        length = len(tapes)
        if counter:
            pass
        else:
            for i in range(length):
                counter.append(0)
        count = 0
        counter_direction = length+1
        for tape in tapes:
            tape_index = []
            tape_table = []
            if directions[counter_direction] == 'R':
                c = counter[count]+1
                counter[count] = c
            if directions[counter_direction] == 'L':
                c = counter[count]-1
                counter[count] = c
            for i in tape:
                tape_index.append(i)
                tape_table.append("")
            tape_index.append(file.xdtm.blank_symbol)
            tape_table.append("")
            possition = counter[count]
            if len(tape)-1 < possition:
                tape_index.append(file.xdtm.blank_symbol)
                tape_table.append("")
            tape_table[possition] = "^"
            dl = pd.DataFrame(data=tape_table,index=tape_index)
            dl.columns=[""]
            dl = dl.T
            list_of_tape.append(dl)
            counter_direction +=1
            count +=1

            
    for i in range(length-1):
        tape_index = []
        tape_table = []
        tape_index.append(file.xdtm.left_end)
        tape_table.append("")
        tape_index.append(file.xdtm.blank_symbol)    
        tape_table.append("")
        tape_table[0] = "^"
        dl = pd.DataFrame(data=tape_table,index=tape_index)
        dl.columns=[""]
        dl = dl.T
        list_of_tape.insert(i,dl)
    
    tape_index = []
    tape_table = []
    tape_index.append(file.xdtm.left_end)
    tape_table.append("")
    for i in vstup:
        tape_index.append(i)    
        tape_table.append("")
    tape_index.append(file.xdtm.blank_symbol)    
    tape_table.append("")
    tape_table[0] = "^"
    dl = pd.DataFrame(data=tape_table,index=tape_index)
    dl.columns=[""]
    dl = dl.T
    list_of_tape.insert(0,dl)

    return df,list_of_table, stroj, list_of_tape, length

def color_red(val):
    color = 'red'
    return 'color: %s' %color

def ntm_table_final(name,vstup,final):
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

    generator = file.ntm.validate_input_ntm_final(vstup, final, step=True)

    
    list_of_table = []
    list_of_tape = []

    tape_index = []
    tape_table = []
    tape_index.append(file.ntm.left_end)
    tape_table.append("")
    for i in vstup:
        tape_index.append(i)    
        tape_table.append("")
    tape_table[0] = "^"
    dl = pd.DataFrame(data=tape_table,index=tape_index)
    dl.columns=[""]
    dl = dl.T
    list_of_tape.append(dl)
    
    stroj = False
    counter = 0
    for s,t,c,tape_symbol, current_state,tape in generator:
        if file.ntm.final_states == current_state:
            stroj = True
        list_of_table.append(df.style.applymap(color_red,subset=pd.IndexSlice[current_state,[tape_symbol]]))
        
        tape_index = []
        tape_table = []
        if c == 'R':  
            counter +=1
        if c == 'L':  
            counter -=1
        for i in tape:
            tape_index.append(i)
            tape_table.append("")
        tape_index.append(file.ntm.blank_symbol)
        tape_table.append("")
        if len(tape)-1 < counter:
            tape_index.append(file.ntm.blank_symbol)
            tape_table.append("")
        tape_table[counter] = "^"
        dl = pd.DataFrame(data=tape_table,index=tape_index)
        dl.columns=[""]
        dl = dl.T
        list_of_tape.append(dl)

    return df,list_of_table,stroj, list_of_tape



