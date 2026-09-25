import { createApp } from 'vue'
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import 'primeicons/primeicons.css' // Icons (z.B. für QR-Code, Schloss, Benutzer)

import './style.css'
import App from './App.vue'

const app = createApp(App)

// PrimeVue mit dem modernen "Aura"-Theme konfigurieren
app.use(PrimeVue, {
    theme: {
        preset: Aura,
        options: {
            darkModeSelector: 'system' // oder 'none' für helles Design
        }
    }
});

app.mount('#app')