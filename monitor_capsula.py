import cv2
import numpy as np
import paho.mqtt.client as mqtt
from datetime import datetime
import os

# =====================================
# CONFIGURAÇÕES
# =====================================

# Altere para True para testar sem hardware físico
modo_simulacao = False

# Estado global da cápsula
capsula = {
    "temperatura": 25,
    "luminosidade": 75,
    "status": "NORMAL",
    "alertas": []
}

# =====================================
# CARREGAMENTO DA IMAGEM DA CÁPSULA
# =====================================

# Busca a imagem no mesmo diretório do script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGEM_CAPSULA_PATH = os.path.join(SCRIPT_DIR, "capsula.webp")

imagem_capsula_original = None
if os.path.exists(IMAGEM_CAPSULA_PATH):
    imagem_capsula_original = cv2.imread(IMAGEM_CAPSULA_PATH, cv2.IMREAD_UNCHANGED)
    if imagem_capsula_original is None:
        print(f"[AVISO] Não foi possível carregar '{IMAGEM_CAPSULA_PATH}'. Usando representação geométrica.")
    else:
        print(f"[OK] Imagem da cápsula carregada: {IMAGEM_CAPSULA_PATH}")
else:
    print(f"[AVISO] Arquivo '{IMAGEM_CAPSULA_PATH}' não encontrado. Usando representação geométrica.")


# =====================================
# MQTT
# =====================================

def on_message(client, userdata, msg):
    """Callback para mensagens MQTT recebidas do ESP."""
    try:
        valor = msg.payload.decode()
        if msg.topic == "capsula/temperatura":
            capsula["temperatura"] = float(valor)
        elif msg.topic == "capsula/luminosidade":
            capsula["luminosidade"] = int(valor)
    except Exception as e:
        print(f"[ERRO MQTT] {e}")


if not modo_simulacao:
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.on_message = on_message
        client.connect("broker.hivemq.com", 1883, 60)
        client.subscribe("capsula/temperatura")
        client.subscribe("capsula/luminosidade")
        client.loop_start()
        print("[OK] MQTT conectado ao broker HiveMQ.")
    except Exception as e:
        print(f"[ERRO] Falha ao conectar no MQTT: {e}")
        modo_simulacao = True
        print("[INFO] Alternando para modo de simulação.")


# =====================================
# FUNÇÕES AUXILIARES
# =====================================

