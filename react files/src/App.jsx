import React, { useState, useEffect, useRef, Suspense } from 'react';
import { initializeApp } from "firebase/app";
import { 
    getAuth, 
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    signOut,
    onAuthStateChanged
} from "firebase/auth";
import { Canvas, useFrame } from '@react-three/fiber';
import { Icosahedron } from '@react-three/drei';


// --- Your Firebase Configuration ---
const firebaseConfig = {
    apiKey: "AIzaSyDFD-6vA02RUqob5JjAUCOOj1dS0mBhin0",
    authDomain: "elysium-ai-2l31ae.firebaseapp.com",
    projectId: "elysium-ai-231ae",
    storageBucket: "elysium-ai-231ae.appspot.com",
    messagingSenderId: "24605739977",
    appId: "1:24605739977:web:a052f5403429c0fbf3f618",
    measurementId: "G-W0RN47546R"
};

// --- Initialize Firebase ---
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);


// --- Main App Component ---
export default function App() {
    const [user, setUser] = useState(null);
    const [isSidebarOpen, setSidebarOpen] = useState(false);
    const [isAuthModalOpen, setAuthModalOpen] = useState(false);
    const [authMode, setAuthMode] = useState('login'); // 'login' or 'signup'
    const [showSuccessPopup, setShowSuccessPopup] = useState(false);
    const [successMessage, setSuccessMessage] = useState('');
    const [messages, setMessages] = useState([]);

    // --- Firebase Auth Listener ---
    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
            setUser(currentUser);
        });
        return () => unsubscribe(); // Cleanup on unmount
    }, []);
    
    // --- Handlers ---
    const handleSendMessage = (text) => {
        setMessages(prev => [...prev, { sender: 'user', text }]);
        // Simulate AI response
        setTimeout(() => {
            setMessages(prev => [...prev, { sender: 'ai', text: "This is a simulated AI response in React!" }]);
        }, 1000);
    };

    const handleLogin = (email, password) => {
        return signInWithEmailAndPassword(auth, email, password)
            .then(() => {
                setAuthModalOpen(false);
                setSuccessMessage('Successfully logged in!');
                setShowSuccessPopup(true);
            });
    };

    const handleSignup = (email, password) => {
        return createUserWithEmailAndPassword(auth, email, password)
            .then(() => {
                setAuthModalOpen(false);
                setSuccessMessage('Account created successfully!');
                setShowSuccessPopup(true);
            });
    };

    const handleLogout = () => {
        signOut(auth);
    };
    
    const openAuthModal = (mode) => {
        setAuthMode(mode);
        setAuthModalOpen(true);
    };

    return (
        <>
            <SuccessPopup message={successMessage} show={showSuccessPopup} setShow={setShowSuccessPopup} />
            <div className="main-container">
                <div className="gradient-glow"></div>
                <div className="content-wrapper">
                    <Sidebar isOpen={isSidebarOpen} />
                    <div className="chat-layout">
                        <Header 
                            user={user} 
                            onMenuClick={() => setSidebarOpen(!isSidebarOpen)}
                            onLoginClick={() => openAuthModal('login')}
                            onSignupClick={() => openAuthModal('signup')}
                            onLogoutClick={handleLogout}
                        />
                        <ChatArea messages={messages} />
                        <ChatInput onSendMessage={handleSendMessage} />
                    </div>
                </div>
            </div>
            {isAuthModalOpen && (
                <AuthModal 
                    mode={authMode}
                    setMode={setAuthMode}
                    onClose={() => setAuthModalOpen(false)}
                    onLogin={handleLogin}
                    onSignup={handleSignup}
                />
            )}
        </>
    );
}

// --- 3D Animation Component ---
const WelcomeAnimation = () => {
    const meshRef = useRef();

    useFrame((state, delta) => {
        if (meshRef.current) {
            meshRef.current.rotation.x += delta * 0.5; // Increased speed
            meshRef.current.rotation.y += delta * 0.5; // Increased speed
        }
    });

    return (
        <mesh ref={meshRef}>
            <Icosahedron args={[3, 0]}> {/* Increased size */}
                <meshStandardMaterial color="#FFFFFF" wireframe /> {/* Changed color to white */}
            </Icosahedron>
        </mesh>
    );
};


// --- UI Components ---

const Sidebar = ({ isOpen }) => (
    <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
        <button className="sidebar-button">
            <span>New Chat</span>
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 5l0 14"/><path d="M5 12l14 0"/></svg>
        </button>
        <div className="sidebar-content">
            <p className="sidebar-heading">Recent</p>
            <nav className="sidebar-nav">
                <a href="#">Frontend design similar to Gemini...</a>
                <a href="#">Explain quantum computing...</a>
                <a href="#">Recipe for a vegan chocolate cake</a>
            </nav>
        </div>
    </aside>
);

