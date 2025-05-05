import { useEffect, useState } from "react";
import "./App.css";
import axios from "axios";
import Header from "./components/Header";
import { Outlet } from "react-router-dom";
import Footer from "./components/Footer";
import { BackgroundLines } from "./components/ui/background-lines";

function App() {
  const [data, setData] = useState<any>();

  useEffect(() => {
    const getData = async () => {
      try {
        const res = await axios.get("http://127.0.0.1:5000/");
        setData(res.data);
        console.log(res.data);
      } catch (error) {
        console.error(error);
      }
    };
    getData();
  }, []);

  return (
    <BackgroundLines className="bg-black text-white">
      <Header />
      <Outlet />
      <Footer />
    </BackgroundLines>
  );
}

export default App;