def desenhar_capsula_geometrica(tela, x1, y1, x2, y2, cor_status):
    """
    Desenha uma representação geométrica simples da cápsula
    caso a imagem não esteja disponível.
    """
    cx = (x1 + x2) // 2
    # Corpo retangular
    cv2.rectangle(tela, (x1 + 30, y1 + 80), (x2 - 30, y2 - 20), (100, 100, 150), -1)
    cv2.rectangle(tela, (x1 + 30, y1 + 80), (x2 - 30, y2 - 20), (200, 200, 255), 2)
    # Cúpula (elipse)
    cv2.ellipse(tela, (cx, y1 + 80), (x2 - x1 - 30) // 2 - 15, 60, 0, 180, 360, (100, 100, 150), -1)
    cv2.ellipse(tela, (cx, y1 + 80), (x2 - x1 - 30) // 2 - 15, 60, 0, 180, 360, (200, 200, 255), 2)
    # Propulsores
    cv2.rectangle(tela, (x1 + 30, y2 - 40), (x1 + 65, y2), (80, 80, 120), -1)
    cv2.rectangle(tela, (x2 - 65, y2 - 40), (x2 - 30, y2), (80, 80, 120), -1)
    cv2.rectangle(tela, (x1 + 30, y2 - 40), (x1 + 65, y2), (200, 200, 255), 1)
    cv2.rectangle(tela, (x2 - 65, y2 - 40), (x2 - 30, y2), (200, 200, 255), 1)
    # Janela
    cv2.circle(tela, (cx, y1 + 130), 30, (50, 50, 80), -1)
    cv2.circle(tela, (cx, y1 + 130), 30, (200, 200, 255), 2)
    cv2.circle(tela, (cx, y1 + 130), 30, cor_status, 1)
    # Label
    cv2.putText(tela, "CAPSULA", (x1 + 50, (y1 + y2) // 2 + 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 255), 2)


def renderizar_imagem_capsula(tela, imagem, x1, y1, x2, y2, cor_status):
    """
    Redimensiona e renderiza a imagem da cápsula na área designada,
    com suporte a canal alpha (transparência). Adiciona tint colorido
    conforme o status do sistema.
    """
    largura = x2 - x1
    altura = y2 - y1

    # Redimensiona mantendo proporção
    h_orig, w_orig = imagem.shape[:2]
    escala = min(largura / w_orig, altura / h_orig)
    novo_w = int(w_orig * escala)
    novo_h = int(h_orig * escala)
    img_resized = cv2.resize(imagem, (novo_w, novo_h), interpolation=cv2.INTER_AREA)

    # Posição centralizada na área
    off_x = x1 + (largura - novo_w) // 2
    off_y = y1 + (altura - novo_h) // 2

    # Verifica se tem canal alpha
    if img_resized.shape[2] == 4:
        alpha = img_resized[:, :, 3:4] / 255.0
        img_rgb = img_resized[:, :, :3]
        regiao = tela[off_y:off_y + novo_h, off_x:off_x + novo_w]
        composito = (img_rgb * alpha + regiao * (1 - alpha)).astype(np.uint8)
        tela[off_y:off_y + novo_h, off_x:off_x + novo_w] = composito
    else:
        tela[off_y:off_y + novo_h, off_x:off_x + novo_w] = img_resized

    # Overlay de status colorido (semitransparente) no canto superior direito da imagem
    raio = 18
    cx_ind = off_x + novo_w - 25
    cy_ind = off_y + 25
    cv2.circle(tela, (cx_ind, cy_ind), raio + 2, (0, 0, 0), -1)  # borda preta
    cv2.circle(tela, (cx_ind, cy_ind), raio, cor_status, -1)


# =====================================
# LOOP PRINCIPAL
# =====================================

historico_temp = []   # Histórico para mini-gráfico de temperatura
MAX_HISTORICO = 50

while True:
    # ----------------------------------
    # TELA BASE
    # ----------------------------------
    tela = np.zeros((700, 1200, 3), dtype=np.uint8)
    tela[:] = (15, 15, 25)  # Fundo escuro levemente azulado (espacial)

    # Grade sutil de fundo
    for x in range(0, 1200, 60):
        cv2.line(tela, (x, 0), (x, 700), (25, 25, 40), 1)
    for y in range(0, 700, 60):
        cv2.line(tela, (0, y), (1200, y), (25, 25, 40), 1)

    # ----------------------------------
    # VALIDAÇÃO DOS DADOS
    # ----------------------------------
    capsula["temperatura"] = max(-20, min(60, capsula["temperatura"]))
    capsula["luminosidade"] = max(0, min(100, capsula["luminosidade"]))

    temperatura = capsula["temperatura"]
    luminosidade = capsula["luminosidade"]

    # ----------------------------------
    # ANÁLISE DE STATUS
    # ----------------------------------
    alertas = []

    if temperatura < 10:
        cor_temperatura = (0, 0, 255)   # Vermelho (BGR)
        status = "CRITICO"
        cor_status = (0, 0, 255)
        alertas.append("TEMPERATURA CRITICA - MUITO BAIXA")
    elif temperatura > 40:
        cor_temperatura = (0, 0, 255)
        status = "CRITICO"
        cor_status = (0, 0, 255)
        alertas.append("SUPERAQUECIMENTO DETECTADO")
    elif temperatura < 20:
        cor_temperatura = (0, 255, 255)  # Amarelo
        status = "ALERTA"
        cor_status = (0, 255, 255)
        alertas.append("TEMPERATURA ABAIXO DO IDEAL")
    elif temperatura > 30:
        cor_temperatura = (0, 255, 255)
        status = "ALERTA"
        cor_status = (0, 255, 255)
        alertas.append("TEMPERATURA ACIMA DO IDEAL")
    else:
        cor_temperatura = (0, 200, 80)   # Verde
        status = "NORMAL"
        cor_status = (0, 200, 80)

    if luminosidade < 15:
        alertas.append("ILUMINACAO INSUFICIENTE")
        if status == "NORMAL":
            status = "ALERTA"
            cor_status = (0, 255, 255)

    capsula["status"] = status
    capsula["alertas"] = alertas

    # Registra histórico de temperatura
    historico_temp.append(temperatura)
    if len(historico_temp) > MAX_HISTORICO:
        historico_temp.pop(0)

    # ----------------------------------
    # TÍTULO
    # ----------------------------------
    cv2.rectangle(tela, (0, 0), (1200, 70), (20, 20, 40), -1)
    cv2.putText(tela, "SISTEMA DE MONITORAMENTO - CAPSULA ESPACIAL",
                (130, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (200, 220, 255), 2)
    # Linha separadora
    cv2.line(tela, (0, 70), (1200, 70), (60, 60, 120), 2)

    # ----------------------------------
    # PAINEL ESQUERDO: IMAGEM DA CÁPSULA
    # ----------------------------------
    cv2.rectangle(tela, (20, 85), (490, 590), (35, 35, 60), -1)
    cv2.rectangle(tela, (20, 85), (490, 590), (80, 80, 140), 2)
    cv2.putText(tela, "VISAO COMPUTACIONAL", (90, 108),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 200), 1)

    # Renderiza imagem ou geometria
    if imagem_capsula_original is not None:
        renderizar_imagem_capsula(tela, imagem_capsula_original, 25, 115, 485, 585, cor_status)
    else:
        desenhar_capsula_geometrica(tela, 25, 115, 485, 585, cor_status)

    # ----------------------------------
    # PAINEL DIREITO: DADOS E BARRAS
    # ----------------------------------
    cv2.rectangle(tela, (510, 85), (1180, 590), (35, 35, 60), -1)
    cv2.rectangle(tela, (510, 85), (1180, 590), (80, 80, 140), 2)
    cv2.putText(tela, "TELEMETRIA", (780, 108),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 200), 1)

    # Fonte de dados
    cor_fonte = (0, 200, 80) if not modo_simulacao else (0, 200, 255)
    fonte_txt = "FONTE: ESP32 via MQTT" if not modo_simulacao else "FONTE: SIMULACAO"
    cv2.putText(tela, fonte_txt, (530, 135),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, cor_fonte, 1)

    # STATUS
    cv2.putText(tela, "STATUS DO SISTEMA:", (530, 175),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (180, 180, 220), 1)
    cv2.putText(tela, status, (530, 215),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, cor_status, 3)

    # --- Temperatura ---
    cv2.putText(tela, f"TEMPERATURA", (530, 265),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (180, 180, 220), 1)
    cv2.putText(tela, f"{temperatura:.1f} C", (850, 265),
                cv2.FONT_HERSHEY_SIMPLEX, 0.85, cor_temperatura, 2)
    # Barra
    cv2.rectangle(tela, (530, 280), (1150, 310), (50, 50, 80), -1)
    cv2.rectangle(tela, (530, 280), (1150, 310), (80, 80, 130), 1)
    larg_temp = int(max(0, min((temperatura / 50.0) * 620, 620)))
    cv2.rectangle(tela, (530, 280), (530 + larg_temp, 310), cor_temperatura, -1)
    # Marcações ideais (20–30 °C)
    pos_20 = 530 + int((20 / 50.0) * 620)
    pos_30 = 530 + int((30 / 50.0) * 620)
    cv2.line(tela, (pos_20, 275), (pos_20, 315), (0, 200, 80), 1)
    cv2.line(tela, (pos_30, 275), (pos_30, 315), (0, 200, 80), 1)
    cv2.putText(tela, "20C", (pos_20 - 10, 330),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 200, 80), 1)
    cv2.putText(tela, "30C", (pos_30 - 10, 330),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 200, 80), 1)

    # --- Luminosidade ---
    cv2.putText(tela, f"LUMINOSIDADE", (530, 365),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (180, 180, 220), 1)
    cv2.putText(tela, f"{luminosidade:.0f} %", (900, 365),
                cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 220, 255), 2)
    # Barra
    cv2.rectangle(tela, (530, 380), (1150, 410), (50, 50, 80), -1)
    cv2.rectangle(tela, (530, 380), (1150, 410), (80, 80, 130), 1)
    larg_lux = int((luminosidade / 100.0) * 620)
    cv2.rectangle(tela, (530, 380), (530 + larg_lux, 410), (0, 220, 255), -1)

    # --- Mini-gráfico de Temperatura ---
    cv2.putText(tela, "HISTORICO TEMPERATURA", (530, 445),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (150, 150, 200), 1)
    graf_x1, graf_y1, graf_x2, graf_y2 = 530, 455, 1150, 545
    cv2.rectangle(tela, (graf_x1, graf_y1), (graf_x2, graf_y2), (50, 50, 80), -1)
    cv2.rectangle(tela, (graf_x1, graf_y1), (graf_x2, graf_y2), (80, 80, 130), 1)

    if len(historico_temp) >= 2:
        larg_graf = graf_x2 - graf_x1
        alt_graf = graf_y2 - graf_y1
        passo = larg_graf / MAX_HISTORICO
        for i in range(1, len(historico_temp)):
            t_prev = historico_temp[i - 1]
            t_curr = historico_temp[i]
            # Normaliza: 0°C = fundo, 50°C = topo
            y_prev = graf_y2 - int(((t_prev + 20) / 80.0) * alt_graf)
            y_curr = graf_y2 - int(((t_curr + 20) / 80.0) * alt_graf)
            x_prev = int(graf_x1 + (i - 1) * passo)
            x_curr = int(graf_x1 + i * passo)
            y_prev = max(graf_y1, min(graf_y2, y_prev))
            y_curr = max(graf_y1, min(graf_y2, y_curr))
            cv2.line(tela, (x_prev, y_prev), (x_curr, y_curr), cor_temperatura, 2)

    # ----------------------------------
    # ALERTAS
    # ----------------------------------
    cv2.rectangle(tela, (20, 600), (1180, 680), (35, 20, 20), -1)
    cv2.rectangle(tela, (20, 600), (1180, 680), (100, 40, 40), 1)

    if alertas:
        y_a = 635
        for i, alerta in enumerate(alertas):
            cv2.putText(tela, f"[!] {alerta}", (40 + i * 400, y_a),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    else:
        cv2.putText(tela, "Todos os sistemas operando normalmente.",
                    (40, 635), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 80), 2)

    # ----------------------------------
    # DATA E HORA
    # ----------------------------------
    agora = datetime.now().strftime("%d/%m/%Y  %H:%M:%S")
    cv2.putText(tela, agora, (900, 660),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (120, 120, 160), 1)

    # ----------------------------------
    # CONTROLES (rodapé)
    # ----------------------------------
    cv2.putText(tela, "ESC: sair" + ("  |  Q/A: temp +/-  |  W/S: lux +/-" if modo_simulacao else ""),
                (30, 693), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (80, 80, 100), 1)

    # ----------------------------------
    # EXIBIÇÃO
    # ----------------------------------
    cv2.imshow("Monitor Capsula Espacial - IOT GS 2026", tela)
    tecla = cv2.waitKey(200)  # Atualiza a cada 200ms

    if tecla == 27:  # ESC
        break

    # ----------------------------------
    # CONTROLES DE SIMULAÇÃO
    # ----------------------------------
    if modo_simulacao:
        if tecla == ord("q"):
            capsula["temperatura"] += 1
        elif tecla == ord("a"):
            capsula["temperatura"] -= 1
        elif tecla == ord("w"):
            capsula["luminosidade"] = min(100, capsula["luminosidade"] + 5)
        elif tecla == ord("s"):
            capsula["luminosidade"] = max(0, capsula["luminosidade"] - 5)

# ----------------------------------
# ENCERRAMENTO
# ----------------------------------
cv2.destroyAllWindows()
if not modo_simulacao:
    try:
        client.loop_stop()
        client.disconnect()
        print("[OK] MQTT desconectado.")
    except Exception:
        pass
print("[OK] Sistema encerrado.")