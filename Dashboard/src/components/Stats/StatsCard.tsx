interface StatsCardProps {
    title: string;
    value: string | number;
    trend: string;
    gradient?: 'gradient-1' | 'gradient-2' | 'gradient-3' | '';
}

const StatsCard = ({ title, value, trend, gradient = '' }: StatsCardProps) => {
    return (
        <div className={`stat-card ${gradient}`}>
            <h3>{title}</h3>
            <div className="value">{value}</div>
            <span className="trend">{trend}</span>
        </div>
    );
};

export default StatsCard;
