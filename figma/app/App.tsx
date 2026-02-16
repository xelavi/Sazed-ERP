import { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { MainContent } from './components/MainContent';
import { NewTaskModal } from './components/NewTaskModal';
import { TopBar } from './components/TopBar';

export default function App() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSidebarVisible, setIsSidebarVisible] = useState(true);

  return (
    <div className="flex flex-col h-screen bg-white overflow-hidden">
      <TopBar onToggleSidebar={() => setIsSidebarVisible(!isSidebarVisible)} />
      <div className="flex flex-1 overflow-hidden">
        {isSidebarVisible && <Sidebar />}
        <MainContent onNewTaskClick={() => setIsModalOpen(true)} />
        <NewTaskModal open={isModalOpen} onClose={() => setIsModalOpen(false)} />
      </div>
    </div>
  );
}