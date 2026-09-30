import { useState } from 'react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { DataTable } from '../components/common/DataTable';
import { TextField } from '../components/forms/TextField';
import { FormSection } from '../components/forms/FormSection';
import type { Organization, User, UserRole } from '../types';

interface Column<T> {
  key: keyof T;
  label: string;
  render?: (value: unknown, row: T) => React.ReactNode;
  width?: string;
}

export function SettingsPage() {
  const [activeTab, setActiveTab] = useState<'org' | 'users' | 'roles' | 'audit'>('org');

  const organization: Organization = {
    id: 'org-1',
    name: 'PM-JAY Automation Platform',
    description: 'Production automation platform for PMJAY beneficiary processing',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };

  const users: User[] = [
    {
      id: '1',
      email: 'admin@example.com',
      name: 'Administrator',
      role: 'ADMIN',
      organization_id: 'org-1',
      is_active: true,
      created_at: new Date().toISOString(),
    },
    {
      id: '2',
      email: 'operator@example.com',
      name: 'John Operator',
      role: 'OPERATOR',
      organization_id: 'org-1',
      is_active: true,
      created_at: new Date().toISOString(),
    },
  ];

  const auditLogs = [
    {
      id: '1',
      user_email: 'admin@example.com',
      action: 'CREATED_WORKFLOW',
      resource_type: 'WORKFLOW',
      resource_id: 'WF-001',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: '2',
      user_email: 'operator@example.com',
      action: 'EXECUTED_AUTOMATION',
      resource_type: 'AUTOMATION',
      resource_id: 'AUTO-001',
      timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
    },
  ];

  const userColumns: Column<User>[] = [
    {
      key: 'name',
      label: 'User',
      render: (value, row) => (
        <div>
          <p style={{ color: '#cbd5e1', margin: 0, fontWeight: 500 }}>{value}</p>
          <p style={{ color: '#64748b', margin: '0.25rem 0 0', fontSize: '0.8rem' }}>
            {row.email}
          </p>
        </div>
      ),
    },
    {
      key: 'role',
      label: 'Role',
      render: (value) => (
        <Badge status={value as UserRole} label={String(value).toUpperCase()} />
      ),
    },
    {
      key: 'is_active',
      label: 'Status',
      render: (value) => (
        <Badge status={value ? 'ACTIVE' : 'INACTIVE'} label={value ? 'Active' : 'Inactive'} />
      ),
    },
    {
      key: 'created_at',
      label: 'Created',
      render: (value) => (
        <span style={{ color: '#64748b', fontSize: '0.85rem' }}>
          {new Date(value as string).toLocaleDateString()}
        </span>
      ),
    },
  ];

  const auditColumns: Column<(typeof auditLogs)[0]>[] = [
    {
      key: 'user_email',
      label: 'User',
      render: (value) => <span style={{ color: '#cbd5e1' }}>{value}</span>,
    },
    {
      key: 'action',
      label: 'Action',
      render: (value) => <span style={{ color: '#60a5fa' }}>{String(value).replace(/_/g, ' ')}</span>,
    },
    {
      key: 'resource_type',
      label: 'Resource',
      render: (value) => <span style={{ color: '#cbd5e1' }}>{value}</span>,
    },
    {
      key: 'timestamp',
      label: 'Timestamp',
      render: (value) => (
        <span style={{ color: '#64748b', fontSize: '0.85rem' }}>
          {new Date(value as string).toLocaleString()}
        </span>
      ),
    },
  ];

  return (
    <div>
      <h1 style={{ color: '#f1f5f9', margin: 0, fontSize: '1.8rem', fontWeight: 700, marginBottom: '2rem' }}>
        Organization Settings
      </h1>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0', marginBottom: '2rem', borderBottom: '1px solid #334155' }}>
        {(['org', 'users', 'roles', 'audit'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              background: 'transparent',
              color: activeTab === tab ? '#60a5fa' : '#475569',
              border: 'none',
              borderBottom: activeTab === tab ? '2px solid #3b82f6' : '2px solid transparent',
              padding: '0.6rem 1.25rem',
              fontWeight: activeTab === tab ? 700 : 400,
              fontSize: '0.9rem',
              cursor: 'pointer',
            }}
          >
            {tab === 'org' && '🏢 Organization'}
            {tab === 'users' && '👥 Users'}
            {tab === 'roles' && '🔐 Roles'}
            {tab === 'audit' && '📋 Audit Log'}
          </button>
        ))}
      </div>

      {/* Organization Tab */}
      {activeTab === 'org' && (
        <Card title="Organization Details">
          <FormSection title="Basic Information" columns={2}>
            <TextField
              label="Organization Name"
              value={organization.name}
              disabled
              fullWidth
            />
            <TextField
              label="Organization ID"
              value={organization.id}
              disabled
              fullWidth
            />
          </FormSection>

          <FormSection title="Description">
            <div style={{ color: '#cbd5e1', fontSize: '0.9rem' }}>
              {organization.description}
            </div>
          </FormSection>

          <div style={{ paddingTop: '1.5rem', borderTop: '1px solid #334155' }}>
            <Button variant="primary">Edit Organization</Button>
          </div>
        </Card>
      )}

      {/* Users Tab */}
      {activeTab === 'users' && (
        <div>
          <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2 style={{ color: '#f1f5f9', margin: 0, fontSize: '1.1rem', fontWeight: 700 }}>
              User Management
            </h2>
            <Button variant="primary">➕ Add User</Button>
          </div>
          <DataTable<User> columns={userColumns} data={users} />
        </div>
      )}

      {/* Roles Tab */}
      {activeTab === 'roles' && (
        <div>
          <div style={{ marginBottom: '2rem' }}>
            <h2 style={{ color: '#f1f5f9', margin: 0, fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem' }}>
              Role-Based Access Control
            </h2>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                gap: '1rem',
              }}
            >
              {['ADMIN', 'SUPERVISOR', 'OPERATOR', 'VIEWER'].map((role) => (
                <Card key={role} title={role}>
                  <ul style={{ margin: 0, paddingLeft: '1.25rem', color: '#cbd5e1', fontSize: '0.85rem' }}>
                    {role === 'ADMIN' && (
                      <>
                        <li>Manage all resources</li>
                        <li>Manage users and roles</li>
                        <li>View audit logs</li>
                      </>
                    )}
                    {role === 'SUPERVISOR' && (
                      <>
                        <li>Create workflows</li>
                        <li>Approve cases</li>
                        <li>View reports</li>
                      </>
                    )}
                    {role === 'OPERATOR' && (
                      <>
                        <li>Execute workflows</li>
                        <li>Manage cases</li>
                        <li>View status</li>
                      </>
                    )}
                    {role === 'VIEWER' && (
                      <>
                        <li>View dashboards</li>
                        <li>Read-only access</li>
                      </>
                    )}
                  </ul>
                </Card>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Audit Log Tab */}
      {activeTab === 'audit' && (
        <div>
          <h2 style={{ color: '#f1f5f9', margin: '0 0 1rem', fontSize: '1.1rem', fontWeight: 700 }}>
            Audit Log
          </h2>
          <DataTable<(typeof auditLogs)[0]> columns={auditColumns} data={auditLogs} />
        </div>
      )}
    </div>
  );
}
