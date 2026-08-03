let allTools = [];
        let allRoles = [];

        // Tab Switching
        function switchTab(tabId) {
            document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            
            document.getElementById('tab-' + tabId).classList.add('active');
            event.currentTarget.classList.add('active');

            if(tabId === 'providers') loadProviders();
            if(tabId === 'roles') loadRoles();
        }

        // Modals
        function closeModals() {
            document.querySelectorAll('.modal-overlay').forEach(el => {
                el.classList.remove('show');
                setTimeout(() => el.style.display = 'none', 300);
            });
        }

        async function openProviderModal() {
            document.getElementById('provider-name').value = '';
            
            // Populate roles dropdown
            const select = document.getElementById('provider-role');
            select.innerHTML = allRoles.map(r => `<option value="${r.name}">${r.name}</option>`).join('');
            
            const modal = document.getElementById('provider-modal');
            modal.style.display = 'flex';
            requestAnimationFrame(() => modal.classList.add('show'));
        }

        async function openRoleModal(roleName = '') {
            document.getElementById('role-name').value = roleName;
            document.getElementById('role-name').disabled = !!roleName; // Disable editing name if updating
            
            let checkedTools = [];
            if(roleName) {
                const role = allRoles.find(r => r.name === roleName);
                if(role) checkedTools = role.tools;
            }

            const grid = document.getElementById('role-tools-grid');
            grid.innerHTML = allTools.map(t => `
                <label class="checkbox-item" title="${t.name}">
                    <input type="checkbox" value="${t.name}" ${checkedTools.includes(t.name) ? 'checked' : ''}>
                    <span class="checkbox-text">${t.name}</span>
                </label>
            `).join('');

            const modal = document.getElementById('role-modal');
            modal.style.display = 'flex';
            requestAnimationFrame(() => modal.classList.add('show'));
        }

        // Data Fetching
        async function fetchAPI(url, options = {}) {
            try {
                const res = await fetch(url, options);
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'API Error');
                return data;
            } catch (err) {
                alert("Error: " + err.message);
                throw err;
            }
        }

        async function init() {
            allTools = await fetchAPI('/api/tools');
            loadRoles();
            loadProviders();
        }

        async function loadRoles() {
            allRoles = await fetchAPI('/api/roles');
            const tbody = document.getElementById('roles-tbody');
            tbody.innerHTML = allRoles.map(r => `
                <tr>
                    <td><strong>${r.name}</strong></td>
                    <td>${r.tools.length} tools allowed</td>
                    <td>
                        <div style="display: flex; gap: 8px; flex-wrap: nowrap; align-items: center;">
                            <button class="btn-icon" onclick="openRoleModal('${r.name}')" title="Edit Role">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>
                            </button>
                            ${r.name !== 'internal' ? `
                            <button class="btn-icon danger" onclick="deleteRole('${r.name}')" title="Delete Role">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
                            </button>` : ''}
                        </div>
                    </td>
                </tr>
            `).join('');
        }

        async function loadProviders() {
            const providers = await fetchAPI('/api/providers');
            const tbody = document.getElementById('providers-tbody');
            tbody.innerHTML = providers.map(p => `
                <tr>
                    <td><strong>${p.name}</strong><br><small style="color:var(--text-muted)">${p.id}</small></td>
                    <td><span class="badge badge-blue">${p.role}</span></td>
                    <td><span class="badge ${p.active ? 'badge-success' : 'badge-danger'}">${p.active ? 'Active' : 'Inactive'}</span></td>
                    <td>${new Date(p.created_at).toLocaleDateString()}</td>
                    <td>
                        <div style="display: flex; gap: 8px; flex-wrap: nowrap; align-items: center;">
                            <button class="btn-icon" onclick="toggleProvider('${p.id}', ${!p.active})" title="${p.active ? 'Deactivate' : 'Activate'}">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18.36 6.64a9 9 0 1 1-12.73 0"></path><line x1="12" y1="2" x2="12" y2="12"></line></svg>
                            </button>
                            <button class="btn-icon" onclick="regenerateKey('${p.id}')" title="Regenerate Key">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>
                            </button>
                            <button class="btn-icon danger" onclick="deleteProvider('${p.id}')" title="Delete Provider">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');
        }

        // Actions
        async function submitRole() {
            const name = document.getElementById('role-name').value.trim();
            const checked = Array.from(document.querySelectorAll('#role-tools-grid input:checked')).map(cb => cb.value);
            
            if(!name || checked.length === 0) return alert("Enter name and select at least 1 tool.");

            const isUpdate = document.getElementById('role-name').disabled;
            await fetchAPI(`/api/roles${isUpdate ? '/'+name : ''}`, {
                method: isUpdate ? 'PUT' : 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ name, tools: checked })
            });
            
            closeModals();
            loadRoles();
        }

        async function deleteRole(name) {
            if(!confirm(`Delete role ${name}?`)) return;
            await fetchAPI(`/api/roles/${name}`, { method: 'DELETE' });
            loadRoles();
        }

        async function submitProvider() {
            const name = document.getElementById('provider-name').value.trim();
            const role = document.getElementById('provider-role').value;
            
            if(!name || !role) return alert("Fill all fields.");

            const res = await fetchAPI('/api/providers', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ name, role })
            });
            
            closeModals();
            loadProviders();
            
            // Show one-time key
            document.getElementById('generated-key').innerText = res.api_key;
            const modal = document.getElementById('key-modal');
            modal.style.display = 'flex';
            requestAnimationFrame(() => modal.classList.add('show'));
        }

        async function toggleProvider(id, active) {
            await fetchAPI(`/api/providers/${id}`, {
                method: 'PATCH',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ active })
            });
            loadProviders();
        }

        async function deleteProvider(id) {
            if(!confirm(`Permanently delete provider ${id}?`)) return;
            await fetchAPI(`/api/providers/${id}`, { method: 'DELETE' });
            loadProviders();
        }

        async function regenerateKey(id) {
            if(!confirm(`Regenerate key for ${id}? The old key will immediately stop working.`)) return;
            const res = await fetchAPI(`/api/providers/${id}/regenerate`, { method: 'POST' });
            
            document.getElementById('generated-key').innerText = res.api_key;
            const modal = document.getElementById('key-modal');
            modal.style.display = 'flex';
            requestAnimationFrame(() => modal.classList.add('show'));
        }

        // Boot
        init();

        // Search Functionality
        document.getElementById('provider-search').addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            const rows = document.querySelectorAll('#providers-tbody tr');
            rows.forEach(row => {
                const text = row.innerText.toLowerCase();
                row.style.display = text.includes(term) ? '' : 'none';
            });
        });

        document.getElementById('role-search').addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            const rows = document.querySelectorAll('#roles-tbody tr');
            rows.forEach(row => {
                const text = row.innerText.toLowerCase();
                row.style.display = text.includes(term) ? '' : 'none';
            });
        });

        document.getElementById('tool-search').addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            const items = document.querySelectorAll('#role-tools-grid .checkbox-item');
            items.forEach(item => {
                const text = item.innerText.toLowerCase();
                item.style.display = text.includes(term) ? 'flex' : 'none';
            });
        });