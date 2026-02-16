import { Search, MoreHorizontal } from 'lucide-react';
import { Checkbox } from './ui/checkbox';
import { useState } from 'react';

interface Task {
  id: string;
  title: string;
  completed: boolean;
  tags: { label: string; color: string }[];
  dueDate: string;
}

const tasks: Task[] = [
  {
    id: '1',
    title: 'Review design mockups for landing page',
    completed: false,
    tags: [
      { label: 'Design', color: 'bg-purple-100 text-purple-700' },
      { label: 'High Priority', color: 'bg-red-100 text-red-700' },
    ],
    dueDate: 'Today',
  },
  {
    id: '2',
    title: 'Update user documentation',
    completed: true,
    tags: [{ label: 'Documentation', color: 'bg-blue-100 text-blue-700' }],
    dueDate: 'Yesterday',
  },
  {
    id: '3',
    title: 'Prepare Q1 presentation slides',
    completed: false,
    tags: [{ label: 'Marketing', color: 'bg-green-100 text-green-700' }],
    dueDate: 'Feb 18',
  },
  {
    id: '4',
    title: 'Code review for mobile app PR #234',
    completed: false,
    tags: [
      { label: 'Development', color: 'bg-orange-100 text-orange-700' },
      { label: 'Mobile', color: 'bg-pink-100 text-pink-700' },
    ],
    dueDate: 'Feb 17',
  },
];

const learningCards = [
  {
    id: '1',
    title: 'Master Project Management',
    description: 'Learn the fundamentals of agile project management in 30 minutes',
    duration: '30 min',
    illustration: 'pink',
  },
  {
    id: '2',
    title: 'Team Collaboration Best Practices',
    description: 'Discover tips to improve team communication and productivity',
    duration: '20 min',
    illustration: 'red',
  },
];

interface MainContentProps {
  onNewTaskClick: () => void;
}

