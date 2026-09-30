import { useState, useEffect } from 'react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { DataTable } from '../components/common/DataTable';
import { TextField } from '../components/forms/TextField';
import { TextAreaField } from '../components/forms/TextAreaField';
import { FormSection } from '../components/forms/FormSection';
import { useForm } from '../hooks/useForm';
import type { Portal, PortalStatus } from '../types';

interface Column<T> {
  key: keyof T;
  label: string;
  render?: (value: unknown, row: T, idx: number) => React.ReactNode;
  width?: string;
}

export function PortalsPage() {
  const [portals, setPortals] = useState<Portal[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPortal, setEditingPortal] = useState<Portal | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<PortalStatus | ''>('');
  const [loading, setLoading] = useState(false);

  // Mock initial data
  useEffect(() => {
    const mockPortals: Portal[] = [
      {
        id: '1',
        organization_id: 'org-1',
        name: 'PM-JAY Portal',
        description: 'Primary PMJAY beneficiary processing portal',
        url: 'https://pmjay.portal.local',
        status: 'ACTIVE',
        automation_config: { retries: 3, timeout: 30000 },
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      {
        id: '2',
        organization_id: 'org-1',
        name: 'Hospital Integration Portal',
        description: 'Hospital management system integration',
        url: 'https://hospital.portal.local',
        status: 'ACTIVE',
        automation_config: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      {
        id: '3',
        organization_id: 'org-1',
        name: 'Claims Portal (Legacy)',
        description: 'Legacy claims processing system',
        url: 'https://legacy-claims.portal.local',
        status: 'MAINTENANCE',
        automation_config: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ];
    setPortals(mockPortals);
  }, []);

  const { values, errors, handleChange, handleSubmit, reset } = useForm({
    initialValues: editingPortal || {
      name: '',
      description: '',
      url: '',
    },
    onSubmit: async (formValues) => {
      setLoading(true);
      try {
        // Simulate API call
        await new Promise((r) => setTimeout(r, 500));

        if (editingPortal) {
          setPortals((prev) =>
            prev.map((p) =>
              p.id === editingPortal.id
                ? {
                    ...p,
                    ...formValues,
                    updated_at: new Date().toISOString(),
                  }
                : p
            )
          );
        } else {
          const newPortal: Portal = {
            id: String(Math.random()),
            organization_id: 'org-1',
            name: (formValues as Record<string, unknown>).name as string,
            description: (formValues as Record<string, unknown>).description as string,
            url: (formValues as Record<string, unknown>).url as string,
            status: 'ACTIVE',
            automation_config: null,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          };
          setPortals((prev) => [...prev, newPortal]);
        }

        setIsModalOpen(false);
        setEditingPortal(null);
        reset();
      } finally {
        setLoading(false);
      }
    },
  });

  const handleOpenModal = () => {
    setEditingPortal(null);
    setIsModalOpen(true);
  };

  const handleDelete = (portalId: string) => {
    if (confirm('Are you sure you want to delete this portal?')) {
      setPortals((prev) => prev.filter((p) => p.id !== portalId));
    }
  };

  const handleModalConfirm = async () => {
    setLoading(true);
    try {
      await new Promise((r) => setTimeout(r, 500));

      if (editingPortal) {
        setPortals((prev) =>
          prev.map((p) =>
            p.id === editingPortal.id
              ? {
                  ...p,
                  name: String(values.name || ''),
                  description: String(values.description || ''),
                  url: String(values.url || ''),
                  updated_at: new Date().toISOString(),
                }
              : p
          )
        );
      } else {
        const newPortal: Portal = {
          id: String(Math.random()),
          organization_id: 'org-1',
          name: String(values.name || ''),
          description: String(values.description || ''),
          url: String(values.url || ''),
          status: 'ACTIVE',
          automation_config: null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
        setPortals((prev) => [...prev, newPortal]);
      }

      setIsModalOpen(false);
      setEditingPortal(null);
      reset();
    } finally {
      setLoading(false);
    }
  };

  const filteredPortals = portals.filter((p) => {
    const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = !statusFilter || p.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ color: '#f1f5f9', margin: 0, fontSize: '1.8rem', fontWeight: 700 }}>
            Portal Management
          </h1>
          <p style={{ color: '#64748b', margin: '0.5rem 0 0', fontSize: '0.95rem' }}>
            Manage and monitor portal integrations
          </p>
        </div>
        <Button variant="primary" onClick={handleOpenModal}>
          ➕ Create Portal
        </Button>
      </div>

      {/* Filters */}
      <Card style={{ marginBottom: '1.5rem' }}>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1rem',
          }}
        >
          <TextField
            placeholder="Search portals..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            fullWidth
          />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as PortalStatus | '')}
            style={{
              background: '#0f172a',
              color: '#cbd5e1',
              border: '1px solid #334155',
              borderRadius: '6px',
              padding: '0.6rem 0.75rem',
              fontSize: '0.9rem',
              cursor: 'pointer',
            }}
          >
            <option value="">All Statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="INACTIVE">Inactive</option>
            <option value="MAINTENANCE">Maintenance</option>
          </select>
        </div>
      </Card>

      {/* Data Table */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', background: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #334155', background: '#0f172a' }}>
                <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: '#94a3b8', fontWeight: 700, fontSize: '0.85rem' }}>Portal Name</th>
                <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: '#94a3b8', fontWeight: 700, fontSize: '0.85rem' }}>URL</th>
                <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: '#94a3b8', fontWeight: 700, fontSize: '0.85rem' }}>Status</th>
                <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: '#94a3b8', fontWeight: 700, fontSize: '0.85rem' }}>Created</th>
                <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: '#94a3b8', fontWeight: 700, fontSize: '0.85rem' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredPortals.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ padding: '2rem', textAlign: 'center', color: '#64748b' }}>
                    No portals found
                  </td>
                </tr>
              ) : (
                filteredPortals.map((portal, idx) => (
                  <tr key={portal.id} style={{ borderBottom: '1px solid #334155', background: idx % 2 === 0 ? '#1e293b' : '#0f172a' }}>
                    <td style={{ padding: '0.75rem 1rem', color: '#cbd5e1', fontWeight: 500 }}>{portal.name}</td>
                    <td style={{ padding: '0.75rem 1rem', color: '#64748b', fontSize: '0.85rem' }}>{portal.url}</td>
                    <td style={{ padding: '0.75rem 1rem' }}>
                      <Badge status={portal.status as PortalStatus} />
                    </td>
                    <td style={{ padding: '0.75rem 1rem', color: '#64748b', fontSize: '0.85rem' }}>
                      {new Date(portal.created_at).toLocaleDateString()}
                    </td>
                    <td style={{ padding: '0.75rem 1rem' }}>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => {
                            setEditingPortal(portal);
                            setIsModalOpen(true);
                          }}
                        >
                          Edit
                        </Button>
                        <Button
                          size="sm"
                          variant="danger"
                          onClick={() => handleDelete(portal.id)}
                        >
                          Delete
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create/Edit Modal */}
      <Modal
        isOpen={isModalOpen}
        title={editingPortal ? 'Edit Portal' : 'Create New Portal'}
        onClose={() => setIsModalOpen(false)}
        onConfirm={() => handleSubmit({ preventDefault: () => {} } as any)}
        confirmLoading={loading}
      >
        <form style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <FormSection title="Portal Information">
            <TextField
              label="Portal Name"
              name="name"
              value={String(values.name || '')}
              onChange={handleChange}
              error={errors.name}
              fullWidth
              required
            />
            <TextField
              label="Portal URL"
              name="url"
              type="url"
              value={String(values.url || '')}
              onChange={handleChange}
              error={errors.url}
              fullWidth
              required
            />
          </FormSection>

          <FormSection title="Description">
            <TextAreaField
              label="Portal Description"
              name="description"
              value={String(values.description || '')}
              onChange={handleChange}
              error={errors.description}
              fullWidth
            />
          </FormSection>
        </form>
      </Modal>
    </div>
  );
}
