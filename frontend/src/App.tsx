import { useState } from "react";
import "./App.css";
// import { BackgroundLines } from "./components/ui/background-lines";
import { Outlet } from "react-router-dom";

function App() {
  const [data, setData] = useState<any>();

  // useEffect(() => {
  //   const getData = async () => {
  //     try {
  //       const res = await axios.get("http://127.0.0.1:5000/");
  //       setData(res.data);
  //       console.log(res.data);
  //     } catch (error) {
  //       console.error(error);
  //     }
  //   };
  //   getData();
  // }, []);

  return (
    <Outlet/>
    // <ChatUI/>
  );
}

export default App;
