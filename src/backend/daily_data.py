import asyncio
from anthropic import AsyncAnthropic
from integrations.gmail import get_messages_since_yesterday
import os

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
    
    return classified_emails

def get_classified_emails():
    classified_emails = asyncio.run(get_and_classify_emails())
    useful_emails = [email for email in classified_emails if email['classification'] == "useful"]
    return classified_emails, useful_emails

if __name__ == "__main__":
    classified_emails, useful_emails = get_classified_emails()
    for i, email in enumerate(classified_emails):
        print(f"Email {i+1}:")
        print(f"Subject: {email['subject']}")
        print(f"From: {email['sender']}")
        if email['classification'] == "useful":
            print(f"\033[92mClassification: {email['classification']}\033[0m")
        elif email['classification'] == "spam":
            print(f"\033[91mClassification: {email['classification']}\033[0m")
        else:
            print(f"\033[93mClassification: {email['classification']}\033[0m")
        print("---")