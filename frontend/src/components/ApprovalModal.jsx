import React from 'react';

export default function ApprovalModal({ isOpen, message, onApprove, onReject }) {
  if (!isOpen) return null;

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
        padding: '2.5rem',
        borderRadius: '16px',
        maxWidth: '500px',
        width: '90%',
        textAlign: 'center',
        color: '#1a1a1a',
        boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
        animation: 'fadeIn 0.3s ease-in'
      }}>
        <div style={{
          fontSize: "3rem",
          marginBottom: "1rem"
        }}>
          🔐
        </div>
        <h3 style={{
          fontSize: '1.6rem',
          marginBottom: '1.5rem',
          fontWeight: '700',
          color: '#1a1a1a'
        }}>
          Action Approval Required
        </h3>
        <p style={{
          fontSize: '1.05rem',
          marginBottom: '2rem',
          color: '#555',
          lineHeight: '1.6',
          padding: '1rem',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px',
          border: '1px solid #e0e0e0'
        }}>
          {message}
        </p>
        <div style={{
          display: 'flex',
          gap: '1rem',
          justifyContent: 'center'
        }}>
          <button
            onClick={onApprove}
            style={{
              padding: '0.9rem 2rem',
              cursor: 'pointer',
              border: 'none',
              borderRadius: '10px',
              fontWeight: '600',
              fontSize: '1rem',
              backgroundColor: '#2e7d32',
              color: 'white',
              boxShadow: '0 2px 8px rgba(46, 125, 50, 0.3)',
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = '#1b5e20';
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0 4px 12px rgba(46, 125, 50, 0.4)';
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = '#2e7d32';
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = '0 2px 8px rgba(46, 125, 50, 0.3)';
            }}
          >
            <span style={{ fontSize: '1.2rem' }}>✓</span>
            Approve and Execute
          </button>
          <button
            onClick={onReject}
            style={{
              padding: '0.9rem 2rem',
              cursor: 'pointer',
              border: 'none',
              borderRadius: '10px',
              fontWeight: '600',
              fontSize: '1rem',
              backgroundColor: '#d32f2f',
              color: 'white',
              boxShadow: '0 2px 8px rgba(211, 47, 47, 0.3)',
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = '#b71c1c';
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0 4px 12px rgba(211, 47, 47, 0.4)';
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = '#d32f2f';
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = '0 2px 8px rgba(211, 47, 47, 0.3)';
            }}
          >
            <span style={{ fontSize: '1.2rem' }}>✕</span>
            Reject
          </button>
        </div>
      </div>
    </div>
  );
}