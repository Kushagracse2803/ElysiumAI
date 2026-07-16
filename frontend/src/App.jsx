import React, { useState, useEffect, useRef, Suspense } from "react";
import { initializeApp } from "firebase/app";
import {
  getAuth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
} from "firebase/auth";
import { Canvas, useFrame } from "@react-three/fiber";
import { Icosahedron } from "@react-three/drei";
import { motion } from "framer-motion";

// --- Firebase Config ---
const firebaseConfig = {
  apiKey: "AIzaSyDFD-6vA02RUqob5JjAUCOOj1dS0mBhin0",
  authDomain: "elysium-ai-2l31ae.firebaseapp.com",
  projectId: "elysium-ai-231ae",
  storageBucket: "elysium-ai-231ae.appspot.com",
  messagingSenderId: "24605739977",
  appId: "1:24605739977:web:a052f5403429c0fbf3f618",
  measurementId: "G-W0RN47546R",
};

// --- Initialize Firebase ---
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// --- Main App Component ---
export default function App() {
  const [user, setUser] = useState(null);
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [selectedModel, setSelectedModel] = useState("groq");
  const [recentChats, setRecentChats] = useState([]); 

  // 🔴 MISSING STATES JO AB ADD KAR DI HAIN:
  const [isAuthModalOpen, setAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState("login");
  const [showSuccessPopup, setShowSuccessPopup] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");

  // ... baaki logic (useEffect, handleNewChat, etc.) wahi rahega
  // Load chats from LocalStorage on mount
  useEffect(() => {
    const saved = JSON.parse(localStorage.getItem("recent_chats") || "[]");
    setRecentChats(saved);
  }, []);

  // Firebase listener
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
    });
    return () => unsubscribe();
  }, []);
  
  // 💾 3. New Chat Function: Save current then clear
 // Screen clear karne aur save karne ke liye
  const handleNewChat = () => {
    if (messages.length > 0) {
      const firstUserMsg = messages.find(m => m.sender === "user")?.text || "New Chat";
      const title = firstUserMsg.substring(0, 25) + "...";
      
      const newSavedChat = { id: Date.now(), title, messages };
      const updatedRecent = [newSavedChat, ...recentChats].slice(0, 10);
      
      setRecentChats(updatedRecent);
      localStorage.setItem("recent_chats", JSON.stringify(updatedRecent));
    }
    setMessages([]); // Screen clear
  };

  // Purani chat wapas lane ke liye
  const loadChat = (chatMessages) => {
    setMessages(chatMessages);
    setSidebarOpen(false); // Sidebar band kar dein
  };
  // --- Handle Chat Send ---
