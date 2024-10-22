from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import openai
import json
from openai import OpenAI
from twilio.twiml.messaging_response import MessagingResponse
import os
from dotenv import load_dotenv


load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

messages = [
    {
        "role": "system",
        "content": "Eres el asistente virtual de Gavilan y Asociados. Tu objetivo es: 1) Recabar más información del cliente sobre problemas relacionados con edificaciones, como posibles causas o detalles adicionales. 2) Si no puedes resolver el problema, debes derivar al cliente a un ingeniero, indicándole que se pondrá en contacto un experto. Si el cliente pregunta sobre algo que no está relacionado con edificaciones, debes indicarle que solo puedes asistir en temas relacionados con estructuras y hormigón."
    }
]


def index(request):
    return render(request, 'index.html')


def get_response(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question = data.get('question')
        # Añadir la nueva pregunta al historial de mensajes
        messages.append({"role": "user", "content": question})
        # Llamada a la API de OpenAI
        response = openai.chat.completions.create(
            model="ft:gpt-3.5-turbo-1106:personal:gya-chat:AJnlAkJW",
            messages=messages,
            max_tokens=200
        )
        answer = response.choices[0].message.content.strip()
        messages.append({"role": "assistant", "content": answer})

        return JsonResponse({'response': answer})


# Vista para recibir mensajes desde Twilio y devolver un mensaje de éxito
@csrf_exempt
def receive_whatsapp(request):
    if request.method == 'POST':
        # Obtener el mensaje entrante desde Twilio (por ahora no lo usaremos)
        incoming_msg = request.POST.get('Body', '').strip()

        # Crear una respuesta simple para Twilio
        twilio_resp = MessagingResponse()
        # Este es el mensaje que se devolverá como respuesta, para verificar la conexión
        twilio_resp.message("Respondido desde el backend por éxito")

        # Enviar la respuesta a Twilio como XML
        return HttpResponse(str(twilio_resp), content_type='text/xml')

