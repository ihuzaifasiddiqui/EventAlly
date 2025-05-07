import axios from "axios";
import { ChangeEvent, useState } from "react";
// import { FileUpload } from "./ui/file-upload";

const Uploader = () => {
  const [file, setFile] = useState<File | null>(null);
  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) setFile(event.target.files[0]);
  };
  
  const fileSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if(file){
      const formData = new FormData();
      formData.append('resume', file);
      try {
        const res = await axios.post("http://127.0.0.1:5000/upload", formData)
        const data = await res.data;
        console.log(data);
      } catch (error) {
          console.log(error);
      }
    }
  };

  return (
    <div className="flex items-center justify-center h-screen max-w-[50%] mx-auto my-2">
      <form action="" encType="multipart/form-data" onSubmit={fileSubmit}>
        {/* <FileUpload onChange={()=> handleFileChange}/> */}
        <input type="file" name="resume" accept="application/pdf" className="border-2 border-red-500 cursor-pointer" onChange={handleFileChange}/>
        {file && (
          <div>
            <p>
              Selected file: {file.name} {file.size} bytes
            </p>
            <button className="bg-black p-3 text-white rounded-xl cursor-pointer" type="submit">Upload File</button>
          </div>
        )}
      </form>
    </div>
  );
};

export default Uploader;
