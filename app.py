import streamlit as st
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os
from datetime import datetime
from PIL import Image
import io
import yagmail # Biblioteca robusta para transporte de e-mail

# --- CONFIGURAÇÕES ---
CONSULTORES = {
    "Diulie": "oficina@sattealam.com",
    "Jonathan": "jonathan@sattealam.com",
    "Jose": "joseantonio@sattealam.com" # Removido acento para evitar conflito de rede
}
EMAIL_COPIA = "oficina@sattealam.com"

# Inicialização do Estado
if 'lista_fotos' not in st.session_state:
    st.session_state.lista_fotos = []
if 'pdf_pronto' not in st.session_state:
    st.session_state.pdf_pronto = None
if 'finalizado' not in st.session_state:
    st.session_state.finalizado = False

def enviar_email_yagmail(pdf_bytes, filename, destinatario, os_numero):
    """
    Utiliza yagmail para contornar erros de codec ASCII.
    O yagmail gerencia automaticamente a codificação de anexos e textos.
    """
    usuario = st.secrets["email_usuario"]
    senha = st.secrets["email_senha"]
    
    try:
        # Inicializa o servidor
        yag = yagmail.SMTP(usuario, senha)
        
        # Grava o PDF em um arquivo temporário (isso isola a imagem e evita erro de stream)
        with open(filename, "wb") as f:
            f.write(pdf_bytes)
        
        assunto = f"Orcamento - Evidencias da OS {os_numero}"
        conteudo = f"Seguem em anexo as evidencias da OS {os_numero} capturadas via App Satte Alam."
        
        # Envio direto (To + Cc)
        yag.send(
            to=[destinatario, EMAIL_COPIA],
            subject=assunto,
            contents=conteudo,
            attachments=filename
        )
        
        # Remove o arquivo temporário após o envio
        if os.path.exists(filename):
            os.remove(filename)
            
    except Exception as e:
        # Se falhar aqui, o erro será exibido com detalhes
        st.error(f"Erro no transporte do e-mail: {e}")
        raise e

def gerar_pdf_bytes(dados, fotos, consultor, os_numero):
    # Limpeza radical de caracteres incompatíveis com PDF padrão
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
            with st.spinner("Processando e enviando e-mail..."):
                try:
                    # 1. Gera o PDF em bytes
                    pdf_bytes = gerar_pdf_bytes(texto, st.session_state.lista_fotos, consultor_nome, os_num)
                    st.session_state.pdf_pronto = pdf_bytes
                    
                    # 2. Envia usando yagmail (Trata o codec automaticamente)
                    enviar_email_yagmail(
                        pdf_bytes, 
                        f"OS_{os_num}.pdf", 
                        CONSULTORES[consultor_nome], 
                        os_num
                    )
                    
                    st.session_state.finalizado = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro Crítico no Envio: {e}")
        else:
            st.warning("⚠️ Informe a OS e capture fotos.")

if st.session_state.finalizado:
    st.success("✅ Orçamento enviado com sucesso!")
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