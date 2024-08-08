import streamlit as st
import openai
import fitz  # PyMuPDF
import re

# Configura tu API key de OpenAI
openai.api_key = 'Aqui va tu api key de open ai'  # Reemplaza con tu clave real

# Función para extraer texto de un PDF
def extract_text_from_pdf(pdf_file):
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text

# Función para generar una respuesta usando OpenAI GPT
def generate_response(user_input, context):
    messages = [
        {"role": "system", "content": context},
        {"role": "user", "content": user_input}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Puedes usar "gpt-4" si es necesario
        messages=messages,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].message['content'].strip()

def main():
    st.set_page_config(page_title="Chatbot de Seguridad Informática", layout="wide")
    st.markdown("<h1 style='text-align: center;'>Chatbot de Seguridad Informática</h1>", unsafe_allow_html=True)

    # Manejar la subida del archivo PDF
    uploaded_file = st.file_uploader("Sube un archivo PDF", type="pdf")

    if uploaded_file is not None:
        # Extraer y mostrar el contenido del PDF
        pdf_text = extract_text_from_pdf(uploaded_file)
        st.text_area("Contenido del PDF", pdf_text, height=300)
        
        # Añadir el contenido del PDF al contexto del chatbot
        context = (
            "Eres un experto en seguridad informática. Responde a las preguntas y brinda consejos sobre prácticas "
            "seguras, gestión de riesgos, y protección contra amenazas cibernéticas. También considera el siguiente "
            "contenido del PDF para responder las preguntas:\n\n" + pdf_text
        )

        # Manejar el historial de la conversación
        if 'history' not in st.session_state:
            st.session_state['history'] = []
            st.session_state['question_step'] = 0
            st.session_state['user_answers'] = []
            st.session_state['feedbacks'] = []  # Para almacenar feedback individual
            st.session_state['questions'] = [
                "¿Qué harías tú en base al contenido del PDF?",
                "¿Cómo manejarías el riesgo mencionado en el PDF?",
                "¿Qué medidas tomarías para mitigar las amenazas descritas en el PDF?",
                "¿Qué recursos adicionales considerarías para resolver el problema planteado en el PDF?"
            ]
            st.session_state['feedback'] = ""
            st.session_state['grade'] = 0

        # Mostrar la pregunta actual y manejar la respuesta
        current_question_index = st.session_state['question_step']
        
        if current_question_index < len(st.session_state['questions']):
            st.markdown(f"<h2>Pregunta {current_question_index + 1}:</h2>", unsafe_allow_html=True)
            st.write(st.session_state['questions'][current_question_index])
            
            # Formulario para la entrada del usuario
            with st.form(key='response_form'):
                chat_input = st.text_input("Tu respuesta:", key="input" + str(current_question_index))
                send_button = st.form_submit_button("Enviar respuesta")
                
                if send_button and chat_input:
                    st.session_state['user_answers'].append(chat_input)
                    st.session_state['history'].append(f"You: {chat_input}")

                    # Obtener feedback individual para la respuesta
                    feedback_request = f"Proporciona retroalimentación para la siguiente respuesta del usuario en base al contenido del PDF: {chat_input}"
                    feedback = generate_response(feedback_request, context)
                    st.session_state['feedbacks'].append(feedback)

                    st.session_state['question_step'] += 1
                    st.experimental_rerun()

        # Calificar y dar feedback al finalizar
        if st.session_state['question_step'] == len(st.session_state['questions']):
            # Generar feedback general
            user_answers_text = "\n".join(st.session_state['user_answers'])
            final_feedback_request = (
                "Basado en el contenido del PDF y las respuestas del usuario, ¿cómo resolvería el problema de seguridad informática presentado en el PDF? "
                "Proporciona una solución detallada para resolver el problema."
            )
            full_context = f"{context}\n\nRespuestas del usuario:\n{user_answers_text}"
            final_feedback = generate_response(final_feedback_request, full_context)
            st.session_state['feedback'] = final_feedback

            # Asignar una calificación
            grade = re.search(r'\b(\d+)\b', final_feedback)
            st.session_state['grade'] = int(grade.group()) if grade else 0

            # Mostrar feedback y calificación general
            st.markdown("<h2>Feedback del profesor:</h2>", unsafe_allow_html=True)
            for i, feedback in enumerate(st.session_state['feedbacks']):
                st.markdown(f"<h3>Feedback para la Pregunta {i + 1}:</h3>", unsafe_allow_html=True)
                st.write(feedback)
            st.markdown("<h2>Solución del problema:</h2>", unsafe_allow_html=True)
            st.write(st.session_state['feedback'])
            st.markdown(f"<h3>Calificación: {st.session_state['grade']} / 20</h3>", unsafe_allow_html=True)

        # Mostrar el historial de la conversación
        if st.session_state['history']:
            st.markdown("<h2>Historial de la conversación:</h2>", unsafe_allow_html=True)
            for msg in st.session_state['history']:
                st.write(msg)

if __name__ == "__main__":
    main()