const handleSendMessage = async (text, formData = null) => {
  // 1. User ka message turant screen par dikhao
  const userMsg = { sender: "user", text: text };
  setMessages((prev) => [...prev, userMsg]);

  try {
    // 2. Agar formData nahi hai (normal chat), toh naya bana lo
    const dataToSend = formData || new FormData();
    if (!formData) dataToSend.append("text", text);
    
    // Default model bhi bhej dete hain
    dataToSend.append("model", selectedModel);

    const response = await fetch("http://localhost:8000/send_message", {
      method: "POST",
      body: dataToSend, // Fetch automatically Content-Type set kar dega multipart ke liye
    });

    const data = await response.json();
    
    setMessages((prev) => [...prev, {
      sender: "ai",
      text: data.text,
      model: data.model || "ELYSIUM"
    }]);
  } catch (error) {
    console.error("Error:", error);
    setMessages((prev) => [...prev, { sender: "ai", text: "⚠️ Server connectivity issue." }]);
  }
};

  // --- Handle Service Button Click ---
  const handlePromptClick = (prompt) => {
    handleSendMessage(prompt);
  };

  // --- Auth Handlers ---
  const handleLogin = (email, password) => {
    return signInWithEmailAndPassword(auth, email, password).then(() => {
      setAuthModalOpen(false);
      setSuccessMessage("Successfully logged in!");
      setShowSuccessPopup(true);
    });
  };

  const handleSignup = (email, password) => {
    return createUserWithEmailAndPassword(auth, email, password).then(() => {
      setAuthModalOpen(false);
      setSuccessMessage("Account created successfully!");
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
      <SuccessPopup
        message={successMessage}
        show={showSuccessPopup}
        setShow={setShowSuccessPopup}
      />
      <div className="main-container">
        <div className="gradient-glow"></div>
        <div className="content-wrapper">
          
          {/* ✅ UPDATE: Yahan props pass karne hain */}
          <Sidebar 
            isOpen={isSidebarOpen} 
            onNewChat={handleNewChat} 
            recentChats={recentChats} 
            onChatClick={loadChat} 
          />

          <div className="chat-layout">
            <Header
              user={user}
              onMenuClick={() => setSidebarOpen(!isSidebarOpen)}
              onLoginClick={() => openAuthModal("login")}
              onSignupClick={() => openAuthModal("signup")}
              onLogoutClick={handleLogout}
              selectedModel={selectedModel}
              setSelectedModel={setSelectedModel}
            />
            <ChatArea messages={messages} onPromptClick={handlePromptClick} />
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

const Sidebar = ({ isOpen, onNewChat, recentChats, onChatClick }) => (
  <aside className={`sidebar ${isOpen ? "open" : ""}`}>
    <button className="sidebar-button" onClick={onNewChat}>
      <span>New Chat</span>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="20" height="20" viewBox="0 0 24 24"
        fill="none" stroke="currentColor" strokeWidth="2"
        strokeLinecap="round" strokeLinejoin="round"
      >
        <path d="M12 5l0 14" />
        <path d="M5 12l14 0" />
      </svg>
    </button>
    <div className="sidebar-content">
      <p className="sidebar-heading">Recent</p>
      <nav className="sidebar-nav">
        {recentChats.length === 0 ? (
          <p style={{ color: "#888", fontSize: "12px", padding: "10px" }}>No recent chats</p>
        ) : (
          recentChats.map((chat) => (
            <a 
              key={chat.id} 
              href="#" 
              onClick={(e) => { 
                e.preventDefault(); 
                onChatClick(chat.messages); 
              }}
              className="recent-chat-link"
            >
              {chat.title}
            </a>
          ))
        )}
      </nav>
    </div>
  </aside>
);
// --- 3D Animation ---
const WelcomeAnimation = () => {
  const meshRef = useRef();
  useFrame((_, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.x += delta * 0.5;
      meshRef.current.rotation.y += delta * 0.5;
    }
  });
  return (
    <mesh ref={meshRef}>
      <Icosahedron args={[3, 0]}>
        <meshStandardMaterial color="#FFFFFF" wireframe />
      </Icosahedron>
    </mesh>
  );
};

// --- 🌈 BEAUTIFUL SERVICE BUTTONS ---
const ServiceButtons = ({ onPromptClick }) => {
  const services = [
    {
      title: "🧠 Text Summarization",
      desc: "Summarize large text in seconds.",
      prompt: "Summarize the following text for me: ",
      gradient: "from-violet-500 via-purple-600 to-indigo-500",
    },
    {
      title: "🎬 Text → Video",
      desc: "Turn any text into a video idea.",
      prompt: "Create a short video script based on this idea: ",
      gradient: "from-pink-500 via-rose-500 to-red-500",
    },
    {
      title: "📄 Resume Analyzer",
      desc: "Get smart insights on your resume.",
      prompt: "Please analyze my resume and provide feedback: ",
      gradient: "from-green-400 via-emerald-500 to-teal-500",
    },
    {
      title: "🧩 MCQ Generator",
      desc: "Generate practice questions instantly.",
      prompt: "Generate multiple-choice questions from this topic: ",
      gradient: "from-yellow-400 via-orange-400 to-amber-500",
    },
  ];

  return (
    <div className="service-buttons-grid px-6 py-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      {services.map((service, i) => (
        <motion.div
          key={service.title}
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1 }}
          whileHover={{ scale: 1.08, y: -6 }}
          whileTap={{ scale: 0.96 }}
          onClick={() => onPromptClick(service.prompt)}
          className={`relative p-5 rounded-2xl cursor-pointer bg-gradient-to-br ${service.gradient} shadow-xl hover:shadow-2xl transition-all duration-300`}
        >
          <div className="absolute inset-0 bg-white/10 backdrop-blur-lg rounded-2xl"></div>
          <div className="relative z-10 text-center text-white">
            <h3 className="text-lg font-bold mb-1 drop-shadow-lg">
              {service.title}
            </h3>
            <p className="text-sm opacity-90">{service.desc}</p>
          </div>
          <div className="absolute inset-0 rounded-2xl border border-white/20 hover:border-white/50 transition-all"></div>
        </motion.div>
      ))}
    </div>
  );
};

