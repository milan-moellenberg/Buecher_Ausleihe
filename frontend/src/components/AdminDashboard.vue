<template>
  <div class="admin-container">
    <!-- 1. PASSWORT-ABFRAGE (Wenn noch nicht authentifiziert) -->
    <Card v-if="!isLoggedIn" class="login-card">
      <template #title>🔒 Admin Login</template>
      <template #content>
        <div class="dialog-form">
          <div class="field">
            <label>Admin-Passwort eingeben:</label>
            <InputPassword 
              v-model="adminPasswordInput" 
              :feedback="false" 
              toggleMask 
              placeholder="Passwort" 
              class="full-width" 
              @keyup.enter="login"
            />
          </div>
          <Button label="Anmelden" icon="pi pi-lock-open" severity="primary" class="full-width" @click="login" />
        </div>
      </template>
    </Card>

    <!-- 2. HAUPT-DASHBOARD (Nach erfolgreichem Login) -->
    <div v-else class="dashboard-content">
      <div class="dashboard-header">
        <h2>🛠️ Admin Dashboard</h2>
        <Button label="Abmelden" icon="pi pi-sign-out" severity="secondary" text @click="logout" />
      </div>

      <!-- PrimeVue v4 Tabs Struktur -->
      <Tabs value="0">
        <!-- Tab-Header Navigation -->
        <TabList>
          <Tab value="0">📦 Kisten</Tab>
          <Tab value="1">👥 Lehrkräfte / User</Tab>
          <Tab value="2">📋 Alle Ausleihen</Tab>
        </TabList>

        <!-- Tab Inhalte -->
        <TabPanels>
          <!-- REITER 1: KISTEN & AUSLEIHHISTORIE -->
          <TabPanel value="0">
            <div class="action-bar">
              <Button 
                label="Alle QR-Codes neu generieren" 
                icon="pi pi-refresh" 
                severity="help" 
                outlined 
                @click="regenerateAllQRCodes" 
              />
              <Button label="Neue Kiste anlegen" 
              icon="pi pi-plus" 
              severity="success" 
              @click="showNewKisteDialog = true" />
            </div>

            <DataTable 
              :value="kistenWithStatus" 
              v-model:expandedRows="expandedRows" 
              dataKey="id" 
              responsiveLayout="scroll"
            >
              <Column expander style="width: 3rem" />
              <Column field="qr_code_id" header="QR-ID" />
              <Column field="titel" header="Titel" />
              <Column field="kategorie" header="Kategorie" />
              <Column header="QR-Code Image">
                <template #body="slotProps">
                  <a :href="api.getQrCodeUrl(slotProps.data.id)" target="_blank">
                    <img 
                      :src="api.getQrCodeUrl(slotProps.data.id)" 
                      alt="QR Code" 
                      style="width: 40px; height: 40px; object-fit: contain;" 
                      @error="handleImageError"
                    />
                  </a>
                </template>
              </Column>
              <Column header="Status">
                <template #body="slotProps">
                  <Tag 
                    :severity="slotProps.data.isAusgeliehen ? 'warn' : 'success'" 
                    :value="slotProps.data.isAusgeliehen ? 'Ausgeliehen' : 'Verfügbar'" 
                  />
                </template>
              </Column>

              <!-- AKTIONEN SPALTE (KISTE BEARBEITEN) -->
              <Column header="Aktionen" style="width: 5rem">
                <template #body="slotProps">
                  <Button 
                    icon="pi pi-pencil" 
                    severity="info" 
                    size="small" 
                    text 
                    @click="openEditKiste(slotProps.data)" 
                  />
                </template>
              </Column>

              <!-- Ausklappbare Ausleihhistorie der Kiste -->
              <template #rowexpansion="slotProps">
                <div class="expansion-box">
                  <h4>📜 Ausleihhistorie für "{{ slotProps.data.titel }}"</h4>
                  <DataTable :value="getKistenHistorie(slotProps.data.id)" size="small">
                    <Column header="Ausleiher">
                      <template #body="s">{{ getLehrerName(s.data.ausleih_user_id) }}</template>
                    </Column>
                    <Column header="Ausleihdatum">
                      <template #body="s">{{ formatDatum(s.data.ausleih_datum) }}</template>
                    </Column>
                    <Column header="Status">
                      <template #body="s">
                        <Tag :severity="s.data.status === 'ausgeliehen' ? 'warn' : 'secondary'" :value="s.data.status" />
                      </template>
                    </Column>
                    <Column header="Rückgabedatum">
                      <template #body="s">{{ formatDatum(s.data.rueckgabe_datum) }}</template>
                    </Column>
                    <Column header="Rückgeber">
                      <template #body="s">{{ getLehrerName(s.data.rueckgabe_user_id) }}</template>
                    </Column>
                  </DataTable>
                </div>
              </template>
            </DataTable>
          </TabPanel>

          <!-- REITER 2: USER / LEHRKRÄFTE -->
          <TabPanel value="1">
            <div class="action-bar">
              <Button label="Neuen User anlegen" icon="pi pi-user-plus" severity="success" @click="openNewUser" />
            </div>

            <DataTable :value="users" responsiveLayout="scroll">
              <Column field="id" header="ID" />
              <Column field="short_name" header="Kürzel / Name" />
              <Column header="Rolle">
                <template #body="slotProps">
                  <Tag 
                    :severity="slotProps.data.rolle === 'Ehemalig' ? 'secondary' : 'primary'" 
                    :value="slotProps.data.rolle" 
                  />
                </template>
              </Column>

              <!-- AKTIONEN SPALTE (USER BEARBEITEN) -->
              <Column header="Aktionen" style="width: 5rem">
                <template #body="slotProps">
                  <Button 
                    icon="pi pi-pencil" 
                    severity="info" 
                    size="small" 
                    text 
                    @click="openEditUser(slotProps.data)" 
                  />
                </template>
              </Column>
            </DataTable>
          </TabPanel>

          <!-- REITER 3: GESAMTE AUSLEIHHISTORIE -->
          <TabPanel value="2">
            <DataTable :value="ausleihen" responsiveLayout="scroll" :paginator="true" :rows="10">
              <Column field="id" header="ID" />
              <Column header="Kiste">
                <template #body="s">{{ getKistenTitel(s.data.kiste_id) }}</template>
              </Column>
              <Column header="Ausleiher">
                <template #body="s">{{ getLehrerName(s.data.ausleih_user_id) }}</template>
              </Column>
              <Column header="Ausleihdatum">
                <template #body="s">{{ formatDatum(s.data.ausleih_datum) }}</template>
              </Column>
              <Column header="Status">
                <template #body="s">
                  <Tag :severity="s.data.status === 'ausgeliehen' ? 'warn' : 'secondary'" :value="s.data.status" />
                </template>
              </Column>
              <Column header="Rückgabedatum">
                <template #body="s">{{ formatDatum(s.data.rueckgabe_datum) }}</template>
              </Column>
            </DataTable>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </div>

    <!-- DIALOG: NEUE KISTE ANLEGEN -->
    <Dialog v-model:visible="showNewKisteDialog" header="Neue Kiste anlegen" :modal="true" class="responsive-dialog">
      <div class="dialog-form">
        <div class="field">
          <label>Titel / Buchtitel</label>
          <InputText v-model="newKiste.titel" placeholder="z. B. Die Welle (Klassensatz)" />
        </div>
        <div class="field">
          <label>Kategorie</label>
          <InputText v-model="newKiste.kategorie" placeholder="z. B. Deutsch 8. Klasse" />
        </div>
        <div class="field">
          <label>Beschreibung</label>
          <Textarea v-model="newKiste.beschreibung" rows="3" placeholder="Optionale Anmerkungen..." />
        </div>
      </div>
      <template #footer>
        <Button label="Abbrechen" severity="secondary" @click="showNewKisteDialog = false" />
        <Button label="Kiste Erstellen" icon="pi pi-check" severity="success" @click="createKiste" />
      </template>
    </Dialog>

    <!-- DIALOG: KISTE BEARBEITEN -->
    <Dialog v-model:visible="showEditKisteDialog" header="Kiste bearbeiten" :modal="true" class="responsive-dialog">
      <div class="dialog-form">
        <div class="field">
          <label>QR-Code-ID</label>
          <InputText v-model="editKisteData.qr_code_id" placeholder="QR-Code ID" />
          <small class="help-text">⚠️ Bei Änderung wird automatisch ein neues QR-Code-Bild generiert.</small>
        </div>
        <div class="field">
          <label>Titel / Buchtitel</label>
          <InputText v-model="editKisteData.titel" placeholder="z. B. Die Welle (Klassensatz)" />
        </div>
        <div class="field">
          <label>Kategorie</label>
          <InputText v-model="editKisteData.kategorie" placeholder="z. B. Deutsch 8. Klasse" />
        </div>
        <div class="field">
          <label>Beschreibung</label>
          <Textarea v-model="editKisteData.beschreibung" rows="3" placeholder="Optionale Anmerkungen..." />
        </div>
      </div>
      <template #footer>
        <Button label="Abbrechen" severity="secondary" @click="showEditKisteDialog = false" />
        <Button label="Speichern" icon="pi pi-check" severity="success" @click="saveKisteEdit" />
      </template>
    </Dialog>

    <!-- DIALOG: USER ANLEGEN / BEARBEITEN -->
    <Dialog 
      v-model:visible="showUserDialog" 
      :header="isEditingUser ? 'User bearbeiten' : 'Neuen User anlegen'" 
      :modal="true" 
      class="responsive-dialog"
    >
      <div class="dialog-form">
        <div class="field">
          <label>Kürzel / Name</label>
          <InputText v-model="userFormData.short_name" placeholder="z. B. MUE (Müller)" />
        </div>
        <div class="field">
          <label>Rolle</label>
          <Select 
            v-model="userFormData.rolle" 
            :options="rollenOptionen" 
            placeholder="Rolle wählen" 
            class="full-width" 
          />
        </div>
      </div>
      <template #footer>
        <Button label="Abbrechen" severity="secondary" @click="showUserDialog = false" />
        <Button label="Speichern" icon="pi pi-check" severity="success" @click="saveUser" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '../api.js'

