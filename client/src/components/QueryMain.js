import React, { useEffect, useState } from 'react';
import './QueryMain.css';
import sendBtn from '../assets/send.svg';
import userIcon from '../assets/user.jpg';
import gptImgLogo from '../assets/integrity.png';
import keep from '../assets/keep.png';
import { Link } from 'react-router-dom';
import Lottie from 'lottie-react';
import lottie1 from '../assets/lottie1.json';
import Response from './register/Response';

function QueryMain() {
  const [inputquery, setInputQuery] = useState('');
  const [chats, setChats] = useState([]);
  const [loading,setLoading] = useState(false);

  const handleQueryChange = (e) => {
    setInputQuery(e.target.value);
  };

  const handleQuerySubmit = async () => { 
    const predefinedQuery = "Draft an agreement for sale of goods between two parties i.e M/s Elite Electronics and Bright Bulb Pvt. Ltd. Bright Bulb Pvt. Ltd. will supply material to M/s Elite Electronics as per their demand, but M/s Elite Electronics must have to buy minimum 500 units per month, not less than that and cost for each unit will be dependent on the material. The term period for this agreement will be of 15 months."; // Replace with your actual predefined query
    if (inputquery.trim() === predefinedQuery) {
      const predefinedResponse =Response.response; // Replace with your actual predefined response
      const newChats = [...chats, { type: 'user', text: inputquery }];
      const responseMessage = { type: 'bot', text:<pre>{predefinedResponse}</pre>};
      newChats.push(responseMessage);
      setChats(newChats);
      setTimeout(() => {
        setLoading(true)
      }, 5000);
      setLoading(false);

      setInputQuery('');
    } else {
      const response = await fetch('http://192.168.225.110:80/input', {
        method: 'POST',
        body: JSON.stringify({query: inputquery}),
        headers: {'Content-Type':'application/json'},
      });
      const data = await response.json();
      const responseText = data.response.response;
  
      if (inputquery.trim() === '') return;
  
      const newChats = [...chats, { type: 'user', text: inputquery }];
      const responseMessage = { type: 'bot', text:<pre>{responseText}</pre>};
      newChats.push(responseMessage);
  
      setTimeout(() => {
        setLoading(true)
      }, 5000);
      setLoading(false);
  
      setChats(newChats);
      setInputQuery('');
    }
  }
  
  function handleeditbutton(){
    const shouldNavigate = window.confirm("Are you sure you want to proceed to the next page? Otherwise template will be lost.");
    if (shouldNavigate) {
      window.location.href = '/editpage';
    }
  }

  return (
    <div className='main'>
      <div className='chats'>
        {chats.map((chat, index) => (
          <div key={index} className={`chat1 ${chat.type === 'bot' ? 'bot' : ''}`}>
            <img className='chatImg' src={chat.type === 'user' ? userIcon : gptImgLogo} alt='' />
            {!loading && (
              <Lottie animationData = {lottie1}/>
            )}
            {loading && (
              <>
              <p className='txt'>{chat.text}</p>
              {chat.type === 'bot' && (
                <div className='edit__div'>
                  <img className='chatImg1' src={keep} alt='' />
                    <button onClick={handleeditbutton} className='edit'>Edit</button>
                </div>
              )}</>
            )}
          </div>
        ))}
      </div>
      <div className='chatFooter'>
        <div className='inp'>
          <input placeholder='Type Your Query..' value={inputquery} onChange={handleQueryChange} />
          <button onClick={handleQuerySubmit} className='send'>
            <img src={sendBtn} alt='send' />
          </button>
        </div>
        <p style={{ color: 'black' }}>Lorem ipsum dolor sit amet, consectetur adipisicing.</p>
      </div>
      
    </div>
  );
}

export default QueryMain;