// --- Sidebar ---


// --- Header ---
const Header = ({
  user,
  onMenuClick,
  onLoginClick,
  onSignupClick,
  onLogoutClick,
  selectedModel,
  setSelectedModel,
}) => (
  <header className="header">
    <button onClick={onMenuClick} className="menu-button">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        height="24"
        width="24"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          d="M4 6h16M4 12h16m-7 6h7"
        />
      </svg>
    </button>

    <h1 className="header-title">Elysium AI</h1>

    <div
      className="header-auth"
      style={{ display: "flex", flexDirection: "column", alignItems: "flex-end" }}
    >
      {user ? (
        <div className="logged-in-view">
          <div className="user-avatar">{user.email.charAt(0).toUpperCase()}</div>
          <button onClick={onLogoutClick} className="auth-button secondary">
            Logout
          </button>
        </div>
      ) : (
        <div className="logged-out-view">
          <button onClick={onLoginClick} className="auth-button secondary">
            Login
          </button>
          <button onClick={onSignupClick} className="auth-button primary">
            Sign Up
          </button>
        </div>
      )}
      <div className="model-selector" style={{ marginTop: "8px" }}>
        <select
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
          style={{
            padding: "6px 10px",
            borderRadius: "8px",
            border: "1px solid #444",
            backgroundColor: "#1e1e2f",
            color: "#fff",
            fontWeight: "600",
            cursor: "pointer",
          }}
        >
          <option value="groq">⚡ Groq</option> 
          <option value="gemini">🌌 Gemini</option>
          <option value="elysiumAI">💻 ElysiumAI</option>
        </select>
      </div>
    </div>
  </header>
);

