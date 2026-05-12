import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useLogin } from '../hooks/useLogin';

function Contact(props) {
  useLogin();

  return (
    <>
      <div>This is the Contact Page{props.name} </div>
    </>
  )
}

export default Contact