from flask import Flask, request, send_file
import subprocess
from flask_cors import CORS
import google.generativeai as genai
import re
import traceback

from TTS.api import TTS

tts = TTS("tts_models/es/css10/vits")

app = Flask(__name__)

CORS(app)


genai.configure(api_key="arriba")

# model = genai.GenerativeModel("gemini-1.5-flash")
model = genai.GenerativeModel("gemini-pro")

COUNT = 0

def readInputUser():
    words = ""
    count = 0
    with open("inputUser.txt","r") as f:
        for i in f.readlines():
            for j in i.split(" "):
                print(j)
                words += j
                words += " "
    
    return words

@app.route('/upload', methods=['POST'])
def upload_audio():
    global COUNT
    try:
        # Check if the post request has the audio file
        if 'audio' not in request.files:
            return {"error": "No audio file provided"}, 400
        
        audio = request.files['audio']
        
        # Save the audio file
        audio_name = audio.filename
        audio.save(audio_name)  # Save with original filename

        subprocess.run(['vosk-transcriber', '-i' ,'recording.wav' ,'-o' ,'inputUser.txt', '--lang' ,'es'])

        words = "Tienes este texto, define la emoción y los sentimientos de este texto, lista todas las emociones que crees que aparece en el texto dado, máximo 3, sin ningun enunciado, solo separalas por espacio "
        # words = "Da respuesta muy concisas y solo ten una conversación no hables de otros temas"
        # words = ""
        words += readInputUser()

        emociones = model.generate_content(words)

        print(emociones.text)

        words = "No te imagines la conversación, solo responde lo que el cliente te diga y trata de convencerlo de que pague la deuda "
        words += "Tus clientes te deben dinero y tienes que convencerlos de que paguen , eres un vendedor, tu tarea es convencerlos de que paguen"
        words += "Da respuesta muy concisas y solo ten una conversación e intenta que el cliente pague su deuda no hables de otros temas "
        words += "Si te preguntan de otros temas, no respondas "
        words += "No simules una conversación con el cliente, solo responde lo que el te diga y convencelo de que pague su deuda. No te inventes enunciados, solo responde lo que dice el usuario "
        words += "Si el cliente dice que si quiere pagar dile que Pague en este link 'LINK PARA EL PAGO' y que estas atento a cualquier otra duda"
        # words = ""
        words += readInputUser()

        respuesta = model.generate_content(words)

        if re.search("\*",respuesta.text):

            respuesta = {"text":"Intentalo de nuevo"}

        print(respuesta.text)

        print("-"*20)

        print("-"*20)

        tts.tts_to_file(text=respuesta.text,file_path="{}.wav".format(COUNT))
        COUNT += 1
        
        # return {"response": f"File '{audio_name}' saved successfully."}, 200
        return {"entrada":readInputUser(),"emociones": emociones.text,"respuesta":respuesta.text,"url_audio":"http://localhost:5000/send-audio/{}".format(COUNT-1)}, 200
    except Exception as e:
        print(str(e))
        traceback.print_exc()
        return {"error": str(e)}, 500

@app.route('/send-audio/<audio_id>', methods=['GET'])
def send_audio(audio_id):
    try:
        # Specify the path to your WAV file
        # audio_file_path = 'assist.wav'

        audio_file_path = f'{audio_id}.wav' 
        return send_file(audio_file_path, mimetype='audio/wav')
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
