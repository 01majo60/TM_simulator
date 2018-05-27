from flask import Flask,render_template, flash, redirect, url_for, request, session
from app import app, db
from app.forms import MyForm, TmachineForm,MyForm1
from app.models import Tmachine
from ast import literal_eval
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module
from multiprocessing import Value
from turing_machine.dtm import DTM
from turing_machine.ntm import NTM
from turing_machine.xdtm import XDTM
from table import table,table_df
import time
from app import parser1
from turing_machine import exceptions
from sqlalchemy import exc


counter = Value('i', 0)


@app.route('/', methods=['GET', 'POST'])
def index():
    form = TmachineForm()
    form.opts.query = Tmachine.query.filter(Tmachine.id >= 1)
    if form.validate_on_submit():
        name = "tm"+str(form.opts.data.id)
        druh = form.opts.data.tm_d_n_x
        return redirect(url_for('vstup',name = name,druh = druh))
    return render_template('index.html', form=form)


@app.route('/vstup/<name>/<druh>', methods=['GET','POST'])
def vstup(name,druh):
    form = TmachineForm()
    with counter.get_lock():
        counter.value = 0
    form.opts.query = Tmachine.query.filter(Tmachine.id >= 1)
    if request.method == 'POST':
        if form.validate_on_submit() and form.submit.data:
            name = "tm"+str(form.opts.data.id)
            druh = form.opts.data.tm_d_n_x
        if request.form.get('Vstup') == 'Zapíš na pásku':
            vstup = request.form.get('vstup')
            name = session.get("newname")
            druh = session.get("newdruh")
            vs = True
            df, input_symbols , input_symbols_dict = table_df.table(name,druh)
            for i in vstup:
                if i not in input_symbols_dict:
                    vs = False
            if vs and vstup != "":
                session["newvstup"] = vstup
                return redirect(url_for('simulacia',vstup=vstup,druh = druh,name = name ))
            else:
                success_message = ("vstup: (")+vstup + (") nie je zo vstupnej abecedy: ") +input_symbols
                if vstup == "":
                    success_message = ("vstup je prázdny, zadajte vstupné slovo zo vstupnej abecedy: ") +input_symbols
                flash(success_message)
        
    df, input_symbols , input_symbols_dict = table_df.table(name,druh)
    session["newname"] = name
    session["newdruh"] = druh
    session["newinput_symbols"] = input_symbols
    return render_template('vstup.html', form = form, data1 = input_symbols, dataframe=df.to_html())     
    
