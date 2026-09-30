import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { TextField } from '../components/forms/TextField';
import { FormSection } from '../components/forms/FormSection';
import { useForm } from '../hooks/useForm';

export function UserProfilePage() {
  const { auth, logout } = useAuth();
  const [activeTab, setActiveTab] = useState<'profile' | 'password' | 'notifications' | 'activity'>('profile');
  const [passwordLoading, setPasswordLoading] = useState(false);

  const { values: passwordValues, errors: passwordErrors, handleChange: handlePasswordChange, handleSubmit: handlePasswordSubmit } = useForm({
    initialValues: {
      current_password: '',
      new_password: '',
      confirm_password: '',
    },
    onSubmit: async (formValues) => {
      setPasswordLoading(true);
      try {
        await new Promise((r) => setTimeout(r, 500));
        alert('Password changed successfully');
      } finally {
        setPasswordLoading(false);
      }
    },
  });

  const { values: notifValues, handleChange: handleNotifChange } = useForm({
    initialValues: {
      email_alerts: true,
      case_updates: true,
      workflow_notifications: true,
      system_alerts: true,
    },
    onSubmit: async () => {
      alert('Notification preferences saved');
    },
  });

  const activityLog = [
    { timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(), action: 'Logged in' },
    { timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(), action: 'Created workflow WF-001' },
    { timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), action: 'Executed automation AUTO-001' },
  ];

  return (
    <div>
      <h1 style={{ color: '#f1f5f9', margin: 0, fontSize: '1.8rem', fontWeight: 700, marginBottom: '2rem' }}>
        User Profile
      </h1>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0', marginBottom: '2rem', borderBottom: '1px solid #334155' }}>
        {(['profile', 'password', 'notifications', 'activity'] as const).map((tab) => (
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
            {tab === 'profile' && '👤 Profile'}
            {tab === 'password' && '🔒 Security'}
            {tab === 'notifications' && '🔔 Notifications'}
            {tab === 'activity' && '📋 Activity'}
          </button>
        ))}
      </div>

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <Card title="Profile Information">
          <FormSection title="Personal Information" columns={2}>
            <TextField label="Full Name" value={auth.name || ''} disabled fullWidth />
            <TextField label="Email" value={auth.email || ''} disabled fullWidth />
            <TextField label="Organization ID" value={auth.organizationId || ''} disabled fullWidth />
          </FormSection>

          <div style={{ paddingTop: '1.5rem', borderTop: '1px solid #334155', display: 'flex', gap: '0.75rem' }}>
            <Button variant="ghost">Edit Profile</Button>
            <Button variant="danger" onClick={() => {
              logout();
              window.location.href = '/';
            }}>
              Sign Out
            </Button>
          </div>
        </Card>
      )}

      {/* Password Tab */}
      {activeTab === 'password' && (
        <Card title="Change Password">
          <form style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <FormSection title="Password Change">
              <TextField
                label="Current Password"
                name="current_password"
                type="password"
                value={String(passwordValues.current_password || '')}
                onChange={handlePasswordChange}
                error={passwordErrors.current_password}
                fullWidth
                required
              />
              <TextField
                label="New Password"
                name="new_password"
                type="password"
                value={String(passwordValues.new_password || '')}
                onChange={handlePasswordChange}
                error={passwordErrors.new_password}
                helperText="At least 8 characters with numbers and special characters"
                fullWidth
                required
              />
              <TextField
                label="Confirm Password"
                name="confirm_password"
                type="password"
                value={String(passwordValues.confirm_password || '')}
                onChange={handlePasswordChange}
                error={passwordErrors.confirm_password}
                fullWidth
                required
              />
            </FormSection>

            <div style={{ paddingTop: '1rem', borderTop: '1px solid #334155' }}>
              <Button
                variant="primary"
                onClick={() => handlePasswordSubmit({ preventDefault: () => {} } as any)}
                isLoading={passwordLoading}
              >
                Update Password
              </Button>
            </div>
          </form>
        </Card>
      )}

      {/* Notifications Tab */}
      {activeTab === 'notifications' && (
        <Card title="Notification Preferences">
          <FormSection title="Email Notifications">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {[
                { id: 'email_alerts', label: 'Email Alerts', desc: 'Critical system alerts' },
                { id: 'case_updates', label: 'Case Updates', desc: 'Case status changes' },
                { id: 'workflow_notifications', label: 'Workflow Notifications', desc: 'Workflow execution status' },
                { id: 'system_alerts', label: 'System Alerts', desc: 'General system notifications' },
              ].map((item) => (
                <label key={item.id} style={{ display: 'flex', gap: '0.75rem', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    name={item.id}
                    checked={(notifValues as Record<string, boolean>)[item.id] || false}
                    onChange={handleNotifChange}
                    style={{ cursor: 'pointer', marginTop: '2px' }}
                  />
                  <div>
                    <p style={{ color: '#cbd5e1', margin: 0, fontWeight: 500 }}>{item.label}</p>
                    <p style={{ color: '#64748b', margin: '0.25rem 0 0', fontSize: '0.8rem' }}>{item.desc}</p>
                  </div>
                </label>
              ))}
            </div>
          </FormSection>

          <div style={{ paddingTop: '1.5rem', borderTop: '1px solid #334155' }}>
            <Button variant="primary">Save Preferences</Button>
          </div>
        </Card>
      )}

      {/* Activity Tab */}
      {activeTab === 'activity' && (
        <Card title="Recent Activity">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {activityLog.map((item, idx) => (
              <div
                key={idx}
                style={{
                  paddingBottom: idx !== activityLog.length - 1 ? '1rem' : 0,
                  borderBottom: idx !== activityLog.length - 1 ? '1px solid #334155' : 'none',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.25rem' }}>
                  <span style={{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', background: '#3b82f6' }} />
                  <p style={{ color: '#cbd5e1', margin: 0, fontWeight: 500 }}>{item.action}</p>
                </div>
                <p style={{ color: '#64748b', margin: 0, fontSize: '0.85rem' }}>
                  {new Date(item.timestamp).toLocaleString()}
                </p>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
