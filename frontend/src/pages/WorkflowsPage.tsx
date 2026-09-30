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
import type { Workflow, WorkflowStatus } from '../types';

interface Column<T> {
  key: keyof T;
  label: string;
  render?: (value: unknown, row: T) => React.ReactNode;
  width?: string;
}

export function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingWorkflow, setEditingWorkflow] = useState<Workflow | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<WorkflowStatus | ''>('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const mockWorkflows: Workflow[] = [
      {
        id: '1',
        organization_id: 'org-1',
        name: 'PM-JAY Beneficiary Processing',
        description: 'Automated beneficiary case processing workflow',
        version: 2,
        status: 'PUBLISHED',
        steps: [
          { id: '1-1', name: 'Validate Input', description: '', order: 1, action_type: 'validate', configuration: {} },
          { id: '1-2', name: 'Portal Login', description: '', order: 2, action_type: 'login', configuration: {} },
        ],
        created_by: 'admin@example.com',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      {
        id: '2',
        organization_id: 'org-1',
        name: 'Hospital Integration',
        description: 'Hospital management system integration',
        version: 1,
        status: 'DRAFT',
        steps: [],
        created_by: 'admin@example.com',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ];
    setWorkflows(mockWorkflows);
  }, []);

  const { values, errors, handleChange, handleSubmit, reset } = useForm({
    initialValues: editingWorkflow || {
      name: '',
      description: '',
    },
    onSubmit: async (formValues) => {
      setLoading(true);
      try {
        await new Promise((r) => setTimeout(r, 500));

        if (editingWorkflow) {
          setWorkflows((prev) =>
            prev.map((w) =>
              w.id === editingWorkflow.id
                ? { ...w, ...formValues, updated_at: new Date().toISOString() }
                : w
            )
          );
        } else {
          const newWorkflow: Workflow = {
            id: String(Math.random()),
            organization_id: 'org-1',
            name: (formValues as Record<string, unknown>).name as string,
            description: (formValues as Record<string, unknown>).description as string,
            version: 1,
            status: 'DRAFT',
            steps: [],
            created_by: 'admin@example.com',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          };
          setWorkflows((prev) => [...prev, newWorkflow]);
        }

        setIsModalOpen(false);
        setEditingWorkflow(null);
        reset();
      } finally {
        setLoading(false);
      }
    },
  });

  const filteredWorkflows = workflows.filter((w) => {
    const matchesSearch = w.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = !statusFilter || w.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const columns: Column<Workflow>[] = [
    {
      key: 'name',
      label: 'Workflow Name',
      render: (value, row) => (
        <div>
          <p style={{ color: '#cbd5e1', margin: 0, fontWeight: 500 }}>{value}</p>
          <p style={{ color: '#64748b', margin: '0.25rem 0 0', fontSize: '0.8rem' }}>
            v{row.version} • {row.steps.length} steps
          </p>
        </div>
      ),
    },
    {
      key: 'description',
      label: 'Description',
      render: (value) => (
        <span style={{ color: '#cbd5e1', fontSize: '0.9rem' }}>
          {String(value).substring(0, 50)}
        </span>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      render: (value) => <Badge status={value as WorkflowStatus} />,
    },
    {
      key: 'created_by',
      label: 'Created By',
      render: (value) => <span style={{ color: '#cbd5e1' }}>{value}</span>,
    },
    {
      key: 'id',
      label: 'Actions',
      render: (_, row) => (
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <Button size="sm" variant="secondary">
            View
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => {
              setEditingWorkflow(row);
              setIsModalOpen(true);
            }}
          >
            Edit
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ color: '#f1f5f9', margin: 0, fontSize: '1.8rem', fontWeight: 700 }}>
            Workflow Management
          </h1>
          <p style={{ color: '#64748b', margin: '0.5rem 0 0', fontSize: '0.95rem' }}>
            Create and manage automation workflows
          </p>
        </div>
        <Button variant="primary" onClick={() => setIsModalOpen(true)}>
          ➕ Create Workflow
        </Button>
      </div>

      <Card style={{ marginBottom: '1.5rem' }}>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1rem',
          }}
        >
          <TextField
            placeholder="Search workflows..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            fullWidth
          />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as WorkflowStatus | '')}
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
            <option value="DRAFT">Draft</option>
            <option value="PUBLISHED">Published</option>
            <option value="ARCHIVED">Archived</option>
          </select>
        </div>
      </Card>

      <div style={{ marginBottom: '2rem' }}>
        <DataTable<Workflow> columns={columns} data={filteredWorkflows} loading={loading} />
      </div>

      <Modal
        isOpen={isModalOpen}
        title={editingWorkflow ? 'Edit Workflow' : 'Create New Workflow'}
        onClose={() => setIsModalOpen(false)}
        onConfirm={() => handleSubmit({ preventDefault: () => {} } as any)}
        confirmLoading={loading}
      >
        <FormSection title="Workflow Information">
          <TextField
            label="Workflow Name"
            name="name"
            value={String(values.name || '')}
            onChange={handleChange}
            error={errors.name}
            fullWidth
            required
          />
          <TextAreaField
            label="Description"
            name="description"
            value={String(values.description || '')}
            onChange={handleChange}
            error={errors.description}
            fullWidth
          />
        </FormSection>
      </Modal>
    </div>
  );
}
