import React from 'react';
import { LayoutDashboard, Code, FileCode, GitBranch, Settings, Activity } from 'lucide-react';
import './Layout.css';

const Layout = ({ children, activeTab, setActiveTab }) => {
    const navItems = [
        { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
        { id: 'profile', icon: Activity, label: 'New Profile' },
        { id: 'compare', icon: GitBranch, label: 'Compare' },
        { id: 'history', icon: FileCode, label: 'History' },
        { id: 'settings', icon: Settings, label: 'Settings' },
    ];

    return (
        <div className="layout">
            <aside className="sidebar">
                <div className="logo">
                    <Activity className="logo-icon" />
                    <span>OmniProfiler</span>
                </div>
                <nav>
                    {navItems.map((item) => (
                        <button
                            key={item.id}
                            className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
                            onClick={() => setActiveTab(item.id)}
                        >
                            <item.icon size={20} />
                            <span>{item.label}</span>
                        </button>
                    ))}
                </nav>
            </aside>
            <main className="content">
                <header className="header">
                    <h2>{navItems.find(i => i.id === activeTab)?.label}</h2>
                    <div className="user-profile">
                        <div className="avatar">OP</div>
                    </div>
                </header>
                <div className="page-content">
                    {children}
                </div>
            </main>
        </div>
    );
};

export default Layout;
