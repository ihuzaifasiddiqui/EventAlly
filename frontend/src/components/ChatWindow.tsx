import axios from "axios";
import { Send, User } from "lucide-react";
import { useState } from "react"

type Message = {
    sender: "user" | "bot",
    content: string
}
const ChatWindow = () => {
    const [messages, setMessages] = useState<Message[]>([])
    const [userQuery, setUserQuery] = useState<string>("");
    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) =>{
        event.preventDefault();
        const userMessage = userQuery.trim()
        if(!userMessage) return;

        setMessages((prev)=>[...prev, {sender: "user", content: userMessage}])
        setUserQuery("");

        try {
            const currentUser = localStorage.getItem("current_user"); // 👈 Get the current user
            const res = await axios.post("http://127.0.0.1:5000/chat", { message: userQuery, user: currentUser });
            console.log(res);
            const botMessage = res.data.message;
            setMessages((prev) => [...prev, {sender: "bot", content: botMessage}]);
          } catch (error) {
            console.error("Error fetching bot response:", error);
          }
    }
  return (
    <div className='h-screen'>
        <form action="" onSubmit={handleSubmit} className="bg-black text-white items-center  p-3 flex flex-col ">
            <div className="h-[80vh] overflow-auto">
            {messages.map((msg, index)=>(
                <div key={index} className={`${msg.sender === "bot" ? 'text-right' : 'text-right'}`}>
                    <p className={`p-2 my-1 rounded text-black flex ${msg.sender === "bot" ? 'bg-green-200' : 'bg-amber-100'} `}><strong>{msg.sender === "bot" ? `🤖` : <span><User /></span>}</strong>: <span> {msg.content}</span></p>
                </div>
            ))}
            </div>
            <div className="flex items-center justify-between p-3 w-full">
                <input type="text" value={userQuery} onChange={(e)=>setUserQuery(e.target.value)} className="p-2 rounded-2xl  bg-white text-black w-[90%]"/>
                <button type="submit" className="cursor-pointer">Send <Send/></button>
            </div>
        </form>
    </div>
  )
}

export default ChatWindow