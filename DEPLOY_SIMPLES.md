# 🚀 Deploy no Streamlit Cloud (Simples!)

## 3 Passos para Colocar Rodando na Nuvem

### 1️⃣ Prepare no GitHub

```bash
cd APP_Orçamentos

# Inicializar git
git init
git add .
git commit -m "Satte Alam App"

# Fazer push
git remote add origin https://github.com/SEU_USUARIO/app-orcamentos.git
git branch -M main
git push -u origin main
```

### 2️⃣ Deploy no Streamlit Cloud

1. Abra: https://share.streamlit.io/
2. Clique: **"Create app"**
3. Selecione:
   - **GitHub account**: seu-usuario
   - **Repository**: app-orcamentos
   - **Branch**: main
   - **Main file path**: app.py
4. Clique: **"Deploy"**

Pronto! ✅

### 3️⃣ Configure as Credenciais de Email

No dashboard do Streamlit Cloud:

1. Clique no menu **⋮** (três pontinhos)
2. Vá em **Settings**
3. Clique em **Secrets**
4. Cole isso:

```
SENDER_EMAIL = "seu_email@gmail.com"
SENDER_PASSWORD = "sua_senha_de_app_gmail"
```

5. **Save** → App reinicia automaticamente ✅

---

## 🎉 Pronto!

Seu app estará em:
```
https://seu-usuario-app-orcamentos.streamlit.app
```

Acesse no navegador, no celular pela mesma URL. Pronto!

---

## 📧 Gerar Senha de App (Gmail)

Se não tem ainda:

1. Acesse: https://myaccount.google.com/apppasswords
2. Gere uma senha
3. Cole no Secrets do Streamlit Cloud

---

**Tudo cloud. Sem complicação.** ☁️
