import streamlit as st
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os
from datetime import datetime
from PIL import Image
import io
import urllib.parse

# --- CONFIGURAÇÕES ---
CONSULTORES = {
    "Diulie": "555330261205",
    "José": "555330261204",
    "Jonathan": "555330261329"
}

# Inicialização do Estado
if 'lista_fotos' not in st.session_state:
    st.session_state.lista_fotos = []
if 'pdf_pronto' not in st.session_state:
    st.session_state.pdf_pronto = None
if 'finalizado' not in st.session_state:
    st.session_state.finalizado = False

def gerar_pdf_bytes(dados, fotos, consultor, os_numero):
    margem = 25.4
    largura_disponivel = 210 - (2 * margem)
    largura_logo = 40 
    
    pdf = FPDF()
    pdf.set_margins(left=margem, top=margem, right=margem)
    pdf.add_page()
    
    # Centralização do logo no PDF: (Largura Total - Largura Logo) / 2
    pos_x_logo = (210 - largura_logo) / 2
    
    if os.path.exists("assets/logo.png"):
        pdf.image("assets/logo.png", x=pos_x_logo, y=15, w=largura_logo)
    
    pdf.set_font("helvetica", "B", 16)
    pdf.ln(25) 
    pdf.cell(0, 10, "Satte Alam - Orçamento", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(10)
    
    pdf.set_font("helvetica", size=12)
    pdf.cell(0, 10, f"OS: {os_numero} | Consultor: {consultor}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 10, f"Data: {datetime.now().strftime('%d/%m/%Y')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)
    
    # Tratamento de texto para evitar erros de codificação no PDF
    texto_pdf = dados.replace('\xa0', ' ').encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, f"Notas:\n{texto_pdf}")
    pdf.ln(10)
    
    for foto in fotos:
        img = Image.open(foto)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=75)
        
        largura_img, altura_img = img.size
        altura_no_pdf = (largura_disponivel / largura_img) * altura_img
        
        if pdf.get_y() + altura_no_pdf > 270:
            pdf.add_page()
            
        pdf.image(img_byte_arr, x=margem, w=largura_disponivel)
        pdf.ln(10)
        
    return bytes(pdf.output())

# --- INTERFACE ---
st.set_page_config(page_title="Satte Alam Mobile", layout="centered")

# CSS para centralizar a imagem no App Streamlit
st.markdown(
    """
    <style>
    .centered-img {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if os.path.exists("assets/logo.png"):
    st.markdown('<div class="centered-img">', unsafe_allow_html=True)
    st.image("assets/logo.png", width=150)
    st.markdown('</div>', unsafe_allow_html=True)

st.title("Registro de Evidências")

c1, c2 = st.columns(2)
consultor_nome = c1.selectbox("Selecione o Consultor", list(CONSULTORES.keys()))
os_num = c2.text_input("Número da OS")

# --- CAPTURA DE FOTOS ---
foto_capturada = st.camera_input("Capturar Foto")

if foto_capturada:
    if 'ultima_foto_id' not in st.session_state or st.session_state.ultima_foto_id != foto_capturada.name:
        st.session_state.lista_fotos.append(foto_capturada)
        st.session_state.ultima_foto_id = foto_capturada.name
        st.toast(f"Foto {len(st.session_state.lista_fotos)} adicionada")

if st.session_state.lista_fotos:
    st.write(f"### Evidências ({len(st.session_state.lista_fotos)})")
    cols = st.columns(3)
    for i, foto in enumerate(st.session_state.lista_fotos):
        with cols[i % 3]:
            st.image(foto, use_container_width=True)
            if st.button(f"Remover", key=f"del_{i}"):
                st.session_state.lista_fotos.pop(i)
                st.rerun()

texto = st.text_area("Observações Técnicas")

# --- FINALIZAÇÃO ---
if not st.session_state.finalizado:
    botao_liberado = True if os_num and st.session_state.lista_fotos else False
    
    if st.button("Gerar Orçamento", use_container_width=True, disabled=not botao_liberado):
        pdf_bytes = gerar_pdf_bytes(texto, st.session_state.lista_fotos, consultor_nome, os_num)
        st.session_state.pdf_pronto = pdf_bytes
        st.session_state.finalizado = True
        st.rerun()

if st.session_state.finalizado:
    st.success(f"PDF da OS {os_num} Gerado")
    
    st.download_button(
        label="1. BAIXAR PDF",
        data=st.session_state.pdf_pronto,
        file_name=f"OS_{os_num}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    
    numero_zap = CONSULTORES[consultor_nome]
    msg = f"Olá {consultor_nome}, seguem fotos da OS {os_num}. Por favor, verifique o orçamento em anexo."
    link_zap = f"https://wa.me/{numero_zap}?text={urllib.parse.quote(msg)}"
    
    st.link_button("2. ENVIAR WHATSAPP", link_zap, use_container_width=True)

    if st.button("Limpar para Nova OS"):
        st.session_state.lista_fotos = []
        st.session_state.pdf_pronto = None
        st.session_state.finalizado = False
        if 'ultima_foto_id' in st.session_state: del st.session_state.ultima_foto_id
        st.rerun()