@app.route('/simuluj')
def simuluj():
    form = MyForm1()
    name = session.get("newname")
    druh = session.get("newdruh")
    vstup = session.get("newvstup")
    input_symbols = session.get("newinput_symbols")
    cas = session.get("cas")
    with counter.get_lock():
        counter.value +=1
    if druh == "ntm":
        if counter.value == 0:
            df,list_of_table,stroj, list_of_tape, final = table.table(name,vstup,druh)
            session['new_final'] = final
        else:
            final = session.get('new_final')
            df,list_of_table,stroj, list_of_tape = table.ntm_table_final(name,vstup,final)     
    elif druh == "xtm":
        df,list_of_table,stroj, list_of_tape, length = table.table(name,vstup,druh)
    else:
        df,list_of_table,stroj, list_of_tape = table.table(name,vstup,druh)

    if counter.value < len(list_of_table)-1:
        dff = list_of_table[counter.value]
        dff = dff.set_table_attributes('border="1" class="dataframe table table-hover table-bordered"')
        dff = dff.set_precision(3)
        df_tape = list_of_tape[counter.value]

        if druh == "xtm":
            dfz = []
            for i in range (length):
                dfz.append(list_of_tape[counter.value*length+i])
            if length == 2:
                return render_template("simuluj.html",content = cas,form=form,data1 = input_symbols,dataframe = dfz[0].to_html(),dataframe1 = dfz[1].to_html() ,data = dff)
            elif length == 3:
                return render_template("simuluj.html",content = cas,form=form,data1 = input_symbols,dataframe = dfz[0].to_html(),dataframe1 = dfz[1].to_html(), dataframe2= dfz[2].to_html(),data = dff)
            elif length == 4:
                return render_template("simuluj.html",content = cas,form=form,data1 = input_symbols,dataframe = dfz[0].to_html(),dataframe1 = dfz[1].to_html(), dataframe2= dfz[2].to_html(), dataframe3= dfz[3].to_html(),data = dff)
            elif length == 5:
                z[5] = render_template("simuluj.html",content = cas,form=form,data1 = input_symbols,dataframe = dfz[0].to_html(),dataframe1 = dfz[1].to_html(), dataframe2= dfz[2].to_html(), dataframe3= dfz[3].to_html(),dataframe4 = dfz[4].to_html(),data = dff)
            elif length == 6:
                z[6] = render_template("simuluj.html",content = cas,form=form,data1 = input_symbols,dataframe = dfz[0].to_html(),dataframe1 = dfz[1].to_html(), dataframe2= dfz[2].to_html(), dataframe3= dfz[3].to_html(),dataframe4 = dfz[4].to_html(), dataframe5 = dfz[5].to_html(),data = dff)
            elif length == 7:
                z[7] = render_template("simuluj.html",content = cas,form=form,data1 = input_symbols,dataframe = dfz[0].to_html(),dataframe1 = dfz[1].to_html(), dataframe2= dfz[2].to_html(), dataframe3= dfz[3].to_html(),dataframe4 = dfz[4].to_html(), dataframe5 = dfz[5].to_html(), dataframe6 = dfz[6].to_html(),data = dff)
        else:
            return render_template("simuluj.html",content = cas,form=form,data1 = input_symbols,dataframe = df_tape.to_html(classes=["table-bordered", "table-striped", "table-hover"]), data = dff)
    else:
        return redirect(url_for('simulacia',vstup=vstup,druh = druh,name = name ))
   
