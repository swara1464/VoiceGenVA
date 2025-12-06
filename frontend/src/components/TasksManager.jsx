import { useState, useEffect } from 'react';
import axios from '../axios';

export default function TasksManager({ isOpen, onClose }) {
  const [taskLists, setTaskLists] = useState([]);
  const [selectedListId, setSelectedListId] = useState('@default');
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newTask, setNewTask] = useState({
    title: '',
    notes: '',
    due_date: ''
  });

  useEffect(() => {
    if (isOpen) {
      loadTaskLists();
      loadTasks(selectedListId);
    }
  }, [isOpen, selectedListId]);

  const loadTaskLists = async () => {
    try {
      const res = await axios.post('/agent/execute', {
        action: 'TASKS_LIST_ALL',
        params: {}
      });
      if (res.data.success && res.data.details) {
        setTaskLists(res.data.details);
      }
    } catch (err) {
      console.error('Failed to load task lists:', err);
    }
  };

  const loadTasks = async (tasklistId) => {
    setLoading(true);
    try {
      const res = await axios.post('/agent/execute', {
        action: 'TASKS_LIST',
        params: { tasklist_id: tasklistId, max_results: 50 }
      });
      if (res.data.success && res.data.details) {
        setTasks(res.data.details);
      }
    } catch (err) {
      console.error('Failed to load tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async () => {
    if (!newTask.title.trim()) {
      alert('Task title is required');
      return;
    }

    try {
      const params = {
        title: newTask.title,
        notes: newTask.notes,
        tasklist_id: selectedListId
      };

      // Add due date if provided
      if (newTask.due_date) {
        params.due_date = new Date(newTask.due_date).toISOString();
      }

      const res = await axios.post('/agent/execute', {
        action: 'TASKS_CREATE',
        params
      });

      if (res.data.success) {
        setNewTask({ title: '', notes: '', due_date: '' });
        setShowCreateForm(false);
        loadTasks(selectedListId);
      } else {
        alert(res.data.message || 'Failed to create task');
      }
    } catch (err) {
      alert('Error creating task');
      console.error(err);
    }
  };

  const handleCompleteTask = async (taskId) => {
    try {
      const res = await axios.post('/agent/execute', {
        action: 'TASKS_COMPLETE',
        params: { task_id: taskId, tasklist_id: selectedListId }
      });

      if (res.data.success) {
        loadTasks(selectedListId);
      } else {
        alert(res.data.message || 'Failed to complete task');
      }
    } catch (err) {
      alert('Error completing task');
      console.error(err);
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (!confirm('Are you sure you want to delete this task?')) return;

    try {
      const res = await axios.post('/agent/execute', {
        action: 'TASKS_DELETE',
        params: { task_id: taskId, tasklist_id: selectedListId }
      });

      if (res.data.success) {
        loadTasks(selectedListId);
      } else {
        alert(res.data.message || 'Failed to delete task');
      }
    } catch (err) {
      alert('Error deleting task');
      console.error(err);
    }
  };

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
        padding: '2rem',
        borderRadius: '16px',
        maxWidth: '900px',
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
            <span style={{ fontSize: '1.8rem' }}>✓</span>
            Tasks Manager
          </h3>
          <button
            onClick={onClose}
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

        {/* Task List Selector */}
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{
            display: 'block',
            marginBottom: '0.5rem',
            fontWeight: '600',
            fontSize: '0.9rem',
            color: '#555'
          }}>
            Select Task List:
          </label>
          <select
            value={selectedListId}
            onChange={(e) => setSelectedListId(e.target.value)}
            style={{
              width: '100%',
              padding: '0.7rem',
              fontSize: '1rem',
              border: '2px solid #e0e0e0',
              borderRadius: '8px',
              outline: 'none',
              cursor: 'pointer'
            }}
          >
            <option value="@default">My Tasks (Default)</option>
            {taskLists.map(list => (
              <option key={list.id} value={list.id}>{list.title}</option>
            ))}
          </select>
        </div>

        {/* Create Task Button */}
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          style={{
            padding: '0.7rem 1.5rem',
            backgroundColor: '#2e7d32',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontWeight: '600',
            fontSize: '0.95rem',
            marginBottom: '1rem',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => e.target.style.backgroundColor = '#1b5e20'}
          onMouseLeave={(e) => e.target.style.backgroundColor = '#2e7d32'}
        >
          {showCreateForm ? '- Cancel' : '+ New Task'}
        </button>

        {/* Create Task Form */}
        {showCreateForm && (
          <div style={{
            backgroundColor: '#f8f9fa',
            padding: '1.5rem',
            borderRadius: '12px',
            marginBottom: '1.5rem',
            border: '1px solid #e0e0e0'
          }}>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{
                display: 'block',
                marginBottom: '0.3rem',
                fontWeight: '600',
                fontSize: '0.9rem',
                color: '#555'
              }}>
                Task Title:
              </label>
              <input
                type="text"
                value={newTask.title}
                onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                placeholder="Enter task title"
                style={{
                  width: '100%',
                  padding: '0.7rem',
                  fontSize: '1rem',
                  border: '2px solid #e0e0e0',
                  borderRadius: '8px',
                  outline: 'none'
                }}
              />
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{
                display: 'block',
                marginBottom: '0.3rem',
                fontWeight: '600',
                fontSize: '0.9rem',
                color: '#555'
              }}>
                Notes (Optional):
              </label>
              <textarea
                value={newTask.notes}
                onChange={(e) => setNewTask({ ...newTask, notes: e.target.value })}
                placeholder="Add notes..."
                rows={3}
                style={{
                  width: '100%',
                  padding: '0.7rem',
                  fontSize: '1rem',
                  border: '2px solid #e0e0e0',
                  borderRadius: '8px',
                  outline: 'none',
                  resize: 'vertical',
                  fontFamily: 'inherit'
                }}
              />
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{
                display: 'block',
                marginBottom: '0.3rem',
                fontWeight: '600',
                fontSize: '0.9rem',
                color: '#555'
              }}>
                Due Date (Optional):
              </label>
              <input
                type="datetime-local"
                value={newTask.due_date}
                onChange={(e) => setNewTask({ ...newTask, due_date: e.target.value })}
                style={{
                  width: '100%',
                  padding: '0.7rem',
                  fontSize: '1rem',
                  border: '2px solid #e0e0e0',
                  borderRadius: '8px',
                  outline: 'none'
                }}
              />
            </div>
            <button
              onClick={handleCreateTask}
              style={{
                padding: '0.7rem 1.5rem',
                backgroundColor: '#1976d2',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: '600',
                fontSize: '0.95rem',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => e.target.style.backgroundColor = '#1565c0'}
              onMouseLeave={(e) => e.target.style.backgroundColor = '#1976d2'}
            >
              Create Task
            </button>
          </div>
        )}

        {/* Tasks List */}
        <div>
          <h4 style={{ marginBottom: '1rem', color: '#333' }}>Tasks:</h4>
          {loading ? (
            <p style={{ textAlign: 'center', color: '#666' }}>Loading tasks...</p>
          ) : tasks.length === 0 ? (
            <p style={{ textAlign: 'center', color: '#666', padding: '2rem' }}>
              No tasks in this list. Create one to get started!
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {tasks.map(task => (
                <div
                  key={task.id}
                  style={{
                    backgroundColor: task.status === 'completed' ? '#e8f5e9' : '#fff',
                    padding: '1rem',
                    borderRadius: '8px',
                    border: '1px solid',
                    borderColor: task.status === 'completed' ? '#c8e6c9' : '#e0e0e0',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    transition: 'all 0.2s'
                  }}
                >
                  <div style={{ flex: 1 }}>
                    <div style={{
                      fontWeight: '600',
                      fontSize: '1rem',
                      color: task.status === 'completed' ? '#2e7d32' : '#1a1a1a',
                      textDecoration: task.status === 'completed' ? 'line-through' : 'none',
                      marginBottom: '0.3rem'
                    }}>
                      {task.status === 'completed' ? '✅ ' : '⏳ '}
                      {task.title}
                    </div>
                    {task.notes && (
                      <div style={{
                        fontSize: '0.85rem',
                        color: '#666',
                        marginBottom: '0.3rem'
                      }}>
                        {task.notes}
                      </div>
                    )}
                    {task.due && task.due !== 'No due date' && (
                      <div style={{
                        fontSize: '0.8rem',
                        color: '#f57c00',
                        fontWeight: '500'
                      }}>
                        Due: {new Date(task.due).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem', marginLeft: '1rem' }}>
                    {task.status !== 'completed' && (
                      <button
                        onClick={() => handleCompleteTask(task.id)}
                        title="Mark as complete"
                        style={{
                          padding: '0.5rem 1rem',
                          backgroundColor: '#2e7d32',
                          color: 'white',
                          border: 'none',
                          borderRadius: '6px',
                          cursor: 'pointer',
                          fontSize: '0.85rem',
                          fontWeight: '600',
                          transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => e.target.style.backgroundColor = '#1b5e20'}
                        onMouseLeave={(e) => e.target.style.backgroundColor = '#2e7d32'}
                      >
                        ✓ Done
                      </button>
                    )}
                    <button
                      onClick={() => handleDeleteTask(task.id)}
                      title="Delete task"
                      style={{
                        padding: '0.5rem 1rem',
                        backgroundColor: '#d32f2f',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontSize: '0.85rem',
                        fontWeight: '600',
                        transition: 'all 0.2s'
                      }}
                      onMouseEnter={(e) => e.target.style.backgroundColor = '#b71c1c'}
                      onMouseLeave={(e) => e.target.style.backgroundColor = '#d32f2f'}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Close Button */}
        <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
          <button
            onClick={onClose}
            style={{
              padding: '0.7rem 2rem',
              backgroundColor: '#666',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: '600',
              fontSize: '0.95rem',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => e.target.style.backgroundColor = '#555'}
            onMouseLeave={(e) => e.target.style.backgroundColor = '#666'}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
