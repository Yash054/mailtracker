import os
from dotenv import load_dotenv
from langchain_cohere import ChatCohere
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage

load_dotenv()

llm = ChatCohere(cohere_api_key=os.getenv("COHERE_API_KEY"), temperature=0.3, model="command-r-plus")  # free tier model

template = """
You are an assistant that processes job application-related emails.

Carefully read the email below and extract the following fields. Your main job is to understand whether this is an actual update about a job application or just a job alert/newsletter.

🔹 If the email is a job alert, newsletter, marketing email, or list of job openings (not a personal application update), mark status as **"Not Relevant"**.

🔹 Do not guess "Applied" unless the email clearly mentions that the user has applied or it’s a follow-up to their application.

Return the following fields:
- Company Name
- Role/Position
- Job ID (if present)
- Application Status: [Applied, Interview, Offer, Rejected, Info Needed, Not Relevant]
- Action Required (if any)
- Is this email an update to a previous application?
- Short Summary (1 sentence)

Email Subject: {subject}
Email Body: {body}
"""

prompt = PromptTemplate.from_template(template)

def parse_email(subject: str, body: str):
    input_prompt = prompt.format(subject=subject, body=body)
    messages = [HumanMessage(content=input_prompt)]
    response = llm.invoke(messages)
    return response.content