@app.route('/simulacia/<name>/<druh>/<vstup>', methods=['GET','POST'])
def simulacia(vstup,druh, name):
    form = TmachineForm()
    form.opts.query = Tmachine.query.filter(Tmachine.id >= 1)
    name = session.get("newname")
    druh = session.get("newdruh")
    vstup = session.get("newvstup")
    input_symbols = session.get("newinput_symbols")
    
    if druh == "ntm":
        if counter.value == 0:
            df,list_of_table,stroj, list_of_tape, final = table.table(name,vstup,druh)
            session['new_final'] = final
        else:
            final = session.get('new_final')
            df,list_of_table,stroj, list_of_tape = table.ntm_table_final(name,vstup,final)
            
    elif druh == "xtm":
        df,list_of_table,stroj, list_of_tape, length = table.table(name,vstup,druh)
    else:
        df,list_of_table,stroj, list_of_tape = table.table(name,vstup,druh)

    if request.method == 'POST':
        if form.validate_on_submit() and form.submit.data:
            name = "tm"+str(form.opts.data.id)
            druh = form.opts.data.tm_d_n_x
            return redirect(url_for('vstup',name = name,druh = druh))            
        elif request.form.get('Krok vpred') == 'Krok vpred':
            if counter.value < len(list_of_table)-1:
                with counter.get_lock():
                    counter.value +=1
        elif request.form.get('Krok späť') == 'Krok späť':
            if counter.value > 0:
                with counter.get_lock():
                    counter.value -=1
        elif request.form.get('Vstup') == 'Zapíš na pásku':
            vstup = request.form.get('vstup')
            name = session.get("newname")
            druh = session.get("newdruh")
            vs = True
            df, input_symbols , input_symbols_dict = table_df.table(name,druh)
            for i in vstup:
                if i not in input_symbols_dict:
                    vs = False
            if vs and vstup != "":
                session["newvstup"] = vstup
                with counter.get_lock():
                    counter.value = 0
                return redirect(url_for('simulacia',vstup=vstup,druh = druh,name = name ))
            else:
                success_message = ("vstup: (")+vstup + (") nie je zo vstupnej abecedy: ") +input_symbols
                if vstup == "":
                    success_message = ("vstup je prázdny, zadajte vstupné slovo zo vstupnej abecedy: ") +input_symbols
                flash(success_message)
                return redirect(url_for('vstup',name = name,druh = druh))   
        elif request.form.get('Simulácia') == 'Simulácia':
            with counter.get_lock():
                counter.value -= 1
            try:
                cas = int(request.form.get('cas'))
                session["cas"] = cas
            except ValueError:
                cas = None
                success_message = ('Časové oneskorenie musí byť celé číslo')
                flash(success_message)
            if cas:
                return redirect(url_for('simuluj'))
            else:
                return redirect(url_for('simulacia',vstup=vstup,druh = druh,name = name ))

    if counter.value == len(list_of_table)-1:
        if stroj:
            success_message = ('Turingov stroj akceptuje vstup: '+vstup)
        else:
            success_message = ('Turingov stroj zamieta vstup: '+vstup )
        flash(success_message)

        
    dff = list_of_table[counter.value]
    dff = dff.set_table_attributes('border="1" class="dataframe table table-hover table-bordered"')
    dff = dff.set_precision(3)
    df_tape = list_of_tape[counter.value]
  

    if druh == "xtm":
        dfz = []
        for i in range (length):
            dfz.append(list_of_tape[counter.value*length+i])
        if length == 2:
            return render_template("simulacia.html",form=form,data1 = input_symbols,dataframe = dfz[0].to_html(),dataframe1 = dfz[1].to_html() ,data = dff)
        elif length == 3:
            return render_template("simulacia.html",form=form,data1 = input_symbols,dataframe = dfz[0].to_html(),dataframe1 = dfz[1].to_html(), dataframe2= dfz[2].to_html(),data = dff)
        elif length == 4:
            return render_template("simulacia.html",form=form,data1 = input_symbols,dataframe = dfz[0].to_html(),dataframe1 = dfz[1].to_html(), dataframe2= dfz[2].to_html(), dataframe3= dfz[3].to_html(),data = dff)
        elif length == 5:
            z[5] = render_template("simulacia.html",form=form,data1 = input_symbols,dataframe = dfz[0].to_html(),dataframe1 = dfz[1].to_html(), dataframe2= dfz[2].to_html(), dataframe3= dfz[3].to_html(),dataframe4 = dfz[4].to_html(),data = dff)
        elif length == 6:
            z[6] = render_template("simulacia.html",form=form,data1 = input_symbols,dataframe = dfz[0].to_html(),dataframe1 = dfz[1].to_html(), dataframe2= dfz[2].to_html(), dataframe3= dfz[3].to_html(),dataframe4 = dfz[4].to_html(), dataframe5 = dfz[5].to_html(),data = dff)
        elif length == 7:
             z[7] = render_template("simulacia.html",form=form,data1 = input_symbols,dataframe = dfz[0].to_html(),dataframe1 = dfz[1].to_html(), dataframe2= dfz[2].to_html(), dataframe3= dfz[3].to_html(),dataframe4 = dfz[4].to_html(), dataframe5 = dfz[5].to_html(), dataframe6 = dfz[6].to_html(),data = dff)
    else:
        return render_template("simulacia.html",form=form,data1 = input_symbols,dataframe = df_tape.to_html(classes=["table-bordered", "table-striped", "table-hover"]), data = dff)


