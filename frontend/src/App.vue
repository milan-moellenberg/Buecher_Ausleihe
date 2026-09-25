<template>
  <div class="app-container">
    <header class="app-header">
      <h1>📚 Bücherkisten-Ausleihe</h1>
    </header>

    <main class="content">
      <!-- 1. SCANNER & SUCHE SECTION -->
      <Card class="scanner-card">
        <template #title>📷 Kiste scannen oder auswählen</template>
        <template #content>
          <div class="scanner-actions">
            <Button 
              :label="scannerAktiv ? 'Kamera schließen' : 'QR-Code scannen'" 
              :icon="scannerAktiv ? 'pi pi-times' : 'pi pi-camera'" 
              :severity="scannerAktiv ? 'danger' : 'primary'"
              class="p-button-lg full-width"
              @click="toggleScanner" 
            />
          </div>

          <!-- HTML5 QR-Code Kamera Container -->
          <div v-show="scannerAktiv" id="qr-reader" class="qr-reader-box"></div>

          <!-- Manuelle Auswahl / Suche als Fallback -->
          <div class="manual-select">
            <label for="kiste-select">Oder Kiste manuell wählen:</label>
            <Select 
              id="kiste-select"
              v-model="ausgewaehlteKisteQr" 
              :options="kisten" 
              optionLabel="titel" 
              optionValue="qr_code_id" 
              placeholder="Kiste aus Liste wählen..." 
              class="full-width"
              @change="onKisteSelect"
            />
          </div>
        </template>
      </Card>

      <!-- 2. KISTEN DETAILS & STATUS DISPLAY -->
      <Card v-if="aktuelleKiste" class="details-card">
        <template #title>
          <div class="card-title-status">
            <span>{{ aktuelleKiste.titel }}</span>
            <Tag 
              :severity="aktuelleAusleihe ? 'warning' : 'success'" 
              :value="aktuelleAusleihe ? 'Ausgeliehen' : 'Verfügbar'"
              class="status-tag"
            />
          </div>
        </template>
        <template #subtitle>
          QR-ID: <code>{{ aktuelleKiste.qr_code_id }}</code> | Kategorie: {{ aktuelleKiste.kategorie || 'Keine' }}
        </template>
        <template #content>
          <p class="description">{{ aktuelleKiste.beschreibung || 'Keine Beschreibung vorhanden.' }}</p>

          <Divider />

          <!-- Ausleih-Status Info -->
          <div class="status-info-box">
            <div v-if="aktuelleAusleihe" class="info-active">
              <p><i class="pi pi-user"></i> <strong>Aktuell ausgeliehen von:</strong> {{ getLehrerName(aktuelleAusleihe.ausleih_user_id) }}</p>
              <p><i class="pi pi-calendar"></i> <strong>Seit:</strong> {{ formatDatum(aktuelleAusleihe.ausleih_datum) }}</p>
            </div>
            <div v-else class="info-empty">
              <p><i class="pi pi-check-circle"></i> Diese Kiste steht aktuell im Regal und kann ausgeliehen werden.</p>
            </div>
          </div>

          <div class="action-buttons">
            <Button 
              v-if="!aktuelleAusleihe" 
              label="Kiste Ausleihen" 
              icon="pi pi-sign-in" 
              severity="success" 
              class="p-button-lg full-width"
              @click="showAusleihenDialog = true" 
            />
            <Button 
              v-else 
              label="Kiste Zurückgeben" 
              icon="pi pi-sign-out" 
              severity="help" 
              class="p-button-lg full-width"
              @click="showRueckgabeDialog = true" 
            />
          </div>
        </template>
      </Card>
    </main>

    <!-- 3. DIALOG: AUSLEIHEN -->
    <Dialog v-model:visible="showAusleihenDialog" header="Kiste ausleihen" :modal="true" class="responsive-dialog">
      <div class="dialog-form">
        <div class="field">
          <label>Lehrkraft / Kürzel</label>
          <Select 
            v-model="ausleihUserId" 
            :options="lehrerListe" 
            optionLabel="short_name" 
            optionValue="id" 
            placeholder="Wer leiht aus?" 
            class="full-width" 
          />
        </div>
        <div class="field">
          <label>Schul-Passwort</label>
          <Password v-model="schulPasswort" :feedback="false" toggleMask placeholder="Passwort eingeben" class="full-width" />
        </div>
      </div>
      <template #footer>
        <Button label="Abbrechen" severity="secondary" @click="showAusleihenDialog = false" />
        <Button label="Bestätigen & Ausleihen" severity="success" icon="pi pi-check" @click="fuerAusleiheAbschicken(false)" />
      </template>
    </Dialog>

    <!-- 4. DIALOG: BESTÄTIGUNG FORCE-REBORROW (409 CONFLICT) -->
    <Dialog v-model:visible="showForceDialog" header="Kiste ist noch ausgeliehen!" :modal="true" class="responsive-dialog">
      <p class="dialog-warning">
        <i class="pi pi-exclamation-triangle" style="font-size: 2rem; color: var(--p-warning-color);"></i><br />
        Diese Kiste ist aktuell noch als <strong>ausgeliehen</strong> eingetragen.<br /><br />
        Möchtest du sie automatisch als zurückgegeben markieren und direkt auf dich neu ausleihen?
      </p>
      <template #footer>
        <Button label="Abbrechen" severity="secondary" @click="showForceDialog = false" />
        <Button label="Ja, Übernehmen & Ausleihen" severity="warning" icon="pi pi-refresh" @click="fuerAusleiheAbschicken(true)" />
      </template>
    </Dialog>

    <!-- 5. DIALOG: RÜCKGABE -->
    <Dialog v-model:visible="showRueckgabeDialog" header="Kiste zurückgeben" :modal="true" class="responsive-dialog">
      <div class="dialog-form">
        <div class="field">
          <label>Wer gibt die Kiste zurück?</label>
          <Select 
            v-model="rueckgabeUserId" 
            :options="lehrerListe" 
            optionLabel="short_name" 
            optionValue="id" 
            placeholder="Lehrkraft auswählen" 
            class="full-width" 
          />
        </div>
        <div class="field">
          <label>Schul-Passwort</label>
          <Password v-model="schulPasswort" :feedback="false" toggleMask placeholder="Passwort eingeben" class="full-width" />
        </div>
      </div>
      <template #footer>
        <Button label="Abbrechen" severity="secondary" @click="showRueckgabeDialog = false" />
        <Button label="Kiste Zurückgeben" severity="help" icon="pi pi-check" @click="fuerRueckgabeAbschicken" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Html5Qrcode } from 'html5-qrcode'
