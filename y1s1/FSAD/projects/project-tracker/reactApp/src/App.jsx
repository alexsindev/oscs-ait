import { Route, Routes, useNavigate } from "react-router-dom";
import "./App.css";
import Contact from "./components/Contact";
import Homepage from "./components/Homepage";
import Login from "./components/Login";
import { NavBar } from "./components/Nav";
import Projects from "./components/Projects";
import Realtime from "./components/Realtime";
import Register from "./components/Register";
import { useLogin } from "./hooks/useLogin";

function App() {
  useLogin();
  return (
    <>
      <NavBar />
      <Routes>
        <Route path="/" element={<Homepage />} />
        <Route path="/chat" element={<Realtime />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="*" element={<p>Page not found.</p>} />
      </Routes>
    </>
  );
}

export default App;
