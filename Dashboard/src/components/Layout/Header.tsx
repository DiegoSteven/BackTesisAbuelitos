interface HeaderProps {
    title: string;
    onRefresh: () => void;
}

const Header = ({ title, onRefresh }: HeaderProps) => {
    return (
        <div className="header">
            <h1>{title}</h1>
            <button className="refresh-btn" onClick={onRefresh}>
                🔄 Actualizar Datos
            </button>
        </div>
    );
};

export default Header;
