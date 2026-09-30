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
import type { Case, CaseStatus } from '../types';

interface Column<T> {
  key: keyof T;
  label: string;
  render?: (value: unknown, row: T) => React.ReactNode;
  width?: string;
}

export function CasesPage() {
  const [cases, setCases] = useState<Case[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedCase, setSelectedCase] = useState<Case | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<CaseStatus | ''>('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const mockCases: Case[] = [
      {
        id: '1',
        organization_id: 'org-1',
        case_number: 'CASE-2024-001',
        beneficiary_id: 'BEN-001',
        beneficiary: {
          id: 'BEN-001',
          name: 'John Doe',
          email: 'john@example.com',
          phone: '+91-9876543210',
          date_of_birth: '1985-05-15',
        },
        status: 'COMPLETED',
        description: 'Beneficiary case processing',
        estimated_amount: 50000,
        created_by: 'admin@example.com',
        created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date().toISOString(),
        completed_at: new Date().toISOString(),
        case_history: [],
      },
      {
        id: '2',
        organization_id: 'org-1',
        case_number: 'CASE-2024-002',
        beneficiary_id: 'BEN-002',
        beneficiary: {
          id: 'BEN-002',
          name: 'Jane Smith',
          email: 'jane@example.com',
          phone: '+91-9876543211',
          date_of_birth: '1990-03-20',
        },
        status: 'IN_PROGRESS',
        description: 'Hospital treatment case',
        estimated_amount: 75000,
        created_by: 'admin@example.com',
        created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date().toISOString(),
        completed_at: null,
        case_history: [],
      },
    ];
    setCases(mockCases);
  }, []);

  const { values, errors, handleChange, handleSubmit, reset } = useForm({
    initialValues: {
      beneficiary_id: '',
      description: '',
      estimated_amount: '',
    },
    onSubmit: async (formValues) => {
      setLoading(true);
      try {
        await new Promise((r) => setTimeout(r, 500));
        const newCase: Case = {
          id: String(Math.random()),
          organization_id: 'org-1',
          case_number: `CASE-${new Date().getFullYear()}-${Math.random().toString().slice(2, 5)}`,
          beneficiary_id: (formValues as Record<string, unknown>).beneficiary_id as string,
          beneficiary: {
            id: (formValues as Record<string, unknown>).beneficiary_id as string,
            name: 'New Beneficiary',
            email: 'beneficiary@example.com',
            phone: '+91-9000000000',
            date_of_birth: '1990-01-01',
          },
          status: 'INITIATED',
          description: (formValues as Record<string, unknown>).description as string,
          estimated_amount: Number((formValues as Record<string, unknown>).estimated_amount),
          created_by: 'admin@example.com',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          completed_at: null,
          case_history: [],
        };
        setCases((prev) => [...prev, newCase]);
        setIsModalOpen(false);
        reset();
      } finally {
        setLoading(false);
      }
    },
  });

  const filteredCases = cases.filter((c) => {
    const matchesSearch = c.case_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.beneficiary.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = !statusFilter || c.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const columns: Column<Case>[] = [
    {
      key: 'case_number',
      label: 'Case #',
      render: (value) => <span style={{ color: '#60a5fa', fontWeight: 500 }}>{value}</span>,
    },
    {
      key: 'beneficiary' as any,
      label: 'Beneficiary',
      render: (_, row) => (
        <div>
          <p style={{ color: '#cbd5e1', margin: 0, fontWeight: 500 }}>{row.beneficiary.name}</p>
          <p style={{ color: '#64748b', margin: '0.25rem 0 0', fontSize: '0.8rem' }}>
            {row.beneficiary.email}
          </p>
        </div>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      render: (value) => <Badge status={value as CaseStatus} />,
    },
    {
      key: 'estimated_amount',
      label: 'Amount',
      render: (value) => (
        <span style={{ color: '#cbd5e1' }}>₹{Number(value).toLocaleString('en-IN')}</span>
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

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ color: '#f1f5f9', margin: 0, fontSize: '1.8rem', fontWeight: 700 }}>
            Case Management
          </h1>
          <p style={{ color: '#64748b', margin: '0.5rem 0 0', fontSize: '0.95rem' }}>
            Track and manage beneficiary cases
          </p>
        </div>
        <Button variant="primary" onClick={() => setIsModalOpen(true)}>
          ➕ Create Case
        </Button>
      </div>

      <Card style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <TextField
            placeholder="Search cases or beneficiaries..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            fullWidth
          />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as CaseStatus | '')}
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
            <option value="INITIATED">Initiated</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="COMPLETED">Completed</option>
          </select>
        </div>
      </Card>

      <div style={{ marginBottom: '2rem' }}>
        <DataTable<Case> columns={columns} data={filteredCases} loading={loading} />
      </div>

      <Modal
        isOpen={isModalOpen}
        title="Create New Case"
        onClose={() => setIsModalOpen(false)}
        onConfirm={() => handleSubmit({ preventDefault: () => {} } as any)}
        confirmLoading={loading}
      >
        <FormSection title="Case Information">
          <TextField
            label="Beneficiary ID"
            name="beneficiary_id"
            value={String(values.beneficiary_id || '')}
            onChange={handleChange}
            error={errors.beneficiary_id}
            fullWidth
            required
          />
          <TextField
            label="Estimated Amount"
            name="estimated_amount"
            type="number"
            value={String(values.estimated_amount || '')}
            onChange={handleChange}
            error={errors.estimated_amount}
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
