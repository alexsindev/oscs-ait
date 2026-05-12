import { useState } from "react";
import { useLogin } from "../hooks/useLogin";

function Homepage(props) {
  useLogin();
  const [projectname, setprojectname] = useState("");

  const handleProjectFetch = async () => {
    try {
      const options = {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      };

      const response = await fetch(
        "http://web07.cs.ait.ac.th:7777/projects/random",
        options
      );
      const data = await response.json();

      setprojectname(data.name);
    } catch (error) {
      console.error(error);
      setError("failed to fetch");
    }
  };

  return (
    <>
      <div>This is the Homepage {props.name} </div>

      <div>
        Random project: {projectname}
        <button onClick={handleProjectFetch}>click me</button>
      </div>
    </>
  );
}

export default Homepage;
