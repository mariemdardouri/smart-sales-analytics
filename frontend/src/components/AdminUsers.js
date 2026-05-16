import React, { useEffect, useState } from "react";
import "./AdminUsers.css";

function AdminUsers() {
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editingUser, setEditingUser] = useState(null);

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem("token");
      const res = await fetch("http://localhost:8000/admin/users", {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      const data = await res.json();
      setUsers(data);
    } catch (error) {
      console.error("Erreur chargement utilisateurs:", error);
    }
  };

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem("token");
      const res = await fetch("http://localhost:8000/admin/stats", {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      const data = await res.json();
      setStats(data);
    } catch (error) {
      console.error("Erreur chargement stats:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
    fetchStats();
  }, []);

  const toggleUser = async (id) => {
    try {
      const token = localStorage.getItem("token");
      await fetch(`http://localhost:8000/admin/users/toggle/${id}`, {
        method: "PUT",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      fetchUsers();
    } catch (error) {
      console.error("Erreur toggle utilisateur:", error);
    }
  };

  const openEditModal = (user) => {
    setEditingUser({ ...user });
  };

  const closeEditModal = () => {
    setEditingUser(null);
  };

  const saveEditUser = async () => {
    if (!editingUser) return;

    try {
      const token = localStorage.getItem("token");
      await fetch(`http://localhost:8000/admin/users/${editingUser.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          username: editingUser.username,
          email: editingUser.email,
          role: editingUser.role,
          is_active: editingUser.is_active
        })
      });
      closeEditModal();
      fetchUsers();
    } catch (error) {
      console.error("Erreur modification:", error);
    }
  };

  if (loading) {
    return (
      <div className="admin-loading">
        <div className="loading-spinner"></div>
        <p>Chargement des données...</p>
      </div>
    );
  }

  return (
    <div className="admin-users-container">
      <div className="admin-header">
        <div>
          <h1>Gestion des utilisateurs</h1>
          <p className="admin-subtitle">Gérez les comptes et permissions de votre équipe</p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M12 12C14.2091 12 16 10.2091 16 8C16 5.79086 14.2091 4 12 4C9.79086 4 8 5.79086 8 8C8 10.2091 9.79086 12 12 12Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
              <path d="M5 20V19C5 15.6863 7.68629 13 11 13H13C16.3137 13 19 15.6863 19 19V20" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
          </div>
          <div className="stat-content">
            <span className="stat-label">Total utilisateurs</span>
            <span className="stat-value">{stats?.total_users || 0}</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="8" r="4" stroke="currentColor" strokeWidth="1.5"/>
              <path d="M5 20V19C5 16.2386 7.23858 14 10 14H14C16.7614 14 19 16.2386 19 19V20" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
              <circle cx="12" cy="8" r="4" stroke="currentColor" strokeWidth="1.5"/>
            </svg>
          </div>
          <div className="stat-content">
            <span className="stat-label">Connectés</span>
            <span className="stat-value">{stats?.logged_users || 0}</span>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="table-container">
        <table className="users-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Utilisateur</th>
              <th>Email</th>
              <th>Rôle</th>
              <th>Statut</th>
              <th>Créé le</th>
              <th>Dernière connexion</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                <td className="user-id">#{user.id}</td>
                <td className="user-name">{user.username}</td>
                <td className="user-email">{user.email}</td>
                <td>
                  <span className={`role-badge ${user.role === 'admin' ? 'role-admin' : 'role-user'}`}>
                    {user.role === 'admin' ? 'Administrateur' : 'Utilisateur'}
                  </span>
                </td>
                <td>
                  <span className={`status-badge ${user.is_active ? 'status-active' : 'status-inactive'}`}>
                    {user.is_active ? 'Actif' : 'Inactif'}
                  </span>
                </td>
                <td>{new Date(user.created_at).toLocaleDateString()}</td>
                <td>{user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Jamais'}</td>
                <td className="actions-cell">
                  <button 
                    className="action-btn edit-btn"
                    onClick={() => openEditModal(user)}
                    title="Modifier"
                  >
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                      <path d="M11.3333 1.99999L14 4.66666L4.66667 14H2V11.3333L11.3333 1.99999Z" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </button>
                  <button 
                    className={`action-btn ${user.is_active ? 'disable-btn' : 'enable-btn'}`}
                    onClick={() => toggleUser(user.id)}
                    title={user.is_active ? "Désactiver" : "Activer"}
                  >
                    {user.is_active ? (
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="1.2"/>
                        <line x1="4.5" y1="8" x2="11.5" y2="8" stroke="currentColor" strokeWidth="1.2"/>
                      </svg>
                    ) : (
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="1.2"/>
                        <line x1="5.5" y1="8" x2="10.5" y2="8" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
                      </svg>
                    )}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Edit Modal */}
      {editingUser && (
        <div className="modal-overlay" onClick={closeEditModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Modifier l'utilisateur</h3>
              <button className="modal-close" onClick={closeEditModal}>×</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Nom d'utilisateur</label>
                <input
                  type="text"
                  value={editingUser.username}
                  onChange={(e) => setEditingUser({...editingUser, username: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={editingUser.email}
                  onChange={(e) => setEditingUser({...editingUser, email: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label>Rôle</label>
                <select
                  value={editingUser.role}
                  onChange={(e) => setEditingUser({...editingUser, role: e.target.value})}
                >
                  <option value="user">Utilisateur</option>
                  <option value="admin">Administrateur</option>
                </select>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-cancel" onClick={closeEditModal}>Annuler</button>
              <button className="btn-save" onClick={saveEditUser}>Enregistrer</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminUsers;