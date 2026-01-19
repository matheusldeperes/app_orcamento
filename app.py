import streamlit as st
from fpdf import FPDF
import os
from datetime import datetime
from PIL import Image
import io
import json
# Bibliotecas para Google Drive
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# --- CONFIGURAÇÕES ---
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = 'credentials.json' # Seu arquivo de credenciais
PARENT_FOLDER_ID = 'ID_DA_SUA_PASTA_NO_DRIVE' # O ID que aparece na URL da pasta do Drive

# Inicialização do Estado para as Fotos
if 'lista_fotos' not in st.session_state:
    st.session_state.lista_fotos = []

def upload_to_drive(file_content, filename, folder_name):
    creds_dict = json.loads(st.secrets["google_credentials"])
    creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)
    
    # 1. Busca ou cria a pasta do Consultor
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and '{PARENT_FOLDER_ID}' in parents"
    results = service.files().list(q=query).execute().get('files', [])
    
    if not results:
        file_metadata = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [PARENT_FOLDER_ID]}
        folder = service.files().create(body=file_metadata, fields='id').execute()
        folder_id = folder.get('id')
    else:
        folder_id = results[0]['id']

    # 2. Upload do PDF
    file_metadata = {'name': filename, 'parents': [folder_id]}
    media = MediaIoBaseUpload(file_content, mimetype='application/pdf')
    service.files().create(body=file_metadata, media_body=media, fields='id').execute()

def gerar_pdf_bytes(dados, fotos, consultor, os_numero):
    pdf = FPDF()
    pdf.add_page()
    
    # Logo (Assets)
    if os.path.exists("assets/logo.png"):
        pdf.image("assets/logo.png", x=10, y=8, w=33)
    
    pdf.set_font("helvetica", "B", 16) # 'helvetica' é mais seguro que 'Arial' no fpdf2
    pdf.cell(0, 10, "Satte Alam - Orçamento", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("helvetica", size=12)
    pdf.cell(0, 10, f"OS: {os_numero} | Consultor: {consultor}", ln=True)
    pdf.cell(0, 10, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(5)
    
    pdf.multi_cell(0, 10, f"Evidências:\n{dados}")
    pdf.ln(10)
    
    for foto in fotos:
        img = Image.open(foto)
        # Converte para RGB para evitar erros com transparência de PNG no PDF
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        
        # Verifica espaço na página
        if pdf.get_y() > 220:
            pdf.add_page()
            
        pdf.image(img_byte_arr, x=10, w=100)
        pdf.ln(5)
        
    # No fpdf2, o output() sem argumentos retorna os bytes do PDF
    pdf_output = pdf.output()
    
    # Se o retorno for bytearray, converte para bytes
    if isinstance(pdf_output, bytearray):
        return bytes(pdf_output)
    return pdf_output

# --- INTERFACE ---
st.set_page_config(page_title="Satte Alam Mobile", layout="centered")

st.title("📸 Orçamento -  Satte Alam")

# Seleção de Consultor e OS
c1, c2 = st.columns(2)
consultor = c1.selectbox("Consultor", ["Diulie", "José", "Jonathan"])
os_num = c2.text_input("Número da OS")

# 1. Coleta de Foto pela Câmera
foto_capturada = st.camera_input("Tirar foto da evidência")

if foto_capturada:
    # Evita duplicatas ao processar o frame
    if foto_capturada not in st.session_state.lista_fotos:
        st.session_state.lista_fotos.append(foto_capturada)

# 2. Exibição e Gerenciamento das Fotos
if st.session_state.lista_fotos:
    st.write("### Fotos Capturadas")
    for i, foto in enumerate(st.session_state.lista_fotos):
        col_img, col_btn = st.columns([3, 1])
        col_img.image(foto, width=150)
        if col_btn.button(f"Excluir", key=f"btn_{i}"):
            st.session_state.lista_fotos.pop(i)
            st.rerun()

# 3. Texto e Envio
texto = st.text_area("Notas do Mecânico")

# --- FINAL DO CÓDIGO (PARTE DO BOTÃO) ---

if st.button("Gerar PDF para Teste", use_container_width=True):
    if os_num and st.session_state.lista_fotos:
        with st.spinner("Construindo PDF..."):
            try:
                # Gera o conteúdo
                raw_pdf = gerar_pdf_bytes(texto, st.session_state.lista_fotos, consultor, os_num)
                
                # Garante que é bytes para o Streamlit
                pdf_final = bytes(raw_pdf)
                
                st.success("✅ PDF gerado com sucesso!")
                
                st.download_button(
                    label="Clique aqui para baixar o PDF",
                    data=pdf_final,
                    file_name=f"OS_{os_num}.pdf",
                    mime="application/pdf"
                )

            except Exception as e:
                st.error(f"Erro ao gerar PDF: {e}")
    else:
        st.warning("⚠️ Preencha a OS e tire uma foto.")