import Card from 'primevue/card'
import Button from 'primevue/button'
import InputPassword from 'primevue/password'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Select from 'primevue/select'
import Tabs from 'primevue/tabs'
import TabList from 'primevue/tablist'
import Tab from 'primevue/tab'
import TabPanels from 'primevue/tabpanels'
import TabPanel from 'primevue/tabpanel'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import Dialog from 'primevue/dialog'

// States
const isLoggedIn = ref(false)
const adminPasswordInput = ref('')
const activeAdminPassword = ref('')

const kisten = ref([])
const users = ref([])
const ausleihen = ref([])
const expandedRows = ref([])

// Rollen-Optionen für User
const rollenOptionen = ref(['Lehrkraft', 'Ehemalig'])

// Dialog States für Kisten
const showNewKisteDialog = ref(false)
const newKiste = ref({ qr_code_id: '', titel: '', kategorie: '', beschreibung: '' })

const showEditKisteDialog = ref(false)
const editKisteData = ref({ id: null, qr_code_id: '', titel: '', kategorie: '', beschreibung: '' })

// Combined Dialog State für User (Anlegen & Bearbeiten)
const showUserDialog = ref(false)
const isEditingUser = ref(false)
const userFormData = ref({ id: null, short_name: '', rolle: 'Lehrkraft' })

