import streamlit as st
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os
from datetime import datetime
from PIL import Image
import io
import yagmail
import unicodedata

# --- CONFIGURAÇÕES ---
# Removidos quaisquer possíveis caracteres especiais ocultos nos nomes
CONSULTORES = {
    "Diulie": "diulie@sattealam.com",
    "Jonathan": "jonathan@sattealam.com",
    "Jose": "joseantonio@sattealam.com"
}
EMAIL_COPIA = "oficina@sattealam.com"

# Inicialização do Estado
if 'lista_fotos' not in st.session_state:
    st.session_state.lista_fotos = []
if 'pdf_pronto' not in st.session_state:
    st.session_state.pdf_pronto = None
if 'finalizado' not in st.session_state:
    st.session_state.finalizado = False

def limpar_header(texto):
    """
    Remove qualquer caractere não-ASCII (como \xa0 ou acentos) 
    apenas para os campos de cabeçalho do e-mail (Assunto e Nome de Arquivo).
    """
    if not texto:
        return ""
    # Normaliza e remove acentos/caracteres especiais
    nfkd_form = unicodedata.normalize('NFKD', str(texto))
    texto_limpo = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    # Substitui o \xa0 e outros espaços por espaço simples e remove o que não for ASCII
    return texto_limpo.replace('\xa0', ' ').encode('ascii', 'ignore').decode('ascii')

def enviar_email_yagmail(pdf_bytes, filename, destinatario, os_numero):
    usuario = st.secrets["email_usuario"]
    senha = st.secrets["email_senha"]
    
    try:
        yag = yagmail.SMTP(usuario, senha)
        
        # Limpeza absoluta dos campos de cabeçalho
        os_limpa = limpar_header(os_numero)
        file_limpo = limpar_header(filename)
        assunto_limpo = limpar_header(f"Orcamento - Evidencias da OS {os_limpa}")
        
        # Salva temporariamente o arquivo com nome limpo
        with open(file_limpo, "wb") as f:
            f.write(pdf_bytes)
        
        conteudo = f"Seguem anexas as evidencias da OS {os_limpa}."
        
        # Envio forçando a limpeza
        yag.send(
            to=[destinatario, EMAIL_COPIA],
            subject=assunto_limpo,
            contents=conteudo,
            attachments=file_limpo
        )
        
        if os.path.exists(file_limpo):
            os.remove(file_limpo)
            
    except Exception as e:
        st.error(f"Erro no transporte do e-mail: {e}")
        raise e

def gerar_pdf_bytes(dados, fotos, consultor, os_numero):
    # No PDF podemos manter caracteres latinos, pois usamos latin-1 ignore
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
    st.write("### Fotos Capturadas")
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
            with st.spinner("Limpando dados e enviando..."):
                try:
                    # 1. Gera o PDF
                    pdf_bytes = gerar_pdf_bytes(texto, st.session_state.lista_fotos, consultor_nome, os_num)
                    st.session_state.pdf_pronto = pdf_bytes
                    
                    # 2. Envia (com os headers blindados em ASCII)
                    enviar_email_yagmail(pdf_bytes, f"OS_{os_num}.pdf", CONSULTORES[consultor_nome], os_num)
                    
                    st.session_state.finalizado = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro Crítico no Envio: {e}")
        else:
            st.warning("⚠️ Preencha a OS e capture fotos.")

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