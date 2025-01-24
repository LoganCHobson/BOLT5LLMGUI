import React, { useState, useEffect } from 'react';
import { Layout, Button, Input, Space, List } from 'antd';
import axios from 'axios';
import './App.css';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { dracula } from 'react-syntax-highlighter/dist/esm/styles/prism';

const { Sider, Content } = Layout;

function App() {
    const [conversations, setConversations] = useState([]);
    const [conversationHistory, setConversationHistory] = useState([]);
    const [prompt, setPrompt] = useState('');
    const [currentConversation, setCurrentConversation] = useState('new_conversation');
    const [selectedConversation, setSelectedConversation] = useState(null); 
    const [isThinking, setIsThinking] = useState(false);

    useEffect(() => {
        axios.get('http://localhost:5000/api/conversations')
            .then(response => setConversations(response.data.conversations));
    }, []);

    const handleConversationSelect = (conversationId) => {
        setCurrentConversation(conversationId);
        setSelectedConversation(conversationId); 
        axios.get(`http://localhost:5000/api/conversation/${conversationId}`)
            .then(response => setConversationHistory(response.data.conversation));
    };

    const handleSendPrompt = () => {
        if (prompt.trim()) {
            setConversationHistory([...conversationHistory, { role: 'user', content: prompt }]);
            setConversationHistory(prevHistory => [
                ...prevHistory,
                { role: 'assistant', content: 'Thinking...' }
            ]);
            setPrompt('');
            setIsThinking(true);

            axios.post('http://localhost:5000/api/generate', { prompt, conversation_id: currentConversation })
                .then(response => {
                    setConversationHistory(prevHistory => [
                        ...prevHistory.slice(0, prevHistory.length - 1),
                        { role: 'assistant', content: response.data.response }
                    ]);
                    setIsThinking(false);
                })
                .catch(error => {
                    console.error("Error sending prompt:", error);
                    setIsThinking(false);
                });
        }
    };

    const handleNewConversation = () => {
        const newConversationId = `new_conversation_${Date.now()}`;
        setCurrentConversation(newConversationId);
        setSelectedConversation(newConversationId); 
        setConversationHistory([]);
        setConversations([...conversations, newConversationId]);

        axios.post('http://localhost:5000/api/generate', { prompt: 'Start a new conversation', conversation_id: newConversationId })
            .then(response => {
                setConversationHistory([{ role: 'assistant', content: response.data.response }]);
            });
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            handleSendPrompt();
        }
    };

    return (
        <Layout style={{ minHeight: '100vh' }}>
            <Sider width={200} style={{ backgroundColor: '#f0f2f5' }}>
                <Button type="primary" block onClick={handleNewConversation}>New Conversation</Button>
                <List
                    style={{ marginTop: 20 }}
                    bordered
                    dataSource={conversations}
                    renderItem={item => (
                        <List.Item style={{ padding: '5px' }}>
                            <Button
                                onClick={() => handleConversationSelect(item)}
                                style={{
                                    width: '100%',
                                    textOverflow: 'ellipsis',
                                    whiteSpace: 'nowrap',
                                    overflow: 'hidden',
                                    backgroundColor: selectedConversation === item ? '#bae7ff' : 'white',
                                    borderColor: selectedConversation === item ? '#1890ff' : '#d9d9d9',
                                }}
                            >
                                {item}
                            </Button>
                        </List.Item>
                    )}
                />
            </Sider>
            <Layout style={{ padding: '0 24px 24px' }}>
                <Content
                    style={{
                        padding: 24,
                        margin: 0,
                        minHeight: 280,
                        background: '#fff',
                    }}
                >
                    <div className="content-wrapper">
                        <div className="messages-container">
                            {conversationHistory.map((message, index) => (
                                <div
                                    key={index}
                                    className={`message ${message.role}`}
                                    style={{
                                        textAlign: message.role === 'user' ? 'right' : 'left',
                                        backgroundColor: message.role === 'user' ? '#d1f7d6' : '#f0f0f0',
                                    }}
                                >
                                    <ReactMarkdown children={message.content} remarkPlugins={[remarkGfm]} />
                                </div>
                            ))}
                        </div>
                        <div className="input-container">
                            <Space direction="vertical" style={{ width: '100%' }}>
                                <Input.TextArea
                                    value={prompt}
                                    onChange={e => setPrompt(e.target.value)}
                                    rows={3}
                                    placeholder="Type your message..."
                                    onKeyDown={handleKeyDown}
                                />
                                <Button type="primary" onClick={handleSendPrompt}>Send</Button>
                            </Space>
                        </div>
                    </div>
                </Content>
            </Layout>
        </Layout>
    );
}

export default App;
