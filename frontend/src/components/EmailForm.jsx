import React, { useState } from 'react';

export default function EmailForm({ isOpen, initialData, onSend, onCancel }) {
  const [formData, setFormData] = useState({
    to: initialData?.to || '',
    cc: initialData?.cc || '',
    bcc: initialData?.bcc || '',
    subject: initialData?.subject || '',
    body: initialData?.body || ''
  });

  if (!isOpen) return null;

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = () => {
    if (!formData.to || !formData.subject || !formData.body) {
      alert('Please fill in To, Subject, and Body fields');
      return;
    }
    onSend(formData);
  };

  return (
    <div style={{
      position: 'fixed',
      top: '0',
      left: '0',
      width: '100%',
      height: '100%',
      backgroundColor: 'rgba(0, 0, 0, 0.6)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      zIndex: 1000,
      backdropFilter: 'blur(4px)',
      animation: 'fadeIn 0.2s ease-in'
    }}>
      <div style={{
        backgroundColor: '#fff',
        padding: '2rem',
        borderRadius: '16px',
        maxWidth: '700px',
        width: '90%',
        maxHeight: '90vh',
        overflowY: 'auto',
        color: '#1a1a1a',
        boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
        animation: 'fadeIn 0.3s ease-in'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1.5rem'
        }}>
          <h3 style={{
            fontSize: '1.6rem',
            margin: 0,
            fontWeight: '700',
            color: '#1a1a1a',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            <span style={{ fontSize: '1.8rem' }}>📧</span>
            Compose Email
          </h3>
          <button
            onClick={onCancel}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '1.5rem',
              cursor: 'pointer',
              color: '#666',
              padding: '0.5rem'
            }}
          >
            ×
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label style={{
              display: 'block',
              marginBottom: '0.3rem',
              fontWeight: '600',
              fontSize: '0.9rem',
              color: '#555'
            }}>
              To: <span style={{ color: '#d32f2f' }}>*</span>
            </label>
            <input
              type="email"
              value={formData.to}
              onChange={(e) => handleChange('to', e.target.value)}
              placeholder="recipient@example.com"
              style={{
                width: '100%',
                padding: '0.7rem',
                fontSize: '1rem',
                border: '2px solid #e0e0e0',
                borderRadius: '8px',
                outline: 'none',
                transition: 'all 0.2s'
              }}
              onFocus={(e) => e.target.style.borderColor = '#1976d2'}
              onBlur={(e) => e.target.style.borderColor = '#e0e0e0'}
            />
          </div>

          <div>
            <label style={{
              display: 'block',
              marginBottom: '0.3rem',
              fontWeight: '600',
              fontSize: '0.9rem',
              color: '#555'
            }}>
              CC:
            </label>
            <input
              type="email"
              value={formData.cc}
              onChange={(e) => handleChange('cc', e.target.value)}
              placeholder="cc@example.com (optional)"
              style={{
                width: '100%',
                padding: '0.7rem',
                fontSize: '1rem',
                border: '2px solid #e0e0e0',
                borderRadius: '8px',
                outline: 'none',
                transition: 'all 0.2s'
              }}
              onFocus={(e) => e.target.style.borderColor = '#1976d2'}
              onBlur={(e) => e.target.style.borderColor = '#e0e0e0'}
            />
          </div>

          <div>
            <label style={{
              display: 'block',
              marginBottom: '0.3rem',
              fontWeight: '600',
              fontSize: '0.9rem',
              color: '#555'
            }}>
              BCC:
            </label>
            <input
              type="email"
              value={formData.bcc}
              onChange={(e) => handleChange('bcc', e.target.value)}
              placeholder="bcc@example.com (optional)"
              style={{
                width: '100%',
                padding: '0.7rem',
                fontSize: '1rem',
                border: '2px solid #e0e0e0',
                borderRadius: '8px',
                outline: 'none',
                transition: 'all 0.2s'
              }}
              onFocus={(e) => e.target.style.borderColor = '#1976d2'}
              onBlur={(e) => e.target.style.borderColor = '#e0e0e0'}
            />
          </div>

          <div>
            <label style={{
              display: 'block',
              marginBottom: '0.3rem',
              fontWeight: '600',
              fontSize: '0.9rem',
              color: '#555'
            }}>
              Subject: <span style={{ color: '#d32f2f' }}>*</span>
            </label>
            <input
              type="text"
              value={formData.subject}
              onChange={(e) => handleChange('subject', e.target.value)}
              placeholder="Email subject"
              style={{
                width: '100%',
                padding: '0.7rem',
                fontSize: '1rem',
                border: '2px solid #e0e0e0',
                borderRadius: '8px',
                outline: 'none',
                transition: 'all 0.2s'
              }}
              onFocus={(e) => e.target.style.borderColor = '#1976d2'}
              onBlur={(e) => e.target.style.borderColor = '#e0e0e0'}
            />
          </div>

          <div>
            <label style={{
              display: 'block',
              marginBottom: '0.3rem',
              fontWeight: '600',
              fontSize: '0.9rem',
              color: '#555'
            }}>
              Body: <span style={{ color: '#d32f2f' }}>*</span>
            </label>
            <textarea
              value={formData.body}
              onChange={(e) => handleChange('body', e.target.value)}
              placeholder="Email body content"
              rows={12}
              style={{
                width: '100%',
                padding: '0.7rem',
                fontSize: '1rem',
                border: '2px solid #e0e0e0',
                borderRadius: '8px',
                outline: 'none',
                resize: 'vertical',
                fontFamily: 'inherit',
                lineHeight: '1.6',
                transition: 'all 0.2s'
              }}
              onFocus={(e) => e.target.style.borderColor = '#1976d2'}
              onBlur={(e) => e.target.style.borderColor = '#e0e0e0'}
            />
          </div>
        </div>

        <div style={{
          display: 'flex',
          gap: '1rem',
          marginTop: '1.5rem',
          justifyContent: 'flex-end'
        }}>
          <button
            onClick={onCancel}
            style={{
              padding: '0.9rem 2rem',
              cursor: 'pointer',
              border: '2px solid #e0e0e0',
              borderRadius: '10px',
              fontWeight: '600',
              fontSize: '1rem',
              backgroundColor: 'white',
              color: '#666',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = '#f5f5f5';
              e.target.style.borderColor = '#bbb';
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = 'white';
              e.target.style.borderColor = '#e0e0e0';
            }}
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            style={{
              padding: '0.9rem 2rem',
              cursor: 'pointer',
              border: 'none',
              borderRadius: '10px',
              fontWeight: '600',
              fontSize: '1rem',
              backgroundColor: '#1976d2',
              color: 'white',
              boxShadow: '0 2px 8px rgba(25, 118, 210, 0.3)',
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = '#1565c0';
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0 4px 12px rgba(25, 118, 210, 0.4)';
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = '#1976d2';
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = '0 2px 8px rgba(25, 118, 210, 0.3)';
            }}
          >
            <span style={{ fontSize: '1.2rem' }}>📤</span>
            Send Email
          </button>
        </div>
      </div>
    </div>
  );
}
