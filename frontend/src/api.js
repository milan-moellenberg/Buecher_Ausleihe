import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'  //zum testen lokal ttp://localhost:8000, auf server später /api, da der reverse proxy die anfragen weiterleitet
// Axios Instanz erstellen
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export default {
  // --- QR-Code URL Helper ---
  getQrCodeUrl(kisteId) {
    return `${API_BASE_URL}/kisten/${kisteId}/qrcode`
  },

  // --- Kisten ---
  getKisten() {
    return api.get('/kisten')
  },
  getKisteByQrCode(qrCodeId) {
    return api.get(`/kisten/${qrCodeId}`)
  },
  createKiste(kisteData, adminPassword) {
    return api.post(`/admin/kisten?password=${encodeURIComponent(adminPassword)}`, kisteData)
  },
  updateKiste(kisteId, data, password) {
    return api.put(`/admin/kisten/${kisteId}?password=${encodeURIComponent(password)}`, data)
  },
  regenerateQRCodes(password) {
    return api.post(`/admin/kisten/regenerate-qrcodes?password=${encodeURIComponent(password)}`)
  },

  // --- Lehrkräfte ---
  getLehrer() {
    return api.get('/lehrer')
  },
  createLehrer(userData, adminPassword) {
    return api.post(`/lehrer?password=${encodeURIComponent(adminPassword)}`, userData)
  },
  updateUser(userId, data, password) {
    return api.put(`/admin/users/${userId}?password=${encodeURIComponent(password)}`, data)
  },

  // --- Ausleihe und Rückgabe ---
  ausleihen(payload, forceReborrow = false) {
    return api.post(`/ausleihe?force_reborrow=${forceReborrow}`, payload)
  },
  rueckgabe(payload) {
    return api.post('/rueckgabe', payload)
  },

  // --- Admin ---
  getHistory(adminPassword) {
    return api.get(`/admin/ausleihe?admin_password=${encodeURIComponent(adminPassword)}`)
  }
}