import React, { useState } from "react";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";

function App() {
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);

    const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen);
    const closeSidebar = () => setIsSidebarOpen(false);

    return (
        <div className="min-h-screen w-full bg-slate-950 text-slate-100 font-sans overflow-hidden text-sm md:text-base lg:text-lg">
            <Sidebar isOpen={isSidebarOpen} closeSidebar={closeSidebar} />
            <Dashboard toggleSidebar={toggleSidebar} />
        </div>
    );
}

export default App;
