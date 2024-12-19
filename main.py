from flask import Flask, render_template, request, jsonify, send_file
from groq import Groq
import os
import uuid
from gtts import gTTS
import dotenv
import json

dotenv.load_dotenv()

app = Flask(__name__)


groq_llm = Groq(api_key=os.environ.get("GROQ_API_KEY"))

os.makedirs("temp", exist_ok=True)

input_data = {
    "overview": {
        "description": "Portal for education-related services in Rajasthan.",
        "departments": [
            "Secondary Education",
            "Elementary Education",
            "Sanskrit Education",
            "Literacy & Continuing Education",
            "Textbook Board",
            "School Education Council",
            "District Institutes of Education and Training",
            "Mid-Day Meal Program",
            "Rajasthan State Open School",
        ],
        "website": "http://education.rajasthan.gov.in/home",
    },
    "departments": {
        "Secondary Education": {
            "functions": "Manage secondary education, teacher transfers, seniority lists, retirement notices.",
            "services": ["Transfer orders", "Seniority lists", "Updates for employees"],
            "link": "http://education.rajasthan.gov.in/secondary",
        },
        "Elementary Education": {
            "functions": "Primary education management, teacher recruitment, student services.",
            "services": [
                "Verification of qualifications",
                "Teacher postings",
                "Admission updates",
            ],
            "link": "http://education.rajasthan.gov.in/elementary",
        },
        "Sanskrit Education": {
            "functions": "Promote Sanskrit, conduct recruitment exams, and organize employment fairs.",
            "services": ["Circulars", "Recruitment updates", "Academic notices"],
            "link": "http://education.rajasthan.gov.in/sanskrit",
        },
        "Literacy & Continuing Education": {
            "functions": "Adult education programs, literacy campaigns.",
            "services": [
                "Event information",
                "Book exhibitions",
                "Ancient manuscripts",
            ],
            "link": "http://education.rajasthan.gov.in/literacyandcontinuingeducation",
        },
        "Textbook Board": {
            "functions": "Textbook publishing and distribution.",
            "services": ["Tenders", "Circulars", "Annual reports"],
            "link": "http://education.rajasthan.gov.in/rstb",
        },
        "School Education Council": {
            "functions": "Implement educational programs like Shaala Darpan, vocational education, ICT in schools.",
            "services": ["Program details", "School reports", "Inclusive education"],
            "link": "http://education.rajasthan.gov.in/rcse",
        },
        "Mid-Day Meal Program": {
            "functions": "Provide free lunches to school children.",
            "services": ["Meal plans", "Updates"],
            "link": "http://education.rajasthan.gov.in/mdm",
        },
        "District Institutes of Education and Training": {
            "functions": "Teacher training and research.",
            "services": ["Workshops", "Educational resources"],
            "link": "http://education.rajasthan.gov.in/diets",
        },
        "Rajasthan State Open School": {
            "functions": "Flexible education for students unable to attend formal schooling.",
            "services": ["Exam schedules", "Results", "Enrollment details"],
            "link": "http://education.rajasthan.gov.in/rsos",
        },
    },
    "initiatives": {
        "Shaala Darpan": {
            "description": "Mobile-friendly platform for parents and students to access school and student information.",
            "link": "http://education.rajasthan.gov.in/rcse/ShaalaDarpan",
        },
        "Model Schools Program": {
            "description": "Focus on quality education and innovation.",
            "link": "http://education.rajasthan.gov.in/rcse/ModelSchools",
        },
        "ICT in Schools": {
            "description": "Integrating technology into classrooms.",
            "link": "http://education.rajasthan.gov.in/rcse/ICT",
        },
    },
    "services": [
        {
            "name": "Recruitment details",
            "link": "http://education.rajasthan.gov.in/elementary/Recruitment",
        },
        {
            "name": "Circulars and orders",
            "link": "http://education.rajasthan.gov.in/home/Circulars",
        },
        {
            "name": "Teacher transfer updates",
            "link": "http://education.rajasthan.gov.in/secondary/TransferOrders",
        },
        {
            "name": "Textbook publishing",
            "link": "http://education.rajasthan.gov.in/rstb",
        },
        {
            "name": "Examination schedules and results",
            "link": "http://education.rajasthan.gov.in/rsos/Examinations",
        },
    ],
    "faqs": {
        "How to apply for teacher recruitment?": {
            "answer": "Navigate to the Elementary Education Department section and click on 'Recruitment.'",
            "link": "http://education.rajasthan.gov.in/elementary/Recruitment",
        },
        "Where can I find transfer orders?": {
            "answer": "Visit the Secondary Education Department and check the 'Transfer Orders' section.",
            "link": "http://education.rajasthan.gov.in/secondary/TransferOrders",
        },
        "How to access Shaala Darpan?": {
            "answer": "Use the 'Shaala Darpan' link on the homepage or search for your school by name or code.",
            "link": "http://education.rajasthan.gov.in/rcse/ShaalaDarpan",
        },
    },
    "contact_info": {
        "General": "http://education.rajasthan.gov.in/home",
        "Secondary Education": "+91-1234567890",
        "Elementary Education": "+91-9876543210",
        "Sanskrit Education": "+91-1112223334",
    },
}


