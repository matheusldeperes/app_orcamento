import streamlit as st
from fpdf import FPDF
import os
from datetime import datetime
from PIL import Image
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- CONFIGURAÇÕES ---
CONSULTORES = {
    "Diulie": "diulie@sattealam.com",
    "Jonathan": "jonathan@sattealam.com",
    "José": "joseantonio@sattealam.com"
}
EMAIL_COPIA = "oficina@sattealam.com"

# Inicialização do Estado
if 'lista_fotos' not in st.session_state:
    st.session_state.lista_fotos = []
if 'pdf_pronto' not in st.session_state:
    st.session_state.pdf_pronto = None
if 'email_enviado' not in st.session_state:
    st.session_state.email_enviado = False

def enviar_email(pdf_bytes, filename, destinatario, os_numero):
    # Pega os dados dos Secrets (Configurado no Streamlit Cloud ou secrets.toml)
    remetente = st.secrets["email_usuario"]
    senha = st.secrets["email_senha"]
    
    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Cc'] = EMAIL_COPIA
    msg['Subject'] = f"Orçamento - Evidências da OS_{os_numero}"
    
    corpo = f"Olá,\n\nSegue em anexo o PDF com as evidências da OS {os_numero}.\n\nEnviado via App Mobile Satte Alam."
    msg.attach(MIMEText(corpo, 'plain'))
    
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(pdf_bytes)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename= {filename}")
    msg.attach(part)
    
    # Conexão segura com o servidor do Gmail
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(remetente, senha)
    
    todos_destinatarios = [destinatario, EMAIL_COPIA]
    server.sendmail(remetente, todos_destinatarios, msg.as_string())
    server.quit()

def gerar_pdf_bytes(dados, fotos, consultor, os_numero):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("assets/logo.png"):
        pdf.image("assets/logo.png", x=10, y=8, w=33)
    
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "Satte Alam - Orçamento", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("helvetica", size=12)
    pdf.cell(0, 10, f"OS: {os_numero} | Consultor: {consultor}", ln=True)
    pdf.cell(0, 10, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(5)
    pdf.multi_cell(0, 10, f"Notas:\n{dados}")
    pdf.ln(10)
    
    for foto in fotos:
        img = Image.open(foto)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        if pdf.get_y() > 220: pdf.add_page()
        pdf.image(img_byte_arr, x=10, w=100)
        pdf.ln(5)
    return bytes(pdf.output())

# --- INTERFACE ---
st.set_page_config(page_title="Satte Alam Mobile", layout="centered")

if os.path.exists("assets/logo.png"):
    st.image("assets/logo.png", width=150)

st.title("📸 Registro de Evidências")

c1, c2 = st.columns(2)
consultor_nome = c1.selectbox("Selecione o Consultor", list(CONSULTORES.keys()))
os_num = c2.text_input("Número da OS")

foto_capturada = st.camera_input("Tirar Foto")
if foto_capturada:
    if foto_capturada not in st.session_state.lista_fotos:
        st.session_state.lista_fotos.append(foto_capturada)

if st.session_state.lista_fotos:
    st.write("### Fotos")
    for i, foto in enumerate(st.session_state.lista_fotos):
        col_img, col_btn = st.columns([3, 1])
        col_img.image(foto, width=150)
        if col_btn.button(f"Excluir", key=f"btn_{i}"):
            st.session_state.lista_fotos.pop(i)
            st.rerun()

texto = st.text_area("Observações Técnicas")

# --- BOTÕES DE AÇÃO ---
if not st.session_state.email_enviado:
    if st.button("🚀 Finalizar e Enviar Orçamento", use_container_width=True):
        if os_num and st.session_state.lista_fotos:
            with st.spinner("Enviando e-mail..."):
                try:
                    pdf_final = gerar_pdf_bytes(texto, st.session_state.lista_fotos, consultor_nome, os_num)
                    st.session_state.pdf_pronto = pdf_final
                    
                    enviar_email(pdf_final, f"OS_{os_num}.pdf", CONSULTORES[consultor_nome], os_num)
                    
                    st.session_state.email_enviado = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
        else:
            st.warning("⚠️ Informe a OS e capture fotos.")

if st.session_state.email_enviado:
    st.success(f"✅ Enviado com sucesso para {consultor_nome} e Oficina!")
    st.download_button(
        label="📥 Baixar Cópia no Celular",
        data=st.session_state.pdf_pronto,
        file_name=f"OS_{os_num}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    if st.button("Nova OS (Limpar)", type="primary"):
        st.session_state.lista_fotos = []
        st.session_state.pdf_pronto = None
        st.session_state.email_enviado = False
        st.rerun()