import os, time
import azure.cognitiveservices.speech as speechsdk
import streamlit as st
from geopy.geocoders import Nominatim

st.set_page_config(page_title="BF-Tag Notfallabfrage", page_icon="🚒", initial_sidebar_state="collapsed")

st.header("Wo ist der Notfallort?")
city_col, address_col = st.columns(2)
city = city_col.text_input("Stadt", value="Dresden", autocomplete="off")
address = address_col.text_input("Adresse", placeholder="Lilienstraße 1 / Bismarcksäule", autocomplete="off")

if(not address):
    st.stop()

try:
    geolocator = Nominatim(user_agent="jf_kaitz_bf_tag_leitstelle")
    location = geolocator.geocode(f"{address}, {city}, Deutschland")

    st.map([{
        "lat": location.latitude,
        "lon": location.longitude
    }], zoom=16, size=10)
except:
    st.info("Die Adresse konnte nicht gefunden werden. Möglicherweise wurde sie falsch verstanden?", icon="📍")

st.header("Was ist passiert?")

description = st.text_area("Kurzbeschreibung", placeholder="Was ist passiert?", help="Stichpunktartig den Unfall/Notfall-Hergang beschreiben.")
category = st.selectbox("Einsatz-Kategorie", ["", "Brandmeldeanlage", "Brandeinsatz", "Technische Hilfeleistung", "Medizinischer Notfall", "Tierrettung"], format_func=lambda x: '🔔 Einsatz-Kategorie auswählen' if x == '' else x)
if(not description or not category):
    st.stop()

st.header("Wer ruft an?")
caller_name = st.text_input("Name", placeholder="Günther Hörmann", autocomplete="off")
st.text_input("Telefonnummer für Rückfragen (optional)", placeholder="0123456789", autocomplete="off")

if(not caller_name):
    st.stop()

st.header("Betroffene Personen")
patient_count = st.number_input("Wie viele Personen sind verletzt/erkrankt?", min_value=0, max_value=10, value=0)

patients = [{'name': f"Unbekannte Person", 'age': 0, 'condition': ''} for i in range(patient_count)]

if(patient_count > 0):
    tabs = [tab for tab in st.tabs([f"Person {i+1}" for i in range(patient_count)])]
    for i in range(patient_count):
        with tabs[i]:
            name = f"Person {i+1}"
            name_new = st.text_input(f"Name", placeholder="Vorname Nachname", key=f"name_{i+1}" , autocomplete="off")
            
            if(name_new):
                patients[i]['name'] = name = name_new
            
            patients[i]['age'] = st.number_input(f"Wie alt ist {name}?", min_value=0, max_value=120, value=0, key=f"age_{i+1}")
            patients[i]['condition'] = st.text_area(
                f"Wie geht es {name} jetzt gerade?", 
                placeholder=f"Beschreibung des aktuellen Zustands von {name}", 
                help="Ansprechbar/bei Bewusstsein? Verletzungen? Vorerkrankungen? Atmung? Orientiert?",
                key=f"description_{i+1}")

st.header("Alarmierung")
col_hlf, col_mtf = st.columns(2)
send_hlf = col_hlf.checkbox("HLF 10", value=False)
send_mtf = col_mtf.checkbox("MTF", value=False)

st.markdown("---")

if(send_hlf or send_mtf):
    alarm = st.button("Alarmieren", use_container_width=True, type="primary")

    if(alarm):
        st.markdown("---")

        st.warning("Die folgenden Audioplayer starten automatisch. Man muss nicht extra auf 'Play' drücken. Sie lassen sich leider aus technischen Gründen nicht verstecken.", icon="⚠️")
        
        pull_stream = speechsdk.audio.PullAudioOutputStream()
    
        speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
        audio_config = speechsdk.audio.AudioOutputConfig(stream=pull_stream)
        speech_config.speech_synthesis_voice_name='de-DE-KatjaNeural'
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        st.write("Gong abspielen...")
        st.audio("./firehouse_alarm_gong.mp3", format="audio/mpeg", autoplay=True)
        time.sleep(3.5)
        
        alarm_text = f"Alarm! {category}! Es kommt zum Einsatz: "
        if(send_hlf and send_mtf):
            alarm_text += "HLF-10 und MTF!"
        elif(send_hlf):
            alarm_text += "HLF-10!"
        elif(send_mtf):
            alarm_text += "MTF!"
        if(city or address):
            alarm_text += " Einsatzort: "
        if(address):
            alarm_text += f" {address} -"
        if(city):
            alarm_text += f" {city}."
            
        if(description):
            alarm_text += f" {description}." 
            
        if(patient_count == 1):
            alarm_text += f" Eine Person verletzt."
        elif(patient_count > 1):
            alarm_text += f" {patient_count} Personen verletzt."
            
        for i in range(len(patients)):
            alarm_text += f"Patient {i+1}: {patients[i]['name']}"
            
            if(patients[i]['age'] == 1):
                alarm_text += " - ein Jahr alt"
            elif(patients[i]['age'] > 1):
                alarm_text += f" - {patients[i]['age']} Jahre alt"                
                            
            if(patients[i]['condition']):
                alarm_text += f" - {patients[i]['condition']}"
            alarm_text += "! "
            
        
        speech_synthesis_result = speech_synthesizer.speak_text_async(alarm_text).get()
        st.write("Alarmmeldung vorlesen...")
        st.audio(speech_synthesis_result.audio_data, format="audio/mpeg", autoplay=True)
