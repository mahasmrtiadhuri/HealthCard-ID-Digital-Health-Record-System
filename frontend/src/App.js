import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import { useDropzone } from 'react-dropzone';
import { 
  Heart, 
  User, 
  MessageCircle, 
  FileText, 
  Search, 
  Plus,
  LogOut,
  Sun,
  Moon,
  Activity,
  Users,
  Calendar,
  Shield,
  Upload,
  Download,
  File,
  Image,
  Trash2,
  Eye,
  AlertCircle,
  CheckCircle,
  Clock,
  FileImage,
  FileType,
  Paperclip,
  Pill,
  CalendarDays,
  Stethoscope,
  UserCheck,
  Edit,
  Save,
  X,
  ChevronRight,
  MapPin,
  Phone,
  Mail,
  Timer,
  AlertTriangle,
  Info,
  Settings,
  BookOpen,
  Clipboard,
  Bell,
  BellRing
} from "lucide-react";
import { NotificationBell } from "./components/NotificationBell";
import { PatientDetailView } from "./components/PatientDetailView";
import { MultiPrescriptionFormMain } from "./components/MultiPrescriptionFormMain";
import "./App.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = React.createContext();

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const userData = localStorage.getItem("user");
    if (token && userData) {
      setUser(JSON.parse(userData));
      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, { email, password });
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem("token", access_token);
      localStorage.setItem("user", JSON.stringify(userData));
      axios.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
      setUser(userData);
      
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || "Login failed" };
    }
  };

  const register = async (userData) => {
    try {
      const response = await axios.post(`${API}/auth/register`, userData);
      const { access_token, user: newUser } = response.data;
      
      localStorage.setItem("token", access_token);
      localStorage.setItem("user", JSON.stringify(newUser));
      axios.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
      setUser(newUser);
      
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || "Registration failed" };
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    delete axios.defaults.headers.common["Authorization"];
    setUser(null);
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>;
  }

  return (
    <AuthContext.Provider value={{ user, login, register, logout }}>
      <div className={darkMode ? "dark" : ""}>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={user ? <Navigate to="/dashboard" /> : <LoginPage />} />
            <Route path="/register" element={user ? <Navigate to="/dashboard" /> : <RegisterPage />} />
            <Route path="/dashboard" element={user ? <Dashboard darkMode={darkMode} setDarkMode={setDarkMode} /> : <Navigate to="/login" />} />
            <Route path="/" element={user ? <Navigate to="/dashboard" /> : <LandingPage />} />
          </Routes>
        </BrowserRouter>
      </div>
    </AuthContext.Provider>
  );
}

// Landing Page
function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <nav className="flex justify-between items-center p-6">
        <div className="flex items-center space-x-2">
          <Heart className="h-8 w-8 text-blue-600" />
          <span className="text-2xl font-bold text-gray-800">HealthCard ID</span>
        </div>
        <div className="space-x-4">
          <a href="/login" className="text-blue-600 hover:text-blue-700">Login</a>
          <a href="/register" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
            Get Started
          </a>
        </div>
      </nav>
      
      <div className="max-w-6xl mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Your Health, <span className="text-blue-600">Simplified</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Complete health record management with appointments, prescriptions, AI insights, and secure file storage. 
            Connect patients and doctors in one unified platform.
          </p>
          <a href="/register" className="bg-blue-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-blue-700 transition">
            Start Your Health Journey
          </a>
        </div>

        <div className="grid md:grid-cols-4 gap-6">
          <FeatureCard 
            icon={<CalendarDays className="h-12 w-12 text-blue-600" />}
            title="Appointment Management"
            description="Schedule, track, and manage appointments with doctors seamlessly."
          />
          <FeatureCard 
            icon={<Pill className="h-12 w-12 text-green-600" />}
            title="Prescription Tracking"
            description="Keep track of all medications, dosages, and prescription histories."
          />
          <FeatureCard 
            icon={<Upload className="h-12 w-12 text-purple-600" />}
            title="Secure File Storage"
            description="Upload and store medical reports, prescriptions, and images securely."
          />
          <FeatureCard 
            icon={<MessageCircle className="h-12 w-12 text-orange-600" />}
            title="AI Health Assistant"
            description="Get instant insights, report summaries, and personalized health guidance."
          />
        </div>
      </div>
    </div>
  );
}

function FeatureCard({ icon, title, description }) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition">
      <div className="mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-gray-800 mb-2">{title}</h3>
      <p className="text-gray-600 text-sm">{description}</p>
    </div>
  );
}

// Login Page
function LoginPage() {
  const { login } = React.useContext(AuthContext);
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const result = await login(formData.email, formData.password);
    if (!result.success) {
      setError(result.error);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-md">
        <div className="flex items-center justify-center mb-8">
          <Heart className="h-8 w-8 text-blue-600 mr-2" />
          <span className="text-2xl font-bold text-gray-800">HealthCard ID</span>
        </div>
        
        <h2 className="text-2xl font-bold text-gray-800 text-center mb-6">Welcome Back</h2>
        
        {error && <div className="bg-red-100 text-red-700 p-3 rounded-lg mb-4">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">Email</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              required
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-bold mb-2">Password</label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Signing In..." : "Sign In"}
          </button>
        </form>
        
        <p className="text-center text-gray-600 mt-4">
          Don't have an account? <a href="/register" className="text-blue-600 hover:underline">Sign up</a>
        </p>
      </div>
    </div>
  );
}

