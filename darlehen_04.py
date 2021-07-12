import math
import pandas as pd
import numpy as np
import streamlit as st
import base64

st.set_page_config(
    page_title="Tilgungsplaner",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

@st.cache
def darlehen(S, Date, idach, tilg, pt = True, Su = 0):
    # S: Kreditsumme
    # idach: Normalzins in % nach Def. der Bank
    # tdach: Anfangstilgung in % nach Def. der Bank
    # pt: Rückzahlungsart (True für prozentuale Anfangstilgung)
    #                      False für Monatsrate
    # tilg: Rückzahlung (entweder Prozentsatz oder Monatsrate)
    # Su: Ursprüngliche Darlehenssumme (bei Tilgungsanpassung)
    
    idach /= 100
    if pt == True:
        tdach = tilg/100
        if Su == 0:
            Rdach = (idach+tdach)*S
        else:
            Rdach = (idach+tdach)*Su
        r = Rdach/12 # Monatliche Rate
    else:
        r = tilg
        Rdach = r*12
        if Su == 0:
            tdach = Rdach/S-idach
        else:
            tdach = Rdach/Su-idach
    
    im = idach/12 # Monatlicher Zins
    i = (1+im)**12-1 # Tatsächlicher Zins
    R = i/im*r # Tatsächliche jährliche Rate
    t = R/S-i # Tatsächliche Anfangstilgung
    n = math.log(1+i/t)/math.log(1+i) # Laufzeit (Jahre)
    
    rs = [S]
    z = []
    t = []
    ms = []
    for k in range(int(n*12)+1):
        z.append(rs[k]*idach/12)
        if rs[k] > r:
            t.append(r-z[k])
        else:
            t.append(rs[k])
        rs.append(rs[k]-t[k])
        ms.append(r*(k+1))
    
    r = [r for i in range(len(z))]
    r[-1] = z[-1] + t[-1]
    rs = rs[1:]
    temp = {'Monatliche Rate': r, 'Zinsanteil': z, 'Tilgung': t, 'Restschuld': rs}
    kredit = pd.DataFrame(temp)
    kredit.index.name = 'Monat'
    meta = {'Darlehensbetrag': S,
            'Normalzins': idach,
            'Anfängliche Monatsrate': Rdach/12,
            'Anfängliche Tilgung': tdach,
            'Laufzeit': n,
           }
    kredit.index = pd.date_range(start = Date-pd.DateOffset(0), end = Date+pd.DateOffset(months = len(kredit)-1), freq = 'MS')


    return kredit, meta

##########################################################################


"""
# Tilgungsrechner
(c) *Dr. Gressel | ver 12.07.2021 | Kein Gewähr auf die Richtigkeit der Berechnungen*

Eine Baufinanzierung wird oft unübersichtlich, besonders wenn die Zinsbindung ausläuft oder
die Tilgung geändert wird. Mit diesem Tilgungsrechner lassen sich auch komplizierte
Annuitätendarlehen akkurat berechnen und auswerten - damit beim Bau keine finanziellen
Überraschungen entstehen.
"""

st.sidebar.markdown('**Eingabe**')

Darlehensbetrag = st.sidebar.number_input('Darlehensbetrag', value = 200000,
min_value = 10000, max_value = 1000000, step = 1000,
help = 'Wie viel Geld leihen Sie sich von der Bank?')

selected_date = st.sidebar.date_input('Auszahldatum',
help = 'Wann soll das Darlehen beginnen bzw. wann wird das Geld ausbezahlt?')
selected_date = pd.to_datetime(selected_date).replace(day = 1)
Start = selected_date

Normalzins = st.sidebar.number_input('Nominalzins', min_value = .01, max_value = 5., value = 1.7,
step = .1, help = 'Nominalzins in % nach Definition der Bank')

ttt = st.sidebar.radio('Rückzahlung', ('Anfängliche Tilgung', 'Gewünschte Monatsrate'))
if ttt == 'Anfängliche Tilgung':
    ProzTilg = True
    Tilgung = st.sidebar.number_input('Anfängliche Tilgung', value = 2., step = .1,
    min_value = .1, max_value = 10.,
    help = 'Bitte geben Sie hier die gewünschte anfängliche Tilgung in % ein')
else:
    ProzTilg = False
    Tilgung = st.sidebar.number_input('Gewünschte Monatsrate', value = 1000., step = 10.,
    min_value = 50., max_value = 10000.,
    help = 'Bitte geben Sie hier die gewünschte Monatsrate in EUR ein')


Zinsbindung = st.sidebar.slider('Zinsbindung', value = 10, min_value = 5, max_value = 35, step = 1,
help = 'Bitte geben Sie die Dauer der Sollzinsbindung in Jahren ein')

NeuerZins = st.sidebar.number_input('Neuer Nominalzins', min_value = .01, max_value = 10., value = 3.0,
step = .1, help = 'Nominalzins in % nach Definition der Bank nach Ablauf der Sollzinsbindung')

with st.sidebar.beta_expander('Tilgungsanpassung 1'):
    Tilgungsanpassung_1 = st.checkbox('Tilgungsanpassung 1', value = False)
    selected_date = st.date_input('Datum', help = 'Wann soll die Tilgung angepasst werden?',
    value = Start + pd.DateOffset(years = 1))
    selected_date = pd.to_datetime(selected_date).replace(day = 1)
    Tilgungsanpassung_1_date = selected_date
    ttt1 = st.radio('Rückzahlung ', ('Tilgung ', 'Gewünschte Monatsrate '))
    if ttt1 == 'Tilgung ':
        ProzTilg1 = True
        Tilgung1 = st.number_input('Neue Tilgung', value = 2., step = .1,
        min_value = .1, max_value = 10.,
        help = 'Bitte geben Sie hier die gewünschte Tilgung in % ein')
    else:
        ProzTilg1 = False
        Tilgung1 = st.number_input('Neue Monatsrate ', value = 1000., step = 10.,
        min_value = 50., max_value = 10000.,
        help = 'Bitte geben Sie hier die gewünschte neue Monatsrate in EUR ein')


with st.sidebar.beta_expander('Tilgungsanpassung 2'):
    Tilgungsanpassung_2 = st.checkbox('Tilgungsanpassung 2', value = False)
    selected_date = st.date_input('Datum', help = 'Wann soll die Tilgung angepasst werden?',
    value = Tilgungsanpassung_1_date + pd.DateOffset(years = 1))
    selected_date = pd.to_datetime(selected_date).replace(day = 1)
    Tilgungsanpassung_2_date = selected_date
    ttt2 = st.radio('Rückzahlung  ', ('Tilgung  ', 'Gewünschte Monatsrate  '))
    if ttt2 == 'Tilgung  ':
        ProzTilg2 = True
        Tilgung2 = st.number_input('Neue Tilgung ', value = 2., step = .1,
        min_value = .1, max_value = 10.,
        help = 'Bitte geben Sie hier die gewünschte Tilgung in % ein')
    else:
        ProzTilg2 = False
        Tilgung2 = st.number_input('Neue Monatsrate  ', value = 1000, step = 10,
        min_value = 100, max_value = 10000,
        help = 'Bitte geben Sie hier die gewünschte neue Monatsrate in EUR ein')
    

##########################################################################

Zinsbindung_date = Start + pd.DateOffset(years = Zinsbindung)
TP1, meta1 = darlehen(Darlehensbetrag, Start, Normalzins, Tilgung, ProzTilg)

if Tilgungsanpassung_1 == False and Tilgungsanpassung_2 == False:
    if Zinsbindung_date <= TP1.index[-1]:
        Normalzins = NeuerZins
        TP1_zins, meta_1_zins = darlehen(TP1['Restschuld'].at[Zinsbindung_date - pd.DateOffset(months = 1)], Zinsbindung_date, Normalzins, Tilgung, ProzTilg, Darlehensbetrag)
        T_z = TP1['Tilgung'].at[Zinsbindung_date] + TP1_zins['Zinsanteil'].at[Zinsbindung_date]
        TP1_zins, meta_1_zins = darlehen(TP1['Restschuld'].at[Zinsbindung_date - pd.DateOffset(months = 1)], Zinsbindung_date, Normalzins, T_z, False, Darlehensbetrag)
        TP1 = TP1.drop(index = pd.date_range(start = Zinsbindung_date, end = TP1.index[-1], freq = 'MS'))
        TP1 = pd.concat([TP1, TP1_zins], axis = 0)

    TP = TP1
    

if Tilgungsanpassung_1 == True and Tilgungsanpassung_2 == False:
    if Zinsbindung_date <= Tilgungsanpassung_1_date:
        Normalzins = NeuerZins
        TP1_zins, meta_1_zins = darlehen(TP1['Restschuld'].at[Zinsbindung_date - pd.DateOffset(months = 1)], Zinsbindung_date, Normalzins, Tilgung, ProzTilg, Darlehensbetrag)
        T_z = TP1['Tilgung'].at[Zinsbindung_date] + TP1_zins['Zinsanteil'].at[Zinsbindung_date]
        TP1_zins, meta_1_zins = darlehen(TP1['Restschuld'].at[Zinsbindung_date - pd.DateOffset(months = 1)], Zinsbindung_date, Normalzins, T_z, False, Darlehensbetrag)
        TP1 = TP1.drop(index = pd.date_range(start = Zinsbindung_date, end = TP1.index[-1], freq = 'MS'))
        TP1 = pd.concat([TP1, TP1_zins], axis = 0)

    TP2, meta2 = darlehen(TP1['Restschuld'].at[Tilgungsanpassung_1_date - pd.DateOffset(months = 1)], Tilgungsanpassung_1_date, Normalzins, Tilgung1, ProzTilg1, Darlehensbetrag)

    if Zinsbindung_date <= TP2.index[-1]:
        Normalzins = NeuerZins
        TP2_zins, meta_2_zins = darlehen(TP2['Restschuld'].at[Zinsbindung_date - pd.DateOffset(months = 1)], Zinsbindung_date, Normalzins, Tilgung, ProzTilg, Darlehensbetrag)
        T_z = TP2['Tilgung'].at[Zinsbindung_date] + TP2_zins['Zinsanteil'].at[Zinsbindung_date]
        TP2_zins, meta_1_zins = darlehen(TP2['Restschuld'].at[Zinsbindung_date - pd.DateOffset(months = 1)], Zinsbindung_date, Normalzins, T_z, False, Darlehensbetrag)
        TP2 = TP2.drop(index = pd.date_range(start = Zinsbindung_date, end = TP2.index[-1], freq = 'MS'))
        TP2 = pd.concat([TP2, TP2_zins], axis = 0)

    TP1 = TP1.drop(index = pd.date_range(start = Tilgungsanpassung_1_date, end = TP1.index[-1], freq = 'MS'))
    TP = pd.concat([TP1, TP2], axis = 0)



if Tilgungsanpassung_2 == True and Tilgungsanpassung_1 == True:
    if Zinsbindung_date <= Tilgungsanpassung_1_date:
        Normalzins = NeuerZins
        TP1_zins, meta_1_zins = darlehen(TP1['Restschuld'].at[Zinsbindung_date - pd.DateOffset(months = 1)], Zinsbindung_date, Normalzins, Tilgung, ProzTilg, Darlehensbetrag)
        T_z = TP1['Tilgung'].at[Zinsbindung_date] + TP1_zins['Zinsanteil'].at[Zinsbindung_date]
        TP1_zins, meta_1_zins = darlehen(TP1['Restschuld'].at[Zinsbindung_date - pd.DateOffset(months = 1)], Zinsbindung_date, Normalzins, T_z, False, Darlehensbetrag)
        TP1 = TP1.drop(index = pd.date_range(start = Zinsbindung_date, end = TP1.index[-1], freq = 'MS'))
        TP1 = pd.concat([TP1, TP1_zins], axis = 0)

    TP2, meta2 = darlehen(TP1['Restschuld'].at[Tilgungsanpassung_1_date - pd.DateOffset(months = 1)], Tilgungsanpassung_1_date, Normalzins, Tilgung1, ProzTilg1, Darlehensbetrag)

    if Zinsbindung_date <= Tilgungsanpassung_2_date:
        Normalzins = NeuerZins
        TP2_zins, meta_2_zins = darlehen(TP2['Restschuld'].at[Zinsbindung_date - pd.DateOffset(months = 1)], Zinsbindung_date, Normalzins, Tilgung, ProzTilg, Darlehensbetrag)
        T_z = TP2['Tilgung'].at[Zinsbindung_date] + TP2_zins['Zinsanteil'].at[Zinsbindung_date]
        TP2_zins, meta_1_zins = darlehen(TP2['Restschuld'].at[Zinsbindung_date - pd.DateOffset(months = 1)], Zinsbindung_date, Normalzins, T_z, False, Darlehensbetrag)
        TP2 = TP2.drop(index = pd.date_range(start = Zinsbindung_date, end = TP2.index[-1], freq = 'MS'))
        TP2 = pd.concat([TP2, TP2_zins], axis = 0)

    TP3, meta3 = darlehen(TP2['Restschuld'].at[Tilgungsanpassung_2_date - pd.DateOffset(months = 1)], Tilgungsanpassung_2_date, Normalzins, Tilgung2, ProzTilg2, Darlehensbetrag)

    if Zinsbindung_date <= TP3.index[-1]:
        Normalzins = NeuerZins
        TP3_zins, meta_2_zins = darlehen(TP3['Restschuld'].at[Zinsbindung_date - pd.DateOffset(months = 1)], Zinsbindung_date, Normalzins, Tilgung, ProzTilg, Darlehensbetrag)
        T_z = TP3['Tilgung'].at[Zinsbindung_date] + TP3_zins['Zinsanteil'].at[Zinsbindung_date]
        TP3_zins, meta_1_zins = darlehen(TP3['Restschuld'].at[Zinsbindung_date - pd.DateOffset(months = 1)], Zinsbindung_date, Normalzins, T_z, False, Darlehensbetrag)
        TP3 = TP3.drop(index = pd.date_range(start = Zinsbindung_date, end = TP3.index[-1], freq = 'MS'))
        TP3 = pd.concat([TP3, TP3_zins], axis = 0)

    TP1 = TP1.drop(index = pd.date_range(start = Tilgungsanpassung_1_date, end = TP1.index[-1], freq = 'MS'))
    TP2 = TP2.drop(index = pd.date_range(start = Tilgungsanpassung_2_date, end = TP2.index[-1], freq = 'MS'))
    TP = pd.concat([TP1, TP2, TP3], axis = 0)

TP['Gesamtkosten'] = TP['Monatliche Rate'].cumsum()
TP['Getilgt'] = TP['Tilgung'].cumsum()
TP['Bezahlte Zinsen'] = TP['Zinsanteil'].cumsum()

st.write('**Laufzeit **', round(np.floor(len(TP)/12)), 'Jahre und', round((len(TP)/12-np.floor(len(TP)/12))*12),
'Monate | **Gesamtkosten **', round(TP['Gesamtkosten'].iloc[-1],2), 'EUR | **Bezahlte Zinsen **',
round(TP['Bezahlte Zinsen'].iloc[-1],2), 'EUR | **Restschuld am Ende der Zinsbindung: **', 
round(TP['Restschuld'].at[Zinsbindung_date - pd.DateOffset(months = 1)], 2 ), 'EUR')


left, right = st.beta_columns(2)


left.area_chart(TP[['Tilgung', 'Zinsanteil']])
left.line_chart(TP[['Restschuld', 'Gesamtkosten', 'Getilgt', 'Bezahlte Zinsen']])

with right.beta_expander('Tilgungsplan'):
    TP.index = TP.index.strftime('%d.%m.%Y')
    st.dataframe(TP, height = 500)
    csv = TP.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    linko= f'<a href="data:file/csv;base64,{b64}" download="tilgungsplan.csv">Tilgungsplan als CSV</a>'
    st.markdown(linko, unsafe_allow_html=True)

