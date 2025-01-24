import React, { useState } from 'react';
import { Input, Button, Typography, Space, message } from 'antd';
import 'antd/dist/antd.css';  // Import Ant Design styles

const { TextArea } = Input;
const { Title } = Typography;

const ChatApp = () => {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');

  const handleSendMessage = async () => {
    if (!userInput) {
      message.error('Please enter a message');
      return;
    }

    // Add user message
    setMessages([...messages, { sender: 'user', text: userInput }]);
    
    // Simulate bot response (replace this with your API call logic)
    setMessages(prevMessages => [
      ...prevMessages,
      { sender: 'user', text: userInput },
      { sender: 'bot', text: 'Hello! How can I assist you today?' }
    ]);

    setUserInput('');  // Clear the input field
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100vh', padding: '20px' }}>
      <div style={{ width: '100%', maxWidth: '600px', height: '80%', display: 'flex', flexDirection: 'column', border: '1px solid #ccc', borderRadius: '8px', overflow: 'hidden' }}>
        <div style={{ flex: 1, padding: '10px', overflowY: 'auto', borderBottom: '1px solid #ccc', maxHeight: '70%' }}>
          {messages.map((msg, idx) => (
            <div key={idx} style={{ textAlign: msg.sender === 'user' ? 'right' : 'left', marginBottom: '10px' }}>
              <Typography.Paragraph
                style={{
                  display: 'inline-block',
                  padding: '10px',
                  borderRadius: '10px',
                  maxWidth: '70%',
                  backgroundColor: msg.sender === 'user' ? '#007bff' : '#f1f1f1',
                  color: msg.sender === 'user' ? 'white' : 'black',
                }}
              >
                {msg.text}
              </Typography.Paragraph>
            </div>
          ))}
        </div>
        <div style={{ display: 'flex', padding: '10px', gap: '10px', backgroundColor: '#f4f4f9' }}>
          <TextArea
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            rows={1}
            placeholder="Type your message..."
            style={{ flex: 1 }}
          />
          <Button type="primary" onClick={handleSendMessage}>
            Send
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ChatApp;
