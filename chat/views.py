from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import openai
import json
from openai import OpenAI
from twilio.twiml.messaging_response import MessagingResponse
import os
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt


load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

conversations = {}

initial_message = [
    {
        "role": "system",
        "content": "Eres el asistente virtual de Gavilan y Asociados. Tu objetivo es: 1) Recabar más información del cliente sobre problemas relacionados con edificaciones, como posibles causas o detalles adicionales. 2) Si no puedes resolver el problema, debes derivar al cliente a un ingeniero, indicándole que se pondrá en contacto un experto. Si el cliente pregunta sobre algo que no está relacionado con edificaciones, debes indicarle que solo puedes asistir en temas relacionados con estructuras y hormigón."
    }
]



def index(request):
    return render(request, 'index.html')


def get_response(request):
    messages = [
        {
            "role": "system",
            "content": "Eres el asistente virtual de Gavilan y Asociados. Tu objetivo es: 1) Recabar más información del cliente sobre problemas relacionados con edificaciones, como posibles causas o detalles adicionales. 2) Si no puedes resolver el problema, debes derivar al cliente a un ingeniero, indicándole que se pondrá en contacto un experto. Si el cliente pregunta sobre algo que no está relacionado con edificaciones, debes indicarle que solo puedes asistir en temas relacionados con estructuras y hormigón."
        }
    ]
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
        from_number = request.POST.get('From', '').strip()
        incoming_msg = request.POST.get('Body', '').strip()

        # Si el usuario envía "reiniciar", se reinicia su conversación
        if incoming_msg.lower() == "reiniciar":
            conversations[from_number] = initial_message.copy()
            answer = "He reiniciado nuestra conversación. ¿En qué puedo ayudarte?"
        else:
            # Si no hay una conversación para este número, iniciamos una nueva
            if from_number not in conversations:
                conversations[from_number] = initial_message.copy()

            # Añadir el mensaje del usuario al historial
            conversations[from_number].append({"role": "user", "content": incoming_msg})

            # Llamada a la API de OpenAI para obtener la respuesta
            answer = openai_chat_completion(conversations[from_number])

            # Añadir la respuesta de OpenAI al historial
            conversations[from_number].append({"role": "assistant", "content": answer})

        # Crear una respuesta de Twilio y enviar la respuesta
        twilio_resp = MessagingResponse()
        twilio_resp.message(answer)

        return HttpResponse(str(twilio_resp), content_type='text/xml')


def openai_chat_completion(conversation):
    try:
        response = openai.chat.completions.create(
            model="ft:gpt-3.5-turbo-1106:personal::ALHyhY5x",
            messages=conversation,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "Lo siento, ocurrió un error al procesar tu solicitud. Intenta de nuevo más tarde."