// listener
const emit = defineEmits(['data-updated'])

async function login() {
  if (!adminPasswordInput.value) return
  try {
    const res = await api.getHistory(adminPasswordInput.value)
    ausleihen.value = res.data
    activeAdminPassword.value = adminPasswordInput.value
    isLoggedIn.value = true
    adminPasswordInput.value = ''
    
    await refreshData()
  } catch (err) {
    alert('Falsches Admin-Passwort oder Authentifizierungsfehler!')
  }
}

function logout() {
  isLoggedIn.value = false
  activeAdminPassword.value = ''
}

async function refreshData() {
  try {
    const [resK, resU, resA] = await Promise.all([
      api.getKisten(),
      api.getLehrer(),
      api.getHistory(activeAdminPassword.value)
    ])
    kisten.value = resK.data
    users.value = resU.data
    ausleihen.value = resA.data
  } catch (err) {
    console.error('Fehler beim Aktualisieren der Admin-Daten:', err)
  }
}

// Errechnet für jede Kiste, ob sie aktuell ausgeliehen ist
const kistenWithStatus = computed(() => {
  return kisten.value.map(k => {
    const activeLoan = ausleihen.value.find(a => a.kiste_id === k.id && a.status === 'ausgeliehen')
    return {
      ...k,
      isAusgeliehen: !!activeLoan
    }
  })
})

function getKistenHistorie(kisteId) {
  return ausleihen.value.filter(a => a.kiste_id === kisteId)
}

