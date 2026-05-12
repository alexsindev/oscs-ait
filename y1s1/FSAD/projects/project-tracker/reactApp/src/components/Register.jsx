import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function Register(props) {
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
        "http://web07.cs.ait.ac.th:7777/users/register",
        options
      );
      const data = await response.json();
      console.log(response.status);

      if (response.status >= 400) {
        throw new Error("registration failed");
      } else {
        navigator("/login");
      }
    } catch (error) {
      console.error(error);
      setError("registration failed" + error.message);
    }
  };

  return (
    <>
      <div>Register page</div>
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
      <button onClick={handleSubmit}> Register </button> |{" "}
      <button onClick={() => navigator("/login")}> Go to login </button>
      <p> {error} </p>
    </>
  );
}

export default Register;
