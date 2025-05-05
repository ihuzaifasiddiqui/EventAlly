import { FileUpload } from "./ui/file-upload"


const Uploader = () => {
  return (
    <div className="flex items-center justify-center h-screen max-w-[50%] mx-auto my-2">
      <FileUpload onChange={()=> console.log("file")}/>
    </div>
  )
}

export default Uploader