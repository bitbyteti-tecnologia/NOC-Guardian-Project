import React from "react";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";

function App() {
    return (
        <div className="flex bg-slate-900 min-h-screen text-slate-100 font-sans">
            <Sidebar />
            <Dashboard />
        </div>
    );
}

export default App;
