interface HeaderProps {
    title: string;
    onRefresh: () => void;
    isDarkTheme?: boolean;
    onToggleTheme?: () => void;
}

const Header = ({ title, onRefresh, isDarkTheme = true, onToggleTheme }: HeaderProps) => {
    return (
        <div className="header">
            <h1>{title}</h1>
            <div style={{ display: 'flex', gap: '12px' }}>
                {onToggleTheme && (
                    <button className="refresh-btn" onClick={onToggleTheme}>
                        {isDarkTheme ? '☀️ Tema Claro' : '🌙 Tema Oscuro'}
                    </button>
                )}
                <button className="refresh-btn" onClick={onRefresh}>
                    🔄 Actualizar Datos
                </button>
            </div>
        </div>
    );
};

export default Header;
