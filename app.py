import streamlit as st

st.set_page_config(page_title="BF-Tag Notfallabfrage", page_icon="🚒", initial_sidebar_state="collapsed")

st.header("Wo ist der Notfallort?")
st.text_input("Stadt", value="Dresden")
address = st.text_input("Adresse", placeholder="Lilienstraße 1 / Bismarksäule")

if(not address):
    st.stop()

st.header("Was ist passiert?")

description = st.text_area("Kurzbeschreibung", placeholder="Was ist passiert?", help="Stichpunktartig den Unfall/Notfall-Hergang beschreiben.")
if(not description):
    st.stop()

st.header("Wer ruft an?")
caller_name = st.text_input("Name", placeholder="Günther Hörmann")
st.text_input("Telefonnummer für Rückfragen (optional)", placeholder="0123456789")

if(not caller_name):
    st.stop()

st.header("Betroffene Personen")
patient_count = st.number_input("Wie viele Personen sind verletzt/erkrankt?", min_value=0, max_value=10, value=0)

if(patient_count > 0):
    patients = []
    tabs = [tab for tab in st.tabs([f"Person {i+1}" for i in range(patient_count)])]
    for i in range(patient_count):
        with tabs[i]:
            name = f"Person {i+1}"
            name_new = st.text_input(f"Name", placeholder="Vorname Nachname")
            
            if(name_new):
                name = name_new
            
            st.number_input(f"Wie alt ist {name}?", min_value=0, max_value=120, value=0, key=f"age_{i+1}")
            st.text_area(
                f"Wie geht es {name} jetzt gerade?", 
                placeholder=f"Beschreibung des aktuellen Zustands von {name}", 
                help="Ansprechbar/bei Bewusstsein? Verletzungen? Vorerkrankungen? Atmung? Orientiert?")

st.header("Alarmierung")
col_hlf, col_mtf = st.columns(2)
send_hlf = col_hlf.checkbox("HLF 10", value=False)
send_mtf = col_mtf.checkbox("MTF", value=False)

st.markdown("---")

if(send_hlf or send_mtf):
    st.button("Alarmieren", use_container_width=True, type="primary")