@app.route('/dtm', methods=['GET', 'POST'])
def dtm():
    form = MyForm()
    if form.validate_on_submit():
        tm = False
        states = parser1.dict_parse(form.states.data)
        states_dict = literal_eval(states)
        input_s = parser1.dict_parse(form.input_symbols.data)
        input_symbols_dict = literal_eval(input_s)
        tape_s = parser1.dict_parse(form.tape_symbols.data)
        tape_symbols_dict = literal_eval(tape_s)
        
        initial_state_d = form.initial_state.data
        if form.left_end.data:    
            left_end_d = form.left_end.data
        else:
            left_end_d = '>'
        try:
            transitions_d = literal_eval(form.prechody.data)
        except:
            transitions_d = {}
            success_message = ("Neočakávaná chyba v prechodovej funkcii")
            flash(success_message)
            
        if form.blank_symbol.data:
            blank_symbol_d = form.blank_symbol.data
        else:
            blank_symbol_d = '#'
        reject_state_d = form.reject_state.data
        final_states_d = form.final_states.data
        try:
            dtm = DTM(
            states = states_dict,
            input_symbols= input_symbols_dict,
            tape_symbols= tape_symbols_dict,
            left_end = left_end_d,
            transitions = transitions_d,
            initial_state = initial_state_d,
            blank_symbol = blank_symbol_d,
            reject_state = reject_state_d,
            final_states = final_states_d
            )
            if dtm:
                tm = True
        except(exceptions.InvalidStateError,exceptions.InvalidSymbolError,exceptions.MissingStateError,exceptions.MissingSymbolError,
               exceptions.InitialStateError,exceptions.FinalStateError,exceptions.RejectStateError,exceptions.LeftEndError,
               exceptions.RejectionError,exceptions.InvalidDirectionError) as err:
            tm = False
            success_message = (err)
            flash(success_message)
        if tm:
            try:
                tmachine = Tmachine(definicia= form.funkcia.data,tm_d_n_x='dtm')
                db.session.add(tmachine)
                db.session.commit()
            except exc.IntegrityError:
                db.session().rollback()
                tm = False
                success_message = ("Definícia/Názov TM už existuje prosím zvolte iný názov")
                flash(success_message)        
        if tm:
            db.session.add(tmachine)
            db.session.commit()

            name = str(tmachine.id)
            with open("tm{}.py".format(name), "w") as text_file:
                text_file.write("from turing_machine.dtm import DTM \ndtm = DTM("
                    "\nstates = {0}"",\ninput_symbols = {1},"
                    "\ntape_symbols = {2},\nleft_end = '{3}',"
                    "\ntransitions = {4},"
                    "\ninitial_state = '{5}',\nblank_symbol = '{6}',"
                    "\nreject_state = '{7}', \nfinal_states = '{8}' \n)"
                    .format(states_dict,input_symbols_dict,tape_symbols_dict,left_end_d,transitions_d,initial_state_d,blank_symbol_d,reject_state_d,final_states_d))
            success_message = ('Nový DTM: '+form.funkcia.data+' je vytvorený')
            flash(success_message)
            return redirect(url_for('index'))  
    return render_template('dtm.html',  title='DTM', form=form)


@app.route('/ntm', methods=['GET', 'POST'])
def ntm():
    form = MyForm()
    if form.validate_on_submit():
        tm = False
        states = parser1.dict_parse(form.states.data)
        states_dict = literal_eval(states)
        input_s = parser1.dict_parse(form.input_symbols.data)
        input_symbols_dict = literal_eval(input_s)
        tape_s = parser1.dict_parse(form.tape_symbols.data)
        tape_symbols_dict = literal_eval(tape_s)
        
        initial_state_d = form.initial_state.data
        if form.left_end.data:    
            left_end_d = form.left_end.data
        else:
            left_end_d = '>'
        try:
            transitions_d = literal_eval(form.prechody.data)
        except:
            transitions_d = {}
            success_message = ("Neočakávaná chyba v prechodovej funkcii")
            flash(success_message)
            
        if form.blank_symbol.data:
            blank_symbol_d = form.blank_symbol.data
        else:
            blank_symbol_d = '#'
        reject_state_d = form.reject_state.data
        final_states_d = form.final_states.data
        try:
            ntm = NTM(
            states = states_dict,
            input_symbols= input_symbols_dict,
            tape_symbols= tape_symbols_dict,
            left_end = left_end_d,
            transitions = transitions_d,
            initial_state = initial_state_d,
            blank_symbol = blank_symbol_d,
            reject_state = reject_state_d,
            final_states = final_states_d
            )
            if ntm:
                tm = True
        except(exceptions.InvalidStateError,exceptions.InvalidSymbolError,exceptions.MissingStateError,exceptions.MissingSymbolError,
               exceptions.InitialStateError,exceptions.FinalStateError,exceptions.RejectStateError,exceptions.LeftEndError,
               exceptions.RejectionError,exceptions.InvalidDirectionError) as err:
            tm = False
            success_message = (err)
            flash(success_message)
        if tm:
            try:
                tmachine = Tmachine(definicia= form.funkcia.data,tm_d_n_x='ntm')
                db.session.add(tmachine)
                db.session.commit()
            except exc.IntegrityError:
                db.session().rollback()
                tm = False
                success_message = ("Definícia/Názov TM už existuje prosím zvolte iný názov")
                flash(success_message)   
        if tm:
            db.session.add(tmachine)
            db.session.commit()
            
            name = str(tmachine.id)
            with open("tm{}.py".format(name), "w") as text_file:
                text_file.write("from turing_machine.ntm import NTM \nntm = NTM("
                    "\nstates = {0}"",\ninput_symbols = {1},"
                    "\ntape_symbols = {2},\nleft_end = '{3}',"
                    "\ntransitions = {4},"
                    "\ninitial_state = '{5}',\nblank_symbol = '{6}',"
                    "\nreject_state = '{7}', \nfinal_states = '{8}' \n)"
                    .format(states_dict,input_symbols_dict,tape_symbols_dict,left_end_d,transitions_d,initial_state_d,blank_symbol_d,reject_state_d,final_states_d))
            success_message = ('Nový NTM: '+form.funkcia.data+' je vytvorený')
            flash(success_message)
            return redirect(url_for('index'))
    return render_template('ntm.html',  title='NTM', form=form)

