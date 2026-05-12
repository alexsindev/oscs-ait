import { useEffect, useState } from 'react';
import { useLogin } from '../hooks/useLogin';

function Projects(props) {
  useLogin();
  const [projects, setProjects] = useState([]);

  useEffect(() => {
  }, []);
    
  const fetchProjects = () => {
    console.log("Fetched")
  }

  return (
    <>
      <br></br>
      <div>This is the Projects {props.name} </div>
      <br></br>
      <button onClick={fetchProjects}>Fetch Projects</button>

      <ul>
        {projects.map((project, index) => (
          <li key={index}>
            {""}
          </li>
        ))}
      </ul>

    </>
  )
}

export default Projects