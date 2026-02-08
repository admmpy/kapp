import './BottomNav.css';

export type Tab = 'courses' | 'dashboard' | 'vocabulary-review' | 'conversation';

interface Props {
  activeTab: Tab;
  onNavigate: (tab: Tab) => void;
}

const tabs: { id: Tab; icon: string; label: string }[] = [
  { id: 'courses', icon: '\uD83D\uDCDA', label: 'Home' },
  { id: 'dashboard', icon: '\uD83D\uDCCA', label: 'Progress' },
  { id: 'vocabulary-review', icon: '\uD83D\uDD04', label: 'Review' },
  { id: 'conversation', icon: '\uD83D\uDCAC', label: 'Chat' },
];

export default function BottomNav({ activeTab, onNavigate }: Props) {
  return (
    <nav className="bottom-nav">
      {tabs.map(tab => (
        <button
          key={tab.id}
          className="bottom-nav-tab"
          aria-current={activeTab === tab.id ? 'page' : undefined}
          onClick={() => onNavigate(tab.id)}
        >
          <span className="bottom-nav-icon">{tab.icon}</span>
          <span className="bottom-nav-label">{tab.label}</span>
        </button>
      ))}
    </nav>
  );
}
