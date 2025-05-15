import axios from "axios";
import { ExternalLink } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

type Attendee = {
  user_id: string;
  name: string;
  linkedin?: string;
};

export default function Network() {
  const [attendees, setAttendees] = useState<Attendee[]>([]);
  const [hasUploaded, setHasUploaded] = useState<boolean | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const checkResumeStatus = async () => {
      const currentUser = localStorage.getItem("current_user");
      if (!currentUser) {
        setHasUploaded(false);
        return;
      }

      try {
        const res = await axios.get(
          `${import.meta.env.VITE_BACKEND_URL}/check_resume/${currentUser}`
        );
        setHasUploaded(res.data.uploaded);
      } catch (error) {
        console.error("Error checking resume status", error);
        setHasUploaded(false);
      }
    };

    checkResumeStatus();
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get(`${import.meta.env.VITE_BACKEND_URL}/network`); // Update with full URL if hosted separately

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
    if (hasUploaded) {
        fetchData();
      }
  }, [hasUploaded]);

  if (hasUploaded === false) {
    return (
      <div className="flex flex-col items-center justify-center h-screen">
        <h2 className="text-2xl font-semibold mb-4 text-white">
          Upload your resume to network with like minded people.
        </h2>
        <button
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          onClick={() => navigate("/upload")}
        >
          Upload Resume
        </button>
      </div>
    );
  }

  if (hasUploaded === null) {
    return (
      <div className="flex justify-center items-center h-screen text-white">
        Checking your resume status...
      </div>
    );
  }

  const handleCardClick = (_userId: string) => {
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
            <p className="text-black">No Linkedin found</p>
          )}
        </div>
      ))}
    </div>
  );
}
