import React from 'react';

export default function QuickActions({ onActionClick }) {
  const actions = [
    { label: 'Gmail', icon: '📧', example: 'send email to john' },
    { label: 'Drive', icon: '📁', example: 'search drive for resume' },
    { label: 'Calendar', icon: '📅', example: 'schedule meeting tomorrow' },
    { label: 'Meet', icon: '📹', example: 'start a meeting now' },
    { label: 'Tasks', icon: '✓', example: 'create task project report' },
    { label: 'Docs', icon: '📄', example: 'create a new document' }
  ];

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
      gap: '0.75rem',
      marginBottom: '1rem',
      padding: '1rem',
      backgroundColor: '#f9f9f9',
      borderRadius: '12px'
    }}>
      {actions.map((action) => (
        <button
          key={action.label}
          onClick={() => onActionClick(action.example)}
          title={`Example: "${action.example}"`}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.5rem',
            padding: '0.75rem 1rem',
            backgroundColor: '#fff',
            border: '2px solid #e0e0e0',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '0.9rem',
            fontWeight: '600',
            color: '#1a1a1a',
            transition: 'all 0.2s ease',
            whiteSpace: 'nowrap'
          }}
          onMouseEnter={(e) => {
            e.target.style.backgroundColor = '#2196F3';
            e.target.style.color = '#fff';
            e.target.style.borderColor = '#2196F3';
          }}
          onMouseLeave={(e) => {
            e.target.style.backgroundColor = '#fff';
            e.target.style.color = '#1a1a1a';
            e.target.style.borderColor = '#e0e0e0';
          }}
        >
          <span style={{ fontSize: '1.2rem' }}>{action.icon}</span>
          <span>{action.label}</span>
        </button>
      ))}
    </div>
  );
}