export function MainContent({ onNewTaskClick }: MainContentProps) {
  const [activeTab, setActiveTab] = useState<'upcoming' | 'overdue' | 'completed'>('upcoming');

  return (
    <div className="flex-1 bg-white overflow-y-auto">
      {/* Header */}
      <header className="border-b border-gray-200 px-12 py-6">
        <div className="flex items-center justify-between mb-2">
          <div>
            <p className="text-sm text-gray-600 mb-1">Monday, February 15</p>
            <h1 className="text-3xl font-light text-gray-900">Good afternoon, Alex</h1>
          </div>
          <div className="flex items-center gap-3">
            <button className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
              My week
            </button>
            <button className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-gradient-to-br from-purple-500 to-pink-500"></span>
              0 tasks completed
            </button>
            <button className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
              1 collaborator
            </button>
            <button className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
              Customize
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="px-12 py-8">
        {/* Tasks Section */}
        <section className="mb-12">
          <div className="flex items-center gap-8 mb-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-medium">
                A
              </div>
              <h2 className="text-xl font-medium text-gray-900">My tasks</h2>
            </div>
            <button className="text-gray-400 hover:text-gray-600">
              <MoreHorizontal className="w-5 h-5" />
            </button>
          </div>

          {/* Tabs */}
          <div className="flex gap-6 mb-4 border-b border-gray-200">
            <button
              onClick={() => setActiveTab('upcoming')}
              className={`pb-3 px-1 text-sm font-medium transition-colors relative ${
                activeTab === 'upcoming'
                  ? 'text-gray-900'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Upcoming
              {activeTab === 'upcoming' && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gray-900"></div>
              )}
            </button>
            <button
              onClick={() => setActiveTab('overdue')}
              className={`pb-3 px-1 text-sm font-medium transition-colors relative ${
                activeTab === 'overdue'
                  ? 'text-gray-900'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Overdue
              {activeTab === 'overdue' && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gray-900"></div>
              )}
            </button>
            <button
              onClick={() => setActiveTab('completed')}
              className={`pb-3 px-1 text-sm font-medium transition-colors relative ${
                activeTab === 'completed'
                  ? 'text-gray-900'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Completed
              {activeTab === 'completed' && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gray-900"></div>
              )}
            </button>
          </div>

          {/* Create Task Button */}
          <button
            onClick={onNewTaskClick}
            className="text-sm text-gray-600 hover:text-gray-900 mb-4 flex items-center gap-2"
          >
            <span className="text-lg">+</span> Create task
          </button>

          <div className="space-y-0">
            {tasks.map((task, index) => (
              <div
                key={task.id}
                className="flex items-center gap-4 py-3 hover:bg-gray-50 transition-colors rounded-lg px-2"
              >
                <Checkbox checked={task.completed} />
                
                <div className="flex-1">
                  <p
                    className={`text-sm ${
                      task.completed ? 'line-through text-gray-400' : 'text-gray-900'
                    }`}
                  >
                    {task.title}
                  </p>
                </div>

                <div className="flex items-center gap-3">
                  {task.tags.map((tag, tagIndex) => (
                    <span
                      key={tagIndex}
                      className="text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-700"
                    >
                      {tag.label}
                    </span>
                  ))}
                  <span className="text-xs text-gray-500 min-w-[80px] text-right">{task.dueDate}</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Learning Section */}
        <section>
          <h2 className="text-xl font-medium text-gray-900 mb-4">Learn Asana</h2>
          <div className="grid grid-cols-2 gap-4">
            {learningCards.map((card) => (
              <div
                key={card.id}
                className="border border-gray-200 rounded-lg p-0 hover:shadow-md transition-shadow cursor-pointer group overflow-hidden"
              >
                {/* Illustration */}
                <div className={`h-32 ${card.illustration === 'pink' ? 'bg-pink-50' : 'bg-red-50'} flex items-center justify-center p-6 relative`}>
                  {card.illustration === 'pink' ? (
                    <svg width="120" height="100" viewBox="0 0 120 100" fill="none">
                      {/* Simple rocket illustration */}
                      <ellipse cx="60" cy="85" rx="30" ry="8" fill="#FFB3C1" opacity="0.3"/>
                      <path d="M50 80L50 45L45 35L48 20L52 10L60 5L68 10L72 20L75 35L70 45L70 80Z" fill="#FF6B9D"/>
                      <circle cx="60" cy="35" r="8" fill="#FFF" opacity="0.8"/>
                      <path d="M40 60L30 65L35 70L50 72Z" fill="#FFB3C1"/>
                      <path d="M80 60L90 65L85 70L70 72Z" fill="#FFB3C1"/>
                      <path d="M55 75L50 90L60 88L65 75Z" fill="#FF8FAB"/>
                    </svg>
                  ) : (
                    <svg width="120" height="100" viewBox="0 0 120 100" fill="none">
                      {/* Simple checklist illustration */}
                      <rect x="35" y="20" width="50" height="60" rx="4" fill="#FFF" stroke="#EF4444" strokeWidth="2"/>
                      <path d="M42 35L48 41L58 31" stroke="#EF4444" strokeWidth="2" fill="none"/>
                      <line x1="42" y1="50" x2="70" y2="50" stroke="#FECACA" strokeWidth="2"/>
                      <line x1="42" y1="58" x2="65" y2="58" stroke="#FECACA" strokeWidth="2"/>
                      <circle cx="65" cy="35" r="2" fill="#EF4444"/>
                      <path d="M55 10L60 5L65 10L60 15Z" fill="#EF4444"/>
                    </svg>
                  )}
                  <div className={`absolute bottom-2 left-3 px-2 py-0.5 rounded text-xs font-medium flex items-center gap-1 ${card.illustration === 'pink' ? 'bg-white/90 text-pink-800' : 'bg-white/90 text-red-800'}`}>
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
                      <circle cx="6" cy="6" r="6"/>
                      <path d="M6 3L6 6L8 8" stroke="white" strokeWidth="1"/>
                    </svg>
                    {card.duration}
                  </div>
                </div>

                <div className="p-4">
                  <h3 className="font-medium text-gray-900 mb-1.5 text-sm">{card.title}</h3>
                  <p className="text-xs text-gray-600">{card.description}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}