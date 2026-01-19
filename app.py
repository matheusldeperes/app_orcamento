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
    # Margem de 1 polegada = 25.4 mm
    margem = 25.4
    largura_disponivel = 210 - (2 * margem)
    
    pdf = FPDF()
    pdf.set_margins(left=margem, top=margem, right=margem)
    pdf.add_page()
    
    if os.path.exists("assets/logo.png"):
        pdf.image("assets/logo.png", x=margem, y=8, w=33)
    
    pdf.set_font("helvetica", "B", 16)
    pdf.ln(10)
    pdf.cell(0, 10, "Satte Alam - Orçamento", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(10)
    
    pdf.set_font("helvetica", size=12)
    pdf.cell(0, 10, f"OS: {os_numero} | Consultor: {consultor}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 10, f"Data: {datetime.now().strftime('%d/%m/%Y')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)
    
    pdf.multi_cell(0, 10, f"Notas:\n{dados.replace('\xa0', ' ')}")
    pdf.ln(10)
    
    for foto in fotos:
        img = Image.open(foto)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        # Redimensionamento proporcional para ocupar a largura total entre margens
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=75)
        
        # Calcula a altura da imagem no PDF para evitar quebras feias
        # largura_pdf / largura_original * altura_original
        largura_img, altura_img = img.size
        altura_no_pdf = (largura_disponivel / largura_img) * altura_img
        
        if pdf.get_y() + altura_no_pdf > 270: # 297mm total - margem
            pdf.add_page()
            
        # x=margem centraliza a imagem automaticamente pois w=largura_disponivel
        pdf.image(img_byte_arr, x=margem, w=largura_disponivel)
        pdf.ln(10)
        
    return bytes(pdf.output())

# --- INTERFACE ---
st.set_page_config(page_title="Satte Alam Mobile", layout="centered")

if os.path.exists("assets/logo.png"):
    st.image("assets/logo.png", width=150)

st.title("📸 Registro de Evidências")

c1, c2 = st.columns(2)
consultor_nome = c1.selectbox("Selecione o Consultor", list(CONSULTORES.keys()))
os_num = c2.text_input("Número da OS")

# --- CAPTURA DE FOTOS ---
# O Streamlit não permite forçar a câmera traseira via código, 
# mas o comportamento de "acumular fotos" abaixo elimina a necessidade de dar "Clear".
foto_capturada = st.camera_input("Capturar Foto")

if foto_capturada:
    # Verificamos se a foto já foi adicionada para evitar duplicatas no loop do Streamlit
    if 'ultima_foto_id' not in st.session_state or st.session_state.ultima_foto_id != foto_capturada.name:
        st.session_state.lista_fotos.append(foto_capturada)
        st.session_state.ultima_foto_id = foto_capturada.name
        # Mensagem rápida para o mecânico saber que funcionou
        st.toast(f"Foto {len(st.session_state.lista_fotos)} adicionada!")

if st.session_state.lista_fotos:
    st.write(f"### Evidências ({len(st.session_state.lista_fotos)})")
    # Mostramos as fotos em colunas menores para não poluir a tela do celular
    cols = st.columns(3)
    for i, foto in enumerate(st.session_state.lista_fotos):
        with cols[i % 3]:
            st.image(foto, use_container_width=True)
            if st.button(f"🗑️", key=f"del_{i}"):
                st.session_state.lista_fotos.pop(i)
                st.rerun()

texto = st.text_area("Observações Técnicas")

# --- FINALIZAÇÃO ---
if not st.session_state.finalizado:
    # Só habilita se tiver OS e ao menos 1 foto
    botao_liberado = True if os_num and st.session_state.lista_fotos else False
    
    if st.button("🚀 Gerar Orçamento", use_container_width=True, disabled=not botao_liberado):
        pdf_bytes = gerar_pdf_bytes(texto, st.session_state.lista_fotos, consultor_nome, os_num)
        st.session_state.pdf_pronto = pdf_bytes
        st.session_state.finalizado = True
        st.rerun()

if st.session_state.finalizado:
    st.success(f"✅ PDF da OS {os_num} Gerado!")
    
    st.download_button(
        label="1. 📥 BAIXAR PDF",
        data=st.session_state.pdf_pronto,
        file_name=f"OS_{os_num}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    
    numero_zap = CONSULTORES[consultor_nome]
    msg = f"Olá {consultor_nome}, seguem fotos da OS {os_num}. (Anexe o PDF que você baixou)"
    link_zap = f"https://wa.me/{numero_zap}?text={urllib.parse.quote(msg)}"
    
    st.link_button(f"2. 🟢 ENVIAR WHATSAPP", link_zap, use_container_width=True)

    if st.button("Limpar para Nova OS"):
        st.session_state.lista_fotos = []
        st.session_state.pdf_pronto = None
        st.session_state.finalizado = False
        if 'ultima_foto_id' in st.session_state: del st.session_state.ultima_foto_id
        st.rerun()