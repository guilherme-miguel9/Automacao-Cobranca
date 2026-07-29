const express = require('express');
const { makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys');
const qrcode = require('qrcode-terminal');
const path = require('path');

const app = express();
app.use(express.json());

const PORT = 8000;
let sock = null;
let isConnected = false;

async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState(path.join(__dirname, 'auth_info_baileys'));

    sock = makeWASocket({
        auth: state,
        printQRInTerminal: false
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            console.log('\n==================================================');
            console.log('📱 ESCANEIE O QR CODE ABAIXO NO SEU WHATSAPP:');
            console.log('==================================================\n');
            qrcode.generate(qr, { small: true });
        }

        if (connection === 'close') {
            const shouldReconnect = (lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut);
            console.log('❌ Conexão fechada. Reconectando:', shouldReconnect);
            isConnected = false;
            if (shouldReconnect) {
                connectToWhatsApp();
            }
        } else if (connection === 'open') {
            console.log('\n==================================================');
            console.log('✅ WHATSAPP CONECTADO COM SUCESSO!');
            console.log(`🚀 Gateway API ativo na porta http://localhost:${PORT}`);
            console.log('==================================================\n');
            isConnected = true;
        }
    });
}

// Endpoint de Envio de Mensagem (Compatível com o Robô Python)
app.post('/api/v1/send-message', async (req, res) => {
    if (!isConnected || !sock) {
        return res.status(503).json({ error: 'WhatsApp não está conectado. Escaneie o QR Code no terminal.' });
    }

    try {
        const { number, message, media_url } = req.body;

        if (!number || !message) {
            return res.status(400).json({ error: 'Parâmetros "number" e "message" são obrigatórios.' });
        }

        // Formatar número para o padrão Baileys (ex: 55859999887766@s.whatsapp.net)
        const cleanNumber = number.replace(/\D/g, '');
        const jid = `${cleanNumber}@s.whatsapp.net`;

        if (media_url) {
            // Envio de mídia/imagem/anexo
            await sock.sendMessage(jid, {
                image: { url: media_url },
                caption: message
            });
            console.log(`📸 Imagem e Mensagem enviadas com sucesso para ${cleanNumber}`);
        } else {
            // Envio apenas de texto
            await sock.sendMessage(jid, { text: message });
            console.log(`💬 Mensagem enviada com sucesso para ${cleanNumber}`);
        }

        return res.status(200).json({ status: 'success', message: 'Mensagem enviada com sucesso!' });

    } catch (error) {
        console.error('Erro ao enviar mensagem via WhatsApp:', error);
        return res.status(500).json({ error: error.message || 'Erro interno no gateway de WhatsApp' });
    }
});

// Endpoint de Health Check
app.get('/health', (req, res) => {
    res.json({ connected: isConnected, status: isConnected ? 'online' : 'offline' });
});

// Iniciar servidor HTTP e Conexão WhatsApp
app.listen(PORT, () => {
    console.log(`Gateway de WhatsApp iniciando na porta ${PORT}...`);
    connectToWhatsApp();
});
