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
    };
    return titles[tab] || 'Dashboard';
  };

  const handleRefresh = () => {
    queryClient.invalidateQueries();
  };

  return (
    <QueryClientProvider client={queryClient}>
      <div className="app">
        <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
        <div className="main-content">
          <Header title={getTitleForTab(activeTab)} onRefresh={handleRefresh} />
          {renderTab()}
        </div>
      </div>
    </QueryClientProvider>
  );
}

export default App;