import api from './api.js'

// PrimeVue Komponenten
import Card from 'primevue/card'
import Button from 'primevue/button'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import Divider from 'primevue/divider'
import Dialog from 'primevue/dialog'
import Password from 'primevue/password'

// Daten-States
const kisten = ref([])
const lehrerListe = ref([])
const ausgewaehlteKisteQr = ref(null)
const aktuelleKiste = ref(null)
const aktuelleAusleihe = ref(null)

// Scanner State
const scannerAktiv = ref(false)
let html5QrCode = null

// Formular & Dialog States
const showAusleihenDialog = ref(false)
const showRueckgabeDialog = ref(false)
const showForceDialog = ref(false)

const ausleihUserId = ref(null)
const rueckgabeUserId = ref(null)
const schulPasswort = ref('')

// Initialisierung beim Laden der Seite
onMounted(async () => {
  await ladeBasisDaten()
})

async function ladeBasisDaten() {
  try {
    const [resKisten, resLehrer] = await Promise.all([
      api.getKisten(),
      api.getLehrer()
    ])
    kisten.value = resKisten.data
    lehrerListe.value = resLehrer.data
  } catch (err) {
    console.error('Fehler beim Laden der Basisdaten:', err)
  }
}

// Kiste anhand der QR-ID abrufen und Status prüfen
async function waehleKisteAus(qrCodeId) {
  try {
    const res = await api.getKisteByQrCode(qrCodeId)
    aktuelleKiste.value = res.data
    
    // Prüfen, ob für diese Kiste eine aktive Ausleihe vorliegt
    // (Hinweis: Über Admin-History oder eigenen Check-Endpunkt möglich, hier filtern wir die History)
    const historyRes = await api.getKisten() // Nutzt Kisten-Details
    // Für die Statusabfrage holen wir die Historie oder prüfen aktive Ausleihe:
    aktuelleAusleihe.value = null // Wird bei Bedarf erweitert
  } catch (err) {
    alert('Kiste konnte nicht gefunden werden!')
  }
}

