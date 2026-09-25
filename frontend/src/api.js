import axios from 'axios'

// use FastAPI-base url to create axios instance
const api = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

export default{
    //  --- Kisten ---
    getKisten(){
        return api.get('/kisten');
    },
    getKisteByQrCode(qrCodeId){
        return api.get(`/kisten/${qrCodeId}`)
    },

    //  --- Lehrkräfte ---
    getLehrer() {
        return api.get('/lehrer');
    },

    //  --- Ausleihe und Rückgabe ---
    ausleihen(payload, forceReborrow = false){
        return api.post(`/ausleihe?force_reborrow=${forceReborrow}`, payload);
    },
    rueckgabe(payload){
        return api.post('/rueckgabe', payload);
    },

    //  --- Admin ---
    getHistory(adminPassword){
        return api.get(`/admin/ausleihe?admin_passwort=${adminPassword}`)
    }
}