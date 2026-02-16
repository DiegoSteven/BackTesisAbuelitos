import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Sidebar from './components/Layout/Sidebar';
import Header from './components/Layout/Header';
import GeneralTab from './pages/GeneralTab';
import MemoryGameTab from './pages/MemoryGameTab';
import AbecedarioTab from './pages/AbecedarioTab';
import PaseoTab from './pages/PaseoTab';
import TrainTab from './pages/TrainTab';
import UsersTab from './pages/UsersTab';
import ProgressionTab from './pages/ProgressionTab';
import './styles/global.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  const [activeTab, setActiveTab] = useState('memory');
  const [isDarkTheme, setIsDarkTheme] = useState(true);

  const renderTab = () => {
    switch (activeTab) {
      case 'general':
        return <GeneralTab />;
      case 'memory':
        return <MemoryGameTab />;
      case 'abecedario':
        return <AbecedarioTab />;
      case 'paseo':
        return <PaseoTab />;
      case 'train':
        return <TrainTab />;
      case 'users':
        return <UsersTab />;
      case 'progression':
        return <ProgressionTab />;
      default:
        return <GeneralTab />;
    }
  };

  const getTitleForTab = (tab: string) => {
    const titles: Record<string, string> = {
      general: 'Dashboard General',
      memory: 'Memory Game - Métricas de IA',
      abecedario: 'Abecedario',
      paseo: 'Paseo',
      train: 'Trenes',
      users: 'Gestión de Usuarios',
      progression: 'Reporte de Progresión',
    };
    return titles[tab] || 'Dashboard';
  };

  const handleRefresh = () => {
    queryClient.invalidateQueries();
  };

  const toggleTheme = () => {
    setIsDarkTheme(!isDarkTheme);
  };

  return (
    <QueryClientProvider client={queryClient}>
      <div className={`app ${isDarkTheme ? 'theme-dark' : 'theme-light'}`}>
        <Sidebar activeTab={activeTab} onTabChange={setActiveTab} isDarkTheme={isDarkTheme} />
        <div className="main-content">
          <Header
            title={getTitleForTab(activeTab)}
            onRefresh={handleRefresh}
            isDarkTheme={isDarkTheme}
            onToggleTheme={toggleTheme}
          />
          {renderTab()}
        </div>
      </div>
    </QueryClientProvider>
  );
}

export default App;