// --- KISTEN HANDLER ---
async function createKiste() {
  if (!newKiste.value.titel) {
    alert('Bitte einen Titel angeben!')
    return
  }
  try {
    await api.createKiste(newKiste.value, activeAdminPassword.value)
    alert('Kiste erfolgreich erstellt, QR-Code wurde generiert!')
    showNewKisteDialog.value = false
    newKiste.value = { titel: '', kategorie: '', beschreibung: '' }
    await refreshData()

    emit('data-updated')
  } catch (err) {
    alert('Fehler beim Erstellen der Kiste: ' + (err.response?.data?.detail || err.message))
  }
}

function openEditKiste(kiste) {
  editKisteData.value = { 
    id: kiste.id, 
    qr_code_id: kiste.qr_code_id, 
    titel: kiste.titel, 
    kategorie: kiste.kategorie || '', 
    beschreibung: kiste.beschreibung || '' 
  }
  showEditKisteDialog.value = true
}

async function saveKisteEdit() {
  try {
    await api.updateKiste(editKisteData.value.id, editKisteData.value, activeAdminPassword.value)
    alert('Kiste wurde erfolgreich aktualisiert!')
    showEditKisteDialog.value = false
    await refreshData()

    emit('data-updated')
  } catch (err) {
    alert('Fehler beim Aktualisieren der Kiste: ' + (err.response?.data?.detail || err.message))
  }
}

async function regenerateAllQRCodes() {
  if (!confirm('Möchtest du wirklich alle QR-Code-Bilder für sämtliche Kisten im Ordner neu generieren?')) {
    return
  }

  try {
    const res = await api.regenerateQRCodes(activeAdminPassword.value)
    alert(res.data.message || 'QR-Codes wurden erfolgreich neu generiert!')
    await refreshData()
  } catch (err) {
    alert('Fehler beim Generieren der QR-Codes: ' + (err.response?.data?.detail || err.message))
  }
}


// --- USER HANDLER ---
function openNewUser() {
  isEditingUser.value = false
  userFormData.value = { id: null, short_name: '', rolle: 'Lehrkraft' }
  showUserDialog.value = true
}

function openEditUser(user) {
  isEditingUser.value = true
  userFormData.value = { id: user.id, short_name: user.short_name, rolle: user.rolle || 'Lehrkraft' }
  showUserDialog.value = true
}

async function saveUser() {
  if (!userFormData.value.short_name) {
    alert('Bitte ein Kürzel angeben!')
    return
  }
  try {
    if (isEditingUser.value) {
      await api.updateUser(userFormData.value.id, userFormData.value, activeAdminPassword.value)
      alert('User erfolgreich aktualisiert!')
    } else {
      await api.createLehrer(userFormData.value, activeAdminPassword.value)
      alert('User erfolgreich angelegt!')
    }
    showUserDialog.value = false
    await refreshData()

    emit('data-updated')
  } catch (err) {
    alert('Fehler beim Speichern des Users: ' + (err.response?.data?.detail || err.message))
  }
}

// Hilfsfunktionen
function getLehrerName(userId) {
  if (!userId) return '-'
  const u = users.value.find(x => x.id === userId)
  return u ? u.short_name : `ID #${userId}`
}

function getKistenTitel(kisteId) {
  const k = kisten.value.find(x => x.id === kisteId)
  return k ? k.titel : `Kiste #${kisteId}`
}

function formatDatum(iso) {
  if (!iso) return '-'
  return new Date(iso).toLocaleString('de-DE', { dateStyle: 'medium', timeStyle: 'short' })
}


function handleImageError(event) {
  // Verhindert Endlosschleifen und setzt ein Platzhalter-Bild oder versteckt das kaputte Bild
  event.target.onerror = null;
  event.target.src = 'https://via.placeholder.com/40?text=QR+Error';
}


</script>

<style scoped>
.admin-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 1rem;
}

.login-card {
  max-width: 400px;
  margin: 2rem auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.action-bar {
  margin-bottom: 1rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.expansion-box {
  padding: 1rem;
  background-color: var(--p-surface-50, #f8f9fa);
  border-radius: 6px;
}

.dialog-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-top: 0.5rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.help-text {
  color: var(--p-surface-500, #6c757d);
  font-size: 0.8rem;
}

.full-width {
  width: 100%;
}

.responsive-dialog {
  width: 90vw;
  max-width: 500px;
}
</style>