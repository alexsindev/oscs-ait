import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export const useLogin = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const navigate = useNavigate()

  useEffect(() => {
    const token = localStorage.getItem("token");
    const userData = localStorage.getItem("userData");

    // if no token or user data
    if (!token || !userData) navigate("/login")

    setIsLoggedIn(!token || !userData);
  }, []);
};
