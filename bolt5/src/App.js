import React, { useState } from 'react';
import { Layout, Input, Button, Typography, Spin, message } from 'antd';
import { SendOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Header, Content } = Layout;
const { Text } = Typography;

const ChatApp = () => {
    const [messages, setMessages] = useState([]);
    const [userInput, setUserInput] = useState('');
    const [loading, setLoading] = useState(false);

    const sendPrompt = async () => {
        if (!userInput.trim()) {
            message.error('Please type a message');
            return;
        }

        // Add user's message to chat
        const newMessages = [...messages, { role: 'user', content: userInput }];
        setMessages(newMessages);
        setUserInput('');
        setLoading(true);

        try {
            // Send request to the backend
            const response = await axios.post('http://localhost:5000/api/generate', {
                prompt: userInput
            });

            // Add assistant's response to chat
            const assistantMessage = response.data.response;
            setMessages([
                ...newMessages,
                { role: 'assistant', content: assistantMessage }
            ]);
        } catch (error) {
            console.error('Error sending prompt:', error);
            message.error('Error sending prompt, please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e) => {
        setUserInput(e.target.value);
    };

    return (
        <Layout style={{ height: '100vh' }}>
            <Header style={{ backgroundColor: '#007bff', color: 'white', textAlign: 'center' }}>
                <h1>Ollama Chat</h1>
            </Header>
            <Content style={{ padding: '20px' }}>
                <div style={{ maxWidth: '600px', margin: '0 auto', backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)' }}>
                    <div style={{ maxHeight: '400px', overflowY: 'auto', marginBottom: '10px' }}>
                        {messages.map((msg, index) => (
                            <div key={index} style={{ textAlign: msg.role === 'user' ? 'right' : 'left', marginBottom: '10px' }}>
                                <Text
                                    style={{
                                        display: 'inline-block',
                                        padding: '10px',
                                        borderRadius: '10px',
                                        maxWidth: '70%',
                                        wordWrap: 'break-word',
                                        backgroundColor: msg.role === 'user' ? '#007bff' : '#f1f1f1',
                                        color: msg.role === 'user' ? 'white' : 'black'
                                    }}
                                >
                                    {msg.content}
                                </Text>
                            </div>
                        ))}
                    </div>
                    <Input.TextArea
                        id="promptInput"
                        rows={1}
                        placeholder="Type your message..."
                        value={userInput}
                        onChange={handleInputChange}
                        onPressEnter={sendPrompt}
                        style={{ marginBottom: '10px' }}
                    />
                    <Button
                        id="sendButton"
                        type="primary"
                        icon={<SendOutlined />}
                        onClick={sendPrompt}
                        loading={loading}
                        block
                    >
                        Send
                    </Button>
                </div>
            </Content>
        </Layout>
    );
};

export default ChatApp;