@app.route('/xtm', methods=['GET', 'POST'])
def xtm():
    form = MyForm()
    if form.validate_on_submit():
        tm = False
        states = parser1.dict_parse(form.states.data)
        states_dict = literal_eval(states)
        input_s = parser1.dict_parse(form.input_symbols.data)
        input_symbols_dict = literal_eval(input_s)
        tape_s = parser1.dict_parse(form.tape_symbols.data)
        tape_symbols_dict = literal_eval(tape_s)

        initial_state_d = form.initial_state.data
        if form.left_end.data:    
            left_end_d = form.left_end.data
        else:
            left_end_d = '>'
        try:
            transitions_d = literal_eval(form.prechody.data)
        except:
            transitions_d = {}
            success_message = ("Neočakávaná chyba v prechodovej funkcii")
            flash(success_message)

        if form.blank_symbol.data:
            blank_symbol_d = form.blank_symbol.data
        else:
            blank_symbol_d = '#'
        reject_state_d = form.reject_state.data
        final_states_d = form.final_states.data
        try:
            xdtm = XDTM(
            states = states_dict,
            input_symbols= input_symbols_dict,
            tape_symbols= tape_symbols_dict,
            left_end = left_end_d,
            transitions = transitions_d,
            initial_state = initial_state_d,
            blank_symbol = blank_symbol_d,
            reject_state = reject_state_d,
            final_states = final_states_d
            )
            if xdtm:
                tm = True
        except(exceptions.InvalidStateError,exceptions.InvalidSymbolError,exceptions.MissingStateError,exceptions.MissingSymbolError,
               exceptions.InitialStateError,exceptions.FinalStateError,exceptions.RejectStateError,exceptions.LeftEndError,
               exceptions.RejectionError,exceptions.InvalidDirectionError,exceptions.Badcounttapes) as err:
            tm = False
            success_message = (err)
            flash(success_message)
        if tm:
            try:
                tmachine = Tmachine(definicia = form.funkcia.data,tm_d_n_x='xtm')
                db.session.add(tmachine)
                db.session.commit()
            except exc.IntegrityError:
                db.session().rollback()
                tm = False
                success_message = ("Definícia/Názov TM už existuje prosím zvolte iný názov")
                flash(success_message)
        if tm:
            name = str(tmachine.id)
            with open("tm{}.py".format(name), "w") as text_file:
                text_file.write("from turing_machine.xdtm import XDTM \nxdtm = XDTM("
                    "\nstates = {0}"",\ninput_symbols = {1},"
                    "\ntape_symbols = {2},\nleft_end = '{3}',"
                    "\ntransitions = {4},"
                    "\ninitial_state = '{5}',\nblank_symbol = '{6}',"
                    "\nreject_state = '{7}', \nfinal_states = '{8}' \n)"
                    .format(states_dict,input_symbols_dict,tape_symbols_dict,left_end_d,transitions_d,initial_state_d,blank_symbol_d,reject_state_d,final_states_d))
            success_message = ('Nový viac páskový DTM: '+form.funkcia.data+' je vytvorený')
            flash(success_message)
            return redirect(url_for('index'))
    return render_template('xtm.html',  title='XTM', form=form)

    
    

    
   