// Register Page
function RegisterPage() {
  const { register } = React.useContext(AuthContext);
  const [formData, setFormData] = useState({ 
    email: "", 
    password: "", 
    name: "", 
    role: "patient",
    specialization: "",
    phone: ""
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const result = await register(formData);
    if (!result.success) {
      setError(result.error);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-md">
        <div className="flex items-center justify-center mb-8">
          <Heart className="h-8 w-8 text-blue-600 mr-2" />
          <span className="text-2xl font-bold text-gray-800">HealthCard ID</span>
        </div>
        
        <h2 className="text-2xl font-bold text-gray-800 text-center mb-6">Create Account</h2>
        
        {error && <div className="bg-red-100 text-red-700 p-3 rounded-lg mb-4">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">Full Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              required
            />
          </div>
          
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">Email</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              required
            />
          </div>
          
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">Phone (Optional)</label>
            <input
              type="tel"
              value={formData.phone}
              onChange={(e) => setFormData({...formData, phone: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
            />
          </div>
          
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">Password</label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              required
            />
          </div>
          
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">I am a:</label>
            <div className="flex space-x-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  value="patient"
                  checked={formData.role === "patient"}
                  onChange={(e) => setFormData({...formData, role: e.target.value})}
                  className="mr-2"
                />
                Patient
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  value="doctor"
                  checked={formData.role === "doctor"}
                  onChange={(e) => setFormData({...formData, role: e.target.value})}
                  className="mr-2"
                />
                Doctor
              </label>
            </div>
          </div>
          
          {formData.role === "doctor" && (
            <div className="mb-6">
              <label className="block text-gray-700 text-sm font-bold mb-2">Specialization</label>
              <input
                type="text"
                value={formData.specialization}
                onChange={(e) => setFormData({...formData, specialization: e.target.value})}
                placeholder="e.g. Cardiology, General Practice"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              />
            </div>
          )}
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Creating Account..." : "Create Account"}
          </button>
        </form>
        
        <p className="text-center text-gray-600 mt-4">
          Already have an account? <a href="/login" className="text-blue-600 hover:underline">Sign in</a>
        </p>
      </div>
    </div>
  );
}

// Dashboard
function Dashboard({ darkMode, setDarkMode }) {
  const { user, logout } = React.useContext(AuthContext);
  const [activeTab, setActiveTab] = useState("overview");

  const handleLogout = () => {
    logout();
  };

  return (
    <div className={`min-h-screen transition-colors ${darkMode ? 'dark bg-gray-900' : 'bg-gray-50'}`}>
      {/* Sidebar */}
      <div className={`fixed left-0 top-0 h-full w-64 transition-colors ${darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border-r shadow-lg`}>
        <div className="p-6">
          <div className="flex items-center space-x-2 mb-8">
            <Heart className="h-8 w-8 text-blue-600" />
            <span className={`text-xl font-bold ${darkMode ? 'text-white' : 'text-gray-800'}`}>HealthCard ID</span>
          </div>
          
          <nav className="space-y-2">
            <NavItem 
              icon={<Activity />} 
              label="Overview" 
              active={activeTab === "overview"} 
              onClick={() => setActiveTab("overview")}
              darkMode={darkMode}
            />
            
            {user.role === "patient" ? (
              <>
                <NavItem 
                  icon={<User />} 
                  label="My Profile" 
                  active={activeTab === "profile"} 
                  onClick={() => setActiveTab("profile")}
                  darkMode={darkMode}
                />
                <NavItem 
                  icon={<CalendarDays />} 
                  label="Appointments" 
                  active={activeTab === "appointments"} 
                  onClick={() => setActiveTab("appointments")}
                  darkMode={darkMode}
                />
                <NavItem 
                  icon={<Pill />} 
                  label="Prescriptions" 
                  active={activeTab === "prescriptions"} 
                  onClick={() => setActiveTab("prescriptions")}
                  darkMode={darkMode}
                />
              </>
            ) : (
              <>
                <NavItem 
                  icon={<Users />} 
                  label="Patients" 
                  active={activeTab === "patients"} 
                  onClick={() => setActiveTab("patients")}
                  darkMode={darkMode}
                />
                <NavItem 
                  icon={<CalendarDays />} 
                  label="Appointments" 
                  active={activeTab === "appointments"} 
                  onClick={() => setActiveTab("appointments")}
                  darkMode={darkMode}
                />
                <NavItem 
                  icon={<Pill />} 
                  label="Prescriptions" 
                  active={activeTab === "prescriptions"} 
                  onClick={() => setActiveTab("prescriptions")}
                  darkMode={darkMode}
                />
              </>
            )}
            
            <NavItem 
              icon={<FileText />} 
              label="Medical Records" 
              active={activeTab === "records"} 
              onClick={() => setActiveTab("records")}
              darkMode={darkMode}
            />
            <NavItem 
              icon={<Upload />} 
              label="File Management" 
              active={activeTab === "files"} 
              onClick={() => setActiveTab("files")}
              darkMode={darkMode}
            />
            <NavItem 
              icon={<MessageCircle />} 
              label="AI Assistant" 
              active={activeTab === "chat"} 
              onClick={() => setActiveTab("chat")}
              darkMode={darkMode}
            />
          </nav>
        </div>
        
        <div className="absolute bottom-0 left-0 right-0 p-6 border-t">
          <div className="flex items-center justify-between mb-4">
            <span className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>Theme</span>
            <button
              onClick={() => setDarkMode(!darkMode)}
              className={`p-2 rounded-lg ${darkMode ? 'bg-gray-700 text-yellow-400' : 'bg-gray-100 text-gray-600'}`}
            >
              {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>
          </div>
          
          <button
            onClick={handleLogout}
            className="flex items-center w-full p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
          >
            <LogOut className="h-4 w-4 mr-2" />
            Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="ml-64 p-8">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
              Welcome back, {user.name}
            </h1>
            <p className={`${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
              {user.role === "patient" 
                ? "Manage your appointments, prescriptions, and health records with AI insights" 
                : "Manage patients, appointments, and medical records with comprehensive tools"
              }
            </p>
          </div>
          
          {/* Notification Bell */}
          <NotificationBell darkMode={darkMode} />
        </div>

        {activeTab === "overview" && <OverviewTab user={user} darkMode={darkMode} />}
        {activeTab === "profile" && <PatientProfile darkMode={darkMode} />}
        {activeTab === "patients" && <DoctorPatients darkMode={darkMode} />}
        {activeTab === "appointments" && <AppointmentsTab user={user} darkMode={darkMode} />}
        {activeTab === "prescriptions" && <PrescriptionsTab user={user} darkMode={darkMode} />}
        {activeTab === "records" && <RecordsTab user={user} darkMode={darkMode} />}
        {activeTab === "files" && <FilesTab user={user} darkMode={darkMode} />}
        {activeTab === "chat" && <ChatTab user={user} darkMode={darkMode} />}
      </div>
    </div>
  );
}

function NavItem({ icon, label, active, onClick, darkMode }) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center w-full p-3 rounded-lg transition ${
        active 
          ? 'bg-blue-600 text-white' 
          : darkMode
            ? 'text-gray-300 hover:bg-gray-700'
            : 'text-gray-600 hover:bg-gray-100'
      }`}
    >
      <span className="mr-3">{icon}</span>
      {label}
    </button>
  );
}

// Overview Tab
function OverviewTab({ user, darkMode }) {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`${API}/dashboard/stats`);
        setStats(response.data);
      } catch (error) {
        console.error("Failed to fetch stats:", error);
      }
    };
    fetchStats();
  }, []);

  if (!stats) return <div>Loading...</div>;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {user.role === "patient" ? (
          <>
            <StatCard 
              icon={<FileText className="h-8 w-8 text-blue-600" />}
              title="Medical Records"
              value={stats.records_count}
              darkMode={darkMode}
            />
            <StatCard 
              icon={<Upload className="h-8 w-8 text-green-600" />}
              title="Uploaded Files"
              value={stats.files_count}
              darkMode={darkMode}
            />
            <StatCard 
              icon={<User className="h-8 w-8 text-purple-600" />}
              title="Profile Status"
              value={stats.profile_complete ? "Complete" : "Incomplete"}
              darkMode={darkMode}
            />
          </>
        ) : (
          <>
            <StatCard 
              icon={<Users className="h-8 w-8 text-blue-600" />}
              title="Total Patients"
              value={stats.patients_count}
              darkMode={darkMode}
            />
            <StatCard 
              icon={<FileText className="h-8 w-8 text-green-600" />}
              title="Records Created"
              value={stats.records_count}
              darkMode={darkMode}
            />
            <StatCard 
              icon={<Upload className="h-8 w-8 text-purple-600" />}
              title="Total Files"
              value={stats.total_files}
              darkMode={darkMode}
            />
          </>
        )}
      </div>
      
      {user.role === "patient" && (
        <AIHealthSummary darkMode={darkMode} />
      )}
    </div>
  );
}

function StatCard({ icon, title, value, darkMode }) {
  return (
    <div className={`p-6 rounded-xl shadow-lg ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>{title}</p>
          <p className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-gray-800'}`}>{value}</p>
        </div>
        {icon}
      </div>
    </div>
  );
}

// AI Health Summary Component
function AIHealthSummary({ darkMode }) {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const generateSummary = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${API}/ai/summarize-reports`);
      setSummary(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to generate summary");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    generateSummary();
  }, []);

  return (
    <div className={`p-6 rounded-xl shadow-lg ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className={`text-xl font-bold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
          🤖 AI Health Summary
        </h3>
        <button
          onClick={generateSummary}
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center"
        >
          {loading ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
          ) : (
            <MessageCircle className="h-4 w-4 mr-2" />
          )}
          {loading ? "Generating..." : "Refresh Summary"}
        </button>
      </div>

      {error && (
        <div className="bg-red-100 text-red-700 p-3 rounded-lg mb-4">
          {error}
        </div>
      )}

      {summary && (
        <div className="space-y-4">
          <div className={`p-4 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
            <div className="flex items-center mb-2">
              <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
              <span className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                Analyzed {summary.records_analyzed} records and {summary.files_analyzed} files
              </span>
            </div>
            <div className="whitespace-pre-wrap text-sm">
              <p className={`${darkMode ? 'text-gray-200' : 'text-gray-700'}`}>
                {summary.summary}
              </p>
            </div>
          </div>
          
          <div className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
            Generated on {new Date(summary.generated_at).toLocaleDateString()}
            {summary.fallback && " (Fallback mode - AI service unavailable)"}
          </div>
        </div>
      )}
    </div>
  );
}

