const express = require('express');
const { makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys');
const qrcode = require('qrcode-terminal');
const path = require('path');
const fs = require('fs');

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
            let fileBuffer = null;
            if (fs.existsSync(media_url)) {
                fileBuffer = fs.readFileSync(media_url);
            }

            let isImage = false;
            let mimetype = 'application/pdf';
            let fileName = 'Anexo_Pendencia.pdf';

            if (fileBuffer && fileBuffer.length > 4) {
                const headerHex = fileBuffer.slice(0, 4).toString('hex');
                const headerStr = fileBuffer.slice(0, 4).toString('ascii');

                if (headerStr === '%PDF') {
                    isImage = false;
                    mimetype = 'application/pdf';
                    fileName = 'Documento_Pendencia.pdf';
                } else if (headerHex.startsWith('ffd8') || headerHex === '89504e47' || headerStr.startsWith('RIFF')) {
                    isImage = true;
                    mimetype = headerHex.startsWith('ffd8') ? 'image/jpeg' : 'image/png';
                }
            } else {
                const urlLower = media_url.toLowerCase();
                isImage = (urlLower.includes('.png') || urlLower.includes('.jpg') || urlLower.includes('.jpeg') || urlLower.includes('.webp')) && !urlLower.includes('.pdf');
            }

            const mediaSource = fileBuffer ? fileBuffer : { url: media_url };

            if (isImage) {
                // Fotos e Imagens aceitam mensagem como legenda na mesma mensagem
                await sock.sendMessage(jid, {
                    image: mediaSource,
                    caption: message
                });
                console.log(`📸 Imagem enviada com legenda para ${cleanNumber}`);
            } else {
                // PDFs e Documentos: Envia o texto primeiro e o documento em seguida
                await sock.sendMessage(jid, { text: message });
                await sock.sendMessage(jid, {
                    document: mediaSource,
                    mimetype: mimetype,
                    fileName: fileName
                });
                console.log(`📄 Texto e Documento PDF entregues com sucesso para ${cleanNumber}`);
            }
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
