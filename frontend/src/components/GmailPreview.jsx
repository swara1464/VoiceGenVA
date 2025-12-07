import React, { useState } from 'react';
import axios from '../axios';

export default function GmailPreview({ isOpen, preview, onSend, onCancel, userEmail }) {
  const [editMode, setEditMode] = useState(false);
  const [editedData, setEditedData] = useState({
    to: preview?.to || [],
    cc: preview?.cc || [],
    bcc: preview?.bcc || [],
    subject: preview?.subject || '',
    body: preview?.body || ''
  });

  console.log("🔍 GmailPreview render - isOpen:", isOpen, "preview:", preview);

  if (!isOpen || !preview) {
    console.log("❌ GmailPreview not showing - isOpen:", isOpen, "preview:", preview);
    return null;
  }

  console.log("✅ GmailPreview showing!");

  const handleEdit = () => {
    setEditedData({
      to: preview.to || [],
      cc: preview.cc || [],
      bcc: preview.bcc || [],
      subject: preview.subject || '',
      body: preview.body || ''
    });
    setEditMode(true);
  };

  const handleSaveEdit = () => {
    setEditMode(false);
  };

  const handleApproveAndSend = async () => {
    const dataToSend = editMode ? editedData : {
      to: preview.to,
      cc: preview.cc,
      bcc: preview.bcc,
      subject: preview.subject,
      body: preview.body
    };

    console.log("📤 Sending email with data:", { ...dataToSend, approved: true });

    try {
      const response = await axios.post('/agent/execute', {
        action: 'GMAIL_SEND',
        params: {
          ...dataToSend,
          approved: true
        }
      });

      console.log("📥 Send response:", response.data);

      if (response.data.success) {
        console.log("✅ Email sent successfully!");
        onSend(response.data);
      } else {
        console.error("❌ Email send failed:", response.data.message);
        alert('Failed to send email: ' + (response.data.message || 'Unknown error'));
      }
    } catch (error) {
      console.error('❌ Error sending email:', error);
      console.error('Error details:', error.response?.data);
      alert('Error sending email: ' + (error.response?.data?.message || error.message));
    }
  };

  if (preview.errors && preview.errors.length > 0) {
    return (
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        backgroundColor: 'rgba(0, 0, 0, 0.6)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 1000,
        backdropFilter: 'blur(4px)'
      }}>
        <div style={{
          backgroundColor: '#fff',
          padding: '2rem',
          borderRadius: '16px',
          maxWidth: '600px',
          width: '90%',
          color: '#1a1a1a',
          boxShadow: '0 8px 32px rgba(0,0,0,0.2)'
        }}>
          <h3>Email Compose Error</h3>
          <div style={{ color: '#d32f2f', marginBottom: '1rem' }}>
            {preview.errors.map((err, i) => <p key={i}>• {err}</p>)}
          </div>
          {preview.disambiguation_prompt && (
            <p style={{ color: '#666', marginBottom: '1.5rem' }}>
              {preview.disambiguation_prompt}
            </p>
          )}
          <button
            onClick={onCancel}
            style={{
              backgroundColor: '#2196F3',
              color: '#fff',
              padding: '0.75rem 1.5rem',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '1rem'
            }}
          >
            OK
          </button>
        </div>
      </div>
    );
  }

  const displayData = editMode ? editedData : {
    to: preview.to || [],
    cc: preview.cc || [],
    bcc: preview.bcc || [],
    subject: preview.subject || '',
    body: preview.body || ''
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      backgroundColor: 'rgba(0, 0, 0, 0.6)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      zIndex: 1000,
      backdropFilter: 'blur(4px)'
    }}>
      <div style={{
        backgroundColor: '#fff',
        padding: '2rem',
        borderRadius: '16px',
        maxWidth: '800px',
        width: '90%',
        maxHeight: '90vh',
        overflowY: 'auto',
        color: '#1a1a1a',
        boxShadow: '0 8px 32px rgba(0,0,0,0.2)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '1.6rem', margin: 0, fontWeight: '700' }}>
            📧 Review Email
          </h3>
          <button
            onClick={onCancel}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '1.5rem',
              cursor: 'pointer',
              color: '#666'
            }}
          >
            ✕
          </button>
        </div>

        {preview.warnings && preview.warnings.length > 0 && (
          <div style={{
            backgroundColor: '#fff3cd',
            padding: '0.75rem 1rem',
            borderRadius: '8px',
            marginBottom: '1rem',
            color: '#856404'
          }}>
            {preview.warnings.map((w, i) => <p key={i} style={{ margin: '0.25rem 0' }}>⚠ {w}</p>)}
          </div>
        )}

        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', fontWeight: '600', marginBottom: '0.5rem' }}>From</label>
          <input
            type="text"
            value={userEmail}
            disabled
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '1px solid #ddd',
              borderRadius: '8px',
              backgroundColor: '#f5f5f5'
            }}
          />
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', fontWeight: '600', marginBottom: '0.5rem' }}>To</label>
          {editMode ? (
            <input
              type="text"
              value={editedData.to.join(', ')}
              onChange={(e) => setEditedData({
                ...editedData,
                to: e.target.value.split(',').map(s => s.trim()).filter(Boolean)
              })}
              style={{
                width: '100%',
                padding: '0.75rem',
                border: '1px solid #2196F3',
                borderRadius: '8px'
              }}
            />
          ) : (
            <div style={{ padding: '0.75rem', backgroundColor: '#f5f5f5', borderRadius: '8px' }}>
              {displayData.to.join(', ')}
            </div>
          )}
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', fontWeight: '600', marginBottom: '0.5rem' }}>CC</label>
          {editMode ? (
            <input
              type="text"
              value={editedData.cc.join(', ')}
              onChange={(e) => setEditedData({
                ...editedData,
                cc: e.target.value.split(',').map(s => s.trim()).filter(Boolean)
              })}
              placeholder="Optional"
              style={{
                width: '100%',
                padding: '0.75rem',
                border: '1px solid #ddd',
                borderRadius: '8px'
              }}
            />
          ) : (
            <div style={{ padding: '0.75rem', backgroundColor: '#f5f5f5', borderRadius: '8px', color: displayData.cc.length === 0 ? '#999' : '#000' }}>
              {displayData.cc.length === 0 ? '(none)' : displayData.cc.join(', ')}
            </div>
          )}
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', fontWeight: '600', marginBottom: '0.5rem' }}>Subject</label>
          {editMode ? (
            <input
              type="text"
              value={editedData.subject}
              onChange={(e) => setEditedData({ ...editedData, subject: e.target.value })}
              style={{
                width: '100%',
                padding: '0.75rem',
                border: '1px solid #2196F3',
                borderRadius: '8px'
              }}
            />
          ) : (
            <div style={{ padding: '0.75rem', backgroundColor: '#f5f5f5', borderRadius: '8px', fontWeight: '500' }}>
              {displayData.subject}
            </div>
          )}
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', fontWeight: '600', marginBottom: '0.5rem' }}>Body</label>
          {editMode ? (
            <textarea
              value={editedData.body}
              onChange={(e) => setEditedData({ ...editedData, body: e.target.value })}
              style={{
                width: '100%',
                padding: '0.75rem',
                border: '1px solid #2196F3',
                borderRadius: '8px',
                minHeight: '150px',
                fontFamily: 'inherit'
              }}
            />
          ) : (
            <div style={{
              padding: '0.75rem',
              backgroundColor: '#f5f5f5',
              borderRadius: '8px',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word'
            }}>
              {displayData.body}
            </div>
          )}
        </div>

        <div style={{
          display: 'flex',
          gap: '1rem',
          justifyContent: 'flex-end'
        }}>
          <button
            onClick={onCancel}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#f0f0f0',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '1rem'
            }}
          >
            Cancel
          </button>

          {editMode ? (
            <button
              onClick={handleSaveEdit}
              style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: '#FFC107',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '1rem',
                fontWeight: '600'
              }}
            >
              Done Editing
            </button>
          ) : (
            <button
              onClick={handleEdit}
              style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: '#FFC107',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '1rem',
                fontWeight: '600'
              }}
            >
              Edit
            </button>
          )}

          <button
            onClick={handleApproveAndSend}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#4CAF50',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '1rem',
              fontWeight: '600'
            }}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
