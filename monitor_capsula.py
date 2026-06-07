import cv2
import numpy as np
from datetime import datetime

# =====================================
# CONFIGURAÇÕES
# =====================================

modo_simulacao = True

capsula = {
    "temperatura": 25,
    "luminosidade": 75,
    "status": "NORMAL",
    "alertas": []
}

# =====================================
# LOOP PRINCIPAL
# =====================================

while True:

    # Tela principal
    tela = np.zeros((700, 1200, 3), dtype=np.uint8)
    tela[:] = (20, 20, 20)

    # =====================================
    # VALIDAÇÃO DOS DADOS
    # =====================================

    capsula["temperatura"] = max(
        -20,
        min(60, capsula["temperatura"])
    )

    capsula["luminosidade"] = max(
        0,
        min(100, capsula["luminosidade"])
    )

    temperatura = capsula["temperatura"]
    luminosidade = capsula["luminosidade"]

# =====================================
# ANÁLISE DE STATUS
# =====================================

    alertas = []

    # Cor da temperatura
    if temperatura < 10:
        cor_temperatura = (0, 0, 255)      # Vermelho
        status = "CRITICO"
        cor_status = (0, 0, 255)
        alertas.append("TEMPERATURA BAIXA")

    elif temperatura > 40:
        cor_temperatura = (0, 0, 255)
        status = "CRITICO"
        cor_status = (0, 0, 255)
        alertas.append("SUPERAQUECIMENTO")

    elif temperatura < 20:
        cor_temperatura = (0, 255, 255)    # Amarelo
        status = "ALERTA"
        cor_status = (0, 255, 255)
        alertas.append("TEMPERATURA ABAIXO DO IDEAL")

    elif temperatura > 30:
        cor_temperatura = (0, 255, 255)
        status = "ALERTA"
        cor_status = (0, 255, 255)
        alertas.append("TEMPERATURA ACIMA DO IDEAL")

    else:
        cor_temperatura = (0, 255, 0)      # Verde
        status = "NORMAL"
        cor_status = (0, 255, 0)

    # Avaliação da luminosidade

    if luminosidade < 15:

        alertas.append("ILUMINACAO INSUFICIENTE")

        # Se a temperatura estava normal,
        # o status geral vira alerta,
        # mas a barra de temperatura continua verde

        if status == "NORMAL":
            status = "ALERTA"
            cor_status = (0, 255, 255)

    capsula["status"] = status
    capsula["alertas"] = alertas

    # =====================================
    # TÍTULO
    # =====================================

    cv2.putText(
        tela,
        "MONITORAMENTO DA CAPSULA ESPACIAL",
        (250, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2
    )

    # =====================================
    # REPRESENTAÇÃO DA CÁPSULA
    # =====================================

    cv2.rectangle(
        tela,
        (50, 100),
        (500, 600),
        (255, 255, 255),
        3
    )

    cv2.putText(
        tela,
        "CAPSULA",
        (160, 350),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.6,
        (255, 255, 255),
        3
    )

    # Indicador visual

    cv2.circle(
        tela,
        (420, 150),
        25,
        cor_status,
        -1
    )

    # =====================================
    # PAINEL DE DADOS
    # =====================================

    cv2.rectangle(
        tela,
        (600, 100),
        (1150, 600),
        (255, 255, 255),
        2
    )

    cv2.putText(
        tela,
        f"Temperatura: {temperatura:.1f} C",
        (650, 180),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        2
    )

    cv2.putText(
        tela,
        f"Luminosidade: {luminosidade:.0f} %",
        (650, 260),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        2
    )

    cv2.putText(
        tela,
        f"STATUS: {status}",
        (650, 340),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        cor_status,
        3
    )

    # =====================================
    # BARRA DE TEMPERATURA
    # =====================================

    cv2.putText(
        tela,
        "TEMPERATURA",
        (650, 420),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.rectangle(
        tela,
        (650, 450),
        (1000, 490),
        (255, 255, 255),
        2
    )

    largura_temp = int(
        max(
            0,
            min((temperatura / 50) * 350, 350)
        )
    )

    cv2.rectangle(
        tela,
        (650, 450),
        (650 + largura_temp, 490),
        cor_temperatura,
        -1 
    )

    # =====================================
    # BARRA DE LUMINOSIDADE
    # =====================================

    cv2.putText(
        tela,
        "LUMINOSIDADE",
        (650, 530),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.rectangle(
        tela,
        (650, 560),
        (1000, 600),
        (255, 255, 255),
        2
    )

    largura_lux = int(
        (luminosidade / 100) * 350
    )

    cv2.rectangle(
        tela,
        (650, 560),
        (650 + largura_lux, 600),
        (255, 255, 0),
        -1
    )

    # =====================================
    # ALERTAS
    # =====================================

    y_alerta = 640

    for alerta in alertas:

        cv2.putText(
            tela,
            f"ALERTA: {alerta}",
            (50, y_alerta),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )

        y_alerta += 30

    # =====================================
    # DATA E HORA
    # =====================================

    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    cv2.putText(
        tela,
        agora,
        (780, 660),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (180, 180, 180),
        2
    )

    # =====================================
    # EXIBIÇÃO
    # =====================================

    cv2.imshow("Capsula Espacial", tela)

    tecla = cv2.waitKey(100)

    # ESC fecha
    if tecla == 27:
        break

    # =====================================
    # CONTROLES DE TESTE
    # =====================================

    if modo_simulacao:

        # Temperatura +

        if tecla == ord("q"):
            capsula["temperatura"] += 1

        # Temperatura -

        if tecla == ord("a"):
            capsula["temperatura"] -= 1

        # Luminosidade +

        if tecla == ord("w"):
            capsula["luminosidade"] += 5

        # Luminosidade -

        if tecla == ord("s"):
            capsula["luminosidade"] -= 5

cv2.destroyAllWindows()