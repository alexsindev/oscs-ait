import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function Login(props) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const navigator = useNavigate();

  const handleSubmit = async () => {
    if (!email || !password) {
      setError("empty credentials!");
      return;
    }

    try {
      const options = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      };

      const response = await fetch(
        "http://web07.cs.ait.ac.th:7777/users/login",
        options
      );
      const data = await response.json();

      if (response.status >= 400) {
        throw new Error("login failed");
      } else {
        const token = data.token;
        const user = data.user;

        localStorage.setItem("token", token);
        localStorage.setItem("userData", JSON.stringify(user));

        navigator("/");
      }
    } catch (error) {
      console.error(error);
      setError("login failed" + error.message);
    }
  };

  return (
    <>
      <div>Login page</div>
      <p>Enter your email</p>
      <input
        name="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <p>Enter your password</p>
      <input
        type="password"
        name="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <br />
      <br />
      <button onClick={handleSubmit}> Login </button> |
      <button onClick={() => navigator("/register")}> go to Register </button>
      <p> {error} </p>
    </>
  );
}

export default Login;