const Header = ({ user, onMenuClick, onLoginClick, onSignupClick, onLogoutClick }) => (
    <header className="header">
        <button onClick={onMenuClick} className="menu-button">
            <svg xmlns="http://www.w3.org/2000/svg" height="24" width="24" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16m-7 6h7" /></svg>
        </button>
        <h1 className="header-title">Elysium AI</h1>
        <div className="header-auth">
            {user ? (
                <div className="logged-in-view">
                    <div className="user-avatar">{user.email.charAt(0).toUpperCase()}</div>
                    <button onClick={onLogoutClick} className="auth-button secondary">Logout</button>
                </div>
            ) : (
                <div className="logged-out-view">
                    <button onClick={onLoginClick} className="auth-button secondary">Login</button>
                    <button onClick={onSignupClick} className="auth-button primary">Sign Up</button>
                </div>
            )}
        </div>
    </header>
);

const ChatArea = ({ messages }) => {
    const chatEndRef = useRef(null);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    return (
        <main className="chat-container">
            <div className="chat-messages">
                {messages.length === 0 ? (
                    <div className="welcome-message">
                        <h2>Hello, how can I help you today?</h2>
                        <div className="welcome-animation-container">
                            <Canvas>
                                <ambientLight intensity={0.5} />
                                <pointLight position={[10, 10, 10]} />
                                <Suspense fallback={null}>
                                    <WelcomeAnimation />
                                </Suspense>
                            </Canvas>
                        </div>
                    </div>
                ) : (
                    messages.map((msg, index) => (
                        <div key={index} className="message-wrapper">
                            <div className={`avatar ${msg.sender === 'ai' ? 'ai' : 'user'}`}></div>
                            <div>
                                <p className="sender-name">{msg.sender === 'ai' ? 'Gemini' : 'You'}</p>
                                <p className="message-text">{msg.text}</p>
                            </div>
                        </div>
                    ))
                )}
                <div ref={chatEndRef} />
            </div>
        </main>
    );
};

const ChatInput = ({ onSendMessage }) => {
    const [input, setInput] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (input.trim()) {
            onSendMessage(input.trim());
            setInput('');
        }
    };

    return (
        <footer className="chat-footer">
            <form className="input-form" onSubmit={handleSubmit}>
                <input 
                    type="text" 
                    placeholder="Message Gemini..." 
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                />
                <button type="submit">
                    <svg xmlns="http://www.w3.org/2000/svg" height="20" width="20" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                    </svg>
                </button>
            </form>
            <p className="footer-disclaimer">
                Gemini may display inaccurate info, so double-check its responses.
            </p>
        </footer>
    );
};

const AuthModal = ({ mode, setMode, onClose, onLogin, onSignup }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    
    const handleSubmit = (e) => {
        e.preventDefault();
        setError('');

        if (mode === 'signup' && password !== confirmPassword) {
            setError('Passwords do not match.');
            return;
        }

        const authAction = mode === 'login' ? onLogin(email, password) : onSignup(email, password);
        
        authAction.catch(err => {
            setError(err.message);
        });
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={e => e.stopPropagation()}>
                <button onClick={onClose} className="close-modal-btn">
                    <svg xmlns="http://www.w3.org/2000/svg" height="24" width="24" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" /></svg>
                </button>
                
                <h2 className="modal-title">{mode === 'login' ? 'Welcome Back' : 'Create Account'}</h2>
                {error && <div className="auth-alert">{error}</div>}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="email">Email</label>
                        <input type="email" id="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" required />
                    </div>
                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input type="password" id="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" required />
                    </div>
                    {mode === 'signup' && (
                         <div className="form-group">
                            <label htmlFor="confirm-password">Confirm Password</label>
                            <input type="password" id="confirm-password" value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} placeholder="••••••••" required />
                        </div>
                    )}
                    <button type="submit" className="form-submit-btn">{mode === 'login' ? 'Login' : 'Create Account'}</button>
                </form>

                <p className="form-switcher">
                    {mode === 'login' ? "Don't have an account? " : "Already have an account? "}
                    <a href="#" onClick={(e) => { e.preventDefault(); setMode(mode === 'login' ? 'signup' : 'login'); setError(''); }}>
                        {mode === 'login' ? 'Sign Up' : 'Login'}
                    </a>
                </p>
            </div>
        </div>
    );
};

const SuccessPopup = ({ message, show, setShow }) => {
    useEffect(() => {
        if (show) {
            const timer = setTimeout(() => {
                setShow(false);
            }, 2500);
            return () => clearTimeout(timer);
        }
    }, [show, setShow]);

    return (
        <div className={`success-popup ${show ? 'show' : ''}`}>
            <svg xmlns="http://www.w3.org/2000/svg" height="24" width="24" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{message}</span>
        </div>
    );
};
