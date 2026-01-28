# 📧 SETUP DE EMAIL - PASSO A PASSO

## ⚠️ Importante: Use GMAIL (não funciona com Outlook, Yahoo, etc)

---

## 🔑 PASSO 1: Gerar Senha de App no Gmail

### 1.1 Acesse sua Conta Google
```
https://myaccount.google.com
```

### 1.2 Ative 2FA (se ainda não tiver)
1. Clique: **Segurança** (lado esquerdo)
2. Role até: **Verificação em duas etapas**
3. Clique: **Ativar**
4. Siga as instruções

### 1.3 Gere Senha de App
1. Acesse: https://myaccount.google.com/apppasswords
2. Você vai ver uma caixa de seleção
3. Selecione:
   - **App:** Mail
   - **Device:** Windows PC (ou qualquer um)
4. Clique: **Gerar**
5. **Copie a senha de 16 caracteres** que aparecer

Exemplo:
```
abcd efgh ijkl mnop
```

---

## ☁️ PASSO 2: Adicionar no Streamlit Cloud

### 2.1 Vá para o Dashboard
https://share.streamlit.io/

### 2.2 Clique no Menu (⋮)
No canto superior direito da sua app

### 2.3 Vá em: Settings

### 2.4 Clique em: Secrets

### 2.5 Copie e Cole Isso:

```
SENDER_EMAIL = "seu_email@gmail.com"
SENDER_PASSWORD = "abcd efgh ijkl mnop"
```

**Substitua:**
- `seu_email@gmail.com` → seu email Gmail (ex: matheus@gmail.com)
- `abcd efgh ijkl mnop` → a senha que você copiou (com ou sem espaços)

### 2.6 Clique: **Save**

A app vai reiniciar automaticamente ✅

---

## ✅ PRONTO!

Agora o app pode enviar emails!

---

## 🧪 Testando

1. Abra seu app: `https://seu-usuario-app-orcamentos.streamlit.app`
2. Selecione um consultor
3. Tire uma foto
4. Clique "Gerar Orçamento"
5. Clique "Enviar por Email"
6. Verifique o email recebido

Se deu erro, verifique:
- [ ] Email está correto
- [ ] Senha de app foi copiada correta (sem erros)
- [ ] Está em SENDER_EMAIL e SENDER_PASSWORD
- [ ] 2FA está ativado no Gmail

---

## ❌ Se Não Funcionar

### Erro: "Login unsuccessful"
- A senha de app está errada
- Copie novamente em: https://myaccount.google.com/apppasswords

### Erro: "SMTP connection failed"
- 2FA pode não estar ativado
- Verifique em: https://myaccount.google.com/security

### Email não chega
- Verifique pasta de SPAM
- Tente enviar para outro email primeiro

---

## 📝 Exemplo Completo

Seu arquivo Secrets no Streamlit Cloud fica assim:

```
SENDER_EMAIL = "matheus@gmail.com"
SENDER_PASSWORD = "ycsp wtei rfxk iohm"
```

(Não compartilhe essa senha com ninguém!)

---

## 🎯 Resumo

| Passo | O Quê |
|-------|-------|
| 1 | Ativar 2FA no Gmail |
| 2 | Gerar senha de app |
| 3 | Copiar a senha |
| 4 | Ir em Streamlit Cloud → Secrets |
| 5 | Colar SENDER_EMAIL e SENDER_PASSWORD |
| 6 | Clique Save |
| 7 | ✅ Pronto! |

---

**Dúvida? Releia este arquivo!** 📖
