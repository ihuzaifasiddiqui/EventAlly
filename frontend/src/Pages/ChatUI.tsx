import React, { useState, useRef, useEffect } from "react";
import { SendHorizonal } from "lucide-react";
import { motion } from "framer-motion";
import axios from "axios";
import { useLocation } from "react-router-dom";

type Message = {
  sender: "user" | "ai";
  content: string;
  isTyping?: boolean;
};

const ChatUI = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: "ai",
      content: "Hello! How can I assist you today?",
      isTyping: false,
    },
  ]);
  const [userInfo, setUserInfo] = useState({email: '', name: ''})
  const location = useLocation()

  useEffect(() => {
    // Extract query params from the URL
    const queryParams = new URLSearchParams(location.search);
    const email = queryParams.get('email');
    const name = queryParams.get('name');

    if (email && name) {
      // Set user information in state
      setUserInfo({ email, name });
    }
  }, [location]);
  
  

  const [input, setInput] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  // New state for typing animation
  const [typingIndex, setTypingIndex] = useState<number | null>(null);
  const [displayText, setDisplayText] = useState<string>("");
  const typingSpeedRef = useRef<number>(100); // Increased from 200 to 300 milliseconds per word

  const sendMessage = async () => {
    const userMessage = input.trim();
    if (!userMessage) return;

    setMessages((prev) => [
      ...prev,
      { sender: "user", content: userMessage, isTyping: true },
    ]);
    setInput("");

    try {
      const currentUser = localStorage.getItem("current_user");
      const res = await axios.post(`${import.meta.env.VITE_BACKEND_URL}/chat`, {
        message: userMessage,
        user: currentUser,
      });
      console.log(res.data);
      

      const botResponse = res.data.message;

      setMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          content: botResponse,
          isTyping: true,
        },
      ]);
      setTypingIndex(messages.length + 1); // Set index of typing message
      setDisplayText("");

      const words = botResponse.split(" ");
      let currentWordIndex = 0;

      const typeNextWord = () => {
        if (currentWordIndex < words.length) {
          setDisplayText(
            (prev) => prev + (prev ? " " : "") + words[currentWordIndex]
          );
          currentWordIndex++;
          setTimeout(typeNextWord, typingSpeedRef.current);
        } else {
          // Typing finished
          setTypingIndex(null);
          setMessages((prev) =>
            prev.map((msg, idx) =>
              idx === prev.length - 1 ? { ...msg, isTyping: false } : msg
            )
          );
        }
      };

      setTimeout(typeNextWord, typingSpeedRef.current);
    } catch (error) {
      console.error("Error fetching bot response:", error);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") sendMessage();
  };

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, displayText]);

  return (
    <div className="w-full min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 text-white flex flex-col items-center justify-center p-4">
      <p className="my-3 text-3xl ">Hey <span className="bg-gradient-to-r from-blue-600 via-green-500 to-indigo-400 text-transparent bg-clip-text">{userInfo.name}
          {/* <TypewriterEffect className="" words={[{text: userInfo.name, className: 'bg-gradient-to-r from-blue-600 via-green-500 to-indigo-400 inline-block text-transparent bg-clip-text'}]} /> */}
      </span> 👋</p>
      <div className="w-full max-w-2xl h-[80vh] bg-gray-800/30 backdrop-blur-md rounded-2xl border border-gray-700 shadow-xl flex flex-col overflow-hidden">
        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-transparent">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex w-full ${
                msg.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className={`max-w-[75%] px-4 py-2 rounded-xl text-sm ${
                  msg.sender === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-700 text-gray-100"
                }`}
              >
                {typingIndex === idx ? displayText : msg.content}
                {typingIndex === idx && (
                  <span className="inline-block ml-1 animate-pulse">▌</span>
                )}
              </motion.div>
            </div>
          ))}
          <div ref={endRef}></div>
        </div>

        {/* Input Bar */}
        <div className="border-t border-gray-700 p-3 bg-gray-900/50 flex items-center gap-2">
          <div className="relative flex-1">
            <input
              type="text"
              placeholder="Type your message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              className="w-full bg-gray-800/50 outline-none text-white placeholder-gray-400 px-4 py-2 rounded-full border border-blue-500/30 text-sm"
            />
          </div>

          <motion.button
            whileTap={{ scale: 0.9 }}
            onClick={sendMessage}
            className="bg-blue-600 hover:bg-blue-700 transition-colors duration-200 text-white p-2 rounded-full flex items-center justify-center"
          >
            <SendHorizonal size={18} />
          </motion.button>
        </div>
      </div>
    </div>
  );
};

export default ChatUI;