// --- Chat Area ---
const ChatArea = ({ messages, onPromptClick }) => {
  const chatEndRef = useRef(null);
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
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
            <ServiceButtons onPromptClick={onPromptClick} />
          </div>
        ) : (
          messages.map((msg, index) => (
            <div key={index} className="message-wrapper">
              <div className={`avatar ${msg.sender === "ai" ? "ai" : "user"}`}></div>
              <div>
                <p className="sender-name">
                  {msg.sender === "ai"
                    ? msg.model?.toUpperCase() || "AI"
                    : "You"}
                </p>
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

// // --- Chat Input ---
// const ChatInput = ({ onSendMessage }) => {
//   const [input, setInput] = useState("");
//   const fileInputRef = useRef(null);

//   const handleSubmit = (e) => {
//     e.preventDefault();
//     if (input.trim()) {
//       onSendMessage(input.trim());
//       setInput("");
//     }
//   };

 const ChatInput = ({ onSendMessage }) => {
  const [input, setInput] = useState("");
  const [selectedFile, setSelectedFile] = useState(null); // 📎 File hold karne ke liye state
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === "application/pdf") {
      setSelectedFile(file); // File select hui par bheji nahi
    } else if (file) {
      alert("Bhai, sirf PDF allow hai!");
      
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() || selectedFile) {
      const formData = new FormData();
      
      if (selectedFile) {
        formData.append("file", selectedFile);
      }
      
      // User ka typed command (e.g., "summarize this")
      const messageText = input.trim() || (selectedFile ? `Analyzing ${selectedFile.name}...` : "");
      formData.append("text", messageText);

      // Final bhej rahe hain backend ko
      onSendMessage(messageText, formData);

      // Resetting states
      setInput("");
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <footer className="chat-footer">
      {/* 📄 File Attachment Preview Tag */}
      {selectedFile && (
        <div style={{ 
          color: 'var(--purple-400)', 
          fontSize: '12px', 
          marginBottom: '8px', 
          paddingLeft: '1.5rem',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <span style={{ background: 'rgba(139, 92, 246, 0.1)', padding: '2px 8px', borderRadius: '4px' }}>
            📄 {selectedFile.name} attached
          </span>
          <button 
            onClick={() => setSelectedFile(null)} 
            style={{ background: 'none', border: 'none', color: '#ff4d4d', cursor: 'pointer', fontSize: '14px' }}
          >
            ✕
          </button>
        </div>
      )}

      <div className="input-form">
        <input 
          type="file" 
          ref={fileInputRef} 
          style={{ display: 'none' }} 
          accept=".pdf" 
          onChange={handleFileChange} 
        />

        {/* 📎 Paperclip Button */}
        <button 
          type="button" 
          className="action-btn upload-trigger" 
          onClick={() => fileInputRef.current.click()}
          style={{ left: '0.5rem', position: 'absolute' }}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
          </svg>
        </button>

        <input 
          type="text" 
          placeholder={selectedFile ? "Type command for PDF..." : "Message AI..."}
          value={input} 
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit(e)}
          style={{ paddingLeft: '3.5rem', paddingRight: '5rem' }} 
        />

        {/* 🚀 Attractive Purple Send Button */}
        <button 
          type="submit" 
          className="send-button" 
          onClick={handleSubmit}
          style={{
            position: 'absolute',
            right: '0.5rem',
            background: 'linear-gradient(135deg, var(--purple-600), var(--purple-400))',
            color: 'white',
            border: 'none',
            borderRadius: '9999px',
            padding: '0.6rem 1.5rem',
            fontWeight: '700',
            cursor: 'pointer',
            boxShadow: '0 4px 15px rgba(124, 58, 237, 0.4)'
          }}
        >
          Send
        </button>
      </div>
      <p className="footer-disclaimer">
        AI may display inaccurate info, so double-check its responses.
      </p>
    </footer>
  );
};
// --- Auth Modal ---
const AuthModal = ({ mode, setMode, onClose, onLogin, onSignup }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");
    if (mode === "signup" && password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    const authAction =
      mode === "login" ? onLogin(email, password) : onSignup(email, password);
    authAction.catch((err) => setError(err.message));
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button onClick={onClose} className="close-modal-btn">
          ✖
        </button>
        <h2 className="modal-title">
          {mode === "login" ? "Welcome Back" : "Create Account"}
        </h2>
        {error && <div className="auth-alert">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          {mode === "signup" && (
            <div className="form-group">
              <label>Confirm Password</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
            </div>
          )}
          <button type="submit">
            {mode === "login" ? "Login" : "Create Account"}
          </button>
        </form>
        <p>
          {mode === "login"
            ? "Don't have an account? "
            : "Already have an account? "}
          <a
            href="#"
            onClick={(e) => {
              e.preventDefault();
              setMode(mode === "login" ? "signup" : "login");
              setError("");
            }}
          >
            {mode === "login" ? "Sign Up" : "Login"}
          </a>
        </p>
      </div>
    </div>
  );
};

// --- Success Popup ---
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
    <div className={`success-popup ${show ? "show" : ""}`}>✅ {message}</div>
  );
};