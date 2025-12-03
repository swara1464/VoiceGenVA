// frontend/src/components/ApprovalModal.jsx
import React from 'react';

export default function ApprovalModal({ isOpen, message, onApprove, onReject }) {
  if (!isOpen) return null;

  const modalStyle = {
    position: 'fixed',
    top: '0',
    left: '0',
    width: '100%',
    height: '100%',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  };

  const contentStyle = {
    backgroundColor: '#fff',
    padding: '20px',
    borderRadius: '10px',
    maxWidth: '400px',
    textAlign: 'center',
    color: '#333'
  };

  const buttonStyle = {
    padding: '10px 20px',
    margin: '10px',
    cursor: 'pointer',
    border: 'none',
    borderRadius: '5px',
    fontWeight: 'bold'
  };

  return (
    <div style={modalStyle}>
      <div style={contentStyle}>
        <h3>Agent Action Approval Required</h3>
        <p>{message}</p>
        <button 
          onClick={onApprove} 
          style={{ ...buttonStyle, backgroundColor: '#4CAF50', color: 'white' }}
        >
          ✅ Approve and Execute
        </button>
        <button 
          onClick={onReject} 
          style={{ ...buttonStyle, backgroundColor: '#f44336', color: 'white' }}
        >
          ❌ Reject
        </button>
      </div>
    </div>
  );
}