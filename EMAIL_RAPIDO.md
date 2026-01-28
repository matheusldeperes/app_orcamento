# 🚀 TESTE RÁPIDO: Email Funcionando?

## ✅ Passo 1: Verifique a Senha

Abra: https://myaccount.google.com/apppasswords

**Você vê a tela de "Select app and device"?**

- ✅ **SIM** → Vá para Passo 2
- ❌ **NÃO** → Seu 2FA não está ativado (volte a EMAIL_SETUP.md)

---

## ✅ Passo 2: Gere Uma Senha

1. Selecione: **Mail**
2. Selecione: **Windows PC** (ou qualquer um)
3. Clique: **Gerar**

**Apareceu uma senha de 16 caracteres?**

- ✅ **SIM** → Vá para Passo 3
- ❌ **NÃO** → Erro no Gmail (tente novamente)

---

## ✅ Passo 3: Copie Corretamente

A senha aparecer assim:
```
abcd efgh ijkl mnop
```

**Com ou sem espaços, copie exatamente como aparece:**

1. Selecione tudo (Cmd+A)
2. Copie (Cmd+C)
3. Não mude nada!

---

## ✅ Passo 4: Adicione ao Streamlit Cloud

1. Vá para: https://share.streamlit.io/
2. Encontre seu app
3. Clique em **⋮** (três pontinhos)
4. Clique em **Settings**
5. Clique em **Secrets**

**Você vê um campo de texto?**

- ✅ **SIM** → Vá para Passo 5
- ❌ **NÃO** → Erro no Streamlit (tente refresh)

---

## ✅ Passo 5: Cole as Credenciais

**Cole isto:**
```
SENDER_EMAIL = "seu_email@gmail.com"
SENDER_PASSWORD = "abcd efgh ijkl mnop"
```

**Substituindo:**
- `seu_email@gmail.com` → seu email do Gmail
- `abcd efgh ijkl mnop` → a senha copiada

---

## ✅ Passo 6: Salve

1. Clique: **Save**
2. Aguarde 30 segundos
3. Veja a mensagem: "Secrets updated"

**A app reiniciou?**

- ✅ **SIM** → Vá para Passo 7
- ⏳ **AGUARDANDO** → Espere mais

---

## ✅ Passo 7: Teste

1. Acesse: https://seu-usuario-app-orcamentos.streamlit.app
2. Selecione um consultor
3. Tire uma foto
4. Clique "Gerar Orçamento"
5. Clique "Enviar por Email"

**Recebeu o email?**

- ✅ **SIM** → 🎉 **PRONTO! Funciona!**
- ❌ **NÃO** → Vá para TROUBLESHOOT
- ⚠️ **ERRO** → Vá para TROUBLESHOOT

---

## ❌ Se Deu Erro

### Erro: "Login unsuccessful"
→ Senha copiada errada  
→ Gere novamente  
→ Copie com MAIS cuidado  

### Erro: "SMTP connection refused"
→ Problema de internet  
→ Tente desativar VPN  
→ Aguarde e tente novamente  

### Erro: "2-Step Verification not enabled"
→ 2FA não está ativado  
→ Vá em: https://myaccount.google.com/security  
→ Ative 2FA  

---

## 📞 Resumo da Configuração

| Item | O Quê |
|------|-------|
| Email | seu_email@gmail.com |
| Senha | De app (não principal) |
| 2FA | Deve estar ON |
| Local | Streamlit Cloud Secrets |
| Nomes | SENDER_EMAIL e SENDER_PASSWORD |

---

**Se seguiu tudo corretamente, vai funcionar!** ✅
