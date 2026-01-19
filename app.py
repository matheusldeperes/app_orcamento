import streamlit as st
from fpdf import FPDF
import os
from datetime import datetime
from PIL import Image
import io
import urllib.parse
import requests

# --- CONFIGURAÇÕES ---
CONSULTORES = {
    "Diulie": "5553981288887",
    "José": "555330261204",
    "Jonathan": "555330261329"
}

# Inicialização do Estado
if 'lista_fotos' not in st.session_state:
    st.session_state.lista_fotos = []
if 'link_pdf' not in st.session_state:
    st.session_state.link_pdf = None

def hospedar_pdf_temporario(pdf_bytes, filename):
    """
    Faz upload para o serviço file.io (grátis e sem conta) 
    para gerar um link que o consultor possa abrir.
    """
    try:
        files = {'file': (filename, pdf_bytes, 'application/pdf')}
        # O arquivo expira em 1 dia ou após o primeiro download
        response = requests.post('https://file.io/?expires=1d', files=files)
        if response.status_code == 200:
            return response.json().get('link')
        else:
            return None
    except:
        return None

def gerar_pdf_bytes(dados, fotos, consultor, os_numero):
    # Limpeza radical para evitar erros de codec
    dados_limpos = "".join(c for c in dados if ord(c) < 256).replace('\xa0', ' ')
    
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

# --- LÓGICA DE ENVIO AUTOMÁTICO ---
if st.button("🚀 FINALIZAR E ENVIAR WHATSAPP", use_container_width=True):
    if os_num and st.session_state.lista_fotos:
        with st.spinner("Gerando Link do PDF..."):
            # 1. Gera o PDF
            pdf_bytes = gerar_pdf_bytes(texto, st.session_state.lista_fotos, consultor_nome, os_num)
            
            # 2. Hospeda o PDF para gerar um link clicável
            link = hospedar_pdf_temporario(pdf_bytes, f"OS_{os_num}.pdf")
            
            if link:
                # 3. Monta o Link do WhatsApp com o link do PDF já na mensagem
                numero_zap = CONSULTORES[consultor_nome]
                msg = f"Olá {consultor_nome}, segue as evidências da OS {os_num}. Clique para abrir o PDF: {link}"
                link_whatsapp = f"https://wa.me/{numero_zap}?text={urllib.parse.quote(msg)}"
                
                # Abre o WhatsApp automaticamente (ou via botão de segurança)
                st.success("PDF pronto para envio!")
                st.link_button("CLIQUE AQUI PARA CONFIRMAR ENVIO", link_whatsapp, type="primary", use_container_width=True)
            else:
                st.error("Erro ao gerar link do arquivo. Verifique sua conexão.")
    else:
        st.warning("⚠️ Preencha a OS e tire fotos.")

if st.button("Nova OS (Limpar)"):
    st.session_state.lista_fotos = []
    st.rerun()