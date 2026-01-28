# ❌ ERRO DE EMAIL - Soluções

## 🔍 Diagnóstico

Você está recebendo erro ao tentar enviar email? Siga este guia.

---

## ⚠️ Erro Comum: "Login unsuccessful"

### Causa 1: Senha Copiada Errada

**Solução:**
1. Acesse: https://myaccount.google.com/apppasswords
2. Gere **NOVAMENTE** uma senha de app
3. **Copie com cuidado** (16 caracteres)
4. **Cole exatamente** no Streamlit Cloud (com espaços, se tiver)
5. Clique: **Save**

---

## ⚠️ Erro: "2-Step Verification not enabled"

### Causa: 2FA Desativado

**Solução:**
1. Abra: https://myaccount.google.com/security
2. Procure: **2-Step Verification**
3. Clique: **Enable**
4. Siga as instruções
5. Depois volte e gere a senha de app

---

## ⚠️ Erro: "SMTP connection refused"

### Causa: Internet ou Firewall

**Solução:**
1. Verifique se está com internet
2. Tente desativar VPN (se tiver)
3. Espere 1 minuto e tente novamente

---

## ✅ Checklist de Verificação

Execute isto:

### 1️⃣ Email Está Correto?
```
SENDER_EMAIL = "seu_email@gmail.com"
                ↑
         VERIFIQUE ISTO
```

Certifique-se:
- [ ] Sem espaços extras
- [ ] Com @gmail.com (não @googlemail.com)
- [ ] Digitado corretamente

### 2️⃣ Senha de App Está Certa?
```
SENDER_PASSWORD = "abcd efgh ijkl mnop"
                   ↑
           VERIFIQUE ISTO
```

Certifique-se:
- [ ] 16 caracteres (com espaços)
- [ ] Copiada de: https://myaccount.google.com/apppasswords
- [ ] Sem erros de digitação

### 3️⃣ 2FA Está Ativado?
```
https://myaccount.google.com/security
→ 2-Step Verification: ON
```

Certifique-se:
- [ ] Status: "On"
- [ ] Não: "Off" ou "Not set up"

### 4️⃣ Streamlit Cloud Secrets
```
Dashboard → Settings → Secrets
```

Certifique-se:
- [ ] SENDER_EMAIL está lá
- [ ] SENDER_PASSWORD está lá
- [ ] Sem typos nos nomes
- [ ] Clicou Save

---

## 🔧 Regenerar Senha (Recomendado)

Se tiver dúvida, **gere uma nova senha**:

1. https://myaccount.google.com/apppasswords
2. Selecione: **Mail** e **Windows PC**
3. Clique: **Gerar**
4. **Copie** a nova senha
5. Vá para Streamlit Cloud
6. Substitua SENDER_PASSWORD pela nova
7. Clique: **Save**

---

## 📝 Exemplo Correto

```
SENDER_EMAIL = "matheus@gmail.com"
SENDER_PASSWORD = "ycsp wtei rfxk iohm"
```

**Sem aspas extras, sem erros, exatamente assim.**

---

## 🧪 Testando

Após salvar no Streamlit:

1. Espere 30 segundos (app reinicia)
2. Acesse seu app
3. Selecione um consultor
4. Tire uma foto
5. Gere PDF
6. Clique "Enviar por Email"
7. Verifique se chegou

Se ainda der erro:

### Opção 1: Verificar Spam
- Abra Gmail
- Procure em "Spam"
- Se encontrar, marque como "Not spam"

### Opção 2: Testar com Outro Email
- Peça para alguém fazer login em outro email
- Tente enviar para lá
- Verifique se funciona

### Opção 3: Reiniciar Tudo
1. Gere **nova** senha de app
2. Atualize no Streamlit Cloud
3. Aguarde app reiniciar
4. Teste novamente

---

## 🆘 Se Nada Funcionar

Verifique estas coisas:

```
☐ Email está correto (matheus@gmail.com)
☐ Senha tem 16 caracteres
☐ 2FA está ativado (Security → 2-Step Verification: On)
☐ Gerou a senha em: apppasswords
☐ Copiou SEM espaços extras
☐ Streamlit Cloud recebeu a senha
☐ Clicou Save no Streamlit
☐ App reiniciou (espere 30s)
☐ Tentou de novo
```

Se tudo está certo e ainda der erro:

**Contate suporte do Gmail ou tente com outro email.**

---

## ✅ Se Funcionar!

Se conseguir enviar um email:
1. ✅ Email está OK
2. ✅ Credenciais estão OK
3. ✅ Tudo pronto para usar!

**Parabéns!** 🎉

---

**Dúvidas? Releia EMAIL_SETUP.md**
