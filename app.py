import streamlit as st
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os
from datetime import datetime
from PIL import Image
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# --- CONFIGURAÇÕES ---
CONSULTORES = {
    "Diulie": {
        "email": "oficina@sattealam.com",
        "whatsapp": "555330261205"
    },
    "José": {
        "email": "jose@sattealam.com",
        "whatsapp": "555330261204"
    },
    "Jonathan": {
        "email": "jonathan@sattealam.com",
        "whatsapp": "555330261329"
    }
}

EMAIL_OFICINA = "oficina@sattealam.com"
SENDER_EMAIL = st.secrets.get("SENDER_EMAIL", "matheusldeperes@gmail.com")
SENDER_PASSWORD = st.secrets.get("SENDER_PASSWORD", "")

# Inicialização do Estado
if 'lista_fotos' not in st.session_state:
    st.session_state.lista_fotos = []
if 'pdf_pronto' not in st.session_state:
    st.session_state.pdf_pronto = None
if 'finalizado' not in st.session_state:
    st.session_state.finalizado = False
if 'pdf_enviado' not in st.session_state:
    st.session_state.pdf_enviado = False

def enviar_email(arquivo_pdf_bytes, os_numero, consultor_nome, destinatarios):
    """Envia o PDF para os consultores e oficina"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = ", ".join(destinatarios)
        msg['Subject'] = f"Orçamento - OS {os_numero} ({consultor_nome})"
        
        corpo = f"""
        <html>
            <body style="font-family: Arial; font-size: 12px;">
                <p>Olá,</p>
                <p>Segue em anexo o orçamento da OS <strong>{os_numero}</strong></p>
                <p>Consultor: <strong>{consultor_nome}</strong></p>
                <p>Data: <strong>{datetime.now().strftime('%d/%m/%Y %H:%M')}</strong></p>
                <p>Atenciosamente,<br>Sistema Satte Alam</p>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(corpo, 'html'))
        
        # Anexar PDF
        parte = MIMEBase('application', 'octet-stream')
        parte.set_payload(arquivo_pdf_bytes)
        encoders.encode_base64(parte)
        parte.add_header('Content-Disposition', f'attachment; filename= OS_{os_numero}.pdf')
        msg.attach(parte)
        
        # Enviar com servidor SMTP (Gmail ou outro)
        # Para usar Gmail, use: smtp.gmail.com, 587, seu_email@gmail.com, sua_senha_de_app
        # Para usar outro servidor, ajuste conforme necessário
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login(SENDER_EMAIL, SENDER_PASSWORD)
        servidor.send_message(msg)
        servidor.quit()
        
        return True
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False

