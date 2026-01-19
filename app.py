import streamlit as st
from fpdf import FPDF
import os
from datetime import datetime
from PIL import Image
import io
# Bibliotecas para Google Drive
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# --- CONFIGURAÇÕES ---
SCOPES = ['https://www.googleapis.com/auth/drive.file']
# Substitua pelo ID da pasta Satte Alam no seu Google Drive
PARENT_FOLDER_ID = '1p-GmmzGCeLM0EX2xYba5ufK3--goB4iN' 

# Inicialização do Estado para as Fotos
if 'lista_fotos' not in st.session_state:
    st.session_state.lista_fotos = []
if 'pdf_pronto' not in st.session_state:
    st.session_state.pdf_pronto = None

def upload_to_drive(file_content, filename, folder_name):
    creds_dict = st.secrets["google_credentials"]
    creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)
    
    # 1. Busca ou cria a pasta do Consultor
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and '{PARENT_FOLDER_ID}' in parents and trashed = false"
    results = service.files().list(q=query, supportsAllDrives=True, includeItemsFromAllDrives=True).execute().get('files', [])
    
    if not results:
        file_metadata = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [PARENT_FOLDER_ID]}
        folder = service.files().create(body=file_metadata, fields='id', supportsAllDrives=True).execute()
        folder_id = folder.get('id')
    else:
        folder_id = results[0]['id']

    # 2. Upload do PDF (Ajustado para usar a cota da pasta pai)
    file_metadata = {
        'name': filename, 
        'parents': [folder_id]
    }
    media = MediaIoBaseUpload(file_content, mimetype='application/pdf', resumable=True)
    
    # Criar o arquivo garantindo que ele herde as permissões e use a cota do proprietário da pasta
    service.files().create(
        body=file_metadata, 
        media_body=media, 
        fields='id',
        supportsAllDrives=True # Essencial para evitar o erro de cota em Service Accounts
    ).execute()

def gerar_pdf_bytes(dados, fotos, consultor, os_numero):
    pdf = FPDF()
    pdf.add_page()
    
    # Logo (Assets)
    if os.path.exists("assets/logo.png"):
        pdf.image("assets/logo.png", x=10, y=8, w=33)
    
    pdf.set_font("helvetica", "B", 16)
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
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        
        if pdf.get_y() > 220:
            pdf.add_page()
            
        pdf.image(img_byte_arr, x=10, w=100)
        pdf.ln(5)
        
    pdf_output = pdf.output()
    return bytes(pdf_output)

# --- INTERFACE ---
st.set_page_config(page_title="Satte Alam Mobile", layout="centered")

# Exibição da Logo no topo
if os.path.exists("assets/logo.png"):
    st.image("assets/logo.png", width=150)

st.title("📸 Orçamento Satte Alam")

# Seleção de Consultor e OS
c1, c2 = st.columns(2)
consultor = c1.selectbox("Consultor", ["Diulie", "José", "Jonathan"])
os_num = c2.text_input("Número da OS")

# 1. Coleta de Foto
foto_capturada = st.camera_input("Capturar Evidência")

if foto_capturada:
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

# 3. Notas
texto = st.text_area("Observações do Orçamento")

# --- LÓGICA DE ENVIO E DOWNLOAD ---

if st.button("🚀 Finalizar e Enviar para o Drive", use_container_width=True):
    if os_num and st.session_state.lista_fotos:
        with st.spinner("Processando..."):
            try:
                # Gera o PDF
                pdf_final = gerar_pdf_bytes(texto, st.session_state.lista_fotos, consultor, os_num)
                st.session_state.pdf_pronto = pdf_final # Salva no estado para o download_button
                
                # Envia para o Drive
                pdf_buffer = io.BytesIO(pdf_final)
                upload_to_drive(pdf_buffer, f"OS_{os_num}.pdf", consultor)
                
                st.success(f"✅ PDF enviado com sucesso para a pasta de {consultor}!")
                
            except Exception as e:
                st.error(f"Erro no processo: {e}")
    else:
        st.warning("⚠️ Informe a OS e capture ao menos uma foto.")

# Se o PDF já foi gerado, mostra a opção de salvar no dispositivo
if st.session_state.pdf_pronto is not None:
    st.write("---")
    st.download_button(
        label="📥 Baixar cópia no Celular",
        data=st.session_state.pdf_pronto,
        file_name=f"OS_{os_num}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    if st.button("Limpar e Nova OS"):
        st.session_state.lista_fotos = []
        st.session_state.pdf_pronto = None
        st.rerun()