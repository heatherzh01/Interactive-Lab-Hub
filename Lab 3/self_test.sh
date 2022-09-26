#from: https://elinux.org/RPi_Text_to_Speech_(Speech_Synthesis)#Festival_Text_to_Speech

echo "Hello, what is the number on the card you draw?" | festival --tts

#arecord -f cd -r 16000 -d 5 -t wav recorded.wav && sox recorded.wav recorded_mono.wav remix 1,2

arecord -D hw:1,0 -f cd -c1 -r 44100 -d 5 -t wav recorded_mono.wav
python3 test_words.py recorded_mono.wav
