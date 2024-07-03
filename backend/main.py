from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from daily_data import get_classified_emails
from integrations.google_calendar import get_today_events

import pickle, os

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def load_or_save_pickle(file_name, data_function):
    if os.path.exists(file_name):
        with open(file_name, 'rb') as f:
            return pickle.load(f)
    else:
        data = await data_function()
        with open(file_name, 'wb') as f:
            pickle.dump(data, f)
        return data


@app.get("/api/get-emails")
async def get_emails():
    email_data = await load_or_save_pickle('email_data.pickle', get_classified_emails)
    return {
        "classified_emails": email_data[0],
        "useful_emails": email_data[1]
    }


@app.get("/api/get-calendar")
async def get_calendar():
    events = await load_or_save_pickle('calendar_events.pickle', get_today_events)
    return {
        "events": events,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)