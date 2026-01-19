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
    "Diulie": "555330261206",
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
    # Limpeza para evitar qualquer erro de caractere no PDF
    dados_limpos = dados.replace('\xa0', ' ').encode('latin-1', 'ignore').decode('latin-1')
    
    pdf = FPDF()
    pdf.add_page()
    
    if os.path.exists("assets/logo.png"):
        pdf.image("assets/logo.png", x=10, y=8, w=33)
    
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "Satte Alam - Orçamento", 
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(10)
    
    pdf.set_font("helvetica", size=12)
    pdf.cell(0, 10, f"OS: {os_numero} | Consultor: {consultor}", 
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 10, f"Data: {datetime.now().strftime('%d/%m/%Y')}", 
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
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
        
    # Converte explicitamente para bytes para evitar erro de binary format no Streamlit
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
    st.write("### Fotos Capturadas")
    for i, foto in enumerate(st.session_state.lista_fotos):
        col_img, col_btn = st.columns([3, 1])
        col_img.image(foto, width=150)
        if col_btn.button(f"Excluir", key=f"btn_{i}"):
            st.session_state.lista_fotos.pop(i)
            st.rerun()

texto = st.text_area("Observações Técnicas")

# --- FLUXO DE FINALIZAÇÃO ---
if not st.session_state.finalizado:
    if st.button("🚀 Gerar Orçamento", use_container_width=True):
        if os_num and st.session_state.lista_fotos:
            with st.spinner("Gerando PDF..."):
                try:
                    pdf_bytes = gerar_pdf_bytes(texto, st.session_state.lista_fotos, consultor_nome, os_num)
                    st.session_state.pdf_pronto = pdf_bytes
                    st.session_state.finalizado = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao gerar: {e}")
        else:
            st.warning("⚠️ Informe a OS e capture fotos.")

# --- AÇÕES PÓS-GERAÇÃO ---
if st.session_state.finalizado:
    st.success(f"✅ Orçamento da OS {os_num} gerado!")
    
    # 1. Botão de Download (Crucial para iOS e Android terem o arquivo na galeria/arquivos)
    st.download_button(
        label="1. 📥 BAIXAR PDF NO CELULAR",
        data=st.session_state.pdf_pronto,
        file_name=f"OS_{os_num}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    
    # 2. Link do WhatsApp
    numero_zap = CONSULTORES[consultor_nome]
    msg = f"Olá {consultor_nome}, seguem evidências da OS {os_num}. (Anexe o PDF que você acabou de baixar)"
    msg_url = urllib.parse.quote(msg)
    link_zap = f"https://wa.me/{numero_zap}?text={msg_url}"
    
    st.link_button(f"2. 🟢 ENVIAR PARA WHATSAPP DE {consultor_nome.upper()}", link_zap, use_container_width=True)

    st.write("---")
    if st.button("Nova OS (Limpar Tudo)", type="primary"):
        st.session_state.lista_fotos = []
        st.session_state.pdf_pronto = None
        st.session_state.finalizado = False
        st.rerun()