"use client";

import { useEffect, useState } from 'react';
import Footer from '../components/Footer';

interface Email {
  subject: string;
  sender: string;
}

interface AttendeeEmail {
  attendee: string;
  summary: string;
}

interface CalendarEvent {
  event: string;
  start: string;
  end: string;
  attendee_summaries: AttendeeEmail[];
}

export default function Home() {
  const [usefulEmails, setUsefulEmails] = useState<Email[]>([]);
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

        setUsefulEmails(emailsData.useful_emails);
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
    <div className="bg-dark_navy flex flex-col min-h-screen text-white">
      <main className="flex-grow container mx-auto px-4 py-8">
        <div className="bg-grey_navy p-6 mb-8 rounded-lg shadow-lg flex justify-center items-center">
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
        <h2 className="text-3xl font-bold mb-6">Calendar Events</h2>
        <ul className="space-y-4 mb-8">
          {calendarEvents.map((event, index) => (
            <li key={index} className="p-4 border border-white rounded-lg">
              <p className="font-semibold">{event.event}</p>
              {event.attendee_summaries.length > 0 && (
                <div>
                  <p className="font-semibold mt-2">Attendee Summaries:</p>
                  <ul className="list-disc list-inside">
                    {event.attendee_summaries.map((summary, idx) => (
                      <li key={idx} className="ml-4">
                        <span className="font-medium">{summary.attendee}:</span> {summary.summary}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </li>
          ))}
        </ul>
        <h2 className="text-3xl font-bold mb-6">Emails</h2>
        <ul className="space-y-4">
          {usefulEmails.map((email, index) => (
            <li key={index} className="p-4 border border-white rounded-lg">
              <p className="font-semibold">{email.subject}</p>
              <p className="text-sm text-gray-300">From: {email.sender}</p>
            </li>
          ))}
        </ul>
      </main>
      <Footer />
    </div>
  );
}