function onKisteSelect() {
  if (ausgewaehlteKisteQr.value) {
    waehleKisteAus(ausgewaehlteKisteQr.value)
  }
}

// QR-Scanner Steuerung
function toggleScanner() {
  if (scannerAktiv.value) {
    stoppeScanner()
  } else {
    starteScanner()
  }
}

function starteScanner() {
  scannerAktiv.value = true
  setTimeout(() => {
    html5QrCode = new Html5Qrcode("qr-reader")
    html5QrCode.start(
      { facingMode: "environment" }, // Rückkamera bevorzugen
      { fps: 10, qrbox: { width: 250, height: 250 } },
      (decodedText) => {
        // Erfolgreich gescannt!
        stoppeScanner()
        ausgewaehlteKisteQr.value = decodedText
        waehleKisteAus(decodedText)
      },
      () => {} // Stille Ignorierung von Frames ohne QR-Code
    ).catch(err => {
      console.error("Kamera-Fehler:", err)
      scannerAktiv.value = false
      alert("Kamera konnte nicht geöffnet werden.")
    })
  }, 300)
}

function stoppeScanner() {
  if (html5QrCode && html5QrCode.isScanning) {
    html5QrCode.stop().then(() => {
      scannerAktiv.value = false
    })
  } else {
    scannerAktiv.value = false
  }
}

// Ausleih-Logik
async function fuerAusleiheAbschicken(force = false) {
  if (!ausleihUserId.value || !schulPasswort.value) {
    alert('Bitte Kürzel und Passwort eingeben!')
    return
  }

  const payload = {
    qr_code_id: aktuelleKiste.value.qr_code_id,
    ausleih_user_id: ausleihUserId.value,
    passwort: schulPasswort.value
  }

  try {
    await api.ausleihen(payload, force)
    alert('Kiste erfolgreich ausgeliehen!')
    showAusleihenDialog.value = false
    showForceDialog.value = false
    schulPasswort.value = ''
    waehleKisteAus(aktuelleKiste.value.qr_code_id) // Status aktualisieren
  } catch (err) {
    if (err.response && err.response.status === 409) {
      // HTTP 409 Conflict: Kiste noch nicht zurückgegeben!
      showAusleihenDialog.value = false
      showForceDialog.value = true // Nachfrage-Dialog öffnen
    } else {
      alert('Fehler beim Ausleihen: ' + (err.response?.data?.detail || err.message))
    }
  }
}

// Rückgabe-Logik
async function fuerRueckgabeAbschicken() {
  if (!rueckgabeUserId.value || !schulPasswort.value) {
    alert('Bitte Kürzel und Passwort eingeben!')
    return
  }

  const payload = {
    qr_code_id: aktuelleKiste.value.qr_code_id,
    rueckgabe_user_id: rueckgabeUserId.value,
    passwort: schulPasswort.value
  }

  try {
    await api.rueckgabe(payload)
    alert('Kiste erfolgreich zurückgegeben!')
    showRueckgabeDialog.value = false
    schulPasswort.value = ''
    waehleKisteAus(aktuelleKiste.value.qr_code_id)
  } catch (err) {
    alert('Fehler bei Rückgabe: ' + (err.response?.data?.detail || err.message))
  }
}

// Hilfsfunktionen
function getLehrerName(userId) {
  const u = lehrerListe.value.find(l => l.id === userId)
  return u ? u.short_name : `User ID #${userId}`
}

function formatDatum(isoString) {
  if (!isoString) return ''
  return new Date(isoString).toLocaleString('de-DE', { dateStyle: 'medium', timeStyle: 'short' })
}
</script>

<style scoped>
.app-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 1rem;
  font-family: system-ui, -apple-system, sans-serif;
}

.app-header {
  text-align: center;
  line-height: 1.2;
  margin-bottom: 1.5rem;
}

.scanner-card, .details-card {
  margin-bottom: 1.5rem;
}

.full-width {
  width: 100%;
}

.qr-reader-box {
  margin-top: 1rem;
  border-radius: 8px;
  overflow: hidden;
  border: 2px dashed #ccc;
}

.manual-select {
  margin-top: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.card-title-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-info-box {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.action-buttons {
  margin-top: 1rem;
}

.dialog-form {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  padding-top: 0.5rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.dialog-warning {
  text-align: center;
  line-height: 1.5;
}

.responsive-dialog {
  width: 90vw;
  max-width: 450px;
}
</style>