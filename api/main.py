import os
import requests
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Mengambil API Key dari Environment Variable (Aman)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# --- Konfigurasi Backend ---
CREATOR_NAME = "Risky HariAdi"
# Nomor WA admin dengan kode negara 62 untuk integrasi wa.me yang benar
ADMIN_PHONE = "6287791881535" 

# --- Database Sederhana (In-Memory) ---
# Catatan: Di Vercel data ini akan reset secara berkala. 
# Gunakan Database eksternal (Supabase/Firebase) untuk penyimpanan permanen.
db = {
    "users": [
        {"username": "admin", "password": "085691230968", "role": "admin", "name": "Risky HariAdi"},
        {"username": "user1", "password": "123", "role": "user", "name": "pengguna baru"}
    ]
}

# --- Frontend HTML + React ---
HTML_TEMPLATE = """
{% raw %}
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EduHub - Student Productivity Hub</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
        body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #F8FAFC; }
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
        .animate-fade { animation: fadeIn 0.4s ease-out forwards; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect, useRef } = React;

        // --- Custom Icon Component (Fix Illegal Constructor) ---
        const LucideIcon = ({ name, size = 20, className = "" }) => {
            useEffect(() => { if (window.lucide) window.lucide.createIcons(); }, [name]);
            return <i data-lucide={name} style={{ width: size, height: size }} className={`inline-block shrink-0 ${className}`}></i>;
        };

        const App = () => {

            const CREATOR_NAME = "Risky HariAdi";
            const ADMIN_NUMBER = "6287791881535"; 

            // Auth States
            const [isLoggedIn, setIsLoggedIn] = useState(false);
            const [currentUser, setCurrentUser] = useState(null);
            const [loginForm, setLoginForm] = useState({ username: "", password: "" });
            const [authError, setAuthError] = useState("");

            // UI States
            const [activeTab, setActiveTab] = useState('ai');
            const [isSidebarOpen, setIsSidebarOpen] = useState(false);
            const [showDonationModal, setShowDonationModal] = useState(false);

            // Data States
            const [allowedUsers, setAllowedUsers] = useState([]);
            const [tasks, setTasks] = useState([
                { id: 1, text: "Selesaikan Laporan Praktikum", completed: false },
                { id: 2, text: "Review Jurnal AI", completed: true }
            ]);
            const [schedule, setSchedule] = useState([
                { id: 1, day: "Senin", time: "08:00", course: "Kalkulus II", room: "L-1" }
            ]);
            const [gpaCourses, setGpaCourses] = useState([
                { id: 1, name: "Algoritma", sks: 3, grade: "A" }
            ]);
            const [messages, setMessages] = useState([{ role: 'assistant', content: "Halo! Saya IG.STORE AI. Ada yang bisa saya bantu dengan tugas kuliahmu hari ini?" }]);
            const [transactions, setTransactions] = useState([
                { id: 1, title: "Uang Saku", amount: 1500000, type: "income" }
            ]);
            
            // Input States
            const [chatInput, setChatInput] = useState("");
            const [isLoading, setIsLoading] = useState(false);
            const [journalQuery, setJournalQuery] = useState("");
            const [journalResults, setJournalResults] = useState([]);
            const [yearFilter, setYearFilter] = useState({ from: 2021, to: 2025 });

            // Form States
            const [adminNewUser, setAdminNewUser] = useState({ username: "", password: "", name: "" });
            const [taskInput, setTaskInput] = useState("");
            const [classForm, setClassForm] = useState({ day: "Senin", time: "", course: "", room: "" });
            const [gpaForm, setGpaForm] = useState({ name: "", sks: 3, grade: "A" });
            const [transForm, setTransForm] = useState({ title: "", amount: "", type: "expense" });

            const [timeLeft, setTimeLeft] = useState(25 * 60);
            const [isTimerActive, setIsTimerActive] = useState(false);
            const [timerMode, setTimerMode] = useState('pomodoro');

            const chatEndRef = useRef(null);
            const gradePoints = { "A": 4, "A-": 3.75, "B+": 3.5, "B": 3, "C+": 2.5, "C": 2, "D": 1, "E": 0 };

            // Fetch Initial Users
            useEffect(() => {
                fetch('/api/users').then(res => res.json()).then(data => setAllowedUsers(data));
            }, []);

            useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

            useEffect(() => {
                let interval = null;
                if (isTimerActive && timeLeft > 0) {
                    interval = setInterval(() => setTimeLeft(prev => prev - 1), 1000);
                } else if (timeLeft === 0) {
                    setIsTimerActive(false);
                }
                return () => clearInterval(interval);
            }, [isTimerActive, timeLeft]);

            // Handlers: Auth
            const handleLogin = (e) => {
                e.preventDefault();
                const user = allowedUsers.find(u => u.username === loginForm.username && u.password === loginForm.password);
                if (user) {
                    setIsLoggedIn(true);
                    setCurrentUser(user);
                    setActiveTab(user.role === 'admin' ? 'admin' : 'ai');
                    setAuthError("");
                } else {
                    setAuthError("Username atau password salah!");
                }
            };

            const handleLogout = () => {
                setIsLoggedIn(false);
                setCurrentUser(null);
                setLoginForm({ username: "", password: "" });
            };

            // --- Handlers: AI ---
            const handleSendMessage = async () => {
            if (!chatInput.trim()) return;
            
            const currentInput = chatInput;
            setMessages(prev => [...prev, { role: 'user', content: currentInput }]);
            setChatInput("");
            setIsLoading(true);

    try {
        // PERUBAHAN DI SINI: Panggil endpoint internal Flask, bukan API Google langsung
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                message: currentInput 
            })
        });

            if (!response.ok) throw new Error("Gagal menghubungi server backend.");

            const data = await response.json();
            
            // Ambil teks dari respon yang dikirim balik oleh Flask
            const aiText = data.candidates?.[0]?.content?.parts?.[0]?.text || "Maaf, saya tidak mendapatkan respon.";
            
            setMessages(prev => [...prev, { role: 'assistant', content: String(aiText) }]);
        } catch (err) {
            console.error(err);
            setMessages(prev => [...prev, { role: 'assistant', content: "Terjadi kesalahan koneksi ke backend. Pastikan server berjalan dan API Key terkonfigurasi di Vercel." }]);
        } finally {
            setIsLoading(false);
        }
    };
                    if (!response.ok) throw new Error("Gagal menghubungi AI");

                    const data = await response.json();
                    const aiText = data.candidates?.[0]?.content?.parts?.[0]?.text || "Maaf, saya tidak mendapatkan respon dari server AI.";
                    
                    setMessages(prev => [...prev, { role: 'assistant', content: String(aiText) }]);
                } catch (err) {
                    setMessages(prev => [...prev, { role: 'assistant', content: "Terjadi kesalahan saat menghubungi asisten AI. Pastikan API Key sudah benar." }]);
                } finally {
                    setIsLoading(false);
                }
            };

            // Handlers: Journal
            const handleSearchJournal = async () => {
                if (!journalQuery.trim()) return;
                setIsLoading(true);
                try {
                    const res = await fetch(`https://api.crossref.org/works?query=${encodeURIComponent(journalQuery)}&filter=from-pub-date:${yearFilter.from},until-pub-date:${yearFilter.to}&rows=10`);
                    const data = await res.json();
                    const items = data.message.items.map(i => ({
                        id: String(i.DOI || Math.random()),
                        title: String(i.title?.[0] || "No Title"),
                        author: String(i.author?.[0]?.family || "Anonim"),
                        year: String(i.created?.['date-parts']?.[0]?.[0] || "-"),
                        publisher: String(i.publisher || "Unknown"),
                        url: String(i.URL || "#")
                    }));
                    setJournalResults(items);
                } catch (e) { setJournalResults([]); }
                finally { setIsLoading(false); }
            };

            // Handlers: Planner
            const addTask = () => {
                if(!taskInput.trim()) return;
                setTasks([{id: Date.now(), text: taskInput, completed: false}, ...tasks]);
                setTaskInput("");
            };
            const toggleTask = (id) => setTasks(tasks.map(t => t.id === id ? {...t, completed: !t.completed} : t));
            const deleteTask = (id) => setTasks(tasks.filter(t => t.id !== id));

            // Handlers: Timetable
            const addClass = () => {
                if(!classForm.course || !classForm.time) return;
                setSchedule([...schedule, {...classForm, id: Date.now()}]);
                setClassForm({...classForm, course: "", time: "", room: ""});
            };
            const deleteClass = (id) => setSchedule(schedule.filter(s => s.id !== id));

            // Handlers: GPA
            const addCourse = () => {
                if(!gpaForm.name || !gpaForm.sks) return;
                setGpaCourses([...gpaCourses, {...gpaForm, id: Date.now()}]);
                setGpaForm({name: "", sks: 3, grade: "A"});
            };
            const deleteCourse = (id) => setGpaCourses(gpaCourses.filter(c => c.id !== id));
            const calculateGPA = () => {
                let totalPoints = 0;
                let totalSKS = 0;
                gpaCourses.forEach(c => {
                    totalPoints += (gradePoints[c.grade] || 0) * Number(c.sks);
                    totalSKS += Number(c.sks);
                });
                return totalSKS === 0 ? "0.00" : (totalPoints / totalSKS).toFixed(2);
            };

            // Handlers: Budgeting
            const addTransaction = () => {
                if(!transForm.title || !transForm.amount) return;
                const amt = parseInt(transForm.amount) * (transForm.type === 'expense' ? -1 : 1);
                setTransactions([{id: Date.now(), title: transForm.title, amount: amt, type: transForm.type}, ...transactions]);
                setTransForm({title: "", amount: "", type: "expense"});
            };
            const deleteTransaction = (id) => setTransactions(transactions.filter(t => t.id !== id));

            // Handlers: Admin
            const addUserByAdmin = () => {
                if(!adminNewUser.username || !adminNewUser.password) return;
                const newUser = { ...adminNewUser, role: 'user' };
                fetch('/api/users', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(newUser)
                }).then(res => res.json()).then(data => {
                    setAllowedUsers(data);
                    setAdminNewUser({ username: "", password: "", name: "" });
                });
            };
            const removeUserByAdmin = (username) => {
                if(username === 'admin') return;
                setAllowedUsers(allowedUsers.filter(u => u.username !== username));
            };

            const formatIDR = (n) => new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(n);
            const formatTime = (s) => `${Math.floor(s/60).toString().padStart(2,'0')}:${(s%60).toString().padStart(2,'0')}`;

            if (!isLoggedIn) {
                return (
                    <div className="h-screen flex items-center justify-center p-6 bg-slate-50">
                        <div className="max-w-md w-full bg-white rounded-[2.5rem] shadow-2xl overflow-hidden border border-slate-100 animate-fade">
                            <div className="bg-indigo-600 p-12 text-center text-white relative overflow-hidden">
                                <div className="absolute top-0 right-0 p-4 opacity-10"><LucideIcon name="sparkles" size={120}/></div>
                                <LucideIcon name="book-open" size={48} className="mx-auto mb-4" />
                                <h1 className="text-4xl font-black tracking-tighter text-white leading-none">EduHub</h1>
                                <p className="text-indigo-100 text-xs font-bold uppercase tracking-widest mt-3 opacity-80 leading-none">Smart Student Hub</p>
                            </div>
                            <form className="p-10 space-y-6" onSubmit={handleLogin}>
                                {authError && <div className="bg-rose-50 text-rose-600 p-4 rounded-2xl text-[11px] font-bold text-center border border-rose-100 animate-pulse">{authError}</div>}
                                <div className="space-y-4 text-left text-slate-700">
                                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1 block">Username</label>
                                    <input className="w-full bg-slate-50 border-2 rounded-2xl px-6 py-4 text-sm font-bold focus:border-indigo-600 outline-none transition-all shadow-inner" value={loginForm.username} onChange={e => setLoginForm({...loginForm, username: e.target.value})} required />
                                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1 block">Password</label>
                                    <input type="password" className="w-full bg-slate-50 border-2 rounded-2xl px-6 py-4 text-sm font-bold focus:border-indigo-600 outline-none transition-all shadow-inner" value={loginForm.password} onChange={e => setLoginForm({...loginForm, password: e.target.value})} required />
                                </div>
                                <button type="submit" className="w-full bg-indigo-600 text-white font-black py-5 rounded-2xl shadow-xl hover:bg-indigo-700 active:scale-95 transition-all text-xs uppercase tracking-widest leading-none">Sign In</button>
                                <div className="pt-8 border-t text-center space-y-4">
                                    <button type="button" onClick={() => window.open(`https://wa.me/${ADMIN_NUMBER}?text=Halo%20Admin%20Risky,%20saya%20ingin%20mendaftar%20akun%20EduHub.`)} className="text-indigo-600 font-black text-[11px] flex items-center justify-center gap-2 mx-auto hover:underline uppercase tracking-tighter transition-all"><LucideIcon name="message-circle" size={14}/> Daftar via WhatsApp Admin</button>
                                    <p className="text-[9px] text-slate-400 font-bold uppercase tracking-widest opacity-60 leading-none">Developed by {CREATOR_NAME}</p>
                                </div>
                            </form>
                        </div>
                    </div>
                );
            }

            return (
                <div className="flex flex-col md:flex-row h-screen overflow-hidden text-slate-800">
                    <aside className={`fixed md:relative inset-y-0 left-0 w-72 bg-white border-r border-slate-100 p-8 flex flex-col gap-6 z-[60] transition-transform duration-500 md:translate-x-0 ${isSidebarOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full'}`}>
                        <div className="flex items-center gap-4 mb-2">
                            <div className="bg-indigo-600 p-2.5 rounded-2xl text-white shadow-xl shadow-indigo-100"><LucideIcon name="book-open" size={26} /></div>
                            <div>
                                <h1 className="text-2xl font-black text-slate-900 leading-none tracking-tight">EduHub<span className="text-indigo-600">.</span></h1>
                                <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest mt-1.5 opacity-60">Smart Suite</p>
                            </div>
                        </div>

                        <nav className="space-y-1 overflow-y-auto pr-2 custom-scrollbar text-left flex-1">
                            <p className="text-[10px] font-black text-slate-300 uppercase tracking-widest mb-4 px-3">Layanan</p>
                            {[
                                {id:'ai', icon:'sparkles', label:'Asisten AI'},
                                {id:'journal', icon:'search', label:'Cari Jurnal'},
                                {id:'planner', icon:'check-circle', label:'Planner Tugas'},
                                {id:'schedule', icon:'calendar', label:'Jadwal Kelas'},
                                {id:'timer', icon:'timer', label:'Pomodoro'},
                                {id:'gpa', icon:'calculator', label:'Indeks IPK'},
                                {id:'budget', icon:'wallet', label:'Keuangan'}
                            ].map(item => (
                                <button key={item.id} onClick={() => {setActiveTab(item.id); setIsSidebarOpen(false);}} className={`w-full flex items-center gap-4 p-4 rounded-2xl font-bold transition-all ${activeTab === item.id ? 'bg-indigo-600 text-white shadow-xl translate-x-2' : 'text-slate-500 hover:bg-slate-50'}`}>
                                    <LucideIcon name={item.icon} size={20} /> <span className="text-sm tracking-tight">{item.label}</span>
                                </button>
                            ))}
                            
                            {currentUser.role === 'admin' && (
                                <>
                                    <p className="text-[10px] font-black text-indigo-300 uppercase tracking-widest mt-8 mb-4 px-3">Management</p>
                                    <button onClick={() => {setActiveTab('admin'); setIsSidebarOpen(false);}} className={`w-full flex items-center gap-4 p-4 rounded-2xl font-bold transition-all ${activeTab === 'admin' ? 'bg-indigo-100 text-indigo-700 shadow-inner' : 'text-indigo-600 hover:bg-indigo-50'}`}>
                                        <LucideIcon name="shield-check" size={20} /> <span className="text-sm tracking-tight">Admin Portal</span>
                                    </button>
                                </>
                            )}
                        </nav>

                        <div className="mt-auto pt-6 border-t border-slate-50 space-y-4">
                            <button onClick={() => setShowDonationModal(true)} className="w-full flex items-center gap-4 p-4 bg-amber-50 text-amber-700 rounded-2xl border border-amber-100 font-bold text-xs hover:bg-amber-100 transition-all group">
                                <LucideIcon name="heart" size={16} className="fill-amber-500 text-amber-500 group-hover:scale-110 transition-all" /> <span>Support {CREATOR_NAME}</span>
                            </button>
                            <div className="flex items-center gap-4 bg-slate-50 p-4 rounded-2xl border border-slate-100">
                                <div className="w-10 h-10 rounded-[0.8rem] bg-indigo-600 text-white flex items-center justify-center font-black uppercase text-lg shadow-lg">{(currentUser.username)[0]}</div>
                                <div className="flex-1 overflow-hidden text-left leading-none">
                                    <p className="text-sm font-black truncate leading-none">{currentUser.name}</p>
                                    <p className="text-[9px] font-bold text-indigo-500 uppercase mt-1.5 opacity-70 tracking-widest">{currentUser.role}</p>
                                </div>
                                <button onClick={handleLogout} className="text-slate-300 hover:text-rose-500 p-2 transition-all hover:scale-110"><LucideIcon name="log-out" size={18}/></button>
                            </div>
                        </div>
                    </aside>

                    <main className="flex-1 overflow-y-auto p-5 md:p-14 bg-[#F9FAFC] relative">
                        {isSidebarOpen && <div onClick={() => setIsSidebarOpen(false)} className="fixed inset-0 bg-slate-900/60 backdrop-blur-md z-[55] md:hidden transition-all"></div>}
                        <button onClick={() => setIsSidebarOpen(true)} className="md:hidden absolute top-5 left-5 p-3 bg-white rounded-xl shadow-lg border z-40 text-slate-600"><LucideIcon name="menu" /></button>

                        <div className="animate-fade max-w-5xl mx-auto">
                            {/* --- TAB AI --- */}
                            {activeTab === 'ai' && (
                                <div className="max-w-4xl mx-auto h-[calc(100vh-160px)] flex flex-col bg-white rounded-[3rem] border border-slate-100 shadow-2xl overflow-hidden">
                                    <div className="p-8 border-b bg-[#FAFBFF] flex items-center justify-between px-10">
                                        <div className="flex items-center gap-5 text-left"><div className="w-14 h-14 bg-indigo-600 rounded-2xl flex items-center justify-center text-white shadow-xl shadow-indigo-100"><LucideIcon name="sparkles" size={28}/></div><div><h3 className="text-xl font-black text-slate-900 leading-none tracking-tight">Halo saya adalah asisten belajar kamu</h3><p className="text-[10px] text-emerald-500 font-bold mt-1.5 uppercase tracking-widest flex items-center gap-1.5 leading-none"><span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> Gemini 2.5 Flash</p></div></div>
                                    </div>
                                    <div className="flex-1 overflow-y-auto p-10 space-y-8 bg-slate-50/20 text-left text-slate-700 custom-scrollbar">
                                        {messages.map((m, i) => (
                                            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                                <div className={`max-w-[85%] md:max-w-[75%] p-6 rounded-[2.5rem] text-sm font-medium leading-relaxed shadow-sm transition-all hover:scale-[1.01] ${m.role === 'user' ? 'bg-gradient-to-br from-indigo-600 to-indigo-800 text-white rounded-tr-none shadow-xl shadow-indigo-100' : 'bg-white border border-slate-100 text-slate-700 rounded-tl-none'}`}>
                                                    {String(m.content)}
                                                </div>
                                            </div>
                                        ))}
                                        {isLoading && <div className="flex justify-start"><div className="bg-white p-5 rounded-[2rem] border border-slate-100 flex gap-3 items-center font-black text-xs text-indigo-600 shadow-sm"><div className="w-2.5 h-2.5 bg-indigo-400 rounded-full animate-bounce"></div>Sedang Mengetik...</div></div>}
                                        <div ref={chatEndRef}></div>
                                    </div>
                                    <div className="p-8 border-t border-slate-50 bg-white flex gap-5">
                                        <input className="flex-1 bg-slate-50 border-2 border-slate-50 rounded-2xl px-8 py-5 text-sm font-bold outline-none focus:border-indigo-600 focus:bg-white transition-all shadow-inner focus:ring-8 focus:ring-indigo-500/5" placeholder="Tanyakan materi perkuliahan..." value={chatInput} onChange={e => setChatInput(e.target.value)} onKeyPress={e => e.key === 'Enter' && handleSendMessage()} />
                                        <button onClick={handleSendMessage} disabled={isLoading || !chatInput.trim()} className="bg-indigo-600 text-white p-5 rounded-2xl shadow-xl hover:bg-indigo-700 active:scale-95 transition-all border-b-4 border-indigo-900 disabled:opacity-50"><LucideIcon name="send" size={26}/></button>
                                    </div>
                                </div>
                            )}

                            {/* --- TAB JOURNAL --- */}
                            {activeTab === 'journal' && (
                                <div className="space-y-12 text-left pb-10">
                                    <header>
                                        <h2 className="text-5xl font-black text-slate-900 tracking-tighter leading-none">Journal Discovery</h2>
                                        <p className="text-slate-500 font-semibold mt-4 text-lg max-w-2xl leading-relaxed">Pencarian literatur ilmiah real-time dari database Crossref untuk mendukung tugas akhir Anda.</p>
                                    </header>
                                    <div className="bg-white p-10 rounded-[3.5rem] border border-slate-100 shadow-2xl space-y-8 relative overflow-hidden">
                                        <div className="flex flex-col md:flex-row gap-5 relative">
                                            <div className="flex-1 relative text-left">
                                                <LucideIcon name="search" size={24} className="absolute left-6 top-1/2 -translate-y-1/2 text-slate-400" />
                                                <input className="w-full pl-16 pr-8 py-6 bg-slate-50 border-2 border-slate-50 rounded-[1.8rem] text-lg font-black outline-none focus:bg-white focus:border-indigo-600 transition-all shadow-inner" placeholder="Judul, Topik, atau Peneliti..." value={journalQuery} onChange={e => setJournalQuery(e.target.value)} onKeyPress={e => e.key === 'Enter' && handleSearchJournal()} />
                                            </div>
                                            <button onClick={handleSearchJournal} disabled={isLoading} className="bg-indigo-600 text-white px-14 py-6 rounded-[1.8rem] font-black text-sm uppercase tracking-widest hover:bg-indigo-700 shadow-2xl active:scale-95 transition-all">{isLoading ? 'Search...' : 'Cari'}</button>
                                        </div>
                                        <div className="flex flex-wrap items-center gap-8 pt-8 border-t border-slate-50">
                                            <div className="flex items-center gap-3"><LucideIcon name="filter" size={20} className="text-indigo-600" /><span className="text-[11px] font-black text-slate-400 uppercase tracking-widest">Tahun Terbit:</span></div>
                                            <div className="flex items-center gap-4">
                                                <input type="number" className="w-28 bg-slate-50 p-4 rounded-2xl text-sm font-black text-center border-2 border-slate-50 focus:border-indigo-600 focus:bg-white outline-none" value={yearFilter.from} onChange={e => setYearFilter({...yearFilter, from: e.target.value})} />
                                                <span className="text-slate-300 font-black">-</span>
                                                <input type="number" className="w-28 bg-slate-50 p-4 rounded-2xl text-sm font-black text-center border-2 border-slate-50 focus:border-indigo-600 focus:bg-white outline-none" value={yearFilter.to} onChange={e => setYearFilter({...yearFilter, to: e.target.value})} />
                                            </div>
                                        </div>
                                    </div>
                                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 pb-12 text-left">
                                        {journalResults.map(j => (
                                            <div key={j.id} className="bg-white p-9 rounded-[3rem] border border-slate-100 shadow-sm hover:shadow-2xl transition-all group flex flex-col h-full text-left hover:-translate-y-2">
                                                <div className="flex justify-between items-start mb-6"><span className="bg-indigo-50 text-indigo-700 text-[10px] font-black px-4 py-2 rounded-xl border border-indigo-100 truncate max-w-[150px] uppercase tracking-widest shadow-sm">{String(j.publisher)}</span><span className="text-xs font-black text-slate-400">{String(j.year)}</span></div>
                                                <h3 className="text-xl font-black text-slate-900 mb-4 group-hover:text-indigo-600 transition-colors line-clamp-3 leading-snug">{String(j.title)}</h3>
                                                <button onClick={() => window.open(j.url, '_blank')} className="mt-auto w-full bg-slate-50 text-slate-800 py-4 rounded-2xl text-[11px] font-black uppercase tracking-widest hover:bg-indigo-600 hover:text-white transition-all border border-slate-100 flex items-center justify-center gap-3">Buka Jurnal <LucideIcon name="external-link" size={14}/></button>
                                            </div>
                                        ))}
                                    </div>
                                    {isLoading && activeTab === 'journal' && <div className="py-28 text-center space-y-6"><div className="w-16 h-16 border-[6px] border-indigo-100 border-t-indigo-600 rounded-full animate-spin mx-auto"></div><p className="text-lg font-black text-indigo-500 animate-pulse uppercase tracking-widest">Mencari Hasil...</p></div>}
                                </div>
                            )}

                            {/* --- TAB PLANNER --- */}
                            {activeTab === 'planner' && (
                                <div className="max-w-4xl mx-auto space-y-12 text-left pb-20">
                                    <h2 className="text-5xl font-black text-slate-900 tracking-tighter leading-none">Task Planner</h2>
                                    <div className="bg-white p-10 rounded-[3.5rem] border border-slate-100 shadow-2xl flex flex-col sm:flex-row gap-5 transition-all focus-within:ring-[12px] focus-within:ring-indigo-500/5">
                                        <input className="flex-1 bg-slate-50 border-2 border-slate-50 rounded-[1.5rem] px-8 py-5 text-lg font-bold outline-none focus:bg-white focus:border-indigo-600 transition-all shadow-inner" placeholder="Tugas baru hari ini?" value={taskInput} onChange={e => setTaskInput(e.target.value)} onKeyPress={e => e.key === 'Enter' && addTask()} />
                                        <button onClick={addTask} className="bg-indigo-600 text-white px-12 py-5 sm:py-0 rounded-[1.5rem] font-black text-sm uppercase tracking-widest hover:bg-indigo-700 shadow-2xl border-b-4 border-indigo-900 active:scale-95 transition-all">Tambah</button>
                                    </div>
                                    <div className="space-y-5">
                                        {tasks.length > 0 ? tasks.map(t => (
                                            <div key={t.id} className="bg-white p-8 rounded-[2.5rem] border border-slate-100 flex items-center gap-7 group hover:border-indigo-400 transition-all shadow-sm hover:shadow-xl hover:-translate-x-3">
                                                <button onClick={() => toggleTask(t.id)} className={`w-12 h-12 rounded-2xl border-[4px] flex items-center justify-center transition-all ${t.completed ? 'bg-emerald-500 border-emerald-500 text-white shadow-xl shadow-emerald-100 rotate-[360deg]' : 'border-slate-100 bg-slate-50 shadow-inner'}`}>
                                                    {t.completed && <LucideIcon name="check" size={24}/>}
                                                </button>
                                                <span className={`flex-1 text-lg font-black text-left transition-all ${t.completed ? 'text-slate-300 line-through' : 'text-slate-800'}`}>{String(t.text)}</span>
                                                <button onClick={() => deleteTask(t.id)} className="text-slate-200 hover:text-rose-500 p-3 hover:bg-rose-50 rounded-2xl transition-all opacity-0 group-hover:opacity-100 hover:scale-110"><LucideIcon name="trash-2" size={24}/></button>
                                            </div>
                                        )) : (
                                            <div className="py-24 text-center bg-white border-2 border-dashed border-slate-100 rounded-[3rem] opacity-30 italic"><p className="font-bold uppercase tracking-widest text-xs">Belum ada tugas hari ini.</p></div>
                                        )}
                                    </div>
                                </div>
                            )}

                            {/* --- TAB JADWAL --- */}
                            {activeTab === 'schedule' && (
                                <div className="max-w-6xl mx-auto space-y-12 text-left pb-10 text-left">
                                    <h2 className="text-5xl font-black text-slate-900 tracking-tighter leading-none text-left">University Timetable</h2>
                                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6 text-left">
                                        {["Senin", "Selasa", "Rabu", "Kamis", "Jumat"].map(day => (
                                            <div key={day} className="bg-white p-7 rounded-[2.5rem] border border-slate-100 shadow-xl flex flex-col min-h-[350px] group hover:shadow-2xl transition-all">
                                                <h3 className="font-black text-indigo-600 mb-6 border-b-2 border-indigo-50 pb-4 uppercase tracking-[0.2em] text-[11px] flex justify-between items-center">{day} <div className="w-2 h-2 rounded-full bg-indigo-200 group-hover:scale-150 transition-all"></div></h3>
                                                <div className="space-y-4 flex-1">
                                                    {schedule.filter(s => s.day === day).map(s => (
                                                        <div key={s.id} className="relative bg-[#F8FAFC] p-5 rounded-[1.8rem] border border-slate-100 group/item hover:bg-indigo-600 hover:text-white transition-all shadow-sm">
                                                            <div className="flex items-center gap-2 mb-2 text-indigo-400 group-hover/item:text-white"><LucideIcon name="clock" size={12}/><p className="text-[10px] font-black uppercase tracking-widest">{String(s.time)}</p></div>
                                                            <p className="text-xs font-black group-hover/item:text-white leading-tight mb-2 capitalize">{String(s.course)}</p>
                                                            <p className="text-[9px] text-slate-400 font-bold group-hover/item:text-indigo-200 uppercase tracking-widest">{String(s.room)}</p>
                                                            <button onClick={() => deleteClass(s.id)} className="absolute top-4 right-4 text-slate-200 hover:text-rose-500 opacity-0 group-hover/item:opacity-100 p-1 bg-white/10 rounded-lg transition-all"><LucideIcon name="x" size={14}/></button>
                                                        </div>
                                                    ))}
                                                    {schedule.filter(s => s.day === day).length === 0 && <div className="h-full flex flex-col items-center justify-center text-[10px] text-slate-300 font-bold uppercase tracking-widest opacity-40 italic"><LucideIcon name="clock" size={24} className="mb-2" /> Free Day</div>}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                    <div className="bg-white p-10 rounded-[3rem] border border-slate-100 max-w-2xl shadow-2xl text-left shadow-indigo-50">
                                        <h4 className="font-black mb-8 text-xs uppercase text-slate-400 tracking-widest flex items-center gap-3 leading-none font-bold"><LucideIcon name="plus-circle" size={20} className="text-indigo-600" /> Tambah Jadwal Baru</h4>
                                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-8 text-left leading-none font-bold">
                                            <div className="space-y-3"><label className="text-[10px] font-black uppercase block text-slate-400 ml-1">Hari</label><select className="w-full bg-slate-50 border-2 border-slate-100 rounded-2xl p-4 text-sm font-bold outline-none focus:border-indigo-600" value={classForm.day} onChange={e => setClassForm({...classForm, day: e.target.value})}>{["Senin", "Selasa", "Rabu", "Kamis", "Jumat"].map(d => <option key={d} value={d}>{d}</option>)}</select></div>
                                            <div className="space-y-3"><label className="text-[10px] font-black uppercase block text-slate-400 ml-1">Jam</label><input type="time" className="w-full bg-slate-50 border-2 border-slate-100 rounded-2xl p-4 text-sm font-bold outline-none focus:border-indigo-600" value={classForm.time} onChange={e => setClassForm({...classForm, time: e.target.value})} /></div>
                                            <div className="space-y-3 md:col-span-2 text-left leading-none"><label className="text-[10px] font-black uppercase block text-slate-400 ml-1">Mata Kuliah</label><input placeholder="Contoh: Pemrograman Mobile" className="w-full bg-slate-50 border-2 border-slate-100 rounded-2xl p-4 text-sm font-bold outline-none focus:border-indigo-600" value={classForm.course} onChange={e => setClassForm({...classForm, course: e.target.value})} /></div>
                                        </div>
                                        <button onClick={addClass} className="w-full bg-indigo-600 text-white py-5 rounded-[1.8rem] font-black text-sm uppercase tracking-widest shadow-xl border-b-4 border-indigo-900 transition-all active:scale-95 active:translate-y-1 shadow-indigo-100">Simpan Jadwal</button>
                                    </div>
                                </div>
                            )}

                            {/* --- TAB POMODORO --- */}
                            {activeTab === 'timer' && (
                                <div className="max-w-3xl mx-auto pt-10 flex flex-col items-center pb-20 animate-fade">
                                    <div className="bg-white w-full rounded-[5rem] shadow-2xl border border-slate-100 p-20 text-center relative overflow-hidden transition-all duration-700 shadow-indigo-50/50">
                                        <div className={`absolute top-0 left-0 w-full h-5 transition-all duration-700 ${timerMode === 'pomodoro' ? 'bg-indigo-600' : 'bg-emerald-500'}`}></div>
                                        <div className="flex justify-center gap-6 mb-16 relative">
                                            {['pomodoro', 'short'].map(m => (
                                                <button key={m} onClick={() => {setTimerMode(m); setTimeLeft(m === 'pomodoro' ? 25*60 : 5*60); setIsTimerActive(false);}} className={`px-12 py-4 rounded-[1.2rem] text-xs font-black uppercase tracking-widest transition-all ${timerMode === m ? 'bg-indigo-600 text-white shadow-xl shadow-indigo-100' : 'bg-slate-50 text-slate-400 hover:bg-slate-100 border border-slate-100'}`}>{m === 'pomodoro' ? 'Fokus' : 'Break'}</button>
                                            ))}
                                        </div>
                                        <h1 className="text-[12rem] font-black text-slate-900 mb-14 font-mono tracking-tighter leading-none select-none drop-shadow-xl">{formatTime(timeLeft)}</h1>
                                        <div className="flex gap-8 justify-center items-center">
                                            <button onClick={() => setIsTimerActive(!isTimerActive)} className={`px-24 py-8 rounded-[3rem] text-3xl font-black transition-all shadow-2xl ${isTimerActive ? 'bg-white text-slate-600 border-4 border-slate-100 shadow-none' : 'bg-indigo-600 text-white hover:bg-indigo-700 active:scale-95 shadow-indigo-100'}`}>{isTimerActive ? 'Pause' : 'Start Focus'}</button>
                                            <button onClick={() => {setIsTimerActive(false); setTimeLeft(timerMode === 'pomodoro' ? 25*60 : 5*60);}} className="p-8 rounded-[3rem] bg-slate-50 text-slate-300 hover:text-indigo-600 border border-slate-100 transition-all hover:rotate-180 duration-700 shadow-sm group active:scale-90"><LucideIcon name="rotate-ccw" size={44} /></button>
                                        </div>
                                    </div>
                                    <div className="mt-16 text-center p-10 bg-white border border-indigo-50 rounded-[3rem] shadow-sm max-w-md shadow-indigo-50/50 leading-relaxed font-bold text-indigo-800 animate-pulse transition-all"><p>"Waktunya fokus! Singkirkan distraksi dan berikan yang terbaik untuk studi Anda hari ini."</p></div>
                                </div>
                            )}

                            {/* --- TAB GPA --- */}
                            {activeTab === 'gpa' && (
                                <div className="max-w-5xl mx-auto space-y-12 text-left pb-20 animate-fade">
                                    <header className="flex flex-col md:flex-row justify-between items-center gap-8 text-left">
                                        <div><h2 className="text-5xl font-black text-slate-900 tracking-tighter leading-none text-left">GPA Simulator</h2><p className="text-slate-500 font-semibold mt-4 text-lg text-left leading-relaxed">Hitung indeks prestasi kumulatif semester ini secara instan untuk memantau progres akademik.</p></div>
                                        <div className="bg-white p-12 rounded-[4rem] shadow-2xl text-center border-b-8 border-indigo-600 min-w-[250px] transition-all hover:scale-105 shadow-indigo-100">
                                            <p className="text-[11px] font-black text-slate-400 uppercase tracking-widest mb-1 leading-none">Estimasi IPK</p>
                                            <p className="text-7xl font-black text-indigo-600 tracking-tighter leading-none mt-4">{calculateGPA()}</p>
                                        </div>
                                    </header>
                                    <div className="grid grid-cols-1 lg:grid-cols-5 gap-10 text-slate-700 font-bold">
                                        <div className="lg:col-span-2 bg-white p-10 rounded-[3rem] border border-slate-100 shadow-2xl space-y-8 text-left leading-none font-bold shadow-indigo-50">
                                            <h4 className="font-black text-sm uppercase text-slate-400 tracking-widest flex items-center gap-3"><LucideIcon name="plus-circle" size={20} className="text-indigo-600"/> Input Nilai</h4>
                                            <div className="space-y-5 text-left leading-none font-bold text-slate-700">
                                                <div className="space-y-3 leading-none">
                                                    <label className="text-[10px] font-black uppercase text-slate-400 px-2 block leading-none">Mata Kuliah</label>
                                                    <input placeholder="Contoh: Algoritma" className="w-full bg-slate-50 border-2 border-slate-100 rounded-2xl p-5 text-sm font-bold outline-none focus:bg-white focus:border-indigo-600 shadow-inner transition-all" value={gpaForm.name} onChange={e => setGpaForm({...gpaForm, name: e.target.value})} />
                                                </div>
                                                <div className="grid grid-cols-2 gap-4 leading-none font-bold">
                                                    <div className="space-y-3 text-left leading-none"><label className="text-[10px] font-black uppercase block leading-none text-slate-400 ml-1">SKS</label><input type="number" className="w-full bg-slate-50 border-2 border-slate-100 rounded-2xl p-5 text-sm font-bold outline-none focus:bg-white transition-all shadow-inner" value={gpaForm.sks} onChange={e => setGpaForm({...gpaForm, sks: e.target.value})} /></div>
                                                    <div className="space-y-3 text-left leading-none"><label className="text-[10px] font-black uppercase block leading-none text-slate-400 ml-1">Grade</label><select className="w-full bg-slate-50 border-2 border-slate-100 rounded-2xl p-5 text-sm font-bold outline-none font-black text-indigo-600 appearance-none cursor-pointer shadow-inner transition-all" value={gpaForm.grade} onChange={e => setGpaForm({...gpaForm, grade: e.target.value})}>{Object.keys(gradePoints).map(g => <option key={g} value={g}>{g}</option>)}</select></div>
                                                </div>
                                                <button onClick={addCourse} className="w-full bg-indigo-600 text-white py-6 rounded-[2rem] font-black text-sm uppercase tracking-widest shadow-xl active:translate-y-1 transition-all border-b-8 border-indigo-900 leading-none shadow-indigo-200">Simpan Nilai</button>
                                            </div>
                                        </div>
                                        <div className="lg:col-span-3 bg-white p-10 rounded-[3rem] border border-slate-100 shadow-2xl flex flex-col h-[550px] text-left relative overflow-hidden shadow-indigo-50">
                                            <h4 className="font-black text-sm uppercase text-slate-400 tracking-widest mb-8 border-b border-slate-50 pb-6 text-left font-bold">Riwayat Nilai</h4>
                                            <div className="space-y-4 overflow-y-auto flex-1 pr-4 custom-scrollbar text-left font-bold text-slate-800">
                                                {gpaCourses.length > 0 ? gpaCourses.map(c => (
                                                    <div key={c.id} className="flex justify-between items-center p-7 bg-slate-50 rounded-[2.5rem] border border-slate-50 transition-all hover:bg-white hover:border-indigo-200 group">
                                                        <div className="text-left leading-none flex flex-col gap-2"><p className="text-xl font-black text-slate-800 mb-2 capitalize leading-tight text-left">{String(c.name)}</p><p className="text-[10px] font-black uppercase text-slate-400 tracking-widest text-left leading-none">{c.sks} SKS • Point {gradePoints[c.grade]}</p></div>
                                                        <div className="flex items-center gap-7 leading-none"><span className="w-16 h-16 bg-white rounded-[1.2rem] flex items-center justify-center font-black text-2xl text-indigo-600 shadow-xl border-2 border-indigo-50 group-hover:bg-indigo-600 group-hover:text-white transition-all shadow-indigo-100/30 leading-none">{c.grade}</span><button onClick={() => deleteCourse(c.id)} className="text-slate-200 hover:text-rose-500 p-2 transition-all group-hover:scale-125"><LucideIcon name="trash-2" size={26}/></button></div>
                                                    </div>
                                                )) : <div className="h-full flex items-center justify-center text-slate-300 font-black uppercase tracking-widest text-xs opacity-50 italic">Belum ada nilai terdaftar.</div>}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* --- TAB BUDGETING --- */}
                            {activeTab === 'budget' && (
                                <div className="space-y-12 text-left animate-fade text-left pb-20">
                                    <h2 className="text-5xl font-black text-slate-900 tracking-tighter leading-none text-left leading-none">University Wallet</h2>
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-left leading-none">
                                        <div className="bg-gradient-to-br from-indigo-600 to-indigo-800 p-10 rounded-[3rem] shadow-2xl text-white shadow-indigo-100 group relative overflow-hidden transition-all hover:scale-105 leading-none">
                                            <div className="absolute inset-0 bg-white/10 blur-[100px] -translate-y-full group-hover:translate-y-0 transition-transform duration-1000 leading-none"></div>
                                            <p className="text-[11px] font-black text-indigo-200 uppercase tracking-widest mb-4 flex items-center gap-2 relative z-10 leading-none font-bold"><LucideIcon name="wallet" size={16}/> Sisa Saldo Mahasiswa</p>
                                            <p className="text-5xl font-black tracking-tighter relative z-10 leading-none font-black">{formatIDR(transactions.reduce((acc, t) => acc + t.amount, 0))}</p>
                                            <div className="mt-10 h-2 w-full bg-white/20 rounded-full overflow-hidden shadow-inner relative z-10 leading-none"><div className="h-full bg-white rounded-full animate-pulse shadow-xl" style={{width: '65%'}}></div></div>
                                        </div>
                                        <div className="bg-white p-10 rounded-[3rem] border border-slate-100 shadow-xl flex flex-col justify-center shadow-emerald-50/50 transition-all hover:bg-emerald-50 text-left"><p className="text-emerald-600 text-[11px] font-black uppercase tracking-widest mb-4 leading-none text-left font-bold">Monthly Income</p><p className="text-3xl font-black text-slate-800 tracking-tighter leading-none font-bold text-left leading-none">{formatIDR(transactions.filter(t => t.type === 'income').reduce((acc, t) => acc + t.amount, 0))}</p></div>
                                        <div className="bg-white p-10 rounded-[3rem] border border-slate-100 shadow-xl flex flex-col justify-center shadow-rose-50/50 transition-all hover:bg-rose-50 text-left"><p className="text-rose-600 text-[11px] font-black uppercase tracking-widest mb-4 leading-none text-left font-bold">Spending</p><p className="text-3xl font-black text-slate-800 tracking-tighter leading-none font-bold text-left leading-none">{formatIDR(Math.abs(transactions.filter(t => t.type === 'expense').reduce((acc, t) => acc + t.amount, 0)))}</p></div>
                                    </div>
                                    
                                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 text-left">
                                        <div className="bg-white p-10 rounded-[3.5rem] border border-slate-100 shadow-2xl space-y-8 text-left leading-none shadow-indigo-50">
                                            <h4 className="font-black text-sm uppercase text-slate-400 tracking-widest flex items-center gap-3 leading-none font-bold text-left"><LucideIcon name="plus-circle" size={20} className="text-indigo-600 text-left" /> Catat Keuangan</h4>
                                            <div className="space-y-5 text-left font-bold text-slate-700 leading-none">
                                                <div className="space-y-4 text-left leading-none">
                                                    <label className="text-[10px] font-black uppercase text-slate-400 px-2 block leading-none text-left">Keterangan</label>
                                                    <input placeholder="Beli buku, Makan, dll..." className="w-full bg-slate-50 border-2 border-slate-100 rounded-2xl p-5 text-sm font-bold outline-none focus:bg-white focus:border-indigo-600 shadow-inner transition-all leading-none" value={transForm.title} onChange={e => setTransForm({...transForm, title: e.target.value})} />
                                                </div>
                                                <div className="grid grid-cols-2 gap-5 leading-none">
                                                    <div className="space-y-4 text-left leading-none"><label className="text-[10px] font-black uppercase block leading-none text-slate-400 ml-1 text-left">Nominal (Rp)</label><input type="number" className="w-full bg-slate-50 border-2 border-slate-100 rounded-2xl p-5 text-sm font-bold outline-none focus:bg-white transition-all shadow-inner leading-none" value={transForm.amount} onChange={e => setTransForm({...transForm, amount: e.target.value})} /></div>
                                                    <div className="space-y-4 text-left leading-none"><label className="text-[10px] font-black uppercase block leading-none text-slate-400 ml-1 text-left">Jenis</label><select className="w-full bg-slate-50 border-2 border-slate-100 rounded-2xl p-5 text-sm font-bold outline-none font-black text-indigo-600 appearance-none cursor-pointer shadow-inner transition-all leading-none" value={transForm.type} onChange={e => setTransForm({...transForm, type: e.target.value})}><option value="expense">Keluar</option><option value="income">Masuk</option></select></div>
                                                </div>
                                                <button onClick={addTransaction} className="w-full bg-indigo-600 text-white py-6 rounded-[2rem] font-black text-sm uppercase tracking-widest shadow-xl active:translate-y-1 transition-all border-b-8 border-indigo-900 leading-none shadow-indigo-200">Simpan Transaksi</button>
                                            </div>
                                        </div>

                                        <div className="bg-white p-10 rounded-[3.5rem] border border-slate-100 shadow-2xl flex flex-col h-[550px] text-left shadow-indigo-50">
                                            <h4 className="font-black text-sm uppercase text-slate-400 tracking-widest mb-8 border-b border-slate-50 pb-6 text-left font-bold leading-none">Riwayat Transaksi</h4>
                                            <div className="space-y-4 overflow-y-auto flex-1 pr-4 custom-scrollbar text-left font-bold text-slate-800">
                                                {transactions.length > 0 ? transactions.slice().reverse().map(t => (
                                                    <div key={t.id} className="flex justify-between items-center p-6 bg-slate-50 rounded-[2.5rem] border border-slate-50 transition-all hover:bg-white hover:border-indigo-200 group leading-none">
                                                        <div className="text-left leading-none flex items-center gap-5 leading-none">
                                                            <div className={`p-3 rounded-2xl shadow-sm leading-none ${t.type === 'income' ? 'bg-emerald-100 text-emerald-600' : 'bg-rose-100 text-rose-600'}`}><LucideIcon name={t.type === 'income' ? "arrow-up-right" : "arrow-down-right"} size={22} /></div>
                                                            <div className="leading-none"><p className="text-lg font-black text-slate-800 mb-2 capitalize leading-tight text-left leading-none">{String(t.title)}</p><p className="text-[10px] font-black uppercase text-slate-400 tracking-widest leading-none text-left">{String(t.type)}</p></div>
                                                        </div>
                                                        <div className="flex items-center gap-7 leading-none"><p className={`font-black text-lg leading-none ${t.type === 'income' ? 'text-emerald-600' : 'text-rose-600'}`}>{t.type === 'income' ? '+' : ''}{formatIDR(t.amount)}</p><button onClick={() => deleteTransaction(t.id)} className="text-slate-200 hover:text-rose-500 p-2 transition-all group-hover:scale-125 leading-none"><LucideIcon name="trash-2" size={24} className="leading-none"/></button></div>
                                                    </div>
                                                )) : <div className="h-full flex items-center justify-center text-slate-300 font-black uppercase tracking-widest text-xs opacity-50 italic">Belum ada transaksi tersimpan.</div>}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* --- ADMIN VIEW --- */}
                            {activeTab === 'admin' && currentUser?.role === 'admin' && (
                                <div className="space-y-12 text-left pb-20 text-left animate-fade">
                                    <header className="flex flex-col sm:flex-row justify-between items-end gap-6 text-left leading-none">
                                        <div className="leading-none"><h2 className="text-5xl font-black text-slate-900 tracking-tighter leading-none text-left leading-none">Admin Hub</h2><div className="flex items-center gap-3 mt-4 text-indigo-600 font-black uppercase text-xs tracking-[0.2em] shadow-sm px-4 py-2 bg-indigo-50 rounded-xl text-left font-bold shadow-indigo-100/50 leading-none"><LucideIcon name="shield" size={16} className="text-left leading-none"/> Master Database Control</div></div>
                                        <div className="bg-white px-14 py-10 rounded-[4rem] border border-slate-100 shadow-2xl flex flex-col items-center shadow-indigo-50 leading-none"><p className="text-[11px] font-black text-slate-400 uppercase tracking-widest mb-1 leading-none font-bold">Total Users</p><p className="text-6xl font-black text-indigo-600 leading-none tracking-tighter leading-none mt-2">{allowedUsers.length}</p></div>
                                    </header>
                                    <div className="bg-white p-12 rounded-[4rem] border border-slate-100 shadow-2xl space-y-10 text-left relative overflow-hidden group leading-none shadow-indigo-50">
                                        <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-50 rounded-full blur-[100px] opacity-20 group-hover:opacity-40 transition-all duration-700 leading-none"></div>
                                        <h3 className="font-black text-2xl text-slate-900 flex items-center gap-5 uppercase tracking-tighter relative leading-none font-black leading-none"><LucideIcon name="user-plus" size={32} className="text-indigo-600 leading-none" /> Onboard Account</h3>
                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-left relative text-slate-700 font-bold leading-none">
                                            <div className="space-y-4 text-left leading-none font-bold text-slate-700 leading-none"><label className="text-[10px] font-black uppercase block leading-none text-slate-400 ml-1 text-left">Username ID</label><input className="w-full bg-slate-50 border-2 rounded-2xl p-5 font-bold outline-none focus:border-indigo-600 shadow-inner leading-none" placeholder="ID User" value={adminNewUser.username} onChange={e => setAdminNewUser({...adminNewUser, username: e.target.value})} /></div>
                                            <div className="space-y-4 text-left leading-none font-bold text-slate-700 leading-none"><label className="text-[10px] font-black uppercase block leading-none text-slate-400 ml-1 text-left">Password PIN</label><input className="w-full bg-slate-50 border-2 rounded-2xl p-5 font-bold outline-none focus:border-indigo-600 shadow-inner leading-none" placeholder="PIN" value={adminNewUser.password} onChange={e => setAdminNewUser({...adminNewUser, password: e.target.value})} /></div>
                                            <div className="space-y-4 text-left leading-none font-bold text-slate-700 leading-none"><label className="text-[10px] font-black uppercase block leading-none text-slate-400 ml-1 text-left">Full Name</label><input className="w-full bg-slate-50 border-2 rounded-2xl p-5 font-bold outline-none focus:border-indigo-600 shadow-inner leading-none" placeholder="Display Name" value={adminNewUser.name} onChange={e => setAdminNewUser({...adminNewUser, name: e.target.value})} /></div>
                                        </div>
                                        <button onClick={addUserByAdmin} className="w-full bg-indigo-600 text-white py-7 rounded-[2.5rem] font-black uppercase text-sm tracking-widest shadow-xl active:translate-y-1 transition-all border-b-8 border-indigo-900 shadow-indigo-100 leading-none">Daftarkan Mahasiswa</button>
                                    </div>
                                    <div className="bg-white rounded-[4rem] border border-slate-100 overflow-hidden shadow-xl text-left shadow-indigo-50">
                                        <table className="w-full text-left min-w-[700px]">
                                            <thead className="bg-[#F8FAFC] border-b text-left font-black text-slate-400 uppercase tracking-widest leading-none"><tr><th className="p-12 text-[11px] px-14 text-left leading-none text-left">Data Mahasiswa</th><th className="p-12 text-[11px] text-left leading-none text-left">Hak Akses</th><th className="p-12 text-[11px] text-right px-14 text-right leading-none text-right">Kontrol Server</th></tr></thead>
                                            <tbody className="divide-y divide-slate-50 text-left">
                                                {allowedUsers.map((u, idx) => (
                                                    <tr key={idx} className="hover:bg-indigo-50/20 transition-all group/row leading-none">
                                                        <td className="p-12 px-14 flex items-center gap-8 text-left leading-none text-left">
                                                            <div className="w-16 h-16 bg-white text-indigo-600 rounded-[1.5rem] flex items-center justify-center font-black text-2xl border-2 border-slate-100 group-hover/row:scale-110 transition-all shadow-sm uppercase leading-none">{(u.username || "U")[0]}</div>
                                                            <div className="text-left leading-none font-bold">
                                                                <p className="text-2xl font-black text-slate-900 tracking-tighter capitalize mb-3 leading-none text-left leading-none">{String(u.name || "Student")}</p>
                                                                <p className="text-[11px] text-slate-400 uppercase font-black tracking-widest flex gap-4 leading-none opacity-60 text-left leading-none text-left leading-none"><span>USER: {u.username}</span> <span>PIN: {u.password}</span></p>
                                                            </div>
                                                        </td>
                                                        <td className="p-12 text-left leading-none text-left leading-none"><span className={`px-10 py-4 rounded-[1.5rem] text-[10px] font-black uppercase tracking-widest border shadow-sm leading-none ${u.role === 'admin' ? 'bg-indigo-600 text-white border-indigo-600 shadow-indigo-100' : 'bg-white text-slate-500 border-slate-100 group-hover/row:bg-white'}`}>{String(u.role)}</span></td>
                                                        <td className="p-12 text-right px-14 text-right leading-none font-bold text-right leading-none"><button onClick={() => removeUserByAdmin(u.username)} className={`p-6 rounded-[2rem] transition-all hover:scale-110 leading-none leading-none ${u.username === 'admin' ? 'opacity-20 cursor-not-allowed text-slate-300' : 'text-slate-200 hover:text-rose-500 hover:bg-rose-50 shadow-sm'}`}><LucideIcon name={u.username === 'admin' ? "lock" : "trash-2"} size={32} className="leading-none"/></button></td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            )}
                        </div>
                    </main>

                    {/* --- DONATION MODAL --- */}
                    {showDonationModal && (
                        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-3xl z-[100] flex items-center justify-center p-6 animate-in fade-in duration-500 text-left leading-none">
                            <div className="bg-white rounded-[4.5rem] shadow-[0_70px_140px_rgba(0,0,0,0.35)] max-w-md w-full overflow-hidden border border-slate-100 transition-all leading-none">
                                <div className="bg-gradient-to-br from-[#00AED6] to-[#0089A7] p-16 text-center text-white relative leading-none">
                                    <button onClick={() => setShowDonationModal(false)} className="absolute top-10 right-10 bg-white/20 hover:bg-white/40 rounded-full p-2.5 border border-white/20 transition-all active:scale-90"><LucideIcon name="x" size={20}/></button>
                                    <div className="bg-white/20 w-32 h-32 rounded-[2.8rem] flex items-center justify-center mx-auto mb-8 border border-white/30 backdrop-blur-md shadow-2xl animate-pulse"><LucideIcon name="coffee" size={64} className="fill-white opacity-80" /></div>
                                    <h3 className="text-4xl font-black tracking-tighter leading-tight text-white drop-shadow-lg text-center font-black leading-none">Traktir Kopi <br/>Untuk Risky</h3>
                                    <p className="text-white/80 text-[11px] font-black uppercase tracking-[0.25em] mt-6 opacity-90 border-t border-white/20 pt-6 text-center leading-none font-bold leading-none">Support Innovation ❤️</p>
                                </div>
                                <div className="p-12 space-y-8 text-left bg-white font-bold text-slate-800 leading-none font-bold">
                                    <div className="space-y-5 leading-none font-bold">
                                        <div className="flex justify-between items-center bg-[#F1FDFE] p-7 rounded-[2.5rem] border-2 border-transparent hover:border-[#00AED6] transition-all cursor-pointer group shadow-sm hover:shadow-xl hover:shadow-[#00AED6]/10 leading-none">
                                            <div className="flex items-center gap-6 text-left leading-none">
                                                <div className="w-14 h-14 bg-[#00AED6] rounded-2xl flex items-center justify-center text-white font-black text-xs shadow-xl group-hover:scale-110 transition-all leading-none font-black shadow-[#00AED6]/40 leading-none">GOPAY</div>
                                                <div className="leading-tight text-left leading-none"><span className="text-[10px] font-black text-slate-400 uppercase tracking-widest block mb-1.5 leading-none font-black leading-none">Support Payment</span><span className="text-xl font-black text-slate-800 tracking-wider font-mono font-black tracking-tighter leading-none leading-none">087791881535</span></div>
                                            </div>
                                            <LucideIcon name="chevron-right" size={24} className="text-[#00AED6] opacity-30 group-hover:opacity-100 group-hover:translate-x-1 transition-all leading-none" />
                                        </div>
                                    </div>
                                    <button onClick={() => setShowDonationModal(false)} className="w-full bg-slate-900 text-white font-black py-7 rounded-[2rem] hover:bg-slate-800 transition-all text-xs uppercase tracking-[0.3em] shadow-2xl active:scale-95 border-b-8 border-slate-700 leading-none shadow-slate-200 leading-none">Konfirmasi Dukungan</button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            );
        };

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<App />);
    </script>
</body>
</html>
{% endraw %}
"""

# --- 3. ROUTES API (Wajib di Bawah Variabel) ---

@app.route('/')
def index():
    # Sekarang HTML_TEMPLATE sudah aman karena didefinisikan di atas
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/users', methods=['GET', 'POST'])
def handle_users():
    if request.method == 'POST':
        new_user = request.json
        if not any(u['username'] == new_user['username'] for u in db['users']):
            db['users'].append(new_user)
        return jsonify(db['users'])
    return jsonify(db['users'])

# Proxy route untuk menyembunyikan API Key
@app.route('/api/chat', methods=['POST'])
def proxy_chat():
    user_input = request.json.get("message")
    model_name = "gemini-2.5-flash" # Gunakan versi stabil
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": user_input}]}],
        "systemInstruction": {"parts": [{"text": "Kamu adalah IG.STORE AI, asisten akademik mahasiswa Indonesia..."}]}
    }
    
    response = requests.post(url, json=payload)
    return jsonify(response.json())

# ... (Route /api/users tetap sama)
# JANGAN PAKAI app.run() jika deploy ke Vercel, biarkan saja.