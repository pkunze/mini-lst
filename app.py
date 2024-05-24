import os
import azure.cognitiveservices.speech as speechsdk
import streamlit as st
from preferredsoundplayer import *

st.set_page_config(page_title="BF-Tag Notfallabfrage", page_icon="🚒", initial_sidebar_state="collapsed")

st.header("Wo ist der Notfallort?")
city = st.text_input("Stadt", value="Dresden")
address = st.text_input("Adresse", placeholder="Lilienstraße 1 / Bismarksäule")

if(not address):
    st.stop()

st.header("Was ist passiert?")

description = st.text_area("Kurzbeschreibung", placeholder="Was ist passiert?", help="Stichpunktartig den Unfall/Notfall-Hergang beschreiben.")
category = st.selectbox("Einsatz-Kategorie", ["Brandmeldeanlage", "Brandeinsatz", "Technische Hilfeleistung", "Medizinischer Notfall", "Tierrettung"], placeholder="Waehle eine Einsatz-Kategorie")
if(not description or not category):
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
    alarm = st.button("Alarmieren", use_container_width=True, type="primary")
    
    if(alarm):
        pull_stream = speechsdk.audio.PullAudioOutputStream()
    
        speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
        audio_config = speechsdk.audio.AudioOutputConfig(stream=pull_stream)
        speech_config.speech_synthesis_voice_name='de-DE-KatjaNeural'
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        st.subheader("Gong abspielen (startet beim ersten mal automatisch)")
        st.audio("./firehouse_alarm_gong.mp3", format="audio/mpeg", autoplay=True)
        sleep(5)
        
        alarm_text = f"Alarm! {category}! Es kommt zum Einsatz: "
        if(send_hlf and send_mtf):
            alarm_text += "HLF-10 und MTF."
        elif(send_hlf):
            alarm_text += "HLF-10."
        elif(send_mtf):
            alarm_text += "MTF."
        
        if(city):
            alarm_text += f" {city}."
        
        if(address):
            alarm_text += f" {address} -"

        if(description):
            alarm_text += f" {description}."
            
        if(patient_count == 1):
            alarm_text += f" Eine Person verletzt."
        elif(patient_count > 1):
            alarm_text += f" {patient_count} Personen verletzt."
        
        speech_synthesis_result = speech_synthesizer.speak_text_async(alarm_text).get()
        st.subheader("Alarmmeldung vorlesen (startet beim ersten mal automatisch)")
        st.audio(speech_synthesis_result.audio_data, format="audio/mpeg", autoplay=True)

