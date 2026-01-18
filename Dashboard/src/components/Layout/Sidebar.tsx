interface SidebarProps {
    activeTab: string;
    onTabChange: (tab: string) => void;
}

const Sidebar = ({ activeTab, onTabChange }: SidebarProps) => {
    const navItems = [
        { id: 'general', icon: '📊', label: 'General' },
        { id: 'memory', icon: '🧠', label: 'Memory Game' },
        { id: 'abecedario', icon: '🔤', label: 'Abecedario' },
        { id: 'paseo', icon: '🚶', label: 'Paseo' },
        { id: 'train', icon: '🚂', label: 'Trenes' },
        { id: 'users', icon: '👥', label: 'Usuarios' },
    ];

    return (
        <div className="sidebar">
            <div className="logo">
                <span>⚡</span> Abuelitos Admin
            </div>
            {navItems.map(item => (
                <div
                    key={item.id}
                    className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
                    onClick={() => onTabChange(item.id)}
                >
                    {item.icon} {item.label}
                </div>
            ))}
        </div>
    );
};

export default Sidebar;
