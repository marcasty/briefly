"use client";

import { useEffect, useState } from 'react';
import Footer from '../components/Footer';

interface Email {
  subject: string;
  sender: string;
  summary: string;
}

interface CalendarEvent {
  summary: string;
  creator: string;
  organizer: string;
  attendees: string[];
  start: string;
  end: string;
  description: string;
  location: string;
  context: string;
}

export default function Home() {
  const [personalEmails, setPersonalEmails] = useState<Email[]>([]);
  const [newsEmails, setNewsEmails] = useState<Email[]>([]);
  const [spamEmails, setSpamEmails] = useState<Email[]>([]);
  const [calendarEvents, setCalendarEvents] = useState<CalendarEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setIsLoading(true);
        setError(null);
        const [emailsResponse, calendarResponse] = await Promise.all([
          fetch('http://localhost:8000/api/get-emails'),
          fetch('http://localhost:8000/api/get-calendar')
        ]);

        if (!emailsResponse.ok || !calendarResponse.ok) {
          throw new Error(`HTTP error! status: ${emailsResponse.status} ${calendarResponse.status}`);
        }

        const emailsData = await emailsResponse.json();
        const calendarData = await calendarResponse.json();

        setPersonalEmails(emailsData.personal_emails);
        setNewsEmails(emailsData.news_emails);
        setSpamEmails(emailsData.spam_emails);
        setCalendarEvents(calendarData.events);
      } catch (error) {
        console.error('Error fetching data:', error);
        setError('Failed to fetch data. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    }

    fetchData();
  }, []);


  return (
    <div className="bg-midjourney_navy flex flex-col min-h-screen text-white">
      <main className="flex-grow container mx-auto px-4 py-8">
        <div className="bg-briefly_box p-6 mb-8 rounded-lg shadow-lg flex justify-center items-center">
          <pre className="text-white font-mono text-sm">
{` _          _       __ _       
| |        (_)     / _| |      
| |__  _ __ _  ___| |_| |_   _ 
| '_ \\| '__| |/ _ \\  _| | | | |
| |_) | |  | |  __/ | | | |_| |
|_.__/|_|  |_|\\___|_| |_|\\__, |
                          __/ |
                         |___/ `}
          </pre>
        </div>
        <h2 className="text-3xl font-bold mb-6">personal</h2>
        <ul className="space-y-2">
          {calendarEvents.map((event, index) => (
            <li key={index} className="p-4">
              <p className="text-md font-semibold text-main_white">{event.summary}</p>
              <p className="text-sm text-sub_grey mb-1">
                {new Date(event.start).toLocaleString()} - {new Date(event.end).toLocaleString()}
              </p>
              {event.location && (
                <p className="text-sm text-sub_grey mb-1">
                  <span className="font-medium">Location:</span> {event.location}
                </p>
              )}
              {event.attendees.length > 0 && (
                <div className="mb-2">
                  <p className="text-sm font-medium text-sub_grey">Attendees:</p>
                  <ul className="list-disc list-inside">
                    {event.attendees.map((attendee, idx) => (
                      <li key={idx} className="text-sm text-sub_sub_grey ml-4">{attendee}</li>
                    ))}
                  </ul>
                </div>
              )}

              {event.context && (
                <div className="mt-2">
                  <p className="text-sm font-medium text-sub_grey mb-1">Context:</p>
                  <p className="text-sm text-sub_sub_grey whitespace-pre-wrap">{event.context}</p>
                </div>
              )}
            </li>
          ))}
          {personalEmails.map((email, index) => (
            <li key={index} className="p-4">
              <p className="text-md font-semibold text-main_white">{email.sender}</p>
              <p className="text-md text-sub_grey">{email.subject}</p>
              <p className="text-sm text-sub_sub_grey">{email.summary}</p>
            </li>
          ))}
        </ul>
        <div className="mt-8"></div>

        <h2 className="text-3xl font-bold mb-6">news</h2>
        <ul className="space-y-2">
          {newsEmails.map((email, index) => (
            <li key={index} className="p-4">
              <p className="text-md font-semibold text-main_white">{email.sender}</p>
              <p className="text-md text-sub_grey">{email.subject}</p>
              <p className="text-sm text-sub_sub_grey">{email.summary}</p>
            </li>
          ))}
        </ul>
      </main>
      <Footer />
    </div>
  );
}