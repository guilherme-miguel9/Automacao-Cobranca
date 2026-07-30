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

const os = require('os');

const sessionPath = path.join(os.homedir(), '.cobobrabot', 'auth_info_baileys');
if (!fs.existsSync(sessionPath)) {
    fs.mkdirSync(sessionPath, { recursive: true });
}

async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState(sessionPath);

    sock = makeWASocket({
        auth: state,
        printQRInTerminal: false,
        syncFullHistory: false, // Prevents Request Time-out on init queries
        markOnlineOnConnect: false, // Reduces initial connection overhead
        connectTimeoutMs: 60000, // 60s timeout instead of 20s
        defaultQueryTimeoutMs: 60000,
        keepAliveIntervalMs: 10000,
        generateHighQualityLinkPreview: false
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
            } else {
                console.log('🔄 Sessão inválida ou deslogada. Apagando credenciais antigas para gerar novo QR Code...');
                try {
                    fs.rmSync(sessionPath, { recursive: true, force: true });
                } catch(e) {
                    console.log('Erro ao apagar sessão:', e);
                }
                setTimeout(connectToWhatsApp, 2000);
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

const mime = require('mime-types');

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

        let jid = '';
        if (number.includes('chat.whatsapp.com/')) {
            // É um link de convite para grupo
            const codeParts = number.split('chat.whatsapp.com/');
            const code = codeParts[1].split('/')[0].split('?')[0];
            try {
                jid = await sock.groupAcceptInvite(code);
                console.log(`✅ Entrou no grupo via link: ${jid}`);
            } catch (err) {
                console.error('❌ Falha ao entrar no grupo via link:', err);
                return res.status(400).json({ error: 'Falha ao entrar no grupo via link de convite. Verifique se o link é válido e não foi revogado.' });
            }
        } else if (number.includes('@g.us')) {
            // É um ID de grupo direto
            jid = number;
        } else {
            // Formatar número para o padrão Baileys de usuário individual (ex: 55859999887766@s.whatsapp.net)
            const cleanNumber = number.replace(/\D/g, '');
            jid = `${cleanNumber}@s.whatsapp.net`;
        }

        if (media_url) {
            let fileBuffer = null;
            if (fs.existsSync(media_url)) {
                fileBuffer = fs.readFileSync(media_url);
            }

            let isImage = false;
            let mimetype = 'application/octet-stream';
            let fileName = path.basename(media_url) || 'Documento_Anexo';

            // Detect mimetype from extension
            const extMime = mime.lookup(media_url);
            if (extMime) {
                mimetype = extMime;
                isImage = mimetype.startsWith('image/');
            } else {
                // Secrecy fallback by header (for raw files without extension)
                if (fileBuffer && fileBuffer.length > 4) {
                    const headerHex = fileBuffer.slice(0, 4).toString('hex');
                    const headerStr = fileBuffer.slice(0, 4).toString('ascii');

                    if (headerStr === '%PDF') {
                        isImage = false;
                        mimetype = 'application/pdf';
                        fileName = fileName.includes('.') ? fileName : fileName + '.pdf';
                    } else if (headerHex.startsWith('ffd8')) {
                        isImage = true;
                        mimetype = 'image/jpeg';
                        fileName = fileName.includes('.') ? fileName : fileName + '.jpg';
                    } else if (headerHex === '89504e47') {
                        isImage = true;
                        mimetype = 'image/png';
                        fileName = fileName.includes('.') ? fileName : fileName + '.png';
                    }
                }
            }

            const mediaSource = fileBuffer ? fileBuffer : { url: media_url };

            if (isImage && !mimetype.includes('pdf')) {
                // Fotos e Imagens aceitam mensagem como legenda na mesma mensagem
                await sock.sendMessage(jid, {
                    image: mediaSource,
                    caption: message
                });
                console.log(`📸 Imagem enviada com legenda para ${jid}`);
            } else {
                // PDFs, Excel, Documentos genéricos: Envia em uma única bolha com legenda!
                await sock.sendMessage(jid, {
                    document: mediaSource,
                    mimetype: mimetype,
                    fileName: fileName,
                    caption: message // Legenda junto ao documento
                });
                console.log(`📄 Documento (${fileName}) enviado com legenda para ${jid}`);
            }
        } else {
            // Envio apenas de texto
            await sock.sendMessage(jid, { text: message });
            console.log(`💬 Mensagem enviada com sucesso para ${jid}`);
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
