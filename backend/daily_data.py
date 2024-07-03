import asyncio
from anthropic import AsyncAnthropic
from integrations.gmail import get_messages_since_yesterday, get_attendee_email_threads
from integrations.google_calendar import get_today_events
import os, base64


SELF_EMAIL = "markacastellano2@gmail.com"

async def summarize_thread(client, thread_messages):
    combined_content = "\n\n".join([f"Subject: {msg['subject']}\nFrom: {msg['sender']}\nBody: {msg['body'][:500]}..." for msg in thread_messages])
    prompt = f"""
    Summarize the following email thread concisely:

    {combined_content}

    Provide a brief summary that captures the main points and any important details.
    """
    
    response = await client.messages.create(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        temperature=0.0,
        model="claude-3-5-sonnet-20240620"
    )
    return response.content[0].text.strip()


async def get_event_related_emails():
    client = AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    
    # Get today's events
    events = await get_today_events()
    
    event_summaries = []
    
    for event in events:
        attendees = event['attendees']
        non_self_attendees = [attendee for attendee in attendees if attendee != SELF_EMAIL]
        
        event_summary = {
            'event': event['summary'],
            'start': event['start'],
            'end': event['end'],
            'attendee_summaries': []
        }


        for attendee in non_self_attendees:
            # Get email threads for the attendee
            thread_messages = get_attendee_email_threads(attendee)
            
            if thread_messages:
                # Summarize the thread
                summary = await summarize_thread(client, thread_messages)
                event_summary['attendee_summaries'].append({
                    'attendee': attendee,
                    'summary': summary
                })
        
        event_summaries.append(event_summary)
    
    return event_summaries

async def classify_email(client, email):
    prompt = f"""
    Classify the following email into one of the following categories:
    <categories>
    useful
    spam
    </categories>

    Useful emails are emails from people or newsletters with interesting information about what's going on in the world. 
    Spam emails are promotional emails that are trying to sell a product, ask for donations, notify terms of service changes 

    Here is the email:
    <email>
    From: {email['sender']}
    Subject: {email['subject']}
    Body: {email['body'][:500]}...
    </email>
    """
    
    response = await client.messages.create(
        messages=[{"role":"user", "content": prompt}, {"role":"assistant", "content": "<category>"}],
        stop_sequences=["</category>"], 
        max_tokens=1024, 
        temperature=0.0,
        model="claude-3-5-sonnet-20240620"
    )
    return response.content[0].text.strip()

async def get_and_classify_emails():
    client = AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    emails = get_messages_since_yesterday()
    
    classification_tasks = [classify_email(client, email) for email in emails]
    classifications = await asyncio.gather(*classification_tasks)
    
    classified_emails = []
    for email, classification in zip(emails, classifications):
        email['classification'] = classification
        classified_emails.append(email)
    
    useful_emails = [email for email in classified_emails if email['classification'] == "useful"]
    return classified_emails, useful_emails

async def get_classified_emails():
    classified_emails, useful_emails = await get_and_classify_emails()
    for i, email in enumerate(classified_emails):
        print(f"Email {i+1}:", flush=True)
        print(f"Subject: {email['subject']}", flush=True)
        print(f"From: {email['sender']}", flush=True)
        if email['classification'] == "useful":
            print(f"\033[92mClassification: {email['classification']}\033[0m", flush=True)
        elif email['classification'] == "spam":
            print(f"\033[91mClassification: {email['classification']}\033[0m", flush=True)
        else:
            print(f"\033[93mClassification: {email['classification']}\033[0m", flush=True)
        print("---", flush=True)
        
    return classified_emails, useful_emails


