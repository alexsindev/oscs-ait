import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export const NavBar = () => {
  const navigator = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token") ?? null;
    const userData = localStorage.getItem("userData") ?? null;

    if (!token || !userData) setIsLoggedIn(false)
    setIsLoggedIn(true)
  }, [])

  console.log(isLoggedIn)

  return (
    <nav>
      <Link to="/projects">Projects</Link>|<Link to="/chat">Chat</Link>|
      <Link to="/contact">Contact</Link>
      {isLoggedIn && <button onClick={() => {
        localStorage.removeItem("token")
        localStorage.removeItem("userData")
        navigator("/login")
      }}>Logout</button>}
    </nav>
  );
};