// Files Tab
function FilesTab({ user, darkMode }) {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg', '.gif']
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    onDrop: handleFileDrop
  });

  async function handleFileDrop(acceptedFiles) {
    for (const file of acceptedFiles) {
      await uploadFile(file);
    }
  }

  const uploadFile = async (file, uploadType = "medical_report") => {
    setUploading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append("file", file);

    try {
      const endpoint = uploadType === "profile_image" ? "/upload/profile-image" : "/upload/medical-report";
      const response = await axios.post(`${API}${endpoint}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      // Refresh file list
      fetchFiles();
      
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const fetchFiles = async () => {
    try {
      const response = await axios.get(`${API}/files`);
      setFiles(response.data);
    } catch (error) {
      console.error("Failed to fetch files:", error);
    }
  };

  const deleteFile = async (fileId) => {
    if (!window.confirm("Are you sure you want to delete this file?")) return;
    
    try {
      await axios.delete(`${API}/files/${fileId}`);
      fetchFiles(); // Refresh list
    } catch (error) {
      console.error("Failed to delete file:", error);
    }
  };

  const downloadFile = async (fileId, filename) => {
    try {
      const response = await axios.get(`${API}/files/${fileId}`, {
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Failed to download file:", error);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (fileType) => {
    if (fileType.startsWith('image/')) {
      return <FileImage className="h-6 w-6 text-green-600" />;
    } else if (fileType === 'application/pdf') {
      return <FileType className="h-6 w-6 text-red-600" />;
    }
    return <File className="h-6 w-6 text-gray-600" />;
  };

  return (
    <div className="space-y-6">
      <div className={`p-6 rounded-xl shadow-lg ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
        <h2 className={`text-2xl font-bold mb-4 ${darkMode ? 'text-white' : 'text-gray-800'}`}>
          File Management
        </h2>

        {error && (
          <div className="bg-red-100 text-red-700 p-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        {/* Upload Area */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition ${
            isDragActive
              ? 'border-blue-500 bg-blue-50'
              : darkMode
                ? 'border-gray-600 hover:border-gray-500'
                : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className={`h-12 w-12 mx-auto mb-4 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`} />
          {isDragActive ? (
            <p className={`text-lg ${darkMode ? 'text-blue-300' : 'text-blue-600'}`}>
              Drop the files here...
            </p>
          ) : (
            <div>
              <p className={`text-lg mb-2 ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                Drag & drop files here, or click to select
              </p>
              <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                Supports PDF, JPG, PNG, GIF (Max 10MB each)
              </p>
            </div>
          )}
        </div>

        {uploading && (
          <div className="mt-4 p-3 bg-blue-100 text-blue-700 rounded-lg flex items-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
            Uploading file...
          </div>
        )}
      </div>

      {/* Files List */}
      <div className={`p-6 rounded-xl shadow-lg ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
        <h3 className={`text-xl font-bold mb-4 ${darkMode ? 'text-white' : 'text-gray-800'}`}>
          Your Files ({files.length})
        </h3>

        {files.length === 0 ? (
          <div className={`text-center py-8 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
            <File className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No files uploaded yet. Upload your first medical document above.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {files.map((file) => (
              <div
                key={file.file_id}
                className={`flex items-center justify-between p-4 border rounded-lg ${
                  darkMode ? 'border-gray-600 hover:bg-gray-700' : 'border-gray-200 hover:bg-gray-50'
                } transition`}
              >
                <div className="flex items-center space-x-3">
                  {getFileIcon(file.file_type)}
                  <div>
                    <h4 className={`font-medium ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                      {file.original_filename}
                    </h4>
                    <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                      {formatFileSize(file.file_size)} • {file.upload_type.replace('_', ' ')} • 
                      {new Date(file.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => downloadFile(file.file_id, file.original_filename)}
                    className="p-2 text-blue-600 hover:bg-blue-100 rounded-lg transition"
                    title="Download"
                  >
                    <Download className="h-4 w-4" />
                  </button>
                  
                  {file.file_type.startsWith('image/') && (
                    <button
                      onClick={() => window.open(`${API}/files/${file.file_id}`, '_blank')}
                      className="p-2 text-green-600 hover:bg-green-100 rounded-lg transition"
                      title="View"
                    >
                      <Eye className="h-4 w-4" />
                    </button>
                  )}

                  <button
                    onClick={() => deleteFile(file.file_id)}
                    className="p-2 text-red-600 hover:bg-red-100 rounded-lg transition"
                    title="Delete"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// Appointments Tab
function AppointmentsTab({ user, darkMode }) {
  const [appointments, setAppointments] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAppointments();
  }, []);

  const fetchAppointments = async () => {
    try {
      const response = await axios.get(`${API}/appointments`);
      setAppointments(response.data);
    } catch (error) {
      console.error("Failed to fetch appointments:", error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'scheduled': return 'bg-blue-100 text-blue-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'canceled': return 'bg-red-100 text-red-800';
      case 'rescheduled': return 'bg-yellow-100 text-yellow-800';
      case 'no_show': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) return <div>Loading appointments...</div>;

  return (
    <div className="space-y-6">
      <div className={`p-6 rounded-xl shadow-lg ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
        <div className="flex items-center justify-between mb-6">
          <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
            Appointments
          </h2>
          {user.role === "doctor" && (
            <button 
              onClick={() => setShowCreateForm(!showCreateForm)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center"
            >
              <Plus className="h-4 w-4 mr-2" />
              Schedule Appointment
            </button>
          )}
        </div>

        {showCreateForm && user.role === "doctor" && (
          <CreateAppointmentForm 
            onClose={() => setShowCreateForm(false)} 
            onSuccess={() => {
              setShowCreateForm(false);
              fetchAppointments();
            }}
            darkMode={darkMode}
          />
        )}

        <div className="space-y-4">
          {appointments.length === 0 ? (
            <div className={`text-center py-8 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
              <CalendarDays className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No appointments scheduled yet.</p>
            </div>
          ) : (
            appointments.map((appointment) => (
              <div key={appointment.id} className={`p-4 border rounded-lg ${
                darkMode ? 'border-gray-600' : 'border-gray-200'
              }`}>
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-4 mb-2">
                      <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                        {user.role === "patient" 
                          ? `Dr. ${appointment.doctor_name || 'Unknown'}` 
                          : appointment.patient_name || 'Unknown Patient'
                        }
                      </h3>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(appointment.status)}`}>
                        {appointment.status.replace('_', ' ')}
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-4 text-sm">
                      <div className="flex items-center">
                        <Calendar className="h-4 w-4 mr-1 text-gray-400" />
                        <span className={darkMode ? 'text-gray-300' : 'text-gray-600'}>
                          {new Date(appointment.appointment_date).toLocaleDateString()}
                        </span>
                      </div>
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 mr-1 text-gray-400" />
                        <span className={darkMode ? 'text-gray-300' : 'text-gray-600'}>
                          {appointment.appointment_time}
                        </span>
                      </div>
                      <div className="flex items-center">
                        <Info className="h-4 w-4 mr-1 text-gray-400" />
                        <span className={darkMode ? 'text-gray-300' : 'text-gray-600'}>
                          {appointment.appointment_type}
                        </span>
                      </div>
                    </div>
                    
                    {appointment.reason && (
                      <p className={`text-sm mt-2 ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                        Reason: {appointment.reason}
                      </p>
                    )}
                    
                    {user.role === "patient" && appointment.doctor_specialization && (
                      <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                        Specialization: {appointment.doctor_specialization}
                      </p>
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {appointment.status === 'scheduled' && (
                      <>
                        <button className="p-2 text-blue-600 hover:bg-blue-100 rounded-lg transition">
                          <Edit className="h-4 w-4" />
                        </button>
                        {user.role === "patient" && (
                          <button className="p-2 text-red-600 hover:bg-red-100 rounded-lg transition">
                            <X className="h-4 w-4" />
                          </button>
                        )}
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

// Create Appointment Form
function CreateAppointmentForm({ onClose, onSuccess, darkMode }) {
  const [formData, setFormData] = useState({
    patient_id: "",
    appointment_date: "",
    appointment_time: "",
    appointment_type: "consultation",
    reason: "",
    notes: ""
  });
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchPatients = async () => {
      try {
        const response = await axios.get(`${API}/patients/search`);
        setPatients(response.data);
      } catch (error) {
        console.error("Failed to fetch patients:", error);
      }
    };
    fetchPatients();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${API}/appointments`, formData);
      onSuccess();
    } catch (error) {
      console.error("Failed to create appointment:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`p-4 border rounded-lg mb-6 ${darkMode ? 'border-gray-600 bg-gray-700' : 'border-gray-200 bg-gray-50'}`}>
      <h3 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-800'}`}>Schedule New Appointment</h3>
      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className={`block text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-1`}>
            Patient
          </label>
          <select
            value={formData.patient_id}
            onChange={(e) => setFormData({...formData, patient_id: e.target.value})}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500 ${
              darkMode ? 'bg-gray-600 border-gray-500 text-white' : 'bg-white border-gray-300'
            }`}
            required
          >
            <option value="">Select a patient</option>
            {patients.map((patient) => (
              <option key={patient.user_id} value={patient.user_id}>
                {patient.name} - {patient.email}
              </option>
            ))}
          </select>
        </div>
        
        <div>
          <label className={`block text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-1`}>
            Date
          </label>
          <input
            type="date"
            value={formData.appointment_date}
            onChange={(e) => setFormData({...formData, appointment_date: e.target.value})}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500 ${
              darkMode ? 'bg-gray-600 border-gray-500 text-white' : 'bg-white border-gray-300'
            }`}
            required
          />
        </div>
        
        <div>
          <label className={`block text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-1`}>
            Time
          </label>
          <input
            type="time"
            value={formData.appointment_time}
            onChange={(e) => setFormData({...formData, appointment_time: e.target.value})}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500 ${
              darkMode ? 'bg-gray-600 border-gray-500 text-white' : 'bg-white border-gray-300'
            }`}
            required
          />
        </div>
        
        <div>
          <label className={`block text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-1`}>
            Type
          </label>
          <select
            value={formData.appointment_type}
            onChange={(e) => setFormData({...formData, appointment_type: e.target.value})}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500 ${
              darkMode ? 'bg-gray-600 border-gray-500 text-white' : 'bg-white border-gray-300'
            }`}
          >
            <option value="consultation">Consultation</option>
            <option value="follow_up">Follow Up</option>
            <option value="check_up">Check Up</option>
            <option value="emergency">Emergency</option>
          </select>
        </div>
        
        <div className="md:col-span-2">
          <label className={`block text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-1`}>
            Reason
          </label>
          <input
            type="text"
            value={formData.reason}
            onChange={(e) => setFormData({...formData, reason: e.target.value})}
            placeholder="Reason for appointment"
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500 ${
              darkMode ? 'bg-gray-600 border-gray-500 text-white' : 'bg-white border-gray-300'
            }`}
          />
        </div>
        
        <div className="md:col-span-2">
          <label className={`block text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-1`}>
            Notes
          </label>
          <textarea
            value={formData.notes}
            onChange={(e) => setFormData({...formData, notes: e.target.value})}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500 ${
              darkMode ? 'bg-gray-600 border-gray-500 text-white' : 'bg-white border-gray-300'
            }`}
            rows="2"
            placeholder="Additional notes"
          />
        </div>
        
        <div className="md:col-span-2 flex space-x-2">
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Scheduling..." : "Schedule Appointment"}
          </button>
          <button
            type="button"
            onClick={onClose}
            className={`px-4 py-2 rounded-lg ${darkMode ? 'bg-gray-600 text-white hover:bg-gray-500' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}`}
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

// Prescriptions Tab
function PrescriptionsTab({ user, darkMode }) {
  const [prescriptions, setPrescriptions] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPrescriptions();
  }, []);

  const fetchPrescriptions = async () => {
    try {
      // Fetch both single prescriptions and multi-prescriptions
      const [singleResponse, multiResponse] = await Promise.all([
        axios.get(`${API}/prescriptions`),
        axios.get(`${API}/multi-prescriptions`)
      ]);
      
      // Combine and format prescriptions
      const singlePrescriptions = singleResponse.data.map(p => ({
        ...p,
        type: 'single',
        medication_name: p.medication_name,
        display_name: p.medication_name
      }));
      
      const multiPrescriptions = multiResponse.data.map(p => ({
        ...p,
        type: 'multi',
        medication_name: `${p.medicines.length} medicines`,
        display_name: p.medicines.map(m => m.name).join(', '),
        medicines_count: p.medicines.length
      }));
      
      setPrescriptions([...multiPrescriptions, ...singlePrescriptions]);
    } catch (error) {
      console.error("Failed to fetch prescriptions:", error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'completed': return 'bg-blue-100 text-blue-800';
      case 'discontinued': return 'bg-red-100 text-red-800';
      case 'expired': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) return <div>Loading prescriptions...</div>;

  return (
    <div className="space-y-6">
      <div className={`p-6 rounded-xl shadow-lg ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
        <div className="flex items-center justify-between mb-6">
          <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
            Prescriptions
          </h2>
          {user.role === "doctor" && (
            <button 
              onClick={() => setShowCreateForm(!showCreateForm)}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center"
            >
              <Plus className="h-4 w-4 mr-2" />
              New Prescription
            </button>
          )}
        </div>

        {showCreateForm && user.role === "doctor" && (
          <MultiPrescriptionFormMain 
            onClose={() => setShowCreateForm(false)} 
            onSuccess={() => {
              setShowCreateForm(false);
              fetchPrescriptions();
            }}
            darkMode={darkMode}
          />
        )}

        <div className="space-y-4">
          {prescriptions.length === 0 ? (
            <div className={`text-center py-8 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
              <Pill className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No prescriptions found.</p>
            </div>
          ) : (
            prescriptions.map((prescription) => (
              <div key={prescription.id} className={`p-4 border rounded-lg ${
                darkMode ? 'border-gray-600' : 'border-gray-200'
              }`}>
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-4 mb-2">
                      <h3 className={`font-bold text-lg ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                        {prescription.type === 'multi' ? 
                          `Multi-Medicine Prescription (${prescription.medicines_count} medicines)` : 
                          prescription.medication_name
                        }
                      </h3>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(prescription.status)}`}>
                        {prescription.status}
                      </span>
                      {prescription.type === 'multi' && (
                        <span className="px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
                          Multi-Medicine
                        </span>
                      )}
                    </div>
                    
                    {prescription.type === 'multi' ? (
                      // Multi-prescription display
                      <div className="space-y-3">
                        <div className="text-sm">
                          <span className={`font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                            Medicines:
                          </span>
                          <p className={`${darkMode ? 'text-gray-200' : 'text-gray-800'} mt-1`}>
                            {prescription.display_name}
                          </p>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className={`font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                              Start Date:
                            </span>
                            <p className={darkMode ? 'text-gray-200' : 'text-gray-800'}>
                              {new Date(prescription.start_date).toLocaleDateString()}
                            </p>
                          </div>
                          <div>
                            <span className={`font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                              Total Medicines:
                            </span>
                            <p className={darkMode ? 'text-gray-200' : 'text-gray-800'}>
                              {prescription.medicines_count}
                            </p>
                          </div>
                        </div>
                        
                        {prescription.general_instructions && (
                          <div className="text-sm">
                            <span className={`font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                              General Instructions:
                            </span>
                            <p className={`${darkMode ? 'text-gray-200' : 'text-gray-700'} mt-1`}>
                              {prescription.general_instructions}
                            </p>
                          </div>
                        )}
                      </div>
                    ) : (
                      // Single prescription display (existing)
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-3">
                        <div>
                          <span className={`font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                            Dosage:
                          </span>
                          <p className={darkMode ? 'text-gray-200' : 'text-gray-800'}>
                            {prescription.dosage}
                          </p>
                        </div>
                        <div>
                          <span className={`font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                            Frequency:
                          </span>
                          <p className={darkMode ? 'text-gray-200' : 'text-gray-800'}>
                            {prescription.frequency}
                          </p>
                        </div>
                        <div>
                          <span className={`font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                            Start Date:
                          </span>
                          <p className={darkMode ? 'text-gray-200' : 'text-gray-800'}>
                            {new Date(prescription.start_date).toLocaleDateString()}
                          </p>
                        </div>
                        <div>
                          <span className={`font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                            End Date:
                          </span>
                          <p className={darkMode ? 'text-gray-200' : 'text-gray-800'}>
                            {prescription.end_date ? new Date(prescription.end_date).toLocaleDateString() : 'Ongoing'}
                          </p>
                        </div>
                      </div>
                    )}
                    
                    {prescription.patient_name && user.role === "doctor" && (
                      <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                        Patient: {prescription.patient_name}
                      </p>
                    )}
                    
                    {prescription.doctor_name && user.role === "patient" && (
                      <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                        Prescribed by: Dr. {prescription.doctor_name}
                        {prescription.doctor_specialization && ` (${prescription.doctor_specialization})`}
                      </p>
                    )}
                  </div>
                  
                  {user.role === "doctor" && (
                    <div className="flex items-center space-x-2">
                      <button className="p-2 text-blue-600 hover:bg-blue-100 rounded-lg transition">
                        <Edit className="h-4 w-4" />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

// Create Prescription Form
function CreatePrescriptionForm({ onClose, onSuccess, darkMode }) {
  const [formData, setFormData] = useState({
    patient_id: "",
    medication_name: "",
    dosage: "",
    frequency: "",
    start_date: new Date().toISOString().split('T')[0],
    end_date: "",
    instructions: "",
    refills_remaining: 0
  });
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchPatients = async () => {
      try {
        const response = await axios.get(`${API}/patients/search`);
        setPatients(response.data);
      } catch (error) {
        console.error("Failed to fetch patients:", error);
      }
    };
    fetchPatients();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${API}/prescriptions`, formData);
      onSuccess();
    } catch (error) {
      console.error("Failed to create prescription:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`p-4 border rounded-lg mb-6 ${darkMode ? 'border-gray-600 bg-gray-700' : 'border-gray-200 bg-gray-50'}`}>
      <h3 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-800'}`}>New Prescription</h3>
      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className={`block text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-1`}>
            Patient
          </label>
          <select
            value={formData.patient_id}
            onChange={(e) => setFormData({...formData, patient_id: e.target.value})}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500 ${
              darkMode ? 'bg-gray-600 border-gray-500 text-white' : 'bg-white border-gray-300'
            }`}
            required
          >
            <option value="">Select a patient</option>
            {patients.map((patient) => (
              <option key={patient.user_id} value={patient.user_id}>
                {patient.name} - {patient.email}
              </option>
            ))}
          </select>
        </div>
        
        <div>
          <label className={`block text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-1`}>
            Medication Name
          </label>
          <input
            type="text"
            value={formData.medication_name}
            onChange={(e) => setFormData({...formData, medication_name: e.target.value})}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500 ${
              darkMode ? 'bg-gray-600 border-gray-500 text-white' : 'bg-white border-gray-300'
            }`}
            required
          />
        </div>
        
        <div>
          <label className={`block text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-1`}>
            Dosage
          </label>
          <input
            type="text"
            value={formData.dosage}
            onChange={(e) => setFormData({...formData, dosage: e.target.value})}
            placeholder="e.g., 10mg, 2 tablets"
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500 ${
              darkMode ? 'bg-gray-600 border-gray-500 text-white' : 'bg-white border-gray-300'
            }`}
            required
          />
        </div>
        
        <div>
          <label className={`block text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-1`}>
            Frequency
          </label>
          <input
            type="text"
            value={formData.frequency}
            onChange={(e) => setFormData({...formData, frequency: e.target.value})}
            placeholder="e.g., twice daily, once before meals"
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500 ${
              darkMode ? 'bg-gray-600 border-gray-500 text-white' : 'bg-white border-gray-300'
            }`}
            required
          />
        </div>
        
        <div>
          <label className={`block text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-1`}>
            Start Date
          </label>
          <input
            type="date"
            value={formData.start_date}
            onChange={(e) => setFormData({...formData, start_date: e.target.value})}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500 ${
              darkMode ? 'bg-gray-600 border-gray-500 text-white' : 'bg-white border-gray-300'
            }`}
            required
          />
        </div>
        
        <div>
          <label className={`block text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-1`}>
            End Date (Optional)
          </label>
          <input
            type="date"
            value={formData.end_date}
            onChange={(e) => setFormData({...formData, end_date: e.target.value})}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500 ${
              darkMode ? 'bg-gray-600 border-gray-500 text-white' : 'bg-white border-gray-300'
            }`}
          />
        </div>
        
        <div className="md:col-span-2">
          <label className={`block text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-1`}>
            Instructions
          </label>
          <textarea
            value={formData.instructions}
            onChange={(e) => setFormData({...formData, instructions: e.target.value})}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500 ${
              darkMode ? 'bg-gray-600 border-gray-500 text-white' : 'bg-white border-gray-300'
            }`}
            rows="3"
            placeholder="Special instructions for taking the medication"
          />
        </div>
        
        <div className="md:col-span-2 flex space-x-2">
          <button
            type="submit"
            disabled={loading}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            {loading ? "Creating..." : "Create Prescription"}
          </button>
          <button
            type="button"
            onClick={onClose}
            className={`px-4 py-2 rounded-lg ${darkMode ? 'bg-gray-600 text-white hover:bg-gray-500' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}`}
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

// Profile Tab
function ProfileTab({ user, darkMode }) {
  if (user.role === "patient") {
    return <PatientProfile darkMode={darkMode} />;
  } else {
    return <DoctorPatients darkMode={darkMode} />;
  }
}

function PatientProfile({ darkMode }) {
  const [profile, setProfile] = useState(null);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({});

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await axios.get(`${API}/patients/me`);
        setProfile(response.data);
        setFormData(response.data);
      } catch (error) {
        console.error("Failed to fetch profile:", error);
      }
    };
    fetchProfile();
  }, []);

  const handleSave = async () => {
    try {
      const response = await axios.put(`${API}/patients/me`, formData);
      setProfile(response.data);
      setEditing(false);
    } catch (error) {
      console.error("Failed to update profile:", error);
    }
  };

  if (!profile) return <div>Loading...</div>;

  return (
    <div className={`p-6 rounded-xl shadow-lg ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
      <div className="flex items-center justify-between mb-6">
        <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-gray-800'}`}>My Health Profile</h2>
        <button
          onClick={() => editing ? handleSave() : setEditing(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          {editing ? "Save" : "Edit"}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <ProfileField 
          label="Age" 
          value={editing ? formData.age : profile.age} 
          editing={editing}
          onChange={(value) => setFormData({...formData, age: parseInt(value) || null})}
          type="number"
          darkMode={darkMode}
        />
        <ProfileField 
          label="Gender" 
          value={editing ? formData.gender : profile.gender} 
          editing={editing}
          onChange={(value) => setFormData({...formData, gender: value})}
          darkMode={darkMode}
        />
        <ProfileField 
          label="Blood Group" 
          value={editing ? formData.blood_group : profile.blood_group} 
          editing={editing}
          onChange={(value) => setFormData({...formData, blood_group: value})}
          darkMode={darkMode}
        />
        <ProfileField 
          label="Weight (kg)" 
          value={editing ? formData.weight : profile.weight} 
          editing={editing}
          onChange={(value) => setFormData({...formData, weight: parseFloat(value) || null})}
          type="number"
          step="0.1"
          darkMode={darkMode}
        />
      </div>
    </div>
  );
}

function ProfileField({ label, value, editing, onChange, type = "text", step, darkMode }) {
  return (
    <div>
      <label className={`block text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-1`}>
        {label}
      </label>
      {editing ? (
        <input
          type={type}
          step={step}
          value={value || ""}
          onChange={(e) => onChange(e.target.value)}
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500 ${
            darkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300'
          }`}
        />
      ) : (
        <p className={`px-3 py-2 ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
          {value || "Not specified"}
        </p>
      )}
    </div>
  );
}

function DoctorPatients({ darkMode }) {
  const [patients, setPatients] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [patientDetails, setPatientDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  useEffect(() => {
    const fetchPatients = async () => {
      try {
        const response = await axios.get(`${API}/patients/search?q=${searchTerm}`);
        setPatients(response.data);
      } catch (error) {
        console.error("Failed to fetch patients:", error);
      }
    };
    fetchPatients();
  }, [searchTerm]);

  const fetchPatientDetails = async (patient) => {
    setLoadingDetails(true);
    try {
      const response = await axios.get(`${API}/patients/${patient.user_id}/profile`);
      setPatientDetails(response.data);
      setSelectedPatient(patient);
    } catch (error) {
      console.error("Failed to fetch patient details:", error);
    } finally {
      setLoadingDetails(false);
    }
  };

  if (selectedPatient && patientDetails) {
    return (
      <PatientDetailView 
        patient={selectedPatient}
        patientDetails={patientDetails}
        darkMode={darkMode}
        onBack={() => {
          setSelectedPatient(null);
          setPatientDetails(null);
        }}
        onRefresh={() => fetchPatientDetails(selectedPatient)}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className={`p-6 rounded-xl shadow-lg ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
        <h2 className={`text-2xl font-bold mb-4 ${darkMode ? 'text-white' : 'text-gray-800'}`}>Patient Search</h2>
        <div className="relative">
          <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search patients by name or email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className={`w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:border-blue-500 ${
              darkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300'
            }`}
          />
        </div>
      </div>

      <div className="grid gap-4">
        {patients.map((patient) => (
          <div 
            key={patient.id} 
            className={`p-4 rounded-xl shadow-lg cursor-pointer hover:shadow-xl transition ${
              darkMode ? 'bg-gray-800 hover:bg-gray-700' : 'bg-white hover:bg-gray-50'
            }`}
            onClick={() => fetchPatientDetails(patient)}
          >
            <div className="flex items-center justify-between">
              <div>
                <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-gray-800'}`}>{patient.name}</h3>
                <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>{patient.email}</p>
              </div>
              <div className="text-right">
                <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                  Age: {patient.age || "N/A"}
                </p>
                <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                  Blood Group: {patient.blood_group || "N/A"}
                </p>
              </div>
              <ChevronRight className={`h-5 w-5 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`} />
            </div>
          </div>
        ))}
      </div>

      {loadingDetails && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className={`p-6 rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className={`text-center ${darkMode ? 'text-white' : 'text-gray-800'}`}>Loading patient details...</p>
          </div>
        </div>
      )}
    </div>
  );
}

// Records Tab
function RecordsTab({ user, darkMode }) {
  const [records, setRecords] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);

  useEffect(() => {
    const fetchRecords = async () => {
      try {
        const response = await axios.get(`${API}/medical-records`);
        setRecords(response.data);
      } catch (error) {
        console.error("Failed to fetch records:", error);
      }
    };
    fetchRecords();
  }, []);

  return (
    <div className="space-y-6">
      <div className={`p-6 rounded-xl shadow-lg ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
        <div className="flex items-center justify-between mb-4">
          <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-gray-800'}`}>Medical Records</h2>
          {user.role === "doctor" && (
            <button 
              onClick={() => setShowCreateForm(!showCreateForm)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Record
            </button>
          )}
        </div>

        {showCreateForm && user.role === "doctor" && (
          <CreateRecordForm 
            onClose={() => setShowCreateForm(false)} 
            onSuccess={() => {
              setShowCreateForm(false);
              // Refresh records
              window.location.reload();
            }}
            darkMode={darkMode}
          />
        )}

        <div className="space-y-4">
          {records.map((record) => (
            <div key={record.id} className={`p-4 border rounded-lg ${darkMode ? 'border-gray-600' : 'border-gray-200'}`}>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-gray-800'}`}>{record.title}</h3>
                  <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    Type: {record.record_type} • {new Date(record.created_at).toLocaleDateString()}
                  </p>
                  {record.description && (
                    <p className={`mt-2 ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>{record.description}</p>
                  )}
                  {record.file_name && (
                    <div className={`mt-2 flex items-center text-sm ${darkMode ? 'text-blue-400' : 'text-blue-600'}`}>
                      <Paperclip className="h-4 w-4 mr-1" />
                      Attached: {record.file_name}
                    </div>
                  )}
                </div>
                <span className={`px-2 py-1 rounded text-xs ${
                  record.record_type === "prescription" ? "bg-green-100 text-green-800" :
                  record.record_type === "report" ? "bg-blue-100 text-blue-800" :
                  "bg-gray-100 text-gray-800"
                }`}>
                  {record.record_type}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function CreateRecordForm({ onClose, onSuccess, darkMode }) {
  const [formData, setFormData] = useState({
    patient_id: "",
    title: "",
    description: "",
    record_type: "notes"
  });
  const [patients, setPatients] = useState([]);

  useEffect(() => {
    const fetchPatients = async () => {
      try {
        const response = await axios.get(`${API}/patients/search`);
        setPatients(response.data);
      } catch (error) {
        console.error("Failed to fetch patients:", error);
      }
    };
    fetchPatients();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/medical-records`, formData);
      onSuccess();
    } catch (error) {
      console.error("Failed to create record:", error);
    }
  };

  return (
    <div className={`p-4 border rounded-lg mb-4 ${darkMode ? 'border-gray-600 bg-gray-700' : 'border-gray-200 bg-gray-50'}`}>
      <h3 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-800'}`}>Create Medical Record</h3>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className={`block text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-1`}>
            Patient
          </label>
          <select
            value={formData.patient_id}
            onChange={(e) => setFormData({...formData, patient_id: e.target.value})}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500 ${
              darkMode ? 'bg-gray-600 border-gray-500 text-white' : 'bg-white border-gray-300'
            }`}
            required
          >
            <option value="">Select a patient</option>
            {patients.map((patient) => (
              <option key={patient.user_id} value={patient.user_id}>
                {patient.name} - {patient.email}
              </option>
            ))}
          </select>
        </div>
        
        <div>
          <label className={`block text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-1`}>
            Title
          </label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => setFormData({...formData, title: e.target.value})}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500 ${
              darkMode ? 'bg-gray-600 border-gray-500 text-white' : 'bg-white border-gray-300'
            }`}
            required
          />
        </div>
        
        <div>
          <label className={`block text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-1`}>
            Type
          </label>
          <select
            value={formData.record_type}
            onChange={(e) => setFormData({...formData, record_type: e.target.value})}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500 ${
              darkMode ? 'bg-gray-600 border-gray-500 text-white' : 'bg-white border-gray-300'
            }`}
          >
            <option value="notes">Notes</option>
            <option value="prescription">Prescription</option>
            <option value="report">Report</option>
          </select>
        </div>
        
        <div>
          <label className={`block text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-1`}>
            Description
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({...formData, description: e.target.value})}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500 ${
              darkMode ? 'bg-gray-600 border-gray-500 text-white' : 'bg-white border-gray-300'
            }`}
            rows="3"
          />
        </div>
        
        <div className="flex space-x-2">
          <button
            type="submit"
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Create Record
          </button>
          <button
            type="button"
            onClick={onClose}
            className={`px-4 py-2 rounded-lg ${darkMode ? 'bg-gray-600 text-white hover:bg-gray-500' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}`}
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

// Chat Tab
function ChatTab({ user, darkMode }) {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!inputMessage.trim() || loading) return;

    const userMessage = inputMessage;
    setInputMessage("");
    setLoading(true);

    // Add user message to chat
    const newMessages = [...messages, { role: "user", content: userMessage }];
    setMessages(newMessages);

    try {
      const response = await axios.post(`${API}/chat`, { message: userMessage });
      setMessages([...newMessages, { role: "assistant", content: response.data.response }]);
    } catch (error) {
      console.error("Chat error:", error);
      setMessages([...newMessages, { role: "assistant", content: "Sorry, I'm having trouble responding right now. Please try again later." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className={`rounded-xl shadow-lg h-96 flex flex-col ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
      <div className={`p-4 border-b ${darkMode ? 'border-gray-700' : 'border-gray-200'}`}>
        <h2 className={`text-xl font-bold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
          AI Health Assistant
        </h2>
        <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
          {user.role === "patient" 
            ? "Ask me about your health data, medications, uploaded files, or general health questions" 
            : "Get help with patient summaries, treatment suggestions, and medical insights"
          }
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className={`text-center py-8 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
            <MessageCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Start a conversation with your AI health assistant!</p>
            {user.role === "patient" && (
              <p className="text-xs mt-2">I can help you understand your medical records, explain uploaded files, and provide health insights.</p>
            )}
          </div>
        )}
        
        {messages.map((message, index) => (
          <div key={index} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
              message.role === "user"
                ? "bg-blue-600 text-white"
                : darkMode
                  ? "bg-gray-700 text-white"
                  : "bg-gray-100 text-gray-800"
            }`}>
              <div className="whitespace-pre-wrap">{message.content}</div>
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="flex justify-start">
            <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
              darkMode ? 'bg-gray-700' : 'bg-gray-100'
            }`}>
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className={`p-4 border-t ${darkMode ? 'border-gray-700' : 'border-gray-200'}`}>
        <div className="flex space-x-2">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about your health records, uploaded files, or get health advice..."
            className={`flex-1 px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500 resize-none ${
              darkMode ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' : 'bg-white border-gray-300'
            }`}
            rows="1"
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !inputMessage.trim()}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;