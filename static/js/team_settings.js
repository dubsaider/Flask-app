const TeamSettingsPage = {
    teamId: null,
    team: null,
    templates: [],
    permissionLabels: {},

    async init() {
        const root = document.querySelector('.team-settings');
        this.teamId = parseInt(root?.dataset.teamId, 10);
        if (!this.teamId) return;

        if (!(await Auth.requireAuth())) return;

        await Sidebar.init(null, 'team-settings');
        this.bindTabs();

        try {
            const [team, meta] = await Promise.all([
                API.getTeam(this.teamId),
                API.getRoleTemplates()
            ]);
            this.team = team;
            this.templates = meta.templates || [];
            this.permissionLabels = meta.permission_labels || PERMISSION_LABELS;

            const ctx = Auth.getUserContext(team);
            Permissions.setContext(ctx.permissions, ctx.slug, ctx.name);
            Sidebar.updateRole(ctx.slug, ctx.name);

            document.getElementById('team-settings-title').textContent = team.name;
            document.getElementById('team-settings-desc').textContent =
                team.description || Locale.get('team_settings.default_desc');

            if (!Permissions.canManageRoles() && !Permissions.canManageTeamMembers()) {
                this.showAccessDenied();
                return;
            }

            this.populateTemplateSelect();
            this.renderRoles();
            this.renderMembers();
            this.bindActions();
            this.updateTeamSettingsNav();
        } catch (error) {
            console.error(error);
            this.showAccessDenied(Locale.get('team_settings.load_error'));
        }
    },

    showAccessDenied(message) {
        document.querySelectorAll('.team-settings__tabs, .team-settings__panel').forEach(el => {
            el.classList.add('hidden');
        });
        const empty = document.getElementById('team-settings-empty');
        empty?.classList.remove('hidden');
        if (message) {
            empty.querySelector('.page-empty__text').textContent = message;
        }
    },

    updateTeamSettingsNav() {
        const link = document.getElementById('nav-team-settings');
        if (link) {
            link.href = `/team/${this.teamId}/settings`;
            link.classList.remove('hidden');
        }
    },

    bindTabs() {
        document.querySelectorAll('.team-settings__tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.team-settings__tab').forEach(t => t.classList.remove('is-active'));
                document.querySelectorAll('.team-settings__panel').forEach(p => p.classList.add('hidden'));
                tab.classList.add('is-active');
                document.querySelector(`[data-panel="${tab.dataset.tab}"]`)?.classList.remove('hidden');
            });
        });
    },

    populateTemplateSelect() {
        const select = document.getElementById('role-template-select');
        if (!select) return;
        select.replaceChildren();
        this.templates.forEach(template => {
            const option = document.createElement('option');
            option.value = template.key;
            option.textContent = `${template.name} — ${template.description}`;
            select.appendChild(option);
        });
    },

    renderRoles() {
        const container = document.getElementById('roles-list');
        if (!container) return;
        DOM.clear(container);

        (this.team.roles || []).forEach(role => {
            container.appendChild(this.buildRoleCard(role));
        });
    },

    buildRoleCard(role) {
        const card = document.createElement('article');
        card.className = 'role-card';
        card.dataset.roleId = role.id;

        const canEdit = Permissions.canManageRoles();
        const badgeText = role.is_system
            ? Locale.get('team_settings.badge_template')
            : Locale.get('team_settings.badge_custom');
        const templateMeta = role.template_key
            ? `${Locale.get('team_settings.template_basis')}${role.template_key}`
            : '';

        card.innerHTML = `
            <div class="role-card__header">
                <div>
                    <div class="role-card__title">${role.name}</div>
                    <div class="role-card__meta">${role.slug}${templateMeta}</div>
                </div>
                <span class="role-card__badge">${badgeText}</span>
            </div>
            <input type="text" class="form-control role-card__name-input" value="${role.name}" ${canEdit ? '' : 'disabled'}>
            <input type="text" class="form-control role-card__desc-input" value="${role.description || ''}" placeholder="${Locale.get('team_settings.role_desc_placeholder')}" ${canEdit ? '' : 'disabled'}>
            <div class="role-card__permissions"></div>
            <div class="role-card__actions"></div>
        `;

        const permsContainer = card.querySelector('.role-card__permissions');
        Object.entries(this.permissionLabels).forEach(([key, label]) => {
            const labelEl = document.createElement('label');
            labelEl.className = 'role-card__perm filter-check';
            labelEl.innerHTML = `
                <input type="checkbox" data-perm="${key}" ${role.permissions?.[key] ? 'checked' : ''} ${canEdit ? '' : 'disabled'}>
                <span>${label}</span>
            `;
            permsContainer.appendChild(labelEl);
        });

        const actions = card.querySelector('.role-card__actions');
        if (canEdit) {
            const saveBtn = document.createElement('button');
            saveBtn.type = 'button';
            saveBtn.className = 'btn btn-primary btn-sm';
            saveBtn.textContent = Locale.get('common.save');
            saveBtn.addEventListener('click', () => this.saveRole(role.id, card));
            actions.appendChild(saveBtn);

            if (!role.is_system) {
                const deleteBtn = document.createElement('button');
                deleteBtn.type = 'button';
                deleteBtn.className = 'btn btn-danger btn-sm';
                deleteBtn.textContent = Locale.get('common.delete');
                deleteBtn.addEventListener('click', () => this.deleteRole(role.id, role.name));
                actions.appendChild(deleteBtn);
            }
        }

        return card;
    },

    async saveRole(roleId, cardEl) {
        const permissions = {};
        cardEl.querySelectorAll('[data-perm]').forEach(input => {
            permissions[input.dataset.perm] = input.checked;
        });

        try {
            await API.updateTeamRole(this.teamId, roleId, {
                user_id: Auth.getCurrentUser().id,
                name: cardEl.querySelector('.role-card__name-input').value.trim(),
                description: cardEl.querySelector('.role-card__desc-input').value.trim(),
                permissions
            });
            await this.reloadTeam();
            alert(Locale.get('team_settings.role_saved'));
        } catch (error) {
            alert(`${Locale.get('common.error')}: ${error.message}`);
        }
    },

    async deleteRole(roleId, name) {
        if (!confirm(Locale.format('team_settings.delete_role_confirm', { name }))) return;
        try {
            await API.deleteTeamRole(this.teamId, roleId, { user_id: Auth.getCurrentUser().id });
            await this.reloadTeam();
        } catch (error) {
            alert(`${Locale.get('common.error')}: ${error.message}`);
        }
    },

    renderMembers() {
        const list = document.getElementById('members-list');
        const userSelect = document.getElementById('add-member-user');
        const roleSelect = document.getElementById('add-member-role');
        const curatorSelect = document.getElementById('team-curator-select');
        if (!list || !userSelect || !roleSelect || !curatorSelect) return;

        DOM.clear(list);
        userSelect.replaceChildren();
        roleSelect.replaceChildren();
        curatorSelect.replaceChildren();

        const emptyCurator = document.createElement('option');
        emptyCurator.value = '';
        emptyCurator.textContent = Locale.get('common.unassigned');
        curatorSelect.appendChild(emptyCurator);

        Auth.allUsers.forEach(user => {
            const inTeam = this.team.members.some(m => m.id === user.id);
            if (!inTeam) {
                const option = document.createElement('option');
                option.value = user.id;
                option.textContent = user.username;
                userSelect.appendChild(option);
            }

            const curatorOption = document.createElement('option');
            curatorOption.value = user.id;
            curatorOption.textContent = user.username;
            if (this.team.curator_id === user.id) curatorOption.selected = true;
            curatorSelect.appendChild(curatorOption);
        });

        (this.team.roles || []).forEach(role => {
            const option = document.createElement('option');
            option.value = role.id;
            option.textContent = role.name;
            roleSelect.appendChild(option);
        });

        this.team.members.forEach(member => {
            list.appendChild(this.buildMemberCard(member));
        });

        curatorSelect.disabled = !Permissions.canManageTeamMembers();
        document.getElementById('add-member-btn')?.classList.toggle(
            'hidden', !Permissions.canManageTeamMembers()
        );
        document.querySelector('.team-settings__create-row--members')?.classList.toggle(
            'hidden', !Permissions.canManageTeamMembers()
        );
    },

    buildMemberCard(member) {
        const card = document.createElement('article');
        card.className = 'member-card';
        card.innerHTML = `
            <div class="member-card__header">
                <div>
                    <div class="member-card__title">${member.username}</div>
                    <div class="member-card__meta">${member.email || ''}</div>
                </div>
            </div>
            <div class="member-card__actions"></div>
        `;

        const actions = card.querySelector('.member-card__actions');
        if (Permissions.canManageTeamMembers()) {
            const select = document.createElement('select');
            select.className = 'form-control member-card__role-select';
            (this.team.roles || []).forEach(role => {
                const option = document.createElement('option');
                option.value = role.id;
                option.textContent = role.name;
                if (role.id === member.role_id) option.selected = true;
                select.appendChild(option);
            });

            const saveBtn = document.createElement('button');
            saveBtn.type = 'button';
            saveBtn.className = 'btn btn-secondary btn-sm';
            saveBtn.textContent = Locale.get('team_settings.change_role');
            saveBtn.addEventListener('click', async () => {
                try {
                    await API.updateTeamMember(this.teamId, member.id, {
                        user_id: Auth.getCurrentUser().id,
                        role_id: parseInt(select.value, 10)
                    });
                    await this.reloadTeam();
                } catch (error) {
                    alert(`${Locale.get('common.error')}: ${error.message}`);
                }
            });

            const removeBtn = document.createElement('button');
            removeBtn.type = 'button';
            removeBtn.className = 'btn btn-danger btn-sm';
            removeBtn.textContent = Locale.get('common.delete');
            removeBtn.addEventListener('click', async () => {
                if (!confirm(Locale.format('team_settings.remove_member_confirm', { name: member.username }))) return;
                try {
                    await API.removeTeamMember(this.teamId, {
                        user_id: Auth.getCurrentUser().id,
                        member_user_id: member.id
                    });
                    await this.reloadTeam();
                } catch (error) {
                    alert(`${Locale.get('common.error')}: ${error.message}`);
                }
            });

            actions.appendChild(select);
            actions.appendChild(saveBtn);
            actions.appendChild(removeBtn);
        } else {
            actions.textContent = member.role_name || member.role || '';
        }

        return card;
    },

    bindActions() {
        document.getElementById('create-role-btn')?.addEventListener('click', async () => {
            if (!Permissions.canManageRoles()) return;
            const templateKey = document.getElementById('role-template-select')?.value;
            try {
                await API.createTeamRole(this.teamId, {
                    user_id: Auth.getCurrentUser().id,
                    template_key: templateKey
                });
                await this.reloadTeam();
            } catch (error) {
                alert(`${Locale.get('common.error')}: ${error.message}`);
            }
        });

        document.getElementById('add-member-btn')?.addEventListener('click', async () => {
            const userId = parseInt(document.getElementById('add-member-user')?.value, 10);
            const roleId = parseInt(document.getElementById('add-member-role')?.value, 10);
            if (!userId || !roleId) return;
            try {
                await API.addTeamMember(this.teamId, {
                    user_id: Auth.getCurrentUser().id,
                    member_user_id: userId,
                    role_id: roleId
                });
                await this.reloadTeam();
            } catch (error) {
                alert(`${Locale.get('common.error')}: ${error.message}`);
            }
        });

        document.getElementById('team-curator-select')?.addEventListener('change', async (event) => {
            const curatorId = event.target.value ? parseInt(event.target.value, 10) : null;
            try {
                await API.updateTeam(this.teamId, {
                    user_id: Auth.getCurrentUser().id,
                    name: this.team.name,
                    description: this.team.description,
                    curator_id: curatorId
                });
                await this.reloadTeam();
            } catch (error) {
                alert(`${Locale.get('common.error')}: ${error.message}`);
            }
        });
    },

    async reloadTeam() {
        this.team = await API.getTeam(this.teamId);
        this.renderRoles();
        this.renderMembers();
    }
};

document.addEventListener('DOMContentLoaded', () => TeamSettingsPage.init());
