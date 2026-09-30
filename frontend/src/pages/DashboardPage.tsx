import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';

interface MetricCardProps {
  label: string;
  value: string | number;
  icon: string;
  trend?: string;
}

function MetricCard({ label, value, icon, trend }: MetricCardProps) {
  return (
    <Card>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <p style={{ color: '#64748b', margin: 0, fontSize: '0.85rem' }}>{label}</p>
          <p
            style={{
              color: '#f1f5f9',
              margin: '0.5rem 0 0',
              fontSize: '1.8rem',
              fontWeight: 700,
            }}
          >
            {value}
          </p>
          {trend && (
            <p
              style={{
                color: trend.startsWith('+') ? '#10b981' : '#ef4444',
                margin: '0.5rem 0 0',
                fontSize: '0.8rem',
              }}
            >
              {trend}
            </p>
          )}
        </div>
        <div
          style={{
            fontSize: '2rem',
            opacity: 0.5,
          }}
        >
          {icon}
        </div>
      </div>
    </Card>
  );
}

interface ActivityItem {
  id: string;
  timestamp: string;
  action: string;
  details: string;
  type: 'case' | 'workflow' | 'automation' | 'user';
}

function ActivityFeed({ items }: { items: ActivityItem[] }) {
  return (
    <Card title="Recent Activity">
      <div>
        {items.length === 0 ? (
          <p style={{ color: '#64748b', margin: 0, fontSize: '0.85rem' }}>No recent activity</p>
        ) : (
          <ul style={{ margin: 0, padding: 0, listStyle: 'none' }}>
            {items.map((item) => (
              <li
                key={item.id}
                style={{
                  padding: '0.75rem',
                  borderBottom: '1px solid #334155',
                  fontSize: '0.85rem',
                }}
              >
                <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
                  <span style={{ color: '#94a3b8' }}>•</span>
                  <div style={{ flex: 1 }}>
                    <p style={{ color: '#cbd5e1', margin: 0, fontWeight: 500 }}>
                      {item.action}
                    </p>
                    <p style={{ color: '#64748b', margin: '0.25rem 0 0', fontSize: '0.75rem' }}>
                      {item.details} • {new Date(item.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </Card>
  );
}

interface DashboardPageProps {
  onNavigate?: (page: string) => void;
}

export function DashboardPage({ onNavigate }: DashboardPageProps) {
  // Mock data
  const metrics = [
    { label: 'Total Cases', value: '1,234', icon: '📋', trend: '+12 this week' },
    { label: 'Active Workflows', value: '45', icon: '⚙️', trend: '+3 new' },
    { label: 'Pending Approvals', value: '18', icon: '⏳', trend: '-2 yesterday' },
    { label: 'Completed Reports', value: '342', icon: '📊', trend: '+28%' },
  ];

  const recentActivity: ActivityItem[] = [
    {
      id: '1',
      timestamp: new Date().toISOString(),
      action: 'Case #PM-2024-001 completed',
      details: 'Beneficiary Case Processing',
      type: 'case',
    },
    {
      id: '2',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      action: 'Workflow "PM-JAY Automation" published',
      details: 'Portal automation workflow',
      type: 'workflow',
    },
    {
      id: '3',
      timestamp: new Date(Date.now() - 7200000).toISOString(),
      action: 'Automation #AUTO-2024-045 passed validation',
      details: 'Portal integration test',
      type: 'automation',
    },
  ];

  return (
    <div>
      {/* Welcome Header */}
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ color: '#f1f5f9', margin: 0, fontSize: '1.8rem', fontWeight: 700 }}>
          Welcome back, Administrator
        </h1>
        <p style={{ color: '#64748b', margin: '0.5rem 0 0', fontSize: '0.95rem' }}>
          Here's your portal automation dashboard for today.
        </p>
      </div>

      {/* Quick Actions */}
      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '2rem', flexWrap: 'wrap' }}>
        <Button
          variant="primary"
          onClick={() => onNavigate?.('cases')}
        >
          ➕ New Case
        </Button>
        <Button
          variant="secondary"
          onClick={() => onNavigate?.('workflows')}
        >
          ⚙️ View Workflows
        </Button>
        <Button
          variant="ghost"
          onClick={() => onNavigate?.('portals')}
        >
          🌐 Browse Portals
        </Button>
      </div>

      {/* Metrics Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '1rem',
          marginBottom: '2rem',
        }}
      >
        {metrics.map((metric) => (
          <MetricCard key={metric.label} {...metric} />
        ))}
      </div>

      {/* Activity Section */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '1rem',
        }}
      >
        <ActivityFeed items={recentActivity} />

        {/* Quick Stats Card */}
        <Card title="System Status">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ color: '#cbd5e1', fontSize: '0.85rem' }}>API Health</span>
                <span style={{ color: '#10b981', fontWeight: 700, fontSize: '0.85rem' }}>Healthy</span>
              </div>
              <div
                style={{
                  width: '100%',
                  height: '4px',
                  background: '#334155',
                  borderRadius: '2px',
                  overflow: 'hidden',
                }}
              >
                <div
                  style={{
                    width: '100%',
                    height: '100%',
                    background: '#10b981',
                  }}
                />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ color: '#cbd5e1', fontSize: '0.85rem' }}>Database</span>
                <span style={{ color: '#10b981', fontWeight: 700, fontSize: '0.85rem' }}>Connected</span>
              </div>
              <div
                style={{
                  width: '100%',
                  height: '4px',
                  background: '#334155',
                  borderRadius: '2px',
                  overflow: 'hidden',
                }}
              >
                <div
                  style={{
                    width: '100%',
                    height: '100%',
                    background: '#10b981',
                  }}
                />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ color: '#cbd5e1', fontSize: '0.85rem' }}>Portal Connections</span>
                <span style={{ color: '#fbbf24', fontWeight: 700, fontSize: '0.85rem' }}>2/3</span>
              </div>
              <div
                style={{
                  width: '100%',
                  height: '4px',
                  background: '#334155',
                  borderRadius: '2px',
                  overflow: 'hidden',
                }}
              >
                <div
                  style={{
                    width: '66.67%',
                    height: '100%',
                    background: '#fbbf24',
                  }}
                />
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
