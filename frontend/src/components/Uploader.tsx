import axios from "axios";
import { ChangeEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { MultiStepLoader } from "./ui/multi-step-loader";
// import { FileUpload } from "./ui/file-upload";

const Uploader = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const loadingStates = [
    { text: "Uploading file" },
    { text: "Processing resume" },
    { text: "Extracting data" },
    { text: "Experience" },
    { text: "Education" },
    { text: "Skills" },
    { text: "Projects" },
    { text: "Storing data" },
  ];
  const [name, setName] = useState<string>("");
  const [file, setFile] = useState<File | null>(null);
  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) setFile(event.target.files[0]);
  };

  const fileSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (file) {
      setLoading(true);
      const formData = new FormData();
      formData.append("resume", file);
      formData.append("name", name);
      try {
        const res = await axios.post("http://127.0.0.1:5000/upload", formData);
        const data = await res.data;
        if (data) {
          localStorage.setItem("current_user", name); // 👈 Store the name in localStorage
          navigate("/chat");
        } else {
          console.log("Failed to upload resume.");
        }
        console.log(data);
      } catch (error) {
        console.log(error);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="flex items-center justify-center h-screen max-w-[50%] mx-auto my-2">
      <MultiStepLoader
        loadingStates={loadingStates}
        loading={loading}
        duration={2000}
      />
      <form
        action=""
        encType="multipart/form-data"
        onSubmit={fileSubmit}
        className="flex flex-col border border-white p-4 rounded-xl"
      >
        {/* <FileUpload onChange={()=> handleFileChange}/> */}
        <div className="flex flex-col items-start justify-start">
          <label htmlFor="name" className="px-2">Enter your name</label>
          <input
            type="text"
            name="name"
            placeholder="Enter your name"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="border-2 p-2 rounded-lg my-2"
          />
        </div>
        <input
          type="file"
          name="resume"
          accept="application/pdf"
          className="border-2 cursor-pointer my-2 p-2"
          onChange={handleFileChange}
        />
        {file && (
          <div>
            <p>
              Selected file: {file.name} {file.size} bytes
            </p>
            <button
              className="bg-white px-3 py-2 my-2 text-black rounded-lg cursor-pointer"
              type="submit"
            >
              Upload File
            </button>
          </div>
        )}
      </form>
    </div>
  );
};

export default Uploader;
