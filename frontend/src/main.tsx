import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Home from "./Pages/Home.tsx";
import Uploader from "./components/Uploader.tsx";
import ChatUI from "./Pages/ChatUI.tsx";
import Network from "./components/Network.tsx";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />}>
          <Route index element={<Home />} />
          <Route path="/network" element={<Network />} />
          <Route path="/upload" element={<Uploader />} />
          <Route path="/chat" element={<ChatUI />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </StrictMode>
);