@app.route("/")
def index():
    return render_template("index.html")


def clean_temp_directory():
    for filename in os.listdir("temp"):
        file_path = os.path.join("temp", filename)
        os.remove(file_path)


def get_chat_response(user_input):
    return groq_llm.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"You are Vidya, a helpful assistant specializing in providing information related to the Department of Education, Rajasthan. Respond only with relevant details about the department, its initiatives, vision, mission, or any other educational content. If the query is unrelated, provide contact details or ask the user to contact the department. For all responses, ensure you return a structured HTML response to display in the chatbot interface and also plain text response in the format of \"{'{'}\"response_html\": \"response\", \"response_text\":\"response\"{'}'}\" and never miss this kind of response type. Use the following data to respond: {input_data}. If information is unavailable, guide the user appropriately",
            },
            {"role": "user", "content": user_input},
        ],
        model="llama3-8b-8192",
        temperature=0.5,
        max_tokens=1024,
        top_p=1,
    )


def generate_audio_response(response_text):
    audio_file = f"temp/{uuid.uuid4()}.mp3"
    tts = gTTS(response_text)
    tts.save(audio_file)
    return f"/audio-response/{os.path.basename(audio_file)}"


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message")
    use_audio_response = data.get("audio_response", False)

    # Send the user input to the LLM model
    chat_response = get_chat_response(user_input)

    response_text = chat_response.choices[0].message.content
    print(response_text)
    response_text = json.loads(response_text)

    is_html = False
    if (
        "<html>" in response_text["response_html"]
        or "</" in response_text["response_html"]
    ):
        is_html = True

    response = {
        "response_html": response_text["response_html"],
        "response_text": response_text["response_text"],
        "is_html": is_html,
    }

    if use_audio_response:
        response["audio_url"] = generate_audio_response(response_text["response_text"])

    return jsonify(response)


@app.route("/audio-response/<filename>", methods=["GET"])
def audio_response(filename):
    return send_file(f"temp/{filename}", mimetype="audio/mpeg")


@app.route("/upload-audio", methods=["POST"])
def upload_audio():
    file = request.files["file"]
    print(request.form)
    use_audio_response = request.form.get("audio_response") == "true"
    audio_file_path = f"temp/{uuid.uuid4()}.m4a"
    file.save(audio_file_path)

    # Open the audio file and transcribe it using Groq Whisper model
    with open(audio_file_path, "rb") as audio_file:
        transcription = groq_llm.audio.transcriptions.create(
            file=(audio_file_path, audio_file.read()),  # Required audio file
            model="whisper-large-v3-turbo",  # Model for transcription
            prompt="Specify context or spelling",  # Optional
            response_format="json",  # Optional
            language="en",  # Language of transcription
            temperature=0.0,  # Optional, can be adjusted based on need
        )

    user_input = transcription.text  # Extract transcribed text
    chat_response = get_chat_response(user_input)
    response_text = chat_response.choices[0].message.content
    print(response_text)
    response_text = json.loads(response_text)
    is_html = False
    if (
        "<html>" in response_text["response_html"]
        or "</" in response_text["response_html"]
    ):
        is_html = True

    response = {
        "response_html": response_text["response_html"],
        "response_text": response_text["response_text"],
        "is_html": is_html,
    }
    if use_audio_response:
        response["audio_url"] = generate_audio_response(response_text["response_text"])
    return jsonify(response)


if __name__ == "__main__":
    clean_temp_directory()
    app.run(debug=True)
