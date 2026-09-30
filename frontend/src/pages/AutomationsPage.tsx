import { useState, useEffect } from 'react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { DataTable } from '../components/common/DataTable';
import type { AutomationInstance, ExecutionStatus } from '../types';

function ProgressBar({ progress }: { progress: number }) {
  return (
    <div style={{ width: '100%', height: '6px', background: '#334155', borderRadius: '3px', overflow: 'hidden' }}>
      <div
        style={{
          width: `${progress}%`,
          height: '100%',
          background: progress === 100 ? '#10b981' : '#3b82f6',
          transition: 'width 0.3s ease',
        }}
      />
    </div>
  );
}

export function AutomationsPage() {
  const [automations, setAutomations] = useState<AutomationInstance[]>([]);

  useEffect(() => {
    const mockAutomations: AutomationInstance[] = [
      {
        id: 'AUTO-001',
        organization_id: 'org-1',
        case_id: 'CASE-001',
        workflow_id: 'WF-001',
        status: 'COMPLETED',
        progress: 100,
        current_step: 5,
        total_steps: 5,
        started_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        completed_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
        created_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: 'AUTO-002',
        organization_id: 'org-1',
        case_id: 'CASE-002',
        workflow_id: 'WF-001',
        status: 'RUNNING',
        progress: 60,
        current_step: 3,
        total_steps: 5,
        started_at: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
        completed_at: null,
        created_at: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
      },
      {
        id: 'AUTO-003',
        organization_id: 'org-1',
        case_id: 'CASE-003',
        workflow_id: 'WF-002',
        status: 'FAILED',
        progress: 40,
        current_step: 2,
        total_steps: 5,
        started_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        completed_at: new Date(Date.now() - 25 * 60 * 1000).toISOString(),
        created_at: new Date(Date.now() - 35 * 60 * 1000).toISOString(),
      },
    ];
    setAutomations(mockAutomations);
  }, []);

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ color: '#f1f5f9', margin: 0, fontSize: '1.8rem', fontWeight: 700 }}>
          Automation Tracking
        </h1>
        <p style={{ color: '#64748b', margin: '0.5rem 0 0', fontSize: '0.95rem' }}>
          Monitor and manage automation executions
        </p>
      </div>

      {/* Summary Cards */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '1rem',
          marginBottom: '2rem',
        }}
      >
        <Card>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <p style={{ color: '#64748b', margin: 0, fontSize: '0.85rem' }}>Total Automations</p>
              <p style={{ color: '#f1f5f9', margin: '0.5rem 0 0', fontSize: '1.5rem', fontWeight: 700 }}>
                {automations.length}
              </p>
            </div>
            <span style={{ fontSize: '2rem', opacity: 0.3 }}>⚙️</span>
          </div>
        </Card>

        <Card>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <p style={{ color: '#64748b', margin: 0, fontSize: '0.85rem' }}>Running</p>
              <p style={{ color: '#f1f5f9', margin: '0.5rem 0 0', fontSize: '1.5rem', fontWeight: 700 }}>
                {automations.filter((a) => a.status === 'RUNNING').length}
              </p>
            </div>
            <span style={{ fontSize: '2rem', opacity: 0.3 }}>🚀</span>
          </div>
        </Card>

        <Card>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <p style={{ color: '#64748b', margin: 0, fontSize: '0.85rem' }}>Completed</p>
              <p style={{ color: '#f1f5f9', margin: '0.5rem 0 0', fontSize: '1.5rem', fontWeight: 700 }}>
                {automations.filter((a) => a.status === 'COMPLETED').length}
              </p>
            </div>
            <span style={{ fontSize: '2rem', opacity: 0.3 }}>✓</span>
          </div>
        </Card>

        <Card>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <p style={{ color: '#64748b', margin: 0, fontSize: '0.85rem' }}>Failed</p>
              <p style={{ color: '#f1f5f9', margin: '0.5rem 0 0', fontSize: '1.5rem', fontWeight: 700 }}>
                {automations.filter((a) => a.status === 'FAILED').length}
              </p>
            </div>
            <span style={{ fontSize: '2rem', opacity: 0.3 }}>✕</span>
          </div>
        </Card>
      </div>

      {/* Automations List */}
      <Card title="Automation Executions">
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #334155' }}>
                <th style={{ padding: '0.75rem', textAlign: 'left', color: '#94a3b8', fontWeight: 700 }}>ID</th>
                <th style={{ padding: '0.75rem', textAlign: 'left', color: '#94a3b8', fontWeight: 700 }}>Case</th>
                <th style={{ padding: '0.75rem', textAlign: 'left', color: '#94a3b8', fontWeight: 700 }}>Progress</th>
                <th style={{ padding: '0.75rem', textAlign: 'left', color: '#94a3b8', fontWeight: 700 }}>Status</th>
                <th style={{ padding: '0.75rem', textAlign: 'left', color: '#94a3b8', fontWeight: 700 }}>Started</th>
              </tr>
            </thead>
            <tbody>
              {automations.map((auto, idx) => (
                <tr key={auto.id} style={{ borderBottom: '1px solid #334155', background: idx % 2 === 0 ? '#1e293b' : '#0f172a' }}>
                  <td style={{ padding: '0.75rem', color: '#60a5fa' }}>{auto.id}</td>
                  <td style={{ padding: '0.75rem', color: '#cbd5e1' }}>{auto.case_id}</td>
                  <td style={{ padding: '0.75rem', width: '150px' }}>
                    <ProgressBar progress={auto.progress} />
                    <p style={{ color: '#94a3b8', fontSize: '0.75rem', margin: '0.25rem 0 0' }}>
                      Step {auto.current_step} of {auto.total_steps}
                    </p>
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    <Badge status={auto.status as ExecutionStatus} />
                  </td>
                  <td style={{ padding: '0.75rem', color: '#64748b', fontSize: '0.85rem' }}>
                    {auto.started_at ? new Date(auto.started_at).toLocaleString() : 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
