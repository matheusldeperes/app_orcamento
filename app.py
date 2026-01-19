import streamlit as st
from fpdf import FPDF
import os
from datetime import datetime
from PIL import Image
import io
import smtplib
from email.message import EmailMessage

# --- CONFIGURAÇÕES ---
CONSULTORES = {
    "Diulie": "oficina@sattealam.com",
    "Jonathan": "jonathan@sattealam.com",
    "José": "joseantonio@sattealam.com"
}
EMAIL_COPIA = "oficina@sattealam.com"

# Inicialização do Estado
if 'lista_fotos' not in st.session_state:
    st.session_state.lista_fotos = []
if 'pdf_pronto' not in st.session_state:
    st.session_state.pdf_pronto = None
if 'finalizado' not in st.session_state:
    st.session_state.finalizado = False

def enviar_email_utf8(pdf_bytes, filename, destinatario, os_numero):
    remetente = st.secrets["email_usuario"]
    senha = st.secrets["email_senha"]
    
    # EmailMessage já utiliza UTF-8 por padrão, evitando o erro de ASCII
    msg = EmailMessage()
    msg['Subject'] = f"Orçamento - Evidências da OS_{os_numero}"
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Cc'] = EMAIL_COPIA
    
    # Limpamos o texto de qualquer caractere invisível problemático antes de enviar
    corpo = f"Olá,\n\nSeguem as evidências fotográficas da OS {os_numero}.\n\nApp Satte Alam."
    msg.set_content(corpo) 

    # Anexamos o PDF como dados binários (pula a leitura de texto, evitando erros de codec)
    msg.add_attachment(
        pdf_bytes,
        maintype='application',
        subtype='pdf',
        filename=filename
    )
    
    # Conexão SSL Segura
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(remetente, senha)
        server.send_message(msg)

def gerar_pdf_bytes(dados, fotos, consultor, os_numero):
    # FILTRO: Remove caracteres que o PDF padrão não entende (como o \xa0)
    # e substitui por espaços normais.
    dados_limpos = dados.replace('\xa0', ' ').encode('latin-1', 'ignore').decode('latin-1')
    
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
    
    pdf.multi_cell(0, 10, f"Notas:\n{dados_limpos}")
    pdf.ln(10)
    
    for foto in fotos:
        img = Image.open(foto)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=70)
        
        if pdf.get_y() > 220:
            pdf.add_page()
        pdf.image(img_byte_arr, x=10, w=100)
        pdf.ln(5)
        
    # Retorna como bytes puros
    return bytes(pdf.output())

# --- INTERFACE ---
st.set_page_config(page_title="Satte Alam Mobile", layout="centered")

if os.path.exists("assets/logo.png"):
    st.image("assets/logo.png", width=150)

st.title("📸 Registro de Evidências")

c1, c2 = st.columns(2)
consultor_nome = c1.selectbox("Consultor", list(CONSULTORES.keys()))
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

# --- LÓGICA DE ENVIO ---
if not st.session_state.finalizado:
    if st.button("🚀 Finalizar e Enviar por E-mail", use_container_width=True):
        if os_num and st.session_state.lista_fotos:
            with st.spinner("Enviando e-mail..."):
                try:
                    pdf_bytes = gerar_pdf_bytes(texto, st.session_state.lista_fotos, consultor_nome, os_num)
                    st.session_state.pdf_pronto = pdf_bytes
                    
                    enviar_email_utf8(pdf_bytes, f"OS_{os_num}.pdf", CONSULTORES[consultor_nome], os_num)
                    
                    st.session_state.finalizado = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro de envio: {e}")
        else:
            st.warning("⚠️ Informe a OS e capture fotos.")

if st.session_state.finalizado:
    st.success("✅ E-mail enviado com sucesso!")
    st.download_button(
        label="📥 Baixar Cópia no Celular",
        data=st.session_state.pdf_pronto,
        file_name=f"OS_{os_num}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    if st.button("Nova OS (Limpar)"):
        st.session_state.lista_fotos = []
        st.session_state.pdf_pronto = None
        st.session_state.finalizado = False
        st.rerun()