def gerar_pdf_bytes(logo_path, consultor, os_numero, observacoes, fotos):
    """Gera PDF com logo no topo, dados do consultor e fotos compactadas sem espaços em branco"""
    margem = 12
    largura_pagina = 210
    altura_pagina = 297
    largura_disponivel = largura_pagina - (2 * margem)
    altura_max_foto = 90  # Altura máxima de cada foto em mm
    
    pdf = FPDF()
    pdf.set_margins(left=margem, top=margem, right=margem)
    pdf.add_page()
    
    # ===== LOGO NO TOPO =====
    if os.path.exists(logo_path):
        pos_x_logo = (largura_pagina - 35) / 2
        pdf.image(logo_path, x=pos_x_logo, y=margem, w=35)
        pdf.ln(25)
    
    # ===== TÍTULO E INFORMAÇÕES =====
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 5, "Satte Alam", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    pdf.set_font("helvetica", "B", 8)
    pdf.cell(0, 4, f"Consultor: {consultor}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_font("helvetica", size=8)
    pdf.cell(0, 4, f"OS: {os_numero}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 4, f"Data: {datetime.now().strftime('%d/%m/%Y')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # ===== OBSERVAÇÕES =====
    pdf.ln(2)
    pdf.set_font("helvetica", "B", 8)
    pdf.cell(0, 4, "Observações:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_font("helvetica", size=7)
    if observacoes:
        try:
            obs_tratada = observacoes.encode('latin-1', 'ignore').decode('latin-1')
        except:
            obs_tratada = observacoes
        pdf.multi_cell(0, 3, obs_tratada)
    else:
        pdf.cell(0, 3, "Nenhuma observação.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # ===== FOTOS =====
    pdf.set_font("helvetica", "B", 8)
    pdf.cell(0, 4, "Evidências:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)
    
    for idx, foto in enumerate(fotos, 1):
        img = Image.open(foto)
        
        # Converter RGBA para RGB
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        # Redimensionar para qualidade otimizada
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=75)
        img_byte_arr.seek(0)
        
        # Calcular dimensões mantendo proporção (limitando altura)
        largura_img, altura_img = img.size
        razao = altura_img / largura_img
        
        # Definir altura máxima e calcular largura proporcional
        altura_final = altura_max_foto
        largura_final = altura_final / razao
        
        # Se a largura calculada exceder a disponível, ajustar
        if largura_final > largura_disponivel:
            largura_final = largura_disponivel
            altura_final = largura_final * razao
        
        # Verificar se cabe na página atual
        espaco_vertical = altura_pagina - pdf.get_y() - margem - 2
        
        if altura_final > espaco_vertical:
            # Criar nova página se não couber
            pdf.add_page()
        
        # Inserir imagem centralizada
        x_pos = margem + (largura_disponivel - largura_final) / 2
        pdf.image(img_byte_arr, x=x_pos, w=largura_final)
        pdf.ln(1)  # Espaço mínimo entre fotos
    
    return bytes(pdf.output())

# --- INTERFACE ---
st.set_page_config(page_title="Satte Alam - Orçamentos", layout="centered", initial_sidebar_state="collapsed")

# CSS para mobile
st.markdown(
    """
    <style>
    .centered-img {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }
    body {
        max-width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Exibir logo
if os.path.exists("assets/logo.png"):
    st.markdown('<div class="centered-img">', unsafe_allow_html=True)
    st.image("assets/logo.png", width=150)
    st.markdown('</div>', unsafe_allow_html=True)

st.title("📋 Registro de Evidências")

# ===== FORMULÁRIO =====
c1, c2 = st.columns(2)
consultor_nome = c1.selectbox("👤 Consultor", list(CONSULTORES.keys()))
os_num = c2.text_input("🔢 Número da OS", placeholder="Ex: 123456")

st.divider()

# ===== CAPTURA COM CÂMERA TRASEIRA =====
st.subheader("📸 Captura de Fotos")
st.info("💡 Em mobile, clique na câmera rotativa para usar a câmera traseira", icon="ℹ️")

foto_capturada = st.camera_input("Capturar Foto")

if foto_capturada:
    if 'ultima_foto_id' not in st.session_state or st.session_state.ultima_foto_id != foto_capturada.name:
        st.session_state.lista_fotos.append(foto_capturada)
        st.session_state.ultima_foto_id = foto_capturada.name
        st.success(f"✅ Foto {len(st.session_state.lista_fotos)} adicionada")

# ===== EXIBIÇÃO DE FOTOS CAPTURADAS =====
if st.session_state.lista_fotos:
    st.subheader(f"📷 Evidências Capturadas ({len(st.session_state.lista_fotos)})")
    cols = st.columns(2)
    for i, foto in enumerate(st.session_state.lista_fotos):
        with cols[i % 2]:
            st.image(foto, use_container_width=True)
            if st.button(f"❌ Remover Foto {i+1}", key=f"del_{i}"):
                st.session_state.lista_fotos.pop(i)
                st.rerun()

st.divider()

# ===== OBSERVAÇÕES =====
observacoes = st.text_area("📝 Observações Importantes", placeholder="Digite observações técnicas ou adicionais...")

st.divider()

# ===== BOTÃO GERAR ORÇAMENTO =====
if not st.session_state.finalizado:
    botao_liberado = bool(os_num and st.session_state.lista_fotos)
    
    if st.button("✅ Gerar Orçamento", use_container_width=True, disabled=not botao_liberado):
        with st.spinner("Gerando PDF..."):
            pdf_bytes = gerar_pdf_bytes(
                "assets/logo.png",
                consultor_nome,
                os_num,
                observacoes,
                st.session_state.lista_fotos
            )
            st.session_state.pdf_pronto = pdf_bytes
            st.session_state.finalizado = True
            st.rerun()

# ===== APÓS GERAR ORÇAMENTO =====
if st.session_state.finalizado:
    st.success(f"✅ PDF da OS {os_num} Gerado com Sucesso!")
    
    # Botão para baixar
    st.download_button(
        label="📥 Baixar PDF",
        data=st.session_state.pdf_pronto,
        file_name=f"OS_{os_num}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    
    # Botão para enviar por email
    if st.button("📧 Enviar por Email (Consultor + Oficina)", use_container_width=True):
        with st.spinner("Enviando emails..."):
            destinatarios = [
                CONSULTORES[consultor_nome]["email"],
                EMAIL_OFICINA
            ]
            sucesso = enviar_email(st.session_state.pdf_pronto, os_num, consultor_nome, destinatarios)
            
            if sucesso:
                st.success(f"✅ PDF enviado com sucesso para:\n- {CONSULTORES[consultor_nome]['email']}\n- {EMAIL_OFICINA}")
                st.session_state.pdf_enviado = True
            else:
                st.error("""❌ Erro ao enviar emails. Verifique:
                
1. **SENDER_EMAIL** está configurado no Streamlit Secrets?
2. **SENDER_PASSWORD** é a senha de app (16 caracteres)?
3. **2FA** está ativo no Gmail?

Consulte: https://myaccount.google.com/apppasswords""")
    
    # Botão limpar
    if st.button("🔄 Limpar para Nova OS", use_container_width=True):
        st.session_state.lista_fotos = []
        st.session_state.pdf_pronto = None
        st.session_state.finalizado = False
        st.session_state.pdf_enviado = False
        if 'ultima_foto_id' in st.session_state:
            del st.session_state.ultima_foto_id
        st.rerun()