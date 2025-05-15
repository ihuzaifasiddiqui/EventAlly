import axios from "axios";
import { ExternalLink } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

type Attendee = {
  user_id: string;
  name: string;
  summary: string;
  linkedin?: string;
};

export default function Network() {
  const [attendees, setAttendees] = useState<Attendee[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get("http://127.0.0.1:5000/network"); // Update with full URL if hosted separately

        if (res.data.attendees) {
          const updatedAttendees = res.data.attendees.map((attendee: any) => {
            const linkedinUrl = attendee.linkedin?.trim();

            if (linkedinUrl) {
              const parts = linkedinUrl.split("/");
              const username = parts.filter(Boolean).pop(); // Get last non-empty segment
              return {
                ...attendee,
                linkedin: username,
              };
            }

            return {
              ...attendee,
              linkedin: null,
            };
          });

          setAttendees(updatedAttendees);
        }
      } catch (error) {
        console.error("Error fetching network data", error);
      }
    };
    fetchData();
  }, []);

  const handleCardClick = (userId: string) => {
    // Optional: Show detailed profile or resume
  };

  return (
    <div className="p-4 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
      {attendees.map((person, index) => (
        <div
          key={index}
          className="rounded-xl shadow-md p-4 bg-white hover:shadow-lg transition cursor-pointer"
          onClick={() => handleCardClick(person.user_id)}
        >
          <h3 className="text-xl font-extrabold text-black">{person.name}</h3>
          {person.linkedin ? (
            <span className="text-blue-400 flex ">
              <a
                className="mr-2"
                href={`https://www.linkedin.com/in/${person.linkedin}`}
                target="_blank"
              >
                Linkedin
              </a>
              <ExternalLink size={20} />
            </span>
          ) : (
            <p>No Linkedin found</p>
          )}
          {person.summary ? (
            <p className="text-gray-600 mt-2">{person.summary}</p>
          ) : (
            <button
              className="mt-3 px-4 py-2 bg-blue-600 text-white rounded"
              onClick={() => navigate("/upload")}
            >
              Upload Resume
            </button>
          )}
        </div>
      ))}
    </div>
  